import sys
import os
from types import ModuleType
from unittest.mock import MagicMock, patch

# Stub out heavy native deps before importing detector so CI doesn't need them
for mod in ('cv2', 'ultralytics'):
    sys.modules.setdefault(mod, MagicMock())
# ultralytics.YOLO must be importable as a class
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

    # cap.read() should have been called exactly _MAX_CONSECUTIVE_FAILURES (30) times
    assert mock_cap.read.call_count == 30
    mock_cap.release.assert_called_once()


@patch('detector.MQTTPublisher')
@patch('detector.MQTT_BROKER_HOST', 'broker.local')
def test_frame_throttle_skips_inference(mock_mqtt_cls):
    """Inference should be skipped when less than _MIN_INFERENCE_INTERVAL has elapsed."""
    import detector

    mock_pub = MagicMock()
    mock_pub.connect.return_value = True
    mock_mqtt_cls.return_value = mock_pub

    mock_cap = MagicMock()
    mock_cap.isOpened.return_value = True
    call_count = {'n': 0}

    def read_side_effect():
        call_count['n'] += 1
        if call_count['n'] > 2:
            detector._running = False
        return (True, MagicMock())

    mock_cap.read.side_effect = read_side_effect
    detector.cv2.VideoCapture.return_value = mock_cap

    mock_model = MagicMock()
    mock_model.return_value = []
    detector.YOLO.return_value = mock_model

    # Both frames arrive within _MIN_INFERENCE_INTERVAL — second should be skipped
    timestamps = [0.0, 0.0, 0.05, 0.05, 0.05, 0.05]
    with patch('detector.time') as mock_time:
        mock_time.monotonic.side_effect = timestamps
        mock_time.sleep = MagicMock()
        detector._running = True
        detector.main()

    # Model called at most once (second frame throttled)
    assert mock_model.call_count <= 1
