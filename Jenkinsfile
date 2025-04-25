pipeline {
    // 指定整个 Pipeline 使用一个包含 Python 的 Docker 镜像作为执行环境
    agent {
        docker {
            image 'python:3.9-slim' // 使用官方 Python 3.9 slim 镜像，体积较小
            // 你可以根据需要选择其他 Python 版本，如 'python:3.10' 或 'python:3.11-slim'
            // slim 版本通常不包含很多系统工具，但 apt-get 通常可用（基于 Debian）
            // 如果需要特定系统库，可能需要构建自己的 Docker 镜像或使用更完整的 Python 镜像
            args '-u root --entrypoint=' // 可选：有时需要以 root 运行容器内的命令，特别是如果需要 apt-get install 其他库
                                        // --entrypoint='' 覆盖默认 entrypoint，允许直接运行 sh
        }
    }

    environment {
         // 可以定义环境变量，如果需要的话
    }

    stages {
        stage('Checkout') {
            steps {
                echo 'Checking out code from GitHub...'
                // checkout scm 会自动在指定的 agent (Docker 容器) 内的工作区执行
                checkout scm
            }
        }

        stage('Setup Dependencies') { // 修改阶段名称
            steps {
                echo "Python environment provided by agent. Installing dependencies..."

                // --- 现在 Python 3 和 pip 已经由 agent 提供了 ---
                // --- 不需要再 apt-get install python3 ---

                // 更新 pip 并安装依赖
                sh 'pip install --upgrade pip'
                sh 'pip install -r requirements.txt'

                // （可选）如果 Python 镜像是 slim 版本，可能缺少某些系统库
                // 如果 pip install 报缺少编译环境等错误，可能需要先安装
                // sh 'apt-get update && apt-get install -y build-essential gcc ...' // 示例
            }
        }

        stage('Run Tests with Allure') {
            steps {
                echo 'Running Pytest with Allure results...'
                // 直接运行 pytest，因为它已经在 agent 环境的 PATH 中
                // 注意：这里不再需要激活虚拟环境，因为整个容器环境就是隔离的
                sh 'pytest --alluredir=allure-results --junitxml=report.xml'
            }
        }
    }

    post {
        always {
            echo 'Pipeline finished. Publishing reports...'
            // Allure 和 JUnit 报告步骤保持不变
            allure(
                results: ['allure-results'],
                installation: 'Default Allure' // 确保这个名字匹配 Jenkins Tools 配置
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