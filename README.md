GPU Text Service
A high-performance text processing service using Ollama and CUDA-accelerated models, designed for distributed AI processing architecture.
Overview
The GPU Text Service is part of a larger distributed AI processing system, specifically handling text-based operations using Large Language Models (LLMs) through Ollama. It's built to run on NVIDIA GPU infrastructure and optimized for high-throughput processing.
Features

🚀 CUDA-accelerated text processing
🤖 Ollama integration for LLM operations
💾 Redis caching for improved performance
🔄 Streaming response support
📊 Performance monitoring
🔒 Secure API endpoints
🎯 Optimized for distributed systems

Prerequisites

NVIDIA GPU with CUDA support
Docker and Docker Compose
NVIDIA Container Toolkit
At least 16GB GPU memory
Ubuntu 22.04 or compatible OS

Quick Start

Clone the repository:

bashCopygit clone https://github.com/your-org/gpu-text-service.git
cd gpu-text-service

Configure environment variables:

bashCopycp .env.example .env
# Edit .env with your configuration

Build and start the service:

bashCopydocker-compose up -d

Verify the service is running:

bashCopycurl http://localhost:8080/health
API Endpoints
Chat Completion
httpCopyPOST /api/v1/chat
Content-Type: application/json

{
    "messages": [
        {
            "role": "system",
            "content": "You are a helpful assistant."
        },
        {
            "role": "user",
            "content": "Hello, how are you?"
        }
    ],
    "temperature": 0.7,
    "max_tokens": 2000
}
Streaming Response
httpCopyPOST /api/v1/chat/stream
Content-Type: application/json

{
    "messages": [...],
    "stream": true
}
Configuration
Key configuration options in .env:
envCopy# Service Configuration
DEBUG=false
API_V1_STR=/api/v1

# Ollama Settings
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama2
DEFAULT_TEMPERATURE=0.7
MAX_TOKENS=2000

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
CACHE_TTL=3600
Architecture
plaintextCopy[Client] → [API Gateway]
              ↓
    [GPU Text Service (This Service)]
              ↓
     [Ollama] ↔ [Redis Cache]
              ↓
        [CUDA/GPU Layer]
Development
Local Development Setup

Create a Python virtual environment:

bashCopypython -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

Install dependencies:

bashCopypip install -r requirements.txt

Run the service:

bashCopyuvicorn app.main:app --reload --port 8080
Running Tests
bashCopypytest tests/
Monitoring
The service exposes Prometheus metrics at /metrics and includes:

Request latency
GPU memory usage
Cache hit/miss rates
Request queue length

Production Deployment
Resource Requirements

Minimum 16GB GPU RAM
4 CPU cores
16GB system RAM
50GB storage

Docker Commands
bashCopy# Build the image
docker-compose build

# Start the service
docker-compose up -d

# View logs
docker-compose logs -f

# Scale service (if needed)
docker-compose up -d --scale gpu-text-service=2
Performance Tuning
GPU Optimization

Set CUDA_VISIBLE_DEVICES to control GPU allocation
Adjust batch sizes based on GPU memory
Monitor GPU memory usage with nvidia-smi

Cache Configuration

Adjust CACHE_TTL based on your use case
Monitor cache hit rates
Configure Redis persistence if needed

Troubleshooting
Common issues and solutions:

GPU Memory Issues

bashCopy# Check GPU memory usage
nvidia-smi

# Clear GPU cache
docker-compose restart gpu-text-service

Service Won't Start

bashCopy# Check logs
docker-compose logs gpu-text-service

# Verify NVIDIA runtime
docker info | grep -i runtime
Contributing

Fork the repository
Create a feature branch
Commit changes
Submit a pull request
