# 🎨 SpriteFlow

> AI-powered 2D sprite animation pipeline for game development

**Generate smooth 30-fps animations from keyframes with automatic background removal for less than $4/month**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0-red.svg)](https://pytorch.org/)

---

## 📋 Overview

SpriteFlow transforms static keyframes into fluid sprite animations using state-of-the-art AI models:

- **RIFE v4.26**: Frame interpolation (generates 30 intermediate frames)
- **rembg (U2-Net)**: Automatic background removal with alpha channel
- **GPU-accelerated**: Runs on RunPod/Vast.ai cloud GPUs
- **Cost-optimized**: $3-4/month for 1,200+ sprites

### Key Features

✅ **30 FPS smooth animations** from just 2 keyframes
✅ **Automatic background removal** with clean alpha channels
✅ **Batch processing** for hundreds of sprites
✅ **GPU cloud deployment** on RunPod ($0.19/hour)
✅ **Production-ready** Docker container
✅ **Zero setup cost** - pay only for GPU time used

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- CUDA-compatible GPU (local) or RunPod account (cloud)
- 2GB disk space for models

### Local Installation

```bash
# Clone repository
git clone https://github.com/yourusername/spriteFlow.git
cd spriteFlow

# Install dependencies
pip install -r requirements.txt

# Clone RIFE
git clone https://github.com/hzwer/Practical-RIFE.git

# Download RIFE model
cd Practical-RIFE
mkdir -p train_log
wget https://github.com/hzwer/Practical-RIFE/releases/download/4.26/flownet-v4.26.pkl -O train_log/flownet.pkl

# Pre-download rembg models
python -c "from rembg import new_session; new_session('u2net')"
```

### Usage

**Single animation:**
```bash
python src/process_sprites.py \
    --start examples/inputs/walk_start.png \
    --end examples/inputs/walk_end.png \
    --frames 30 \
    --output output/walk_animation
```

**Batch processing:**
```bash
# Create config file
python src/batch_process.py --create-example

# Edit batch_config_example.json with your animations
# Then run:
python src/batch_process.py batch_config_example.json
```

---

## ☁️ Cloud Deployment (RunPod)

### Why Cloud GPU?

| Option | Monthly Cost | Initial Investment | Break-even |
|--------|--------------|-------------------|------------|
| **RunPod** | **$3-4** | **$0** | Immediate |
| Local RTX 4060 | $9 (electricity) | $900 | ~100 months |
| API Services | $68-152 | $0 | Never cheaper |

### RunPod Setup (15 minutes)

1. **Create RunPod account**: https://www.runpod.io/

2. **Deploy GPU Pod**:
   - Template: `PyTorch 2.0.1`
   - GPU: RTX A4000 ($0.19/hour)
   - Container Disk: 20GB
   - Volume: 50GB

3. **SSH into pod**:
   ```bash
   ssh root@X.tcp.runpod.net -p XXXXX
   ```

4. **Clone and setup**:
   ```bash
   cd /workspace
   git clone https://github.com/yourusername/spriteFlow.git
   cd spriteFlow

   # Install dependencies
   pip install -r requirements.txt

   # Setup RIFE
   git clone https://github.com/hzwer/Practical-RIFE.git
   cd Practical-RIFE
   mkdir -p train_log
   wget https://github.com/hzwer/Practical-RIFE/releases/download/4.26/flownet-v4.26.pkl -O train_log/flownet.pkl

   # Pre-download rembg models
   python -c "from rembg import new_session; new_session('u2net')"
   ```

5. **Test installation**:
   ```bash
   cd /workspace/spriteFlow
   python src/process_sprites.py --help
   ```

### Weekly Workflow

```bash
# 1. Upload inputs (from local machine)
scp -P XXXXX -r ./weekly_batch/ root@X.tcp.runpod.net:/workspace/spriteFlow/inputs/

# 2. SSH into pod and process
ssh root@X.tcp.runpod.net -p XXXXX
cd /workspace/spriteFlow
python src/batch_process.py inputs/batch_config.json

# 3. Download results (from local machine)
scp -P XXXXX -r root@X.tcp.runpod.net:/workspace/spriteFlow/batch_output/ ./results/

# 4. STOP POD (important!)
# Go to RunPod dashboard and click "Stop Pod"
```

**💰 Cost for 300 images/week**: ~3 hours GPU time = $0.57/session × 4 weeks = **$2.28/month**

---

## 🎮 Use Cases

- **Game Development**: Sprite animations for characters, enemies, items
- **Animation Studio**: Pre-visualization and animatics
- **NFT Projects**: Generative avatar animations
- **Education**: Teaching animation principles
- **Prototyping**: Rapid game asset creation

---

## 📊 Performance Benchmarks

**Hardware**: RTX A4000 (16GB VRAM)

| Task | Time | Cost |
|------|------|------|
| Single animation (2 imgs → 30 frames) | 2-3 min | $0.01 |
| Batch 10 animations | 25-30 min | $0.10 |
| Batch 100 animations | 4-5 hours | $0.95 |
| Weekly 300 images | 3 hours | $0.57 |

**Quality**:
- Frame interpolation: Smooth motion blur
- Background removal: Clean alpha edges (U2-Net)
- Output format: PNG with transparency

---

## 🛠️ Configuration

### Batch Config Format

```json
{
  "rembg_model": "u2net",
  "rife_model": "train_log/flownet.pkl",
  "animations": [
    {
      "name": "walk_right",
      "start": "inputs/walk_right_start.png",
      "end": "inputs/walk_right_end.png",
      "frames": 30,
      "remove_bg": true
    }
  ]
}
```

### rembg Models

- `u2net` (176MB): General purpose - **recommended**
- `isnet-anime` (175MB): Anime/manga characters
- `birefnet-general` (250MB): Best quality, slower

### RIFE Models

- `v4.26` (45MB): General - **recommended**
- `v4.9.2` (45MB): Anime-optimized

---

## 🔧 Automation

### Auto-start/stop RunPod

```bash
# Configure credentials
export RUNPOD_API_KEY="your_api_key"
export RUNPOD_POD_ID="your_pod_id"

# Start pod
python src/runpod_manager.py start

# Check status
python src/runpod_manager.py status

# Stop pod (important to avoid charges!)
python src/runpod_manager.py stop
```

### Weekly Automation Script

See `scripts/weekly_batch.sh` for fully automated workflow:
1. Start pod
2. Upload inputs
3. Process batch
4. Download results
5. Stop pod

Schedule with cron:
```bash
# Run every Monday at 9 AM
0 9 * * 1 cd /path/to/spriteFlow && ./scripts/weekly_batch.sh
```

---

## 📁 Project Structure

```
spriteFlow/
├── src/
│   ├── process_sprites.py      # Main processing script
│   ├── batch_process.py        # Batch processing
│   └── runpod_manager.py       # RunPod automation
├── docker/
│   └── Dockerfile              # Optimized container
├── scripts/
│   ├── setup.sh                # Initial setup
│   └── weekly_batch.sh         # Automated workflow
├── examples/
│   ├── inputs/                 # Sample input images
│   └── batch_config_example.json
├── docs/
│   ├── SETUP.md               # Detailed setup guide
│   └── COSTS.md               # Cost optimization
├── requirements.txt
└── README.md
```

---

## 💡 Tips & Best Practices

### Cost Optimization

1. **Batch everything**: Process weekly, not daily
2. **Stop pods immediately**: Only pay for active GPU time
3. **Pre-process locally**: Crop/resize before uploading
4. **Use persistent storage wisely**: Only 2GB for models

### Quality Tips

1. **Matching sizes**: Ensure start/end images are same resolution
2. **Similar poses**: Better interpolation with similar keyframes
3. **Clean inputs**: Better background removal with clean edges
4. **Test first**: Process 1-2 animations before large batches

### Troubleshooting

**"CUDA out of memory"**:
```python
# Add to process_sprites.py
torch.cuda.empty_cache()  # Clear cache between frames
```

**"rembg model not found"**:
```bash
# Force download
python -c "from rembg import new_session; new_session('u2net')"
```

**Slow performance**:
```bash
# Check GPU usage
nvidia-smi

# Verify PyTorch sees GPU
python -c "import torch; print(torch.cuda.is_available())"
```

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing`)
5. Open Pull Request

---

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [RIFE](https://github.com/hzwer/Practical-RIFE) by Huang et al. - Frame interpolation
- [rembg](https://github.com/danielgatis/rembg) by Daniel Gatis - Background removal
- [RunPod](https://runpod.io) - GPU cloud infrastructure

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/spriteFlow/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/spriteFlow/discussions)
- **RunPod Support**: [RunPod Discord](https://discord.gg/runpod)

---

## 🗺️ Roadmap

- [ ] Web UI for easier usage
- [ ] More interpolation models (AnimateDiff, FILM)
- [ ] Sprite sheet export
- [ ] Video output support
- [ ] Batch download from cloud storage
- [ ] Integration with game engines (Unity, Godot)

---

**Made with ❤️ for game developers**

⭐ Star this repo if you find it useful!
