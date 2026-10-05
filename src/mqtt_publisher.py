import json
import time
import logging
import paho.mqtt.client as mqtt

logger = logging.getLogger(__name__)


class MQTTPublisher:
    def __init__(self, host: str, port: int, client_id: str):
        self._host = host
        self._port = port
        self._connected = False

        self._client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, client_id=client_id)
        self._client.on_connect = self._on_connect
        self._client.on_disconnect = self._on_disconnect

    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self._connected = True
            logger.info("Connected to MQTT broker %s:%d", self._host, self._port)
        else:
            logger.error("MQTT connection refused, rc=%d", rc)

    def _on_disconnect(self, client, userdata, rc):
        self._connected = False
        if rc != 0:
            logger.warning("Unexpected MQTT disconnect, rc=%d", rc)

    def connect(self, timeout: float = 5.0) -> bool:
        try:
            self._client.connect(self._host, self._port, keepalive=60)
            self._client.loop_start()
            deadline = time.time() + timeout
            while not self._connected and time.time() < deadline:
                time.sleep(0.05)
            return self._connected
        except Exception as exc:
            logger.error("Could not reach MQTT broker: %s", exc)
            return False

    def publish(self, topic: str, payload: dict) -> bool:
        if not self._connected:
            logger.warning("Skipping publish — not connected")
            return False
        result = self._client.publish(topic, json.dumps(payload), qos=1)
        if result.rc != mqtt.MQTT_ERR_SUCCESS:
            logger.error("Publish failed, rc=%d", result.rc)
            return False
        return True

    def disconnect(self):
        self._client.loop_stop()
        self._client.disconnect()
