// Jenkinsfile - 修正 Allure 参数和移除 JUnit/重复 Checkout，并使用正确的 catchError 语法
pipeline {
    // 默认 agent 为 any，用于隐式 SCM checkout、cleanWs、unstash 和 post block
    // SCM checkout 步骤会自动在 agent any 上执行，无需显式 stage
    agent any

    environment {
        // 定义 pytest 结果文件和 allure 报告的输出目录，相对于 Jenkins Workspace
        ALLURE_RESULTS_DIR = 'allure-results'
    }

    stages {
        // 新增 清理工作区 阶段
        // 放在第一个 stage 确保每次构建从干净状态开始
        stage('Clean Workspace') {
            steps {
                echo 'Cleaning workspace before starting...'
                cleanWs() // 调用 cleanWs 步骤
            }
        }

        // Implicit SCM Checkout happens after agent is allocated and before the first stage begins.
        // Clean Workspace runs *after* this initial checkout in this structure.

        // 阶段: 构建和测试 (在指定的 Docker Agent 容器中执行)
        stage('Build and Test') {
            agent {
                docker {
                    image 'python:3.9-slim'
                    // 临时解决 Pip 权限问题：以 root 用户运行容器
                    // 日志显示这种方式奏效了，但长期仍推荐自定义镜像
                    args '-u root'

                    // Docker Agent 模式下，Jenkins 会将宿主机的 Workspace 目录
                    // 自动挂载到容器内部，并在容器内将工作目录切换到此挂载点。
                    // allure-results 目录会生成在此共享的 Workspace 目录中。
                }
            }
            steps {
                echo "Running inside Python container: ${sh(script: 'python --version', returnStdout: true).trim()}"
                echo "Working directory inside container: ${sh(script: 'pwd', returnStdout: true).trim()}"

                echo "Installing dependencies..."
                sh 'pip install --upgrade pip'
                // 添加详细输出，方便调试 pip install
                sh 'pip install -r requirements.txt --verbose'
                // 验证安装了 allure-pytest
                sh 'pip list | grep allure-pytest || echo "allure-pytest not found in pip list"'

                echo 'Running Pytest with Allure results only...'
                // 移除 --junitxml=report.xml 参数
                sh "pytest --alluredir=${ALLURE_RESULTS_DIR}"

                // 步骤: (调试用) 检查 allure-results 是否生成
                echo "Checking if ${ALLURE_RESULTS_DIR} directory exists INSIDE container..."
                sh "if [ -d ${ALLURE_RESULTS_DIR} ]; then echo '${ALLURE_RESULTS_DIR} directory found:'; ls -la ${ALLURE_RESULTS_DIR}/; else echo '${ALLURE_RESULTS_DIR} directory NOT found!'; fi"

                // **Stash Allure results**
                echo "Stashing Allure results..."
                // Ensure the path to stash is correct relative to the Docker Agent's workspace
                // Since pytest wrote to ALLURE_RESULTS_DIR, this is correct.
                stash includes: "${ALLURE_RESULTS_DIR}/**", name: 'allure-results-stash'
                // 使用一个唯一的名字用于 stash 和 unstash
            }
        }
    }

    // 构建后操作 (在默认 agent 上执行)
    post {
        always {
            echo 'Pipeline finished. Unstashing and Publishing Allure report...'

            // **Unstash Allure results**
            // 这个步骤必须在 allure() 步骤之前执行
            // 如果 unstash 失败（例如，因为 stash 没有运行），post 块将在这里失败
            // 除非将 unstash 本身也包裹在 catchError 中。通常允许 unstash 失败更合理。
            unstash 'allure-results-stash' // 使用 stash 时使用的名字

            echo "Unstashed Allure results to ${sh(script: 'pwd', returnStdout: true).trim()}"
            // Debug: 再次检查 unstash 后 allure-results 是否存在于默认 agent 的 workspace
            sh "if [ -d ${ALLURE_RESULTS_DIR} ]; then echo '${ALLURE_RESULTS_DIR} directory found after unstash:'; ls -la ${ALLURE_RESULTS_DIR}/; else echo '${ALLURE_RESULTS_DIR} directory NOT found after unstash!'; fi"


            // **Publish Allure report using catchError**
            // 将 allure() 步骤包裹在 catchError 中
            // 如果 allure 步骤失败，构建状态将根据 buildResult/stageResult 参数设置，而不会导致整个 post block 失败
            catchError(buildResult: 'SUCCESS', stageResult: 'UNSTABLE') {
                echo 'Attempting to publish Allure report using corrected syntax...'
                // Allure Step 现在可以在默认 agent 的 Workspace 中找到 unstash 的结果文件
                allure(
                    results: [[path: env.ALLURE_RESULTS_DIR]] // 正确的语法
                    // 可以添加其他参数，例如 keepLongStories: true, reportBuildPolicy: 'UNSTABLE' 等
                )
            }

            // 在所有后置操作完成后清理工作区
            echo 'Pipeline finished. Performing cleanup...'
            cleanWs()

        }
        // 其他后置操作，例如 email 通知等...
        // success { echo 'Pipeline succeeded!' } // 这些会被顶层 post conditions 覆盖
        // failure { echo 'Pipeline failed!' }
         unstable {
            echo 'Pipeline is unstable (possibly due to test failures or report publishing issues)!'
         }
         // 如果需要，可以添加其他条件，例如：
         // fixed { echo 'Build is now fixed!' }
         // changed { echo 'Build status changed!' }
    }
}