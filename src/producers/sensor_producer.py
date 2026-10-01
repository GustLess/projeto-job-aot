import time
import sys

from kafka import KafkaProducer
from kafka.errors import KafkaError

from src.collectors.simulator import SensorSimulator
from src.kafka_config import get_kafka_bootstrap_servers


TOPIC = "sensor-readings"


def create_producer():
    return KafkaProducer(
        bootstrap_servers=get_kafka_bootstrap_servers(),
        value_serializer=lambda value: value.encode("utf-8"),
    )


if __name__ == "__main__":
    simulator = SensorSimulator()
    producer = None

    try:
        producer = create_producer()
        print(f"Producer iniciado. Enviando dados para '{TOPIC}'.")
        print("Ctrl+C para parar.\n")

        while True:
            reading = simulator.generate_reading()
            message = reading.to_json()

            producer.send(TOPIC, value=message).get(timeout=10)

            print(f"Enviado: {message}")

            time.sleep(1)

    except KeyboardInterrupt:
        print("\nProducer encerrado.")
    except (KafkaError, TimeoutError) as error:
        print(f"Erro Kafka no producer: {error}", file=sys.stderr)

    finally:
        if producer is not None:
            producer.close()
