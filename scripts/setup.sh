#!/bin/bash
# SpriteFlow Setup Script
# Automated setup for RunPod or local environment

set -e

echo "🚀 SpriteFlow Setup Script"
echo "======================================"
echo ""

# Check if running on GPU
if command -v nvidia-smi &> /dev/null; then
    echo "✅ NVIDIA GPU detected"
    nvidia-smi --query-gpu=name --format=csv,noheader
else
    echo "⚠️  No GPU detected - will use CPU (slower)"
fi

echo ""
echo "📦 Installing system dependencies..."

# Update package list
apt-get update -qq

# Install required packages
apt-get install -y -qq \
    git \
    wget \
    curl \
    ffmpeg \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1

echo "✅ System dependencies installed"
echo ""

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

echo "✅ Python dependencies installed"
echo ""

# Clone RIFE repository
echo "📦 Setting up RIFE..."
if [ ! -d "Practical-RIFE" ]; then
    git clone -q https://github.com/hzwer/Practical-RIFE.git
    echo "✅ RIFE cloned"
else
    echo "✅ RIFE already exists"
fi

# Download RIFE model
cd Practical-RIFE
mkdir -p train_log

if [ ! -f "train_log/flownet.pkl" ]; then
    echo "📥 Downloading RIFE model (v4.26)..."
    wget -q --show-progress https://github.com/hzwer/Practical-RIFE/releases/download/4.26/flownet-v4.26.pkl -O train_log/flownet.pkl
    echo "✅ RIFE model downloaded"
else
    echo "✅ RIFE model already exists"
fi

cd ..

# Pre-download rembg models
echo ""
echo "📥 Downloading rembg models..."
python3 -c "from rembg import new_session; print('Downloading u2net...'); new_session('u2net')"
echo "✅ rembg models downloaded"

# Create directories
echo ""
echo "📁 Creating working directories..."
mkdir -p inputs outputs batch_output

echo "✅ Directories created"
echo ""

# Test installation
echo "🧪 Testing installation..."

# Test PyTorch CUDA
python3 -c "import torch; print(f'PyTorch version: {torch.__version__}'); print(f'CUDA available: {torch.cuda.is_available()}')"

# Test rembg
python3 -c "from rembg import remove; print('rembg: OK')"

# Test opencv
python3 -c "import cv2; print(f'OpenCV version: {cv2.__version__}')"

echo ""
echo "======================================"
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Place your input images in 'inputs/' directory"
echo "  2. Create batch_config.json (see examples/batch_config_example.json)"
echo "  3. Run: python src/batch_process.py batch_config.json"
echo ""
echo "Or process single animation:"
echo "  python src/process_sprites.py --start img1.png --end img2.png --frames 30"
echo ""
echo "======================================"
