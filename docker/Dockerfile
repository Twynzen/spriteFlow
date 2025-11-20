# SpriteFlow Docker Image
# Optimizado para RunPod GPU Cloud
# Base: PyTorch 2.0.1 + CUDA 11.8 + Ubuntu 22.04

FROM runpod/pytorch:2.0.1-py3.10-cuda11.8.0-devel-ubuntu22.04

# Metadata
LABEL maintainer="spriteflow"
LABEL description="AI-powered sprite animation pipeline with RIFE + rembg"
LABEL version="1.0.0"

# Configurar environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512
ENV PYTHONUNBUFFERED=1

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    git \
    wget \
    curl \
    ffmpeg \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /workspace

# Instalar dependencias Python
COPY requirements.txt /workspace/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Clonar e instalar RIFE
RUN git clone https://github.com/hzwer/Practical-RIFE.git /workspace/Practical-RIFE

# Descargar modelos RIFE
WORKDIR /workspace/Practical-RIFE
RUN mkdir -p train_log && \
    wget -q https://github.com/hzwer/Practical-RIFE/releases/download/4.26/flownet-v4.26.pkl -O train_log/flownet.pkl && \
    echo "✅ RIFE model downloaded"

# Pre-descargar modelos rembg (para evitar descarga en runtime)
RUN python3 -c "from rembg import new_session; new_session('u2net')" && \
    echo "✅ rembg u2net model downloaded"

# Copiar scripts de SpriteFlow
COPY src/ /workspace/spriteflow/

# Configurar permisos
RUN chmod +x /workspace/spriteflow/*.py

# Crear directorios de trabajo
RUN mkdir -p /workspace/inputs /workspace/outputs /workspace/batch_output

# Volver a workspace
WORKDIR /workspace

# Healthcheck (verificar que GPU esté disponible)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python3 -c "import torch; assert torch.cuda.is_available()" || exit 1

# Comando por defecto (shell interactivo)
CMD ["/bin/bash"]

# Notas de uso:
# 1. Build: docker build -t spriteflow:latest -f docker/Dockerfile .
# 2. Run local: docker run --gpus all -it spriteflow:latest
# 3. En RunPod: Usar template "PyTorch 2.0.1" y clonar este repo
