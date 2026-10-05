import os

MQTT_BROKER_HOST = os.environ.get("MQTT_BROKER_HOST", "your-mqtt-broker-ip")
MQTT_BROKER_PORT = int(os.environ.get("MQTT_BROKER_PORT", "1883"))
MQTT_CLIENT_ID   = os.environ.get("MQTT_CLIENT_ID", "person-detector-pi")
MQTT_TOPIC_DETECTION = "home/detection/person"
MQTT_TOPIC_STATUS    = "home/detection/status"
MQTT_KEEPALIVE       = 60

CAMERA_INDEX  = int(os.environ.get("CAMERA_INDEX", "0"))
FRAME_WIDTH   = 640
FRAME_HEIGHT  = 480

# YOLOv8n: lightweight model suited for Raspberry Pi inference
YOLO_MODEL               = "yolov8n.pt"
YOLO_INPUT_SIZE          = 320
YOLO_CONFIDENCE_THRESHOLD = 0.5

# Suppress repeated MQTT publishes while a person stays in frame
DETECTION_COOLDOWN_SECONDS = 5
