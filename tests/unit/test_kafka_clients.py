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
