#!/bin/bash

echo "Starting GPU Text Service..."

# Kill any existing processes
pkill ollama
pkill uvicorn
screen -ls | grep -o '[0-9]*\.ollama' | cut -d. -f1 | xargs -I{} screen -X -S {} quit
screen -ls | grep -o '[0-9]*\.fastapi' | cut -d. -f1 | xargs -I{} screen -X -S {} quit

# Start Ollama
echo "Starting Ollama..."
screen -dmS ollama bash -c 'ollama serve'

# Wait for Ollama service to be ready
timeout=180 # 3 minutes for service to start
counter=0
echo "Waiting for Ollama service to be ready..."
while ! curl -s http://localhost:11434/api/tags >/dev/null; do
  sleep 1
  counter=$((counter + 1))
  if [ $counter -ge $timeout ]; then
    echo "Timeout waiting for Ollama service. Checking logs..."
    exit 1
  fi
  echo "Attempt $counter of $timeout..."
done

echo "Ollama service is ready!"

# Verify model is available or pull it
if ! ollama list | grep -q "llama3.1:70b"; then
  echo "Pulling llama3.1:70b model..."
  echo "This may take up to 10 minutes..."
  ollama pull llama3.1:70b
fi

# Verify model is loaded
echo "Verifying model load..."
echo "This may take up to 10 minutes for first inference..."
timeout=600 # 10 minutes for model load
counter=0
echo "Sending test inference to verify model load..."
curl -s -X POST http://localhost:11434/api/chat -d '{
    "model": "llama3.1:70b",
    "messages": [{"role": "user", "content": "hi"}],
    "stream": false
}' >/dev/null &
CURL_PID=$!

while kill -0 $CURL_PID 2>/dev/null; do
  sleep 10
  counter=$((counter + 10))
  if [ $counter -ge $timeout ]; then
    echo "Timeout waiting for model load. Check GPU memory and logs."
    kill $CURL_PID 2>/dev/null
    exit 1
  fi
  echo "Still loading model... ($counter seconds)"
  nvidia-smi | grep "MiB" # Show GPU memory usage
done

echo "Model is loaded and ready!"

# Start FastAPI
echo "Starting FastAPI..."
export PYTHONPATH=/app
screen -dmS fastapi bash -c 'cd /app && uvicorn app.main:app --host 0.0.0.0 --port 8080 --log-level debug'

# Wait for FastAPI
timeout=60 # 1 minute for FastAPI
counter=0
echo "Waiting for FastAPI to be ready..."
while ! curl -s http://localhost:8080/health >/dev/null; do
  sleep 1
  counter=$((counter + 1))
  if [ $counter -ge $timeout ]; then
    echo "Timeout waiting for FastAPI. Checking logs..."
    exit 1
  fi
  echo "Attempt $counter of $timeout..."
done

echo -e "\nAll services are running!"
echo -e "\nScreen sessions:"
screen -ls

echo -e "\nService status:"
echo "1. Ollama API:"
curl -s http://localhost:11434/api/tags
echo -e "\n2. FastAPI:"
curl -s http://localhost:8080/health

echo -e "\nGPU Memory Usage:"
nvidia-smi | grep "MiB"

echo -e "\nTo view logs:"
echo "tail -f fastapi.log    # For FastAPI logs"
echo "tail -f ollama.log     # For Ollama logs"

echo -e "\nTo attach to screens:"
echo "screen -r ollama    # For Ollama screen"
echo "screen -r fastapi   # For FastAPI screen"
echo "(Use Ctrl+A+D to detach from screen)"
