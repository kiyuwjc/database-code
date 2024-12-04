# 使用官方的 Python 基础镜像
FROM ubuntu:20.04

# 设置工作目录
WORKDIR /app

# 将本地的 Python 应用代码复制到容器中
COPY cache_server.py /app/cache_server.py

# 安装 Python 依赖项
RUN pip install flask redis

# 安装 Redis 服务和 jq
RUN apt-get update && \
    apt-get install -y redis-server python3 python-pip && \
    rm -rf /var/lib/apt/lists/*

# 配置 Redis 为后台启动
RUN sed -i 's/^daemonize no$/daemonize yes/' /etc/redis/redis.conf

# 暴露 Flask 端口和 Redis 端口
EXPOSE 9527 9528 9529 6379

# 启动 Redis 服务并启动 Flask 应用
# 使用 supervisord 来管理多个进程
CMD redis-server /etc/redis/redis.conf && \
    python3 cache_server.py 9527 & \
    python3 cache_server.py 9528 & \
    python3 cache_server.py 9529
