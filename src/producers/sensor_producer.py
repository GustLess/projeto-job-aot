import time

from kafka import KafkaProducer

from src.collectors.simulator import SensorSimulator


KAFKA_BROKER = "kafka:29092"
TOPIC = "sensor-readings"


def create_producer():
    return KafkaProducer(
        bootstrap_servers=KAFKA_BROKER,
        value_serializer=lambda value: value.encode("utf-8"),
    )


if __name__ == "__main__":
    simulator = SensorSimulator()
    producer = create_producer()

    print(f"Producer iniciado. Enviando dados para '{TOPIC}'.")
    print("Ctrl+C para parar.\n")

    try:
        while True:
            reading = simulator.generate_reading()
            message = reading.to_json()

            producer.send(TOPIC, value=message)
            producer.flush()

            print(f"Enviado: {message}")

            time.sleep(1)

    except KeyboardInterrupt:
        print("\nProducer encerrado.")

    finally:
        producer.close()
