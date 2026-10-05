# rpi-person-detector

A Raspberry Pi person detection system using YOLOv8n and MQTT. Detects people via a Pi Camera and publishes events to an MQTT broker in real time.

```
Pi Camera → YOLOv8n inference → MQTT publish → home/detection/person
```

Includes a Yocto meta-layer (`meta-rpi-detector`) for building a minimal embedded Linux image with the detector pre-installed.

## Quick Start (native Pi setup)

```bash
# Clone and run setup
git clone https://github.com/ahmedmoabdeldayem/rpi-person-detector
cd rpi-person-detector
bash setup.sh

# Configure MQTT broker (or use environment variables)
export MQTT_BROKER_HOST=192.168.1.100   # IP of your MQTT broker
export MQTT_BROKER_PORT=1883            # optional, default 1883

# Start the service
sudo systemctl start person-detector
journalctl -u person-detector -f
```

## Configuration

All settings are controlled via environment variables (with sensible defaults):

| Variable | Default | Description |
|---|---|---|
| `MQTT_BROKER_HOST` | `192.168.1.100` | IP of the MQTT broker |
| `MQTT_BROKER_PORT` | `1883` | MQTT port |
| `MQTT_CLIENT_ID` | `person-detector-pi` | MQTT client identifier |
| `CAMERA_INDEX` | `0` | `/dev/video0` (Pi Camera via v4l2) |

## MQTT Events

**Detection event** — published to `home/detection/person` when a person is detected:
```json
{ "detected": true, "count": 1, "confidence": 0.87, "timestamp": "2026-10-05T12:00:00+00:00" }
```

**Status event** — published to `home/detection/status` on start/stop:
```json
{ "status": "online", "timestamp": "2026-10-05T12:00:00+00:00" }
```

## Yocto Build (embedded image)

```bash
# Initialize build environment (requires Poky + meta-openembedded + meta-raspberrypi)
source /opt/yocto/poky/oe-init-build-env build

# Copy and configure build files
cp build/conf/bblayers.conf.template build/conf/bblayers.conf
cp build/conf/local.conf.template    build/conf/local.conf
# Edit both files to match your layer paths and machine

# Build the image
bitbake rpi-detector-image
```

Flash the resulting `.wic` image to an SD card with `dd` or Balena Etcher.

## Project Structure

```
rpi-person-detector/
├── src/                        # Python source (single source of truth)
│   ├── detector.py             # Main detection loop
│   ├── mqtt_publisher.py       # MQTT client wrapper
│   └── config.py               # Configuration via env vars
├── meta-rpi-detector/          # Yocto meta-layer
│   ├── recipes-app/            # person-detector recipe (pulls from src/)
│   ├── recipes-core/images/    # rpi-detector-image
│   └── recipes-support/        # ml-bootstrap (downloads YOLO weights on first boot)
├── systemd/                    # systemd service unit
├── build/conf/                 # Yocto build config templates
├── requirements.txt            # Python dependencies (pinned)
└── setup.sh                    # Native Pi setup script
```
