pipeline {
    // 使用您在 Jenkins UI Docker Template 中设置的标签
    agent { label 'python-allure-agent' }

    options {
        // 根据需要保留 skipDefaultCheckout true 和手动 checkout
        // 如果您希望 cleanWs 发生在 checkout 之前，保留这两项
        skipDefaultCheckout true
        // 其他 options...
    }

    environment {
        ALLURE_RESULTS_DIR = 'allure-results'
    }

    stages {
        // Clean Workspace stage (推荐保留)
        stage('Clean Workspace') {
            steps {
                echo 'Cleaning workspace before starting...'
                cleanWs()
            }
        }

        // Checkout Code stage (如果您使用了 skipDefaultCheckout true)
        stage('Checkout Code') {
            steps {
                echo 'Checking out code after cleaning...'
                checkout scm
            }
        }

        // Build and Test stage (现在将在顶层 agent 上运行)
        stage('Build and Test') {
            // 移除 agent { docker {...} } 块
            steps {
                // 这些步骤现在将在您的自定义 Docker Agent 容器中执行
                echo "Running on custom agent: ${sh(script: 'hostname', returnStdout: true).trim()}"
                echo "Working directory: ${sh(script: 'pwd', returnStdout: true).trim()}" // 应该显示 Remote File System Root 下的 Job 目录

                echo "Setting up Python environment and installing dependencies..."
                // 使用 venv 并安装依赖（您的自定义镜像已包含 Python/Pip/Venv）
                sh '''
                    python3 -m venv venv
                    venv/bin/pip install --no-cache-dir -r requirements.txt
                '''

                echo 'Running Pytest with Allure results only...'
                // 运行 Pytest 并生成 Allure 结果
                sh "venv/bin/pytest tests/ --alluredir=${ALLURE_RESULTS_DIR}"

                // Debug: Check results directory (在自定义 Agent 的 Workspace 中)
                echo "Checking if ${ALLURE_RESULTS_DIR} directory exists on agent..."
                sh "if [ -d ${ALLURE_RESULTS_DIR} ]; then echo '${ALLURE_RESULTS_DIR} directory found:'; ls -la ${ALLURE_RESULTS_DIR}/; else echo '${ALLURE_RESULTS_DIR} directory NOT found!'; fi"

                // **移除 stash 步骤**，因为 post 块在同一个 Agent 上运行
                // stash ...
            }
        }

        // 其他 stages...
    }

    // Post Actions (现在将在顶层 agent 上执行)
    post {
        always {
            echo 'Pipeline finished. Publishing Allure report...'

            // **移除 unstash 步骤**
            // try { unstash ... } catch {...}

            // Publish Allure report (在同一个 Agent 的 Workspace 中查找结果)
            catchError(buildResult: 'SUCCESS', stageResult: 'UNSTABLE') {
                echo 'Attempting to publish Allure report...'
                // Allure step 现在可以直接访问 Workspace/${ALLURE_RESULTS_DIR}
                allure(
                    results: [[path: env.ALLURE_RESULTS_DIR]] // 正确的语法
                    // 其他参数...
                )
            }

        }
        // 其他 post conditions...
        success { echo 'Pipeline succeeded!' }
        failure { echo 'Pipeline failed!' }
        unstable { echo 'Pipeline is unstable!' }
        aborted { echo 'Pipeline was aborted!' }
    }
}