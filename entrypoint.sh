#!/bin/bash
# entrypoint.sh

# Start Ollama in the background
ollama serve &

# Wait for Ollama to be ready
while ! curl -s http://localhost:11434/api/tags >/dev/null; do
  echo "Waiting for Ollama to be ready..."
  sleep 1
done

# Pull the model if it doesn't exist
if ! ollama list | grep -q "llama3.1:70b"; then
  echo "Pulling llama3.1:70b model..."
  ollama pull llama3.1:70b
fi

# Start the FastAPI application
exec uvicorn app.main:app --host 0.0.0.0 --port 8080
