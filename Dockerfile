# Dockerfile
# 使用官方 Jenkins LTS 镜像作为基础
FROM jenkins/jenkins:lts-jdk17

# 切换到 root 用户以安装软件
USER root

# 安装 Docker CLI 所需的依赖
RUN apt-get update && apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release \
    sudo \
    python3 \
    python3-pip \
    python3-venv \
    git \
    openjdk-11-jre

# 添加 Docker 的官方 GPG 密钥
RUN mkdir -p /etc/apt/keyrings && curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# 设置 Docker 的 APT 仓库
RUN echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian \
  $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

# 更新包列表并安装 Docker CLI
# 注意：我们只安装 docker-ce-cli，不需要完整的 docker-ce (引擎)
RUN apt-get update && apt-get install -y docker-ce-cli

# 3. 安装 Allure Commandline Tool
# 从 Allure GitHub Release 下载最新版本
# 请检查 Allure 的最新版本，并替换下面的 URL
# 例如：https://github.com/allure-framework/allure-commandline/releases/download/2.24.1/allure-2.24.1.zip
# 使用 wget 或 curl 下载 zip 包，并解压到 /opt/allure
# 建议使用 zip 包，因为更常见且跨平台
ARG ALLURE_VERSION="2.27.0" # 定义 Allure 版本作为构建参数
ENV ALLURE_HOME="/opt/allure-${ALLURE_VERSION}" # 设置 Allure 的安装目录环境变量

RUN apt-get update -y && \
    apt-get install -y --no-install-recommends unzip wget && \ # 安装 unzip 和 wget
    mkdir -p /opt && \ # 创建 /opt 目录
    wget https://github.com/allure-framework/allure-commandline/releases/download/${ALLURE_VERSION}/allure-${ALLURE_VERSION}.zip -O /tmp/allure.zip && \ # 下载 Allure 到 /tmp
    unzip /tmp/allure.zip -d /opt && \ # 解压到 /opt
    rm /tmp/allure.zip && \ # 删除下载的 zip 包
    # 将 Allure 的 bin 目录添加到系统的 PATH 环境变量中，这样可以直接在命令行使用 'allure' 命令
    # 方法1: 创建一个 symlink (推荐)
    ln -s ${ALLURE_HOME}/bin/allure /usr/local/bin/allure


# （可选）将 jenkins 用户添加到 docker 组，这样 jenkins 用户也能执行 docker 命令
# 注意：这需要 docker 组存在，通常在安装 docker-ce 时创建，仅安装 cli 可能没有
# 更好的做法是让 Pipeline 通过挂载的 socket 通信，执行者仍是 jenkins 用户，权限由 socket 控制
# RUN usermod -aG docker jenkins

RUN usermod -aG root jenkins

# 清理 APT 缓存以减小镜像体积
RUN rm -rf /var/lib/apt/lists/*

# 切换回 jenkins 用户
USER jenkins