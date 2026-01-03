# 使用官方 Python 运行时作为基础镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# 复制 requirements 文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY . .

# 创建必要的目录
RUN mkdir -p /app/temp_email_uploads && \
    mkdir -p /app/qikan/output_pdfs && \
    chmod -R 755 /app/temp_email_uploads && \
    chmod -R 755 /app/qikan/output_pdfs

# 收集静态文件（如果需要）
# RUN python manage.py collectstatic --noinput

# 暴露端口
EXPOSE 8000

# 启动命令（生产环境使用 Gunicorn）
CMD ["gunicorn", "qk.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4", "--timeout", "120"]

