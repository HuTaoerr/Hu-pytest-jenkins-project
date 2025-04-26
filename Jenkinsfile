// Jenkinsfile - 移除重复 checkout 并确保 Clean 在 Checkout 之前 (高级)
pipeline {
    // 使用自定义 Agent 如果可能，或者继续使用 any
    agent any // 或 agent { label 'python-allure-agent' }

    options {
        // 跳过默认的隐式 SCM checkout
        skipDefaultCheckout true
        // 其他 options...
    }

    environment {
        ALLURE_RESULTS_DIR = 'allure-results'
    }

    stages {
        stage('Clean Workspace') {
            steps {
                echo 'Cleaning workspace before starting...'
                cleanWs()
            }
        }

        stage('Checkout Code') { // 新增显式 Checkout 阶段
             // 这个 Stage 在顶层 agent 上运行
            steps {
                echo 'Checking out code after cleaning...'
                checkout scm // 手动执行 Checkout
            }
        }


        stage('Build and Test') {
            agent {
                docker {
                    image 'python:3.9-slim'
                    args '-u root'
                }
            }
            steps {
                // ... 安装依赖, 运行 pytest ...
                echo 'Running Pytest with Allure results only...'
                sh "pytest --alluredir=${ALLURE_RESULTS_DIR}"

                // Debug: Check results
                echo "Checking if ${ALLURE_RESULTS_DIR} directory exists INSIDE container..."
                sh "if [ -d ${ALLURE_RESULTS_DIR} ]; then echo '${ALLURE_RESULTS_DIR} directory found:'; ls -la ${ALLURE_RESULTS_DIR}/; else echo '${ALLURE_RESULTS_DIR} directory NOT found!'; fi"

                // Stash results
                echo "Stashing Allure results..."
                stash includes: "${ALLURE_RESULTS_DIR}/**", name: 'allure-results-stash'
            }
        }
    }

    post {
        always {
            echo 'Pipeline finished. Unstashing and Publishing Allure report...'

            // Unstash results

            unstash 'allure-results-stash'
            echo "Unstashed Allure results to ${sh(script: 'pwd', returnStdout: true).trim()}"
            // Debug: Check unstash results
            sh "if [ -d ${ALLURE_RESULTS_DIR} ]; then echo '${ALLURE_RESULTS_DIR} directory found after unstash:'; ls -la ${ALLURE_RESULTS_DIR}/; else echo '${ALLURE_RESULTS_DIR} directory NOT found after unstash!'; fi"


            // Publish report
            catchError(buildResult: 'SUCCESS', stageResult: 'UNSTABLE') {
               echo 'Attempting to publish Allure report...'
               allure(
                        results: [[path: env.ALLURE_RESULTS_DIR]]
                    )

        }
        unstable { echo 'Pipeline is unstable!' }
    }
}