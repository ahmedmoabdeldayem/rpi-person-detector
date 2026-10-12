import sys
import os
from unittest.mock import MagicMock, patch

# Stub out heavy native deps before importing detector so CI doesn't need them.
for _mod in ('cv2', 'ultralytics'):
    sys.modules.setdefault(_mod, MagicMock())
sys.modules['ultralytics'].YOLO = MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


@patch('detector.MQTTPublisher')
@patch('detector.MQTT_BROKER_HOST', 'broker.local')
def test_circuit_breaker_exits_after_max_failures(mock_mqtt_cls):
    """Loop must exit after MAX_CONSECUTIVE_FAILURES consecutive frame-read failures."""
    import detector

    mock_pub = MagicMock()
    mock_pub.connect.return_value = True
    mock_mqtt_cls.return_value = mock_pub

    mock_cap = MagicMock()
    mock_cap.isOpened.return_value = True
    mock_cap.read.return_value = (False, None)
    detector.cv2.VideoCapture.return_value = mock_cap

    detector._running = True
    detector.main()

    # read() called exactly MAX_CONSECUTIVE_FAILURES (30) times before giving up
    assert mock_cap.read.call_count == detector.MAX_CONSECUTIVE_FAILURES
    mock_cap.release.assert_called_once()


def test_frame_throttle_constant_is_positive():
    """MIN_INFERENCE_INTERVAL must be a positive float."""
    import detector
    assert detector.MIN_INFERENCE_INTERVAL > 0


def test_frame_throttle_logic():
    """Throttle condition: skip inference when elapsed < MIN_INFERENCE_INTERVAL."""
    import detector

    last_inference = 0.0
    now = 0.05  # less than 0.2s interval

    should_skip = (now - last_inference) < detector.MIN_INFERENCE_INTERVAL
    assert should_skip is True

    now = 0.25  # greater than 0.2s interval
    should_skip = (now - last_inference) < detector.MIN_INFERENCE_INTERVAL
    assert should_skip is False


def test_max_consecutive_failures_constant():
    """MAX_CONSECUTIVE_FAILURES must be a positive integer."""
    import detector
    assert detector.MAX_CONSECUTIVE_FAILURES > 0
    assert isinstance(detector.MAX_CONSECUTIVE_FAILURES, int)
