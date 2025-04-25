// Jenkinsfile
pipeline {
    // 1. 修改：将顶层 agent 改回 any
    agent any

    // 2. 移除：删除空的 environment 块

    stages {
        stage('Checkout') {
            // 这个阶段会在默认 agent (Jenkins master 或配置的静态 agent) 上执行
            steps {
                echo 'Checking out code from GitHub...'
                checkout scm
            }
        }

        // 3. 修改：为需要 Python 的 Stage 单独指定 Docker Agent
        stage('Setup Dependencies') {
            agent {
                docker {
                    image 'python:3.9-slim'
                    // args '-u root --entrypoint=' // 如果需要 root 或遇到问题再取消注释
                }
            }
            steps {
                echo "Installing dependencies inside Python container..."
                // 在 Docker Agent 容器内执行
                sh 'pip install --upgrade pip'
                sh 'pip install -r requirements.txt'
            }
        }

        // 4. 修改：为需要 Python 的 Stage 单独指定 Docker Agent
        stage('Run Tests with Allure') {
            agent {
                docker {
                    image 'python:3.9-slim' // 使用与上一个 stage 相同的镜像确保环境一致
                    // args '-u root --entrypoint='
                }
            }
            steps {
                echo 'Running Pytest with Allure results inside Python container...'
                // 在 Docker Agent 容器内执行
                sh 'pytest --alluredir=allure-results --junitxml=report.xml'
            }
        }
    }

    post {
        always {
            echo 'Pipeline finished. Publishing reports...'
            // 5. 修改：将 installation 改为 tool
            allure(
                results: ['allure-results'],
                tool: 'Default Allure' // 使用 'tool' 参数指定名称
            )
            junit 'report.xml'
        }
        success {
            echo 'Pipeline succeeded!'
        }
        failure {
            echo 'Pipeline failed!'
        }
    }
}



// // Jenkinsfile
// pipeline {
//     agent any
//
//     environment {
//          PYTHON_VERSION = '3.9'
//     }
//
//     stages {
//         stage('Checkout') {
//             steps {
//                 echo 'Checking out code from GitHub...'
//                 checkout scm
//             }
//         }
//
//         stage('Setup Environment') {
//             steps {
//                 echo "Setting up Python environment..."
//                 echo "Updating package lists and installing Python 3..."
//                 // 在 apt-get 命令前加上 sudo
//                 sh 'sudo apt-get update && sudo apt-get install -y python3 python3-pip python3-venv'
//
//                 // 验证安装 (可选，但有助于调试)
//                 sh 'python3 --version'
//                 sh 'pip3 --version'
//
//                 sh 'python3 -m venv venv_jenkins'
//                 sh '. venv_jenkins/bin/activate && pip install --upgrade pip'
//                 sh '. venv_jenkins/bin/activate && pip install -r requirements.txt'
//             }
//         }
//
//         stage('Run Tests with Allure') { // 修改 Stage 名称 (可选)
//             steps {
//                 echo 'Running Pytest with Allure results...'
//                  // 修改 pytest 命令：
//                  // 1. 添加 --alluredir=allure-results
//                  // 2. 移除或保留 --junitxml (如果还想保留 JUnit 报告可以留着)
//                 sh '. venv_jenkins/bin/activate && pytest --alluredir=allure-results --junitxml=report.xml' // 同时生成两种报告
//                 // 或者只生成 Allure:
//                 // sh '. venv_jenkins/bin/activate && pytest --alluredir=allure-results'
//             }
//         }
//     }
//
//     post {
//         always {
//             echo 'Pipeline finished. Publishing reports...'
//
//             // --- 添加 Allure 报告发布步骤 ---
//             allure(
//                 // 指定包含 Allure 结果的目录 (相对于工作空间)
//                 results: ['allure-results'],
//                 // (可选) 指定你在全局工具配置中设置的 Allure Commandline 的名称
//                 // installation: 'Default Allure',
//                 // (可选) 指定报告标题
//                 // reportBuildPolicy: 'ALWAYS', // 总是生成报告，即使构建失败
//                 // includeProperties: false // 是否包含 Jenkins 环境变量等属性
//             )
//
//             // --- 保留或移除 JUnit 报告发布 ---
//             junit 'report.xml' // 如果 pytest 命令中保留了 --junitxml
//
//             // 清理工作区（可选）
//             // cleanWs()
//         }
//         success {
//             echo 'Pipeline succeeded!'
//         }
//         failure {
//             echo 'Pipeline failed!'
//         }
//     }
// }