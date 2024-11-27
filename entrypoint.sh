#!/bin/bash

# Start Ollama in the background
ollama serve &

# Wait for Ollama to be ready
while ! curl -s http://localhost:11434/api/tags >/dev/null; do
    echo "Waiting for Ollama to be ready..."
    sleep 1
done

echo "Pulling llama3.1:70b model..."
# Pull the model from ollama.com/library
ollama pull llama3.1:70b

# Phase 2 - Redis Check (commented out)
# while ! nc -z $REDIS_HOST $REDIS_PORT; do
#     echo "Waiting for Redis..."
#     sleep 1
# done

# Start the FastAPI application
exec uvicorn app.main:app --host 0.0.0.0 --port 8080
