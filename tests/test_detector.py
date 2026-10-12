import sys
import os
from unittest.mock import MagicMock, patch, call

# Stub out heavy native deps before importing detector so CI doesn't need them
for _mod in ('cv2', 'ultralytics'):
    sys.modules.setdefault(_mod, MagicMock())
sys.modules['ultralytics'].YOLO = MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


@patch('detector.MQTTPublisher')
@patch('detector.MQTT_BROKER_HOST', 'broker.local')
def test_circuit_breaker_exits_after_max_failures(mock_mqtt_cls):
    """Loop must exit after _MAX_CONSECUTIVE_FAILURES consecutive frame-read failures."""
    import detector

    mock_pub = MagicMock()
    mock_pub.connect.return_value = True
    mock_mqtt_cls.return_value = mock_pub

    mock_cap = MagicMock()
    mock_cap.isOpened.return_value = True
    mock_cap.read.return_value = (False, None)  # always fail
    detector.cv2.VideoCapture.return_value = mock_cap

    detector._running = True
    detector.main()

    # read() called exactly _MAX_CONSECUTIVE_FAILURES (30) times before giving up
    assert mock_cap.read.call_count == 30
    mock_cap.release.assert_called_once()


@patch('detector.MQTTPublisher')
@patch('detector.MQTT_BROKER_HOST', 'broker.local')
def test_frame_throttle_skips_inference(mock_mqtt_cls):
    """Inference must be skipped when less than _MIN_INFERENCE_INTERVAL has elapsed."""
    import detector

    mock_pub = MagicMock()
    mock_pub.connect.return_value = True
    mock_mqtt_cls.return_value = mock_pub

    mock_cap = MagicMock()
    mock_cap.isOpened.return_value = True

    frames_read = {'n': 0}

    def _read():
        frames_read['n'] += 1
        if frames_read['n'] >= 3:
            detector._running = False
        return (True, MagicMock())

    mock_cap.read.side_effect = _read
    detector.cv2.VideoCapture.return_value = mock_cap

    mock_model = MagicMock()
    mock_model.return_value = []
    detector.YOLO.return_value = mock_model

    # Monotonic always returns 0.0 so every frame appears within the 0.2s interval
    with patch('detector.time') as mock_time:
        mock_time.monotonic.return_value = 0.0
        mock_time.sleep = MagicMock()
        detector._running = True
        detector.main()

    # With all frames at t=0.0 and last_inference starting at 0.0,
    # the throttle (now - last_inference < 0.2) is True for all frames
    # after the first, so model is called at most once.
    assert mock_model.call_count <= 1
