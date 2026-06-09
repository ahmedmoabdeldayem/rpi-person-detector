MQTT_BROKER_HOST = "192.168.1.100"  # IP of the rpi-yocto-mqtt broker node
MQTT_BROKER_PORT = 1883
MQTT_CLIENT_ID = "person-detector-pi"
MQTT_TOPIC_DETECTION = "home/detection/person"
MQTT_TOPIC_STATUS = "home/detection/status"
MQTT_KEEPALIVE = 60

CAMERA_INDEX = 0       # /dev/video0 — Pi Camera via v4l2
FRAME_WIDTH = 640
FRAME_HEIGHT = 480

# YOLOv8n: lightweight model suited for Raspberry Pi inference
YOLO_MODEL = "yolov8n.pt"
YOLO_INPUT_SIZE = 320          # Smaller input = faster inference on Pi
YOLO_CONFIDENCE_THRESHOLD = 0.5

# Suppress repeated MQTT publishes while a person stays in frame
DETECTION_COOLDOWN_SECONDS = 5
