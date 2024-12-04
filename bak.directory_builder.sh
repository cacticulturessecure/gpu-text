#!/bin/bash

# directory_builder.sh
echo "Creating GPU Text Service project structure..."

# Create main project directories
mkdir -p app/{models,services,core,utils} tests .github/workflows

# Create __init__.py files
touch app/__init__.py
touch app/models/__init__.py
touch app/services/__init__.py
touch app/core/__init__.py
touch app/utils/__init__.py
touch tests/__init__.py

# Create core application files
cat >app/main.py <<'EOF'
from fastapi import FastAPI
from app.core.config import settings
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title=settings.APP_NAME)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
EOF

# Create configuration files
cat >app/core/config.py <<'EOF'
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    APP_NAME: str = "GPU-Text-Service"
    DEBUG: bool = False
    API_V1_STR: str = "/api/v1"
    
    OLLAMA_HOST: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama2"
    DEFAULT_TEMPERATURE: float = 0.7
    MAX_TOKENS: int = 2000
    
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    CACHE_TTL: int = 3600
    
    ALLOWED_ORIGINS: List[str] = ["http://localhost:8001"]
    
    class Config:
        env_file = ".env"

settings = Settings()
EOF

# Create Docker files
cat >Dockerfile <<'EOF'
FROM nvidia/cuda:11.8.0-runtime-ubuntu22.04

ENV PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    CUDA_HOME=/usr/local/cuda \
    PATH=/usr/local/cuda/bin:$PATH \
    LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH

RUN apt-get update -y && \
    apt-get install -y git ffmpeg software-properties-common && \
    add-apt-repository -y ppa:deadsnakes/ppa && \
    apt-get install -y python3.10 python3-pip && \
    pip3 install setuptools-rust && \
    pip3 install torch==2.1.2 torchvision==0.16.2 torchaudio==2.1.2 --index-url https://download.pytorch.org/whl/cu118 && \
    pip3 install colorama ctranslate2==3.24.0 rich pydantic

RUN apt-get update -y && \
    apt-get install -y \
        curl \
        wget \
        build-essential \
        redis-server && \
    curl -fsSL https://ollama.ai/install.sh | sh && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt /tmp/requirements.txt
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt

WORKDIR /app
COPY . /app/

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
EOF

# Create docker-compose.yml
cat >docker-compose.yml <<'EOF'
version: '3.8'

services:
  gpu-text-service:
    build: .
    ports:
      - "8080:8080"
      - "11434:11434"
    volumes:
      - ./app:/app/app
      - ollama-models:/root/.ollama
    environment:
      - CUDA_VISIBLE_DEVICES=0
      - OLLAMA_HOST=http://localhost:11434
      - REDIS_HOST=localhost
      - REDIS_PORT=6379
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]

volumes:
  ollama-models:
EOF

# Create GitHub Actions workflows
mkdir -p .github/workflows

# Development workflow
cat >.github/workflows/dev.yml <<'EOF'
name: Development CI/CD

on:
  push:
    branches: [ dev ]
  pull_request:
    branches: [ dev ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.10'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    - name: Run tests
      run: |
        pytest tests/

  build-and-push:
    needs: test
    runs-on: ubuntu-latest
    if: github.event_name == 'push'
    steps:
    - uses: actions/checkout@v2
    
    - name: Login to Docker Hub
      uses: docker/login-action@v1
      with:
        username: ${{ secrets.DOCKERHUB_USERNAME }}
        password: ${{ secrets.DOCKERHUB_TOKEN }}
    
    - name: Build and push
      uses: docker/build-push-action@v2
      with:
        context: .
        push: true
        tags: ${{ secrets.DOCKERHUB_USERNAME }}/gpu-text-service:dev
EOF

# Staging workflow
cat >.github/workflows/staging.yml <<'EOF'
name: Staging CI/CD

on:
  push:
    branches: [ staging ]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    
    - name: Login to Docker Hub
      uses: docker/login-action@v1
      with:
        username: ${{ secrets.DOCKERHUB_USERNAME }}
        password: ${{ secrets.DOCKERHUB_TOKEN }}
    
    - name: Build and push
      uses: docker/build-push-action@v2
      with:
        context: .
        push: true
        tags: ${{ secrets.DOCKERHUB_USERNAME }}/gpu-text-service:staging
    
    - name: Deploy to staging
      uses: appleboy/ssh-action@master
      with:
        host: ${{ secrets.STAGING_HOST }}
        username: ${{ secrets.STAGING_USERNAME }}
        key: ${{ secrets.STAGING_SSH_KEY }}
        script: |
          docker pull ${{ secrets.DOCKERHUB_USERNAME }}/gpu-text-service:staging
          docker-compose -f docker-compose.staging.yml up -d
EOF

# Production workflow
cat >.github/workflows/main.yml <<'EOF'
name: Production CI/CD

on:
  push:
    branches: [ main ]
    tags:
      - 'v*'

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    
    - name: Login to Docker Hub
      uses: docker/login-action@v1
      with:
        username: ${{ secrets.DOCKERHUB_USERNAME }}
        password: ${{ secrets.DOCKERHUB_TOKEN }}
    
    - name: Build and push
      uses: docker/build-push-action@v2
      with:
        context: .
        push: true
        tags: |
          ${{ secrets.DOCKERHUB_USERNAME }}/gpu-text-service:latest
          ${{ secrets.DOCKERHUB_USERNAME }}/gpu-text-service:${{ github.ref_name }}
    
    - name: Deploy to production
      uses: appleboy/ssh-action@master
      with:
        host: ${{ secrets.PROD_HOST }}
        username: ${{ secrets.PROD_USERNAME }}
        key: ${{ secrets.PROD_SSH_KEY }}
        script: |
          docker pull ${{ secrets.DOCKERHUB_USERNAME }}/gpu-text-service:latest
          docker-compose -f docker-compose.prod.yml up -d
EOF

# Create requirements.txt
cat >requirements.txt <<'EOF'
fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.4.2
pydantic-settings==2.0.3
python-dotenv==1.0.0
httpx==0.25.2
redis==5.0.1
loguru==0.7.2
asyncio==3.4.3
aioredis==2.0.1
prometheus-client==0.19.0
pytest==7.4.3
pytest-asyncio==0.21.1
EOF

# Create .env.example
cat >.env.example <<'EOF'
DEBUG=false
API_V1_STR=/api/v1
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama2
DEFAULT_TEMPERATURE=0.7
MAX_TOKENS=2000
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
CACHE_TTL=3600
EOF

# Create .gitignore
cat >.gitignore <<'EOF'
__pycache__/
*.py[cod]
*$py.class
*.so
.env
.venv
env/
venv/
ENV/
.idea/
.vscode/
*.log
.pytest_cache/
EOF

# Make the script executable
chmod +x directory_builder.sh

echo "Project structure created successfully!"
