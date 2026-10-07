import os
import importlib
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


def reload_config(env):
    os.environ.update(env)
    import config
    importlib.reload(config)
    return config


def test_default_broker_host():
    os.environ.pop("MQTT_BROKER_HOST", None)
    cfg = reload_config({})
    assert cfg.MQTT_BROKER_HOST == "your-mqtt-broker-ip"


def test_env_overrides_broker_host():
    cfg = reload_config({"MQTT_BROKER_HOST": "10.0.0.5"})
    assert cfg.MQTT_BROKER_HOST == "10.0.0.5"
    os.environ.pop("MQTT_BROKER_HOST")


def test_default_broker_port():
    os.environ.pop("MQTT_BROKER_PORT", None)
    cfg = reload_config({})
    assert cfg.MQTT_BROKER_PORT == 1883


def test_env_overrides_broker_port():
    cfg = reload_config({"MQTT_BROKER_PORT": "1884"})
    assert cfg.MQTT_BROKER_PORT == 1884
    os.environ.pop("MQTT_BROKER_PORT")


def test_detection_cooldown_is_positive():
    cfg = reload_config({})
    assert cfg.DETECTION_COOLDOWN_SECONDS > 0


def test_confidence_threshold_in_range():
    cfg = reload_config({})
    assert 0.0 < cfg.YOLO_CONFIDENCE_THRESHOLD < 1.0
