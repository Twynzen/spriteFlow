# 💰 SpriteFlow - Cost Optimization Guide

Complete breakdown of costs and how to minimize them.

## Table of Contents

- [Cost Breakdown](#cost-breakdown)
- [Keeping Costs Under $4/month](#keeping-costs-under-4month)
- [Cloud Provider Comparison](#cloud-provider-comparison)
- [When to Consider Local GPU](#when-to-consider-local-gpu)
- [Cost Monitoring](#cost-monitoring)

---

## Cost Breakdown

### RunPod Pricing

| Component | Cost | Notes |
|-----------|------|-------|
| **RTX A4000** | **$0.19/hour** | Recommended |
| RTX 3090 | $0.29/hour | More VRAM (24GB) |
| RTX A5000 | $0.39/hour | Best for 4K sprites |
| Storage (persistent) | $0.10/GB/month | Only for models |
| Data transfer | Free | Included |

### Real-World Costs

**300 sprites/week workflow:**

```
Weekly session:
- Background removal: 150 pairs × 2 imgs × 0.2s = 1 min
- Frame interpolation: 150 × 30 frames × 2s = 2.5 hours
- Overhead (loading, I/O): 15 min
────────────────────────────────────────
Total: ~3 hours/week

Cost per session: 3 hours × $0.19 = $0.57
Weekly: $0.57
Monthly (4 weeks): $0.57 × 4 = $2.28

With buffer for re-runs: +30% = $2.96/month
Rounded estimate: $3-4/month
```

**Detailed per-sprite cost:**
```
Single animation (2 keyframes → 30 frames):
- Time: 2-3 minutes
- Cost: 0.05 hours × $0.19 = $0.0095 ≈ $0.01/animation

1,000 sprites: $10
10,000 sprites: $100
```

---

## Keeping Costs Under $4/month

### Strategy: Weekly Batch Processing

**DON'T**: Process sprites as you create them
```
Monday: Process 10 sprites (30 min) = $0.10
Tuesday: Process 8 sprites (24 min) = $0.08
...
Total overhead: ~2 hours starting/stopping pods
Total cost: ~$6-7/month
```

**DO**: Batch weekly
```
Monday 9 AM:
1. Start pod (1 min)
2. Upload all 75 sprites (15 min)
3. Process batch (2h 15min)
4. Download results (15 min)
5. Stop pod (1 min)

Total: 2h 47min = $0.53
Per month: $0.53 × 4 = $2.12
```

**Savings**: 60-70% cost reduction

---

### Rule #1: ALWAYS Stop Pods

**Running pod 24/7:**
```
720 hours/month × $0.19 = $136.80/month ❌
```

**Only running when needed (20 hours/month):**
```
20 hours/month × $0.19 = $3.80/month ✅
```

**How to ensure pods are stopped:**

```bash
# 1. Use automation script (recommended)
python src/runpod_manager.py stop

# 2. Set reminder
# Add to crontab:
0 */2 * * * python /path/to/runpod_manager.py status || echo "Pod still running!"

# 3. RunPod dashboard
# Check regularly: https://www.runpod.io/console/pods
```

---

### Rule #2: Optimize Storage

**Bad approach:**
```
Persistent storage: 50GB × $0.10 = $5.00/month
- Store all inputs
- Store all outputs
- Store temporary files
Total: $5/month just for storage ❌
```

**Good approach:**
```
Persistent storage: 2GB × $0.10 = $0.20/month
- Only RIFE model (~45MB)
- Only rembg models (~176MB)
- Delete inputs after processing
- Delete outputs after downloading
Total: $0.20/month ✅
```

**Workflow:**
1. Upload inputs → Process → Download outputs → Delete all from pod
2. Keep models persistent (avoid re-downloading)
3. Everything else is temporary

---

### Rule #3: Pre-process Locally

**Bad approach: Upload raw files**
```
- Upload 4K images (15MB each)
- RunPod resizes them
- Wastes GPU time on I/O
- Wastes upload bandwidth
```

**Good approach: Pre-process locally**
```bash
# On local machine (free):
# 1. Resize to optimal size
mogrify -resize 512x512 *.png

# 2. Crop to sprite bounds
mogrify -trim *.png

# 3. Normalize formats (PNG with alpha)
for img in *.jpg; do convert "$img" "${img%.jpg}.png"; done

# Upload optimized files → Faster upload, faster processing
```

**Time saved**: 15-30 minutes per batch = $0.05-0.10 saved

---

### Rule #4: Test Small, Scale Up

**Bad approach:**
```
1. Upload 100 sprites
2. Start processing
3. Realize config error halfway
4. Wasted 2 hours = $0.38 ❌
```

**Good approach:**
```
1. Upload 3 test sprites
2. Process and verify (5 min = $0.016)
3. If good, upload remaining 97
4. Process full batch
Total waste if error: $0.016 ✅
```

---

## Cloud Provider Comparison

### Monthly Cost for 300 Sprites/Week

| Provider | GPU | $/hour | Hours/month | Total/month |
|----------|-----|---------|-------------|-------------|
| **RunPod** | **RTX A4000** | **$0.19** | **20** | **$3.80** |
| Vast.ai | RTX 3060 | $0.12 | 20 | $2.40 |
| Lambda Labs | RTX 3080 | $0.50 | 20 | $10.00 |
| AWS EC2 (g4dn.xlarge) | T4 | $0.526 | 20 | $10.52 |
| Google Cloud (n1-standard-4) | T4 | $0.35 | 20 | $7.00 |
| Paperspace | RTX 5000 | $0.82 | 20 | $16.40 |

### Provider Pros/Cons

**RunPod** ⭐ Recommended
- ✅ Best price/performance ratio
- ✅ Reliable infrastructure
- ✅ Easy to use
- ❌ Limited GPU availability sometimes

**Vast.ai** (Budget option)
- ✅ Cheapest option
- ✅ Many GPU choices
- ❌ Instances can be interrupted
- ❌ Less reliable
- ❌ More complex setup

**Lambda Labs** (Premium)
- ✅ Very reliable
- ✅ Great support
- ✅ Persistent storage included
- ❌ 2.5X more expensive

**AWS/GCP** (Enterprise)
- ✅ Enterprise features
- ✅ Integration with other services
- ❌ 2-3X more expensive
- ❌ Complex billing
- ❌ Requires cloud expertise

---

## When to Consider Local GPU

### Break-even Analysis

**RunPod costs over time:**
```
Year 1: $3.80 × 12 = $45.60
Year 2: $45.60
Year 3: $45.60
────────────────────────
3 years total: $136.80
```

**Local GPU (RTX 4060) costs:**
```
Initial: $900 (GPU + PSU upgrade)
Year 1 electricity: $9/month × 12 = $108
Year 2 electricity: $108
Year 3 electricity: $108
────────────────────────
3 years total: $900 + $324 = $1,224
```

**Break-even**: ~25 years ❌

### When Local Makes Sense

**Consider local GPU if:**

1. **High volume**: >1,000 sprites/week
   ```
   RunPod: 60 hours/month × $0.19 = $11.40/month
   Local: $9/month (electricity only)
   Break-even: 100 months (~8 years)
   ```

2. **Other use cases**: Gaming, 3D rendering, ML training
   ```
   Amortize cost across multiple uses
   ```

3. **Privacy concerns**: Can't upload to cloud
   ```
   No alternative to local
   ```

**Otherwise**: Stick with cloud ✅

---

## Cost Monitoring

### Track Actual Usage

**RunPod Dashboard:**
1. Go to https://www.runpod.io/console/user/billing
2. View "Usage This Month"
3. Check running pods regularly

**Automated monitoring:**
```bash
# Check pod status daily
python src/runpod_manager.py status

# Get cost estimate
# Approximate formula:
# Cost = (Current uptime in hours) × $0.19
```

**Set budget alerts:**
```bash
# Create alert script
cat > alert_cost.sh << 'EOF'
#!/bin/bash
COST=$(python src/runpod_manager.py status | grep "Costo aproximado" | awk '{print $4}')
if (( $(echo "$COST > 5.00" | bc -l) )); then
    echo "⚠️  WARNING: Cost exceeded $5! Current: $$COST"
    # Send email/notification
fi
EOF

# Add to crontab (check daily)
0 12 * * * /path/to/alert_cost.sh
```

---

## Scaling Costs

### If You Need More

**600 sprites/week:**
```
40 hours/month × $0.19 = $7.60/month
Still cheaper than any alternative ✅
```

**1,200 sprites/week:**
```
80 hours/month × $0.19 = $15.20/month
Consider Lambda Labs at this scale (more reliable)
```

**3,000+ sprites/week:**
```
200+ hours/month × $0.19 = $38/month
Strongly consider local GPU (break-even ~24 months)
```

---

## Cost Optimization Checklist

Before each batch:
- [ ] Images pre-processed locally (resized, cropped)
- [ ] Batch config tested with 2-3 samples first
- [ ] Pod stopped immediately after download
- [ ] Old inputs/outputs deleted from pod
- [ ] Only models kept in persistent storage

Weekly review:
- [ ] Check RunPod billing dashboard
- [ ] Verify no pods left running
- [ ] Calculate actual $/sprite ratio
- [ ] Adjust workflow if costs creeping up

Monthly review:
- [ ] Total cost under $5? ✅
- [ ] If over, identify cause (pods left running?)
- [ ] Optimize workflow based on actual usage
- [ ] Consider different GPU if needs changed

---

## Summary

**Target monthly cost: $3-4**

**How to achieve:**
1. Batch weekly (not daily)
2. Stop pods immediately after use
3. Minimal persistent storage (2GB)
4. Pre-process images locally
5. Test small before scaling

**When costs increase:**
- Check for pods left running (most common!)
- Review storage usage
- Optimize batch size/frequency

**Questions?**
- [Report issue](https://github.com/yourusername/spriteFlow/issues)
- [Back to README](../README.md)
