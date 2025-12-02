FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080
# Make sure EB's PORT env variable is used
CMD ["sh", "-c", "exec uvicorn server.server:app --host 0.0.0.0 --port ${PORT:-8080}"]
