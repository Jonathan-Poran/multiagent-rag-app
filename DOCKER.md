# Docker Setup Guide

## Prerequisites

- Docker and Docker Compose installed
- `.env` file with required environment variables

## Environment Variables

Create a `.env` file in the root directory with:

```env
OPENAI_API_KEY=your_openai_api_key
MONGODB_URI=mongodb://mongo:27017
MONGODB_DB_NAME=multiagent_rag
LANGCHAIN_API_KEY=your_langchain_key (optional)
LANGCHAIN_TRACING_V2=false (optional)
LANGCHAIN_PROJECT=multiagent-rag-app (optional)
```

## Running with Docker Compose

### Start all services (app + MongoDB):

```bash
docker-compose up --build
```

### Run in detached mode:

```bash
docker-compose up -d --build
```

### Stop services:

```bash
docker-compose down
```

### View logs:

```bash
docker-compose logs -f app
```

## Running with Docker only

### Build the image:

```bash
docker build -t multiagent-rag-app .
```

### Run the container:

```bash
docker run -p 8000:8000 \
  -e OPENAI_API_KEY=your_key \
  -e MONGODB_URI=your_mongodb_uri \
  -e MONGODB_DB_NAME=multiagent_rag \
  multiagent-rag-app
```

### Run with .env file:

```bash
docker run -p 8000:8000 --env-file .env multiagent-rag-app
```

## Access the Application

- Web UI: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

## MongoDB

When using docker-compose, MongoDB is automatically started and accessible at `mongodb://mongo:27017` from within the app container.

To connect from your host machine:
- Host: `localhost`
- Port: `27017`

## Troubleshooting

### Check if containers are running:

```bash
docker-compose ps
```

### Restart a specific service:

```bash
docker-compose restart app
```

### Remove volumes (clears MongoDB data):

```bash
docker-compose down -v
```

### View container logs:

```bash
docker logs multiagent-rag-app
```

