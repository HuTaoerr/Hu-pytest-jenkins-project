// Jenkinsfile - 尝试在 Docker Agent 内复制结果到 Default Agent Workspace
pipeline {
    agent any // Default agent for post block

    environment {
        ALLURE_RESULTS_DIR = 'allure-results'
        // Jenkins 会提供 WORKSPACE 环境变量，这是当前 Agent 的 Workspace 路径
        // 对于 Default Agent，它通常是 /var/jenkins_home/workspace/my-pytest-ci-job
        // 对于 Docker Agent，它通常是 /var/jenkins_home/workspace/my-pytest-ci-job@<suffix>
    }

    stages {
        stage('Clean Workspace') {
            steps {
                echo 'Cleaning workspace before starting...'
                cleanWs() // Cleans the current agent's workspace (here, agent any's)
            }
        }

        stage('Checkout Code') {
            options { skipDefaultCheckout true } // Skip default checkout
            steps {
                echo 'Checking out code after cleaning...'
                checkout scm // Explicit checkout on agent any
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
                echo "Running inside Python container: ${sh(script: 'python --version', returnStdout: true).trim()}"
                echo "Working directory inside container: ${sh(script: 'pwd', returnStdout: true).trim()}"
                sh 'pip install --upgrade pip'
                sh 'pip install -r requirements.txt --verbose'
                sh 'pip list | grep allure-pytest || echo "allure-pytest not found in pip list"'

                echo 'Running Pytest with Allure results only...'
                sh "pytest --alluredir=${ALLURE_RESULTS_DIR}"

                echo "Checking if ${ALLURE_RESULTS_DIR} directory exists INSIDE container..."
                sh "if [ -d ${ALLURE_RESULTS_DIR} ]; then echo '${ALLURE_RESULTS_DIR} directory found:'; ls -la ${ALLURE_RESULTS_DIR}/; else echo '${ALLURE_RESULTS_DIR} directory NOT found!'; fi"

                // **核心修改：在 Docker Agent 容器内，复制结果到 Default Agent 的 Workspace 路径**
                // ${env.WORKSPACE} 在这个 sh 步骤中是 Docker Agent 的 Workspace 路径
                // 获取 Default Agent 的 Workspace 路径是关键，通常可以通过 Jenkins 环境变量或约定获取
                // Default Agent 的 Workspace 通常是去掉 @<suffix> 的路径
                // Let's try copying from current WORKSPACE/allure-results to WORKSPACE without suffix
                sh """
                    #!/bin/bash
                    # Current Docker Agent Workspace (e.g., /var/jenkins_home/workspace/my-pytest-ci-job@2)
                    CURRENT_WORKSPACE="${env.WORKSPACE}"

                    # Attempt to derive Default Agent Workspace (e.g., /var/jenkins_home/workspace/my-pytest-ci-job)
                    # This relies on Jenkins' naming convention and shared volume.
                    # Be cautious: This might not work in all Jenkins/Docker setups.
                    DEFAULT_WORKSPACE_BASE="\$(echo "\${CURRENT_WORKSPACE}" | sed 's/@.*/')" # Remove @suffix
                    # Alternative: Use a fixed known path if you configured Remote File System Root explicitly
                    # DEFAULT_WORKSPACE_BASE="/var/jenkins_home/workspace/my-pytest-ci-job" # If you know the exact path

                    echo "Attempting to copy allure-results from \$CURRENT_WORKSPACE to \$DEFAULT_WORKSPACE_BASE"

                    # Ensure the target directory exists on the shared volume
                    mkdir -p "\${DEFAULT_WORKSPACE_BASE}/${ALLURE_RESULTS_DIR}"

                    # Copy contents - Use rsync for efficiency, or cp
                    # cp -r "\${CURRENT_WORKSPACE}/${ALLURE_RESULTS_DIR}/" "\${DEFAULT_WORKSPACE_BASE}/${ALLURE_RESULTS_DIR}/"
                    # Or just copy the files if directory already exists and needs overwrite
                    cp -r "\${CURRENT_WORKSPACE}/${ALLURE_RESULTS_DIR}" "\${DEFAULT_WORKSPACE_BASE}/"

                    echo "Copy attempt finished. Checking target directory contents on Docker Agent side (should reflect shared volume)..."
                    if [ -d "\${DEFAULT_WORKSPACE_BASE}/${ALLURE_RESULTS_DIR}" ]; then
                        echo "Target directory exists:"
                        ls -la "\${DEFAULT_WORKSPACE_BASE}/${ALLURE_RESULTS_DIR}/"
                    else
                        echo "Target directory NOT found after copy attempt!"
                    fi

                """
            }
        }
    }

    post {
        always {
            echo 'Pipeline finished. Publishing Allure report...'

            // **无需 unstash 步骤**
            // Try-catch block for allure() step
            catchError(buildResult: 'SUCCESS', stageResult: 'UNSTABLE') {
                echo 'Attempting to publish Allure report...'
                // allure() 步骤现在会在 Default Agent 的 Workspace 中查找结果文件
                // 如果复制成功，allure-results 目录应该已经在这里了
                allure(
                    results: [[path: env.ALLURE_RESULTS_DIR]] // 查找 ${env.WORKSPACE}/allure-results
                )
            }

        }
        success { echo 'Pipeline succeeded!' }
        failure { echo 'Pipeline failed!' }
        unstable { echo 'Pipeline is unstable!' }
        aborted { echo 'Pipeline was aborted!' }
    }
}