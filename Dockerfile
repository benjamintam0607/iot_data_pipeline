FROM python:3.11-slim

WORKDIR /app

# 复制依赖并安装
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制代码
COPY schema.sql .
COPY src/ ./src/
COPY scripts/ ./scripts/

# 复制启动脚本并赋予执行权限
COPY startup.sh .
RUN chmod +x startup.sh

ENV PYTHONUNBUFFERED=1

# 设置入口点为启动脚本
ENTRYPOINT ["./startup.sh"]