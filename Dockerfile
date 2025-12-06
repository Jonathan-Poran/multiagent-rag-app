FROM python:3.11-slim

WORKDIR /app

# Install Node.js and npm
RUN apt-get update && apt-get install -y \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Install mermaid-cli globally
RUN npm install -g @mermaid-js/mermaid-cli

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080
# Make sure EB's PORT env variable is used
CMD ["sh", "-c", "exec uvicorn src.server:app --host 0.0.0.0 --port ${PORT:-8080}"]
