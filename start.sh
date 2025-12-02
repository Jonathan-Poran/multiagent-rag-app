#!/bin/bash
# Startup script for AWS Elastic Beanstalk

# Get port from environment or default to 8080
PORT=${PORT:-8080}

echo "Starting application on port $PORT"
echo "Environment variables:"
echo "  PORT=$PORT"
echo "  OPENAI_API_KEY=${OPENAI_API_KEY:0:10}..." # Show first 10 chars only

# Start uvicorn
exec uvicorn server.server:app --host 0.0.0.0 --port $PORT

