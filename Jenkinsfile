pipeline {
    agent any

    environment {
        // 设置 Python 和 Allure 的版本
        PYTHON_VERSION = '3.9-slim'
        ALLURE_VERSION = '2.19.0'
    }

    stages {
        stage('Checkout') {
            steps {
                echo 'Checking out code from GitHub...'
                checkout scm
            }
        }

        stage('Install Dependencies') {
            steps {
                script {
                    // 安装 Python 和相关工具
                    sh '''
                        apt-get update
                        apt-get install -y python3 python3-pip wget unzip openjdk-11-jre-headless
                        python3 -m pip install --upgrade pip
                        python3 -m pip install pytest allure-pytest
                    '''
                }
            }
        }

        stage('Run Tests') {
            steps {
                script {
                    // 运行 Pytest 并生成 Allure 结果
                    sh '''
                        python3 -m pytest --alluredir=allure-results
                    '''
                }
            }
        }

        stage('Generate Allure Report') {
            steps {
                script {
                    // 安装 Allure 命令行工具
                    sh '''
                        wget https://repo.maven.apache.org/maven2/io/qameta/allure/allure-commandline/${env.ALLURE_VERSION}/allure-commandline-${env.ALLURE_VERSION}-bin.zip -O /tmp/allure.zip
                        unzip /tmp/allure.zip -d /opt/
                        ln -s /opt/allure-${env.ALLURE_VERSION}/bin/allure /usr/bin/allure
                        rm /tmp/allure.zip
                    '''
                    // 生成 Allure 报告
                    sh '''
                        allure generate allure-results -o allure-report
                    '''
                }
            }
        }
    }

    post {
        always {
            echo 'Pipeline finished. Attempting to publish Allure report...'

            // 发布 Allure 报告
            allure(
                results: [[path: 'allure-results']],
                reportBuildPolicy: 'ALWAYS',
                includeProperties: false,
                jdk: ''
            )

            // 清理工作区（可选）
            // cleanWs()
        }
    }
}