// Jenkinsfile
// 使用 Stage 级别的 Docker Agent (优化 Allure Only)
pipeline {
    // 默认 agent 为 any，允许 Jenkins 在任何可用节点上开始执行
    agent any

    stages {
        stage('Checkout') {
            steps {
                echo 'Checking out code from GitHub...'
                checkout scm
            }
        }

        stage('Build and Test') {
            agent {
                docker {
                    image 'python:3.9-slim'

                    // 挂载工作区并设置工作目录为 /app，以 root 用户身份运行
                    args "-v ${WORKSPACE}:/app -w /app -u root"

                    // 使用当前 Jenkins Workspace 作为容器内的工作目录，这是默认且推荐的
                    // 确保容器内的用户对这个目录有写权限
//                     args '-u root --entrypoint=' // 如果后续步骤需要 root 权限或遇到问题再尝试
                }
            }
            steps {
                echo "Running inside Python container: ${sh(script: 'python --version', returnStdout: true).trim()}"
                echo "Working directory inside container: ${sh(script: 'pwd', returnStdout: true).trim()}" // 显示当前工作目录 (容器内)

                // 清理工作区中的 allure-results 和 allure-report 目录，新增
                sh 'rm -rf allure-results allure-report'


                echo "Installing dependencies..."
                sh 'pip install --upgrade pip'
                sh 'pip install -r requirements.txt --verbose'
                sh 'pip list | grep allure-pytest || echo "allure-pytest not found in pip list"'

                // 步骤 2.2: 运行 Pytest 测试并只生成 Allure 结果
                echo 'Running Pytest with Allure results only...'
                sh 'pytest --alluredir=allure-results'

                // 步骤 2.3: (调试用) 检查 allure-results 是否生成在容器内
                echo "Checking if allure-results directory exists INSIDE container..."
                sh 'if [ -d allure-results ]; then echo "allure-results directory found:"; ls -la allure-results/; else echo "allure-results directory NOT found!"; fi'


                // 在 Stage 结束时，allure-results 应该通过 Docker 卷挂载同步到宿主机的 Jenkins Workspace
            }
        }
    }

    post {
        always {
            echo 'Pipeline finished. Attempting to publish Allure report...'

            // 这个 allure 步骤在默认 agent (any) 上执行
            // 它需要能够访问宿主机的 Jenkins Workspace，以及能够调用 Allure CLI (通过 Global Tool Config 或其他方式)
            // allure() 步骤会自动查找 allure-results 目录，并调用 Allure CLI 生成并展示报告
            catchError(buildResult: 'SUCCESS', stageResult: 'UNSTABLE') {
                echo 'Attempting to publish Allure report...'
                allure(
                    results: [[path: 'allure-results']], // 指向 pytest 生成的结果目录 (相对于 Workspace)
                    reportBuildPolicy: 'ALWAYS', // 总是生成报告
                )
            }


            // 清理工作区（可选，会清理宿主机的 Workspace，包括 allure-results）
            // 如果你希望构建历史保留报告，可能需要小心 cleanWs() 的位置或使用 archiveArtifacts

            // 在所有后置操作完成后清理工作区
//             echo 'Pipeline finished. Performing cleanup...'
//             cleanWs()
        }
        success {
            echo 'Pipeline succeeded!'
        }
        failure {
            echo 'Pipeline failed!'
        }
    }
}