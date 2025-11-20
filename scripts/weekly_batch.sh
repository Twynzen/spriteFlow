#!/bin/bash
# SpriteFlow Weekly Batch Processing
# Automated workflow: start → upload → process → download → stop

set -e

# Configuration (edit these)
RUNPOD_HOST="${RUNPOD_HOST:-X.tcp.runpod.net}"
RUNPOD_PORT="${RUNPOD_PORT:-XXXXX}"
INPUT_DIR="${INPUT_DIR:-./weekly_inputs}"
OUTPUT_DIR="${OUTPUT_DIR:-./weekly_outputs}"
CONFIG_FILE="${CONFIG_FILE:-batch_config.json}"

echo "🎬 SpriteFlow Weekly Batch Processing"
echo "======================================"
echo ""
echo "Configuration:"
echo "  RunPod Host: $RUNPOD_HOST"
echo "  RunPod Port: $RUNPOD_PORT"
echo "  Input Dir: $INPUT_DIR"
echo "  Output Dir: $OUTPUT_DIR"
echo "  Config: $CONFIG_FILE"
echo ""
echo "======================================"
echo ""

# Check if input directory exists
if [ ! -d "$INPUT_DIR" ]; then
    echo "❌ Error: Input directory not found: $INPUT_DIR"
    exit 1
fi

# Check if config exists
if [ ! -f "$INPUT_DIR/$CONFIG_FILE" ]; then
    echo "❌ Error: Config file not found: $INPUT_DIR/$CONFIG_FILE"
    exit 1
fi

# 1. Start RunPod
echo "1️⃣  Starting RunPod..."
python src/runpod_manager.py start

if [ $? -ne 0 ]; then
    echo "❌ Failed to start pod"
    exit 1
fi

echo ""
echo "⏳ Waiting 30 seconds for pod to fully initialize..."
sleep 30

# 2. Upload inputs
echo ""
echo "2️⃣  Uploading inputs..."
scp -P $RUNPOD_PORT -r $INPUT_DIR/* root@$RUNPOD_HOST:/workspace/spriteFlow/inputs/

if [ $? -ne 0 ]; then
    echo "❌ Failed to upload inputs"
    echo "⚠️  Stopping pod to avoid charges..."
    python src/runpod_manager.py stop
    exit 1
fi

echo "✅ Inputs uploaded"

# 3. Run processing
echo ""
echo "3️⃣  Running batch processing on RunPod..."
ssh -p $RUNPOD_PORT root@$RUNPOD_HOST "cd /workspace/spriteFlow && python src/batch_process.py inputs/$CONFIG_FILE"

if [ $? -ne 0 ]; then
    echo "❌ Batch processing failed"
    echo "⚠️  Stopping pod..."
    python src/runpod_manager.py stop
    exit 1
fi

echo "✅ Processing complete"

# 4. Download results
echo ""
echo "4️⃣  Downloading results..."
mkdir -p $OUTPUT_DIR
scp -P $RUNPOD_PORT -r root@$RUNPOD_HOST:/workspace/spriteFlow/batch_output/* $OUTPUT_DIR/

if [ $? -ne 0 ]; then
    echo "❌ Failed to download results"
    echo "⚠️  Results may still be on pod. Stopping pod..."
    python src/runpod_manager.py stop
    exit 1
fi

echo "✅ Results downloaded to: $OUTPUT_DIR"

# 5. Stop pod
echo ""
echo "5️⃣  Stopping RunPod..."
python src/runpod_manager.py stop

if [ $? -ne 0 ]; then
    echo "⚠️  Warning: Failed to stop pod via script"
    echo "⚠️  Please manually stop pod in RunPod dashboard to avoid charges!"
    exit 1
fi

# Summary
echo ""
echo "======================================"
echo "✅ Weekly batch processing complete!"
echo ""
echo "Results saved to: $OUTPUT_DIR"
echo ""
echo "Summary:"
ls -lh $OUTPUT_DIR/batch_report.json 2>/dev/null && cat $OUTPUT_DIR/batch_report.json | grep -E "(total|successful|failed|time_elapsed)" || echo "No report found"
echo ""
echo "======================================"

# Optional: Send notification (macOS)
if [[ "$OSTYPE" == "darwin"* ]]; then
    osascript -e 'display notification "SpriteFlow batch processing complete!" with title "SpriteFlow"'
fi

# Optional: Send notification (Linux with notify-send)
if command -v notify-send &> /dev/null; then
    notify-send "SpriteFlow" "Batch processing complete!"
fi
