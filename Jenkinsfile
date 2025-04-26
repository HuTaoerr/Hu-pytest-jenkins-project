// Jenkinsfile - 使用 stash/unstash 传递 Allure 结果
pipeline {
    agent any // post 块将在此 agent 上执行，需要在这里 unstash

    environment {
        ALLURE_RESULTS_DIR = 'allure-results'
    }

    stages {
        // 删除显式 Checkout Stage

        stage('Build and Test') {
            agent {
                docker {
                    image 'python:3.9-slim'
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

                // **新增: Stash Allure results**
                echo "Stashing Allure results..."
                stash includes: "${ALLURE_RESULTS_DIR}/**", name: 'allure-results'
                // 'name' 参数给 stash 起个名字，在 unstash 时使用
            }
        }
    }

    post {
        always {
            echo 'Pipeline finished. Unstashing and Publishing Allure report...'

            // **新增: Unstash Allure results**
            // 这个步骤在默认 agent (any) 上执行
            try {
                unstash 'allure-results' // 解包之前 stash 的文件到当前 Workspace
                echo "Unstashed Allure results to ${sh(script: 'pwd', returnStdout: true).trim()}"
                sh "if [ -d ${ALLURE_RESULTS_DIR} ]; then echo '${ALLURE_RESULTS_DIR} directory found after unstash:'; ls -la ${ALLURE_RESULTS_DIR}/; else echo '${ALLURE_RESULTS_DIR} directory NOT found after unstash!'; fi"

                // 尝试发布 Allure 报告
                catchError(buildResult: 'SUCCESS', stageResult: 'UNSTABLE') {
                    echo 'Attempting to publish Allure report using corrected syntax...'
                    // Allure Step 现在可以在默认 agent 的 Workspace 中找到 unstash 的结果文件
                    allure(
                        results: [[path: env.ALLURE_RESULTS_DIR]]
                    )
                }
            } catch (Exception e) {
                echo "Error unstashing or publishing Allure report: ${e}"
                // 可以选择标记构建不稳定
                currentBuild.result = 'UNSTABLE'
            }

        }
        success { echo 'Pipeline succeeded!' }
        failure { echo 'Pipeline failed!' }
    }
}