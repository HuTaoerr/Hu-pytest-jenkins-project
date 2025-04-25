// Jenkinsfile
// Jenkinsfile - 使用 Stage 级别的 Docker Agent
pipeline {
    // 默认 agent 为 any，允许 Jenkins 在任何可用节点上开始执行
    agent any

    // 全局环境变量（如果需要的话）
    // environment {
    //     MY_GLOBAL_VAR = 'some_value'
    // }

    stages {
        // 阶段 1: 检出代码 (在默认 agent 上执行)
        stage('Checkout') {
            steps {
                echo 'Checking out code from GitHub...'
                checkout scm
            }
        }

        // 阶段 2: 运行测试 (在指定的 Docker Agent 容器中执行)
        // 将环境准备和测试合并到一个使用相同 agent 的阶段，避免多次启动容器
        stage('Build and Test') {
            // 指定这个阶段使用 Docker Agent
            agent {
                docker {
                    image 'python:3.9-slim' // 使用官方 Python 镜像
                    // label 'docker-agent' // 如果你配置了特定的 Docker agent 标签
                    // args '-v /path/on/host:/path/in/container' // 如果需要挂载额外目录
                    // args '-u root --entrypoint=' // 如果后续步骤需要 root 权限或遇到问题再尝试
                }
            }
            steps {
                echo "Running inside Python container: ${sh(script: 'python --version', returnStdout: true).trim()}"
                echo "Working directory: ${sh(script: 'pwd', returnStdout: true).trim()}" // 显示当前工作目录

                // 步骤 2.1: 安装依赖
                echo "Installing dependencies..."
                sh 'pip install --upgrade pip'
                // 添加详细输出，方便调试 pip install
                sh 'pip install -r requirements.txt --verbose'
                // 验证安装了 allure-pytest
                sh 'pip list | grep allure-pytest || echo "allure-pytest not found in pip list"'

                // 步骤 2.2: 运行 Pytest 测试并生成 Allure 结果
                echo 'Running Pytest with Allure results...'
                // 执行 pytest，如果失败则让 stage 失败
                sh 'pytest --alluredir=allure-results --junitxml=report.xml'

                // 步骤 2.3: (调试用) 检查 allure-results 是否生成
                echo "Checking if allure-results directory exists..."
                sh 'ls -la' // 查看当前目录内容
                // 检查 allure-results 目录是否存在及其内容
                sh 'if [ -d allure-results ]; then echo "allure-results directory found:"; ls -la allure-results/; else echo "allure-results directory NOT found!"; fi'
            }
        }
        // 你可以根据需要添加更多阶段，比如 'Deploy' 等
    }

    // 构建后操作 (在默认 agent 上执行)
    post {
        always {
            echo 'Pipeline finished. Publishing reports...'

            // 检查 allure-results 是否真的存在，避免插件报错
            // 注意：这里的 sh 也在默认 agent 执行，它看不到 Docker Agent 内的文件系统！
            // 因此，我们需要在 Docker Agent 内部生成报告，或者用更高级的方式传递结果。
            // 简单的做法是在 Test 阶段结束后直接生成报告并存档

            // **修改：将报告生成和存档移到 Test 阶段内部或使用 stash/unshash**
            // **或者直接尝试发布，如果前面检查了 allure-results 目录存在**

            // 尝试发布 Allure 报告
            // 使用 try-catch 增加健壮性
            catchError(buildResult: 'SUCCESS', stageResult: 'UNSTABLE') {
                echo 'Attempting to publish Allure report...'
                allure(
                    results: ['allure-results'], // 指向 pytest 生成的结果目录
                    tool: 'Default Allure'       // 确保这个名字与 Jenkins Tools 配置匹配
                )
            }

            // 尝试发布 JUnit 报告
            catchError(buildResult: 'SUCCESS', stageResult: 'UNSTABLE') {
                 echo 'Attempting to publish JUnit report...'
                junit 'report.xml' // 指向 pytest 生成的 xml 文件
            }

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