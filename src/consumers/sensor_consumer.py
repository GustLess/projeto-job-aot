import sys
import json

from src.detectors.anomaly_detector import RuleBasedAnomalyDetector, DetectionResult

from kafka import KafkaConsumer
from kafka.errors import KafkaError

from src.models.sensor_reading import SensorReading
from src.kafka_config import get_kafka_bootstrap_servers


TOPIC = "sensor-readings"
CONSUMER_GROUP = "anomaly-detector"


def create_consumer(group_id=CONSUMER_GROUP):
    return KafkaConsumer(
        TOPIC,
        bootstrap_servers=get_kafka_bootstrap_servers(),
        group_id=group_id,
        auto_offset_reset="earliest",
        enable_auto_commit=True,
    )


def deserialize_reading(value: bytes) -> SensorReading:
    """Decodifica e valida uma mensagem do tópico."""

    try:
        return SensorReading.from_json(value.decode("utf-8"))
    except (UnicodeDecodeError, ValueError, TypeError, AttributeError) as error:
        raise ValueError(f"mensagem inválida: {error}") from error


def process_message(
    value: bytes, detector: RuleBasedAnomalyDetector | None = None,
) -> DetectionResult:
    """Decodifica, valida e classifica, sem efeitos externos."""
    reading = deserialize_reading(value)
    if detector is None:
        detector = RuleBasedAnomalyDetector()
    return detector.detect(reading)


def consume_messages(consumer, detector: RuleBasedAnomalyDetector | None = None) -> None:
    if detector is None:
        detector = RuleBasedAnomalyDetector()
    for message in consumer:
        try:
            result = process_message(message.value, detector)
        except ValueError as error:
            print(f"Mensagem ignorada: {error}", file=sys.stderr)
            continue
        status = "ANOMALY" if result.is_anomaly else "NORMAL"
        print(f"{status} | {json.dumps(result.to_dict(), ensure_ascii=False)}")


if __name__ == "__main__":
    consumer = None

    try:
        consumer = create_consumer()
        print(f"Consumer iniciado. Lendo dados de '{TOPIC}'.")
        print("Ctrl+C para parar.\n")

        consume_messages(consumer)

    except KeyboardInterrupt:
        print("\nConsumer encerrado.")
    except KafkaError as error:
        print(f"Erro Kafka no consumer: {error}", file=sys.stderr)

    finally:
        if consumer is not None:
            consumer.close()
