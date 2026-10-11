import sys
import os
from unittest.mock import MagicMock, patch, call

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


@patch('detector.YOLO')
@patch('detector.cv2')
@patch('detector.MQTTPublisher')
@patch('detector.MQTT_BROKER_HOST', 'broker.local')
def test_circuit_breaker_exits_after_max_failures(mock_mqtt_cls, mock_cv2, mock_yolo):
    """Loop must exit after _MAX_CONSECUTIVE_FAILURES consecutive frame-read failures."""
    mock_pub = MagicMock()
    mock_pub.connect.return_value = True
    mock_mqtt_cls.return_value = mock_pub

    mock_cap = MagicMock()
    mock_cap.isOpened.return_value = True
    mock_cap.read.return_value = (False, None)  # always fail
    mock_cv2.VideoCapture.return_value = mock_cap

    mock_yolo.return_value = MagicMock()

    import detector
    detector._running = True
    detector.main()

    # cap.read() should have been called exactly _MAX_CONSECUTIVE_FAILURES times
    assert mock_cap.read.call_count == 30
    mock_cap.release.assert_called_once()
    # offline status published on cleanup
    mock_pub.publish.assert_any_call(
        'home/detection/status', {'status': 'offline', 'timestamp': mock_pub.publish.call_args_list[-1][0][1]['timestamp']}
    )


@patch('detector.YOLO')
@patch('detector.cv2')
@patch('detector.MQTTPublisher')
@patch('detector.MQTT_BROKER_HOST', 'broker.local')
@patch('detector.time')
def test_frame_throttle_skips_inference(mock_time, mock_mqtt_cls, mock_cv2, mock_yolo):
    """Inference should be skipped when less than _MIN_INFERENCE_INTERVAL has elapsed."""
    mock_pub = MagicMock()
    mock_pub.connect.return_value = True
    mock_mqtt_cls.return_value = mock_pub

    mock_cap = MagicMock()
    mock_cap.isOpened.return_value = True
    # Two successful frames then stop
    frame = MagicMock()
    call_count = {'n': 0}

    def read_side_effect():
        call_count['n'] += 1
        if call_count['n'] > 2:
            import detector as d
            d._running = False
        return (True, frame)

    mock_cap.read.side_effect = read_side_effect
    mock_cv2.VideoCapture.return_value = mock_cap

    mock_model = MagicMock()
    mock_yolo.return_value = mock_model

    # Both frames arrive within _MIN_INFERENCE_INTERVAL — second should be skipped
    mock_time.monotonic.side_effect = [0.0, 0.0, 0.05, 0.05, 0.05]
    mock_time.sleep = MagicMock()

    import detector
    detector._running = True
    detector.main()

    # Model called at most once (second frame throttled)
    assert mock_model.call_count <= 1
