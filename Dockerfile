FROM nvidia/cuda:11.8.0-runtime-ubuntu22.04

ENV PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    CUDA_HOME=/usr/local/cuda \
    PATH=/usr/local/cuda/bin:$PATH \
    LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH \
    PYTHONPATH=/app \
    OLLAMA_MODEL=llama3.1:70b \
    DEFAULT_TEMPERATURE=0.7 \
    MAX_TOKENS=2000

# Install system dependencies
RUN apt-get update -y && \
    apt-get install -y \
        git \
        ffmpeg \
        software-properties-common \
        curl \
        wget \
        build-essential && \
    add-apt-repository -y ppa:deadsnakes/ppa && \
    apt-get install -y python3.10 python3-pip && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip3 install setuptools-rust && \
    pip3 install torch==2.1.2 torchvision==0.16.2 torchaudio==2.1.2 --index-url https://download.pytorch.org/whl/cu118 && \
    pip3 install colorama ctranslate2==3.24.0 rich pydantic

# Install Ollama (using the official installation URL)
RUN curl -fsSL https://ollama.com/install.sh | sh && \
    ollama --version  # Verify installation

# Install application dependencies
COPY requirements.txt /tmp/
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt

WORKDIR /app
COPY . /app/

# Make entrypoint script executable
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8080 11434

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

ENTRYPOINT ["/entrypoint.sh"]
