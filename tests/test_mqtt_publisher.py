import sys
import os
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from mqtt_publisher import MQTTPublisher


@patch('mqtt_publisher.mqtt')
def test_publish_skips_when_not_connected(mock_mqtt):
    mock_client = MagicMock()
    mock_mqtt.Client.return_value = mock_client
    mock_mqtt.CallbackAPIVersion.VERSION1 = 1

    pub = MQTTPublisher("localhost", 1883, "test-client")
    pub._connected = False

    result = pub.publish("home/test", {"key": "value"})
    assert result is False
    mock_client.publish.assert_not_called()


@patch('mqtt_publisher.mqtt')
def test_publish_sends_json_when_connected(mock_mqtt):
    mock_client = MagicMock()
    mock_mqtt.Client.return_value = mock_client
    mock_mqtt.CallbackAPIVersion.VERSION1 = 1
    mock_mqtt.MQTT_ERR_SUCCESS = 0

    result_mock = MagicMock()
    result_mock.rc = 0
    mock_client.publish.return_value = result_mock

    pub = MQTTPublisher("localhost", 1883, "test-client")
    pub._connected = True

    result = pub.publish("home/test", {"detected": True})
    assert result is True
    mock_client.publish.assert_called_once()
    call_args = mock_client.publish.call_args
    assert call_args[0][0] == "home/test"
    assert '"detected": true' in call_args[0][1].lower() or 'detected' in call_args[0][1]


@patch('mqtt_publisher.mqtt')
def test_disconnect_stops_loop(mock_mqtt):
    mock_client = MagicMock()
    mock_mqtt.Client.return_value = mock_client
    mock_mqtt.CallbackAPIVersion.VERSION1 = 1

    pub = MQTTPublisher("localhost", 1883, "test-client")
    pub.disconnect()

    mock_client.loop_stop.assert_called_once()
    mock_client.disconnect.assert_called_once()
