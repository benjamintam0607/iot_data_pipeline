FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY schema.sql .
COPY src/ ./src/
COPY scripts/ ./scripts/

ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["python", "-m", "src.main"]
