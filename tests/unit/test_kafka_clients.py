from unittest.mock import patch

from src.consumers import sensor_consumer
from src.producers import sensor_producer


def test_producer_uses_shared_bootstrap_environment(monkeypatch):
    monkeypatch.setenv("KAFKA_BOOTSTRAP_SERVERS", "broker-test:9092")

    with patch.object(sensor_producer, "KafkaProducer") as kafka_producer:
        sensor_producer.create_producer()

    assert kafka_producer.call_args.kwargs["bootstrap_servers"] == "broker-test:9092"


def test_consumer_uses_shared_bootstrap_environment_and_keeps_auto_commit(monkeypatch):
    monkeypatch.setenv("KAFKA_BOOTSTRAP_SERVERS", "broker-test:9092")

    with patch.object(sensor_consumer, "KafkaConsumer") as kafka_consumer:
        sensor_consumer.create_consumer(group_id="unit-group")

    kwargs = kafka_consumer.call_args.kwargs
    assert kafka_consumer.call_args.args == (sensor_consumer.TOPIC,)
    assert kwargs["bootstrap_servers"] == "broker-test:9092"
    assert kwargs["group_id"] == "unit-group"
    assert kwargs["enable_auto_commit"] is True
    assert kwargs["auto_offset_reset"] == "earliest"


def test_default_bootstrap_address_is_compose_internal(monkeypatch):
    monkeypatch.delenv("KAFKA_BOOTSTRAP_SERVERS", raising=False)

    with patch.object(sensor_producer, "KafkaProducer") as kafka_producer:
        sensor_producer.create_producer()

    assert kafka_producer.call_args.kwargs["bootstrap_servers"] == "kafka:29092"


def test_consumer_rejects_invalid_json_and_utf8():
    import pytest

    with pytest.raises(ValueError, match="mensagem inválida"):
        sensor_consumer.deserialize_reading(b"{invalid")

    with pytest.raises(ValueError, match="mensagem inválida"):
        sensor_consumer.deserialize_reading(b"\xff")


def test_consumer_continues_after_invalid_events(capsys):
    from types import SimpleNamespace
    from src.models.sensor_reading import SensorReading
    normal = SensorReading.create('s', 25, 50, 1010)
    anomaly = SensorReading.create('s', 75, 95, 900)
    messages = [b'\xff', b'null', b'{}', normal.to_json().encode(),
                b'{invalid', anomaly.to_json().encode()]
    sensor_consumer.consume_messages([SimpleNamespace(value=value) for value in messages])
    output = capsys.readouterr()
    assert output.err.count('Mensagem ignorada') == 4
    assert output.out.count('NORMAL |') == 1
    assert output.out.count('ANOMALY |') == 1
    assert anomaly.event_id in output.out
    for field in ('temperature', 'humidity', 'pressure'):
        assert field in output.out


def test_process_message_reuses_injected_detector():
    from src.detectors.anomaly_detector import RangeRule, RuleBasedAnomalyDetector
    from src.models.sensor_reading import SensorReading
    detector = RuleBasedAnomalyDetector([RangeRule('temperature', 0, 80)])
    with patch.object(detector, 'detect', wraps=detector.detect) as detect:
        for temperature, expected in [(75, False), (81, True)]:
            reading = SensorReading.create('s', temperature, 95, 900)
            result = sensor_consumer.process_message(reading.to_json().encode(), detector)
            assert result.is_anomaly is expected
            assert result.event_id == reading.event_id
        assert detect.call_count == 2


def test_consume_messages_constructs_one_detector_for_loop(capsys):
    from types import SimpleNamespace
    from src.detectors.anomaly_detector import RuleBasedAnomalyDetector
    from src.models.sensor_reading import SensorReading
    messages = [SimpleNamespace(value=SensorReading.create('s', t, 50, 1010).to_json().encode())
                for t in (25, 75)]
    detector = RuleBasedAnomalyDetector()
    with patch.object(sensor_consumer, 'RuleBasedAnomalyDetector', return_value=detector) as factory:
        with patch.object(detector, 'detect', wraps=detector.detect) as detect:
            sensor_consumer.consume_messages(messages)
            factory.assert_called_once_with()
            assert detect.call_count == 2
    output = capsys.readouterr().out
    assert 'NORMAL |' in output and 'ANOMALY |' in output


def test_consume_messages_uses_injected_detector(capsys):
    from types import SimpleNamespace
    from src.detectors.anomaly_detector import RangeRule, RuleBasedAnomalyDetector
    from src.models.sensor_reading import SensorReading
    detector = RuleBasedAnomalyDetector([RangeRule('temperature', 0, 80)])
    message = SimpleNamespace(value=SensorReading.create('s', 75, 95, 900).to_json().encode())
    with patch.object(sensor_consumer, 'RuleBasedAnomalyDetector') as factory:
        sensor_consumer.consume_messages([message, message], detector)
        factory.assert_not_called()
    assert capsys.readouterr().out.count('NORMAL |') == 2
