// Jenkinsfile - 使用顶层标签指定自定义 Docker Agent
pipeline {
    // **在顶层使用自定义 Agent 的标签**
    // 'python-allure-agent' 是您在 Jenkins Docker Cloud 中为自定义镜像设置的标签
    agent { label 'python-allure-agent' }

    options {
        // **如果希望 cleanWs() 在 checkout 之前，则继续使用 skipDefaultCheckout true**
        // **否则，如果 cleanWs() 在 checkout 之后运行也可以接受，则可以移除 skipDefaultCheckout true**
        // 对于新 Job 或确保干净，skipDefaultCheckout true + 显式 checkout 更好
        skipDefaultCheckout true
        // 其他 options...
    }

    environment {
        ALLURE_RESULTS_DIR = 'allure-results'
    }

    stages {
        // 清理工作区 Stage
        stage('Clean Workspace') {
            steps {
                echo 'Cleaning workspace before starting...'
                cleanWs() // 调用 cleanWs 步骤
            }
        }

        // 显式 Checkout 阶段 (因为上面使用了 skipDefaultCheckout true)
        stage('Checkout Code') {
             // 这个 Stage 在顶层 agent (python-allure-agent) 上运行
            steps {
                echo 'Checking out code after cleaning...'
                checkout scm // 手动执行 Checkout
            }
        }

        // 阶段: 构建和测试 (也在顶层 agent 容器中执行)
        stage('Build and Test') {
            // **无需再次指定 agent { docker {...} }**
            steps {
                // 这些步骤将在顶层 agent (你的自定义容器) 中执行
                echo "Running on custom agent: ${sh(script: 'hostname', returnStdout: true).trim()}"
                echo "Working directory: ${sh(script: 'pwd', returnStdout: true).trim()}"

                echo "Setting up Python environment and installing dependencies..."
                // 由于自定义镜像有 python/venv 和 pip，可以直接用
                sh '''
                    python3 -m venv venv
                    # 激活虚拟环境（在多行sh脚本中，source 不会影响后续独立的 sh 命令，
                    # 但使用 venv/bin/... 路径更可靠）
                    # source venv/bin/activate

                    # 使用虚拟环境中的pip安装依赖
                    venv/bin/pip install --no-cache-dir -r requirements.txt
                '''

                echo 'Running Pytest with Allure results only...'
                // 由于 allure-pytest 已安装，Allure CLI 在 PATH 中 (因为你的自定义镜像已设置)，可以直接用
                sh "venv/bin/pytest tests/ --alluredir=${ALLURE_RESULTS_DIR}"

                // Debug: Check results
                echo "Checking if ${ALLURE_RESULTS_DIR} directory exists on agent..."
                sh "if [ -d ${ALLURE_RESULTS_DIR} ]; then echo '${ALLURE_RESULTS_DIR} directory found:'; ls -la ${ALLURE_RESULTS_DIR}/; else echo '${ALLURE_RESULTS_DIR} directory NOT found!'; fi"

                // **无需 stash 步骤**，因为 post 块在同一个 agent 上执行，可以直接访问 Workspace
                // echo "Stashing Allure results..."
                // stash includes: "${ALLURE_RESULTS_DIR}/**", name: 'allure-results-stash'
            }
        }

        // 你可以根据需要添加更多阶段，它们都会在这个自定义 agent 容器中执行
        // stage('Deploy') {
        //     steps {
        //         // Deploy commands...
        //     }
        // }
    }

    // 构建后操作 (也在顶层 agent 上执行)
    post {
        always {
            echo 'Pipeline finished. Publishing Allure report...'

            // **无需 unstash 步骤**
            // try {
            //     unstash 'allure-results-stash'
            //     ...
            // } catch (...) { ... }

            // Publish Allure report using catchError
            // 这个 allure() 步骤在与测试 Stage 相同的 agent 上执行
            // 它可以直接访问 $WORKSPACE/${ALLURE_RESULTS_DIR}
            // 并且 Allure CLI 在此 agent 上可用 (因为是自定义镜像的一部分)
            catchError(buildResult: 'SUCCESS', stageResult: 'UNSTABLE') {
                echo 'Attempting to publish Allure report...'
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
    }
}