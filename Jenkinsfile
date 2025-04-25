// Jenkinsfile
pipeline {
    agent any // 在任何可用的 Jenkins agent 上运行

    environment {
         // 定义环境变量，如果需要的话
         PYTHON_VERSION = '3.9' // 示例
    }

    stages {
        stage('Checkout') { // 阶段1：检出代码
            steps {
                echo 'Checking out code from GitHub...'
                // 从配置的 SCM (Source Code Management) 中检出代码
                checkout scm
            }
        }

        stage('Setup Environment') { // 阶段2：设置环境并安装依赖
            steps {
                echo "Setting up Python environment..."
                // 注意：在 Docker 容器中运行 Jenkins 时，容器内可能需要安装 Python 和 pip
                // 更好的做法是使用带 Python 的 Docker agent，但这里为了简单，
                // 我们假设基础镜像或手动在容器内安装了 Python 和 pip
                // sh 'apt-get update && apt-get install -y python3 python3-pip python3-venv' // 示例：在 Debian/Ubuntu 基础镜像中安装
                sh 'python3 -m venv venv_jenkins' // 创建虚拟环境
                sh '. venv_jenkins/bin/activate && pip install --upgrade pip' // 激活并升级pip (Linux/macOS 语法)
                // 对于 Windows agent，激活命令是 '.\venv_jenkins\Scripts\activate'
                sh '. venv_jenkins/bin/activate && pip install -r requirements.txt' // 安装依赖
                // Windows: sh '.\venv_jenkins\Scripts\activate && pip install -r requirements.txt'

            }
        }

        stage('Run Tests') { // 阶段3：运行 Pytest 测试
            steps {
                echo 'Running Pytest...'
                 // 在虚拟环境中执行 pytest
                sh '. venv_jenkins/bin/activate && pytest --junitxml=report.xml'
                // Windows: sh '.\venv_jenkins\Scripts\activate && pytest --junitxml=report.xml'
            }
        }
    }

    post { // 构建后操作
        always { // 无论成功失败总是执行
            echo 'Pipeline finished.'
             // 归档测试报告，需要 JUnit Plugin
            junit 'report.xml'
            // 清理工作区（可选）
            // cleanWs()
        }
        success {
            echo 'Pipeline succeeded!'
            // 可以在这里添加成功的通知，如邮件、Slack 等
        }
        failure {
            echo 'Pipeline failed!'
            // 可以在这里添加失败的通知
        }
    }
}