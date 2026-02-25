FROM python:3.9-slim

WORKDIR /app

# 复制依赖文件并安装
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制所有代码
COPY . .

# 关键：转换换行符 + 添加执行权限
RUN sed -i 's/\r$//' ./startup.sh && chmod +x ./startup.sh

# 执行脚本
CMD ["./startup.sh"]