#!/bin/bash
set -e

echo "[1/5] Installing system dependencies..."
sudo apt-get update -qq
sudo apt-get install -y python3-pip python3-venv libopencv-dev v4l-utils

echo "[2/5] Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

echo "[3/5] Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "[4/5] Pre-downloading YOLOv8n model weights..."
python3 -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"

echo "[5/5] Installing systemd service..."
sudo cp systemd/person-detector.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable person-detector.service

echo ""
echo "Setup complete."
echo "Edit src/config.py to set MQTT_BROKER_HOST, then:"
echo "  sudo systemctl start person-detector"
echo "  journalctl -u person-detector -f"
