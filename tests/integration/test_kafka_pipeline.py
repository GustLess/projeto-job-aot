import os
import time
import uuid

import pytest

from src.consumers.sensor_consumer import TOPIC, create_consumer, process_message
from src.models.sensor_reading import SensorReading
from src.producers.sensor_producer import create_producer


pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        os.getenv("RUN_KAFKA_INTEGRATION") != "1",
        reason="defina RUN_KAFKA_INTEGRATION=1 para executar com Kafka",
    ),
]


@pytest.mark.parametrize("temperature,is_anomaly", [(23.5, False), (75.0, True)])
def test_sensor_reading_round_trip_through_kafka(temperature, is_anomaly):
    marker = f"integration-{uuid.uuid4()}"
    reading = SensorReading.create(marker, temperature, 51.0, 1013.0)
    producer = create_producer()
    consumer = create_consumer(group_id=f"test-{uuid.uuid4()}")
    received = None

    try:
        producer.send(TOPIC, value=reading.to_json()).get(timeout=10)
        deadline = time.monotonic() + 20

        while time.monotonic() < deadline and received is None:
            records = consumer.poll(timeout_ms=1000)
            for messages in records.values():
                for message in messages:
                    restored = SensorReading.from_json(message.value.decode("utf-8"))
                    if restored.sensor_id == marker:
                        result = process_message(message.value)
                        assert result.event_id == reading.event_id
                        assert result.is_anomaly is is_anomaly
                        assert [v.variable for v in result.violations] == (["temperature"] if is_anomaly else [])
                        received = restored
                        break

        assert received == reading
    finally:
        consumer.close()
        producer.close()
