# 使用官方轻量级 Python 镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 防止 Python 生成 .pyc 文件
ENV PYTHONDONTWRITEBYTECODE=1
# 确保控制台输出不被缓存 (日志实时显示)
ENV PYTHONUNBUFFERED=1

# 修改为国内源 (阿里云)，加快构建速度
RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources

# 安装系统依赖 (比如编译某些库需要的 gcc)
# 如果你的项目以后用到 cv2 等库，也在这里加
RUN apt-get update && apt-get install -y \
    build-essential \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

# 先复制依赖文件 (利用 Docker 缓存层机制)
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 复制项目代码
COPY . .

# 暴露端口
EXPOSE 8000

# 启动命令
# 使用生产级配置：host=0.0.0.0 确保外部可访问
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]