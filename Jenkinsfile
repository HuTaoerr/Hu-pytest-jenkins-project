// Jenkinsfile
pipeline {
    agent any

    environment {
         PYTHON_VERSION = '3.9'
    }

    stages {
        stage('Checkout') {
            steps {
                echo 'Checking out code from GitHub...'
                checkout scm
            }
        }

        stage('Setup Environment') {
            steps {
                echo "Setting up Python environment..."
                sh 'apt-get update && apt-get install -y python'
                sh 'python3 -m venv venv_jenkins'
                sh '. venv_jenkins/bin/activate && pip install --upgrade pip'
                sh '. venv_jenkins/bin/activate && pip install -r requirements.txt'
            }
        }

        stage('Run Tests with Allure') { // 修改 Stage 名称 (可选)
            steps {
                echo 'Running Pytest with Allure results...'
                 // 修改 pytest 命令：
                 // 1. 添加 --alluredir=allure-results
                 // 2. 移除或保留 --junitxml (如果还想保留 JUnit 报告可以留着)
                sh '. venv_jenkins/bin/activate && pytest --alluredir=allure-results --junitxml=report.xml' // 同时生成两种报告
                // 或者只生成 Allure:
                // sh '. venv_jenkins/bin/activate && pytest --alluredir=allure-results'
            }
        }
    }

    post {
        always {
            echo 'Pipeline finished. Publishing reports...'

            // --- 添加 Allure 报告发布步骤 ---
            allure(
                // 指定包含 Allure 结果的目录 (相对于工作空间)
                results: ['allure-results'],
                // (可选) 指定你在全局工具配置中设置的 Allure Commandline 的名称
                // installation: 'Default Allure',
                // (可选) 指定报告标题
                // reportBuildPolicy: 'ALWAYS', // 总是生成报告，即使构建失败
                // includeProperties: false // 是否包含 Jenkins 环境变量等属性
            )

            // --- 保留或移除 JUnit 报告发布 ---
            junit 'report.xml' // 如果 pytest 命令中保留了 --junitxml

            // 清理工作区（可选）
            // cleanWs()
        }
        success {
            echo 'Pipeline succeeded!'
        }
        failure {
            echo 'Pipeline failed!'
        }
    }
}