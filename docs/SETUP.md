# 🛠️ SpriteFlow - Detailed Setup Guide

This guide covers detailed setup instructions for various environments.

## Table of Contents

- [Local Setup (GPU)](#local-setup-gpu)
- [RunPod Cloud Setup](#runpod-cloud-setup)
- [Vast.ai Setup](#vastai-setup)
- [Docker Setup](#docker-setup)
- [Troubleshooting](#troubleshooting)

---

## Local Setup (GPU)

### Prerequisites

- NVIDIA GPU with 4GB+ VRAM (8GB recommended)
- CUDA 11.8+ installed
- Python 3.10+
- Ubuntu 20.04+ / Windows 10+ with WSL2

### Step 1: Install CUDA

**Ubuntu:**
```bash
# Check if CUDA is installed
nvcc --version

# If not installed:
wget https://developer.download.nvidia.com/compute/cuda/11.8.0/local_installers/cuda_11.8.0_520.61.05_linux.run
sudo sh cuda_11.8.0_520.61.05_linux.run
```

**Windows (WSL2):**
```powershell
# Install WSL2 and Ubuntu
wsl --install

# Inside WSL2, install CUDA toolkit
# Follow Ubuntu instructions above
```

### Step 2: Clone Repository

```bash
git clone https://github.com/yourusername/spriteFlow.git
cd spriteFlow
```

### Step 3: Create Virtual Environment

```bash
# Create venv
python3 -m venv venv

# Activate
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\activate  # Windows
```

### Step 4: Install Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt

# Verify PyTorch sees GPU
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
```

### Step 5: Setup RIFE

```bash
# Clone RIFE
git clone https://github.com/hzwer/Practical-RIFE.git

# Download model
cd Practical-RIFE
mkdir -p train_log
wget https://github.com/hzwer/Practical-RIFE/releases/download/4.26/flownet-v4.26.pkl -O train_log/flownet.pkl

cd ..
```

### Step 6: Pre-download rembg Models

```bash
# This will download ~176MB
python -c "from rembg import new_session; new_session('u2net')"
```

### Step 7: Test Installation

```bash
# Create test images (or use your own)
mkdir -p test_inputs

# Run test
python src/process_sprites.py \
    --start test_inputs/img1.png \
    --end test_inputs/img2.png \
    --frames 10 \
    --output test_output
```

---

## RunPod Cloud Setup

### Why RunPod?

- **$0.19/hour** for RTX A4000 (16GB VRAM)
- Pay only for GPU time used
- No commitment, no monthly fees
- Setup in 15 minutes

### Step 1: Create Account

1. Go to https://www.runpod.io/
2. Sign up with email
3. Verify email
4. Add payment method (minimum $10)

### Step 2: Deploy Pod

1. Click **"Deploy"** → **"GPU Pods"**
2. Filter by **"RTX A4000"**
3. Select **"Community Cloud"** (cheaper)
4. Template: **"PyTorch 2.0.1"**
5. Configure:
   - Container Disk: 20GB
   - Volume Disk: 50GB
   - Expose Ports: 22, 8888

6. Click **"Deploy On-Demand"**

### Step 3: Connect via SSH

```bash
# Get SSH command from RunPod dashboard
# Will look like:
ssh root@X.tcp.runpod.net -p XXXXX -i ~/.ssh/id_ed25519
```

### Step 4: Setup SpriteFlow

```bash
# Once connected to pod:
cd /workspace

# Clone repository
git clone https://github.com/yourusername/spriteFlow.git
cd spriteFlow

# Run automated setup
chmod +x scripts/setup.sh
bash scripts/setup.sh
```

### Step 5: Test

```bash
# Create test config
python src/batch_process.py --create-example

# Edit batch_config_example.json with your test images
# Then run:
python src/batch_process.py batch_config_example.json
```

### Step 6: STOP POD

**IMPORTANT**: Stop pod when not in use!

```bash
# Via web dashboard: Click "Stop Pod"
# Or via CLI:
python src/runpod_manager.py stop
```

---

## Vast.ai Setup

### Why Vast.ai?

- **$0.10-0.30/hour** depending on GPU
- More options (but less stable)
- Good for budget-conscious users

### Step 1: Create Account

1. Go to https://vast.ai/
2. Sign up
3. Add credit ($10 minimum)

### Step 2: Find Instance

1. Go to **"Search"**
2. Filters:
   - GPU: RTX 3060 or better
   - VRAM: 8GB minimum
   - CUDA: 11.8+
   - DLPerf: >60

3. Sort by **"$/hr"**
4. Click **"Rent"**

### Step 3: Setup

```bash
# SSH into instance
ssh -p XXXXX root@X.vast.ai

# Install dependencies
apt-get update
apt-get install -y git wget curl

# Clone and setup
cd /root
git clone https://github.com/yourusername/spriteFlow.git
cd spriteFlow

bash scripts/setup.sh
```

**Note**: Vast.ai instances can be interrupted (preemptible). Save work frequently!

---

## Docker Setup

### Build Image

```bash
# From repository root
docker build -t spriteflow:latest -f docker/Dockerfile .
```

### Run Local (with GPU)

```bash
docker run --gpus all -it \
    -v $(pwd)/inputs:/workspace/inputs \
    -v $(pwd)/outputs:/workspace/outputs \
    spriteflow:latest
```

### Run on RunPod

RunPod supports custom Docker images:

1. Push image to Docker Hub:
   ```bash
   docker tag spriteflow:latest yourusername/spriteflow:latest
   docker push yourusername/spriteflow:latest
   ```

2. In RunPod, use custom template:
   - Container Image: `yourusername/spriteflow:latest`
   - Container Disk: 20GB
   - Expose ports: 22, 8888

---

## Troubleshooting

### CUDA Out of Memory

**Symptoms**: `RuntimeError: CUDA out of memory`

**Solutions**:
```python
# 1. Reduce batch size (edit process_sprites.py)
torch.cuda.empty_cache()  # Add before interpolation

# 2. Use smaller images
# Resize to 512x512 or smaller before processing

# 3. Process fewer frames
python src/process_sprites.py --frames 15  # Instead of 30
```

### rembg Model Download Fails

**Symptoms**: `Model not found` or download timeout

**Solution**:
```bash
# Manual download
mkdir -p ~/.u2net
cd ~/.u2net
wget https://github.com/danielgatis/rembg/releases/download/v0.0.0/u2net.onnx

# Or use different model
python src/process_sprites.py --rembg-model isnet-anime
```

### PyTorch Not Using GPU

**Symptoms**: Processing very slow, `nvidia-smi` shows 0% GPU usage

**Solutions**:
```bash
# 1. Check CUDA availability
python -c "import torch; print(torch.cuda.is_available())"

# 2. Re-install PyTorch with CUDA
pip uninstall torch torchvision
pip install torch==2.0.1 torchvision --index-url https://download.pytorch.org/whl/cu118

# 3. Check CUDA version matches PyTorch
nvcc --version  # Should be 11.8 or compatible
```

### SSH Connection Refused (RunPod)

**Symptoms**: `Connection refused` when trying to SSH

**Solutions**:
1. Check pod is RUNNING (not stopped)
2. Verify port number from dashboard
3. Check firewall rules
4. Try web terminal in RunPod dashboard

### Slow Performance

**Expected times** (RTX A4000):
- Single animation: 2-3 minutes
- 10 animations: 25-30 minutes

**If slower**:
```bash
# Check GPU is being used
nvidia-smi

# Check disk I/O isn't bottleneck
# Use SSD storage, not HDD

# Ensure images aren't too large
# Recommended: 512x512 to 1024x1024
```

### Permission Denied Errors

```bash
# Make scripts executable
chmod +x scripts/*.sh
chmod +x src/*.py

# Or run with python explicitly
python src/process_sprites.py
```

---

## Performance Optimization

### Best Practices

1. **Image sizes**: 512x512 optimal, up to 1024x1024 acceptable
2. **Batch processing**: Process multiple animations in one session
3. **GPU selection**: RTX 3060+ recommended (8GB+ VRAM)
4. **Storage**: Use SSD for faster I/O
5. **Network**: Fast internet for cloud uploads/downloads

### Benchmarks

| GPU | VRAM | Time per Animation | Recommended |
|-----|------|-------------------|-------------|
| GTX 1060 | 6GB | 5-7 min | ❌ Too slow |
| RTX 3060 | 12GB | 2-3 min | ✅ Good |
| RTX 3080 | 10GB | 1-2 min | ✅ Excellent |
| RTX A4000 | 16GB | 2-3 min | ✅ Best value |
| RTX 4090 | 24GB | 1 min | ⚠️ Overkill/expensive |

---

## Next Steps

- [Cost Optimization Guide](COSTS.md)
- [Back to README](../README.md)
- [Report Issues](https://github.com/yourusername/spriteFlow/issues)
