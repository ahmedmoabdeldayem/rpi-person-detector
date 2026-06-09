#!/bin/sh
# Runs once on first boot to install ultralytics + pre-download YOLOv8n weights.
# Controlled by the ml-bootstrap.service (RemainAfterExit + ConditionPathExists).

set -e

LOG=/var/log/ml-bootstrap.log
STAMP=/var/lib/ml-bootstrap/done

mkdir -p /var/lib/ml-bootstrap

echo "[$(date)] Starting ML bootstrap..." | tee -a "$LOG"

pip3 install --no-cache-dir ultralytics 2>&1 | tee -a "$LOG"

# Pre-download model weights so the detector starts immediately on next boot
python3 -c "from ultralytics import YOLO; YOLO('yolov8n.pt')" 2>&1 | tee -a "$LOG"

touch "$STAMP"
echo "[$(date)] ML bootstrap complete." | tee -a "$LOG"
