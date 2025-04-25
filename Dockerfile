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
    sudo

# 添加 Docker 的官方 GPG 密钥
RUN mkdir -p /etc/apt/keyrings && curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# 设置 Docker 的 APT 仓库
RUN echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian \
  $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

# 更新包列表并安装 Docker CLI
# 注意：我们只安装 docker-ce-cli，不需要完整的 docker-ce (引擎)
RUN apt-get update && apt-get install -y docker-ce-cli

# （可选）将 jenkins 用户添加到 docker 组，这样 jenkins 用户也能执行 docker 命令
# 注意：这需要 docker 组存在，通常在安装 docker-ce 时创建，仅安装 cli 可能没有
# 更好的做法是让 Pipeline 通过挂载的 socket 通信，执行者仍是 jenkins 用户，权限由 socket 控制
# RUN usermod -aG docker jenkins

RUN usermod -aG root jenkins

# 清理 APT 缓存以减小镜像体积
RUN rm -rf /var/lib/apt/lists/*

# 切换回 jenkins 用户
USER jenkins