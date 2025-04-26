// Jenkinsfile - 修正 Allure 参数和移除 JUnit/重复 Checkout，并使用正确的 catchError 语法，确保花括号完整
pipeline {
    // 默认 agent 为 any，用于隐式 SCM checkout、cleanWs、unstash 和 post block
    agent any

    options {
        // 跳过默认的隐式 SCM checkout
        skipDefaultCheckout true
        // 其他 options...
        // 例如，如果希望构建失败时也尝试 unstash/allure，可能不需要在 unstash 或 allure 的 catchError 中设置 buildResult
        // 可以依赖 post always 块的执行，并通过 unstable/failure 块设置最终状态
    }

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

        // 显式 Checkout 阶段 (因为上面使用了 skipDefaultCheckout true)
        stage('Checkout Code') {
            // 这个 Stage 在顶层 agent (any) 上运行
            steps {
                echo 'Checking out code after cleaning...'
                checkout scm // 手动执行 Checkout
            }
        }

        // 阶段: 构建和测试 (在指定的 Docker Agent 容器中执行)
        stage('Build and Test') {
            agent {
                docker {
                    image 'python:3.9-slim'
                    // 临时解决 Pip 权限问题：以 root 用户运行容器
                    args '-u root'
                }
            }
            steps {
                echo "Running inside Python container: ${sh(script: 'python --version', returnStdout: true).trim()}"
                echo "Working directory inside container: ${sh(script: 'pwd', returnStdout: true).trim()}"

                echo "Installing dependencies..."
                sh 'pip install --upgrade pip'
                sh 'pip install -r requirements.txt --verbose'
                sh 'pip list | grep allure-pytest || echo "allure-pytest not found in pip list"'

                echo 'Running Pytest with Allure results only...'
                sh "pytest --alluredir=${ALLURE_RESULTS_DIR}"

                echo "Checking if ${ALLURE_RESULTS_DIR} directory exists INSIDE container..."
                sh "if [ -d ${ALLURE_RESULTS_DIR} ]; then echo '${ALLURE_RESULTS_DIR} directory found:'; ls -la ${ALLURE_RESULTS_DIR}/; else echo '${ALLURE_RESULTS_DIR} directory NOT found!'; fi"

                // **Stash Allure results**
                echo "Stashing Allure results..."
                // Stash the results from the Docker Agent's workspace
                stash includes: "${ALLURE_RESULTS_DIR}/**", name: 'allure-results-stash'
            }
        }
    }

    // 构建后操作 (在默认 agent 上执行)
    post {
        always {
            echo 'Pipeline finished. Unstashing and Publishing Allure report...'

            // **Unstash Allure results**
            // 必须在 allure() 步骤之前执行
            // 将 unstash 放在 try-catch 中，即使 unstash 失败（比如 stash 没运行），也不中断 post 块的后续步骤（如清理或其他报告）

                unstash 'allure-results-stash' // 使用 stash 时使用的名字
                echo "Unstashed Allure results to ${sh(script: 'pwd', returnStdout: true).trim()}"
                // Debug: 再次检查 unstash 后 allure-results 是否存在于默认 agent 的 workspace
                sh "if [ -d ${ALLURE_RESULTS_DIR} ]; then echo '${ALLURE_RESULTS_DIR} directory found after unstash:'; ls -la ${ALLURE_RESULTS_DIR}/; else echo '${ALLURE_RESULTS_DIR} directory NOT found after unstash!'; fi"

                // **Publish Allure report using catchError**
                // 将 allure() 步骤包裹在 catchError 中
                catchError(buildResult: 'SUCCESS', stageResult: 'UNSTABLE') {
                    echo 'Attempting to publish Allure report using corrected syntax...'
                    // Allure Step 现在可以在默认 agent 的 Workspace 中找到 unstash 的结果文件
                    allure(
                        results: [[path: env.ALLURE_RESULTS_DIR]] // 正确的语法
                        // 其他参数...
                    )
                }


        }
        // 这些 post conditions 会在 'always' 块执行后，根据构建的最终状态触发
        success {
            echo 'Pipeline succeeded!'
        }
        failure {
            echo 'Pipeline failed!'
        }
         unstable {
            echo 'Pipeline is unstable (possibly due to test failures or report publishing issues)!'
         }
         aborted {
            echo 'Pipeline was aborted!'
         }
         // 如果需要，可以添加其他条件，例如：
         // fixed { echo 'Build is now fixed!' }
         // changed { echo 'Build status changed!' }
    } // <--- 闭合 post 块的花括号
} // <--- 闭合 pipeline 块的花括号