import sys

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


if __name__ == "__main__":
    consumer = None

    try:
        consumer = create_consumer()
        print(f"Consumer iniciado. Lendo dados de '{TOPIC}'.")
        print("Ctrl+C para parar.\n")

        for message in consumer:
            try:
                reading = deserialize_reading(message.value)
            except ValueError as error:
                print(f"Mensagem ignorada: {error}", file=sys.stderr)
                continue

            print(
                f"Sensor: {reading.sensor_id} | "
                f"Temperatura: {reading.temperature} °C | "
                f"Umidade: {reading.humidity}% | "
                f"Pressão: {reading.pressure} hPa"
            )

    except KeyboardInterrupt:
        print("\nConsumer encerrado.")
    except KafkaError as error:
        print(f"Erro Kafka no consumer: {error}", file=sys.stderr)

    finally:
        if consumer is not None:
            consumer.close()
