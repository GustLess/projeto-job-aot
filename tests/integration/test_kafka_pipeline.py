import os
import time
import uuid

import pytest

from src.consumers.sensor_consumer import TOPIC, create_consumer
from src.models.sensor_reading import SensorReading
from src.producers.sensor_producer import create_producer


pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        os.getenv("RUN_KAFKA_INTEGRATION") != "1",
        reason="defina RUN_KAFKA_INTEGRATION=1 para executar com Kafka",
    ),
]


def test_sensor_reading_round_trip_through_kafka():
    marker = f"integration-{uuid.uuid4()}"
    reading = SensorReading.create(marker, 23.5, 51.0, 1013.0)
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
                        received = restored
                        break

        assert received == reading
    finally:
        consumer.close()
        producer.close()
