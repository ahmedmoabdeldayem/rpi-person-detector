#!/usr/bin/env python3
"""
Person detector — Raspberry Pi + Pi Camera + YOLOv8n + MQTT

Captures frames from the camera, runs YOLOv8n inference, and publishes
an MQTT event whenever a person is detected with sufficient confidence.
A cooldown timer prevents flooding the broker when a person stays in frame.
"""

import signal
import sys
import time
import logging
from datetime import datetime, timezone

import cv2
from ultralytics import YOLO

from config import (
    CAMERA_INDEX, FRAME_WIDTH, FRAME_HEIGHT,
    YOLO_MODEL, YOLO_INPUT_SIZE, YOLO_CONFIDENCE_THRESHOLD,
    DETECTION_COOLDOWN_SECONDS,
    MQTT_BROKER_HOST, MQTT_BROKER_PORT, MQTT_CLIENT_ID,
    MQTT_TOPIC_DETECTION, MQTT_TOPIC_STATUS,
)
from mqtt_publisher import MQTTPublisher

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("detector")

_running = True


def _handle_signal(sig, frame):
    global _running
    logger.info("Signal %d received — shutting down", sig)
    _running = False


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def main():
    signal.signal(signal.SIGTERM, _handle_signal)
    signal.signal(signal.SIGINT, _handle_signal)

    logger.info("Loading YOLOv8n model (%s)...", YOLO_MODEL)
    model = YOLO(YOLO_MODEL)

    mqtt = MQTTPublisher(MQTT_BROKER_HOST, MQTT_BROKER_PORT, MQTT_CLIENT_ID)
    if not mqtt.connect():
        logger.error("Failed to connect to MQTT broker at %s:%d", MQTT_BROKER_HOST, MQTT_BROKER_PORT)
        sys.exit(1)

    mqtt.publish(MQTT_TOPIC_STATUS, {"status": "online", "timestamp": _now_iso()})

    cap = cv2.VideoCapture(CAMERA_INDEX)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

    if not cap.isOpened():
        logger.error("Cannot open camera at index %d", CAMERA_INDEX)
        mqtt.publish(MQTT_TOPIC_STATUS, {"status": "error", "reason": "camera_unavailable", "timestamp": _now_iso()})
        mqtt.disconnect()
        sys.exit(1)

    logger.info("Camera open. Starting detection loop (confidence >= %.2f, cooldown %ds)",
                YOLO_CONFIDENCE_THRESHOLD, DETECTION_COOLDOWN_SECONDS)

    last_published = 0.0

    try:
        while _running:
            ret, frame = cap.read()
            if not ret:
                logger.warning("Frame read failed — retrying")
                time.sleep(0.1)
                continue

            results = model(frame, imgsz=YOLO_INPUT_SIZE, verbose=False)

            best_conf = 0.0
            person_count = 0

            for result in results:
                for box in result.boxes:
                    cls = int(box.cls[0])
                    conf = float(box.conf[0])
                    # COCO class 0 == 'person'
                    if cls == 0 and conf >= YOLO_CONFIDENCE_THRESHOLD:
                        person_count += 1
                        if conf > best_conf:
                            best_conf = conf

            now = time.monotonic()
            if person_count > 0 and (now - last_published) >= DETECTION_COOLDOWN_SECONDS:
                last_published = now
                payload = {
                    "detected": True,
                    "count": person_count,
                    "confidence": round(best_conf, 3),
                    "timestamp": _now_iso(),
                }
                logger.info("Person detected: count=%d conf=%.3f", person_count, best_conf)
                mqtt.publish(MQTT_TOPIC_DETECTION, payload)

    finally:
        cap.release()
        mqtt.publish(MQTT_TOPIC_STATUS, {"status": "offline", "timestamp": _now_iso()})
        mqtt.disconnect()
        logger.info("Detector stopped cleanly")


if __name__ == "__main__":
    main()
