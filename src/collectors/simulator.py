import random
import time

from src.models.sensor_reading import SensorReading


class SensorSimulator:
    def __init__(self, sensor_ids=None, anomaly_probability=0.05):
        self.sensor_ids = sensor_ids or [
            "sensor-001",
            "sensor-002",
            "sensor-003",
        ]
        self.anomaly_probability = anomaly_probability

    def generate_reading(self) -> SensorReading:
        sensor_id = random.choice(self.sensor_ids)

        temperature = random.uniform(20.0, 30.0)
        humidity = random.uniform(40.0, 75.0)
        pressure = random.uniform(1000.0, 1025.0)

        # Ocasionalmente gera uma leitura propositalmente anômala.
        if random.random() < self.anomaly_probability:
            anomaly_type = random.choice(
                ["temperature", "humidity", "pressure"]
            )

            if anomaly_type == "temperature":
                temperature = random.uniform(60.0, 100.0)

            elif anomaly_type == "humidity":
                humidity = random.uniform(90.0, 100.0)

            elif anomaly_type == "pressure":
                pressure = random.uniform(850.0, 930.0)

        return SensorReading.create(
            sensor_id=sensor_id,
            temperature=round(temperature, 2),
            humidity=round(humidity, 2),
            pressure=round(pressure, 2),
        )


if __name__ == "__main__":
    simulator = SensorSimulator()

    print("Simulador de sensores iniciado. Ctrl+C para parar.\n")

    try:
        while True:
            reading = simulator.generate_reading()
            print(reading.to_json())
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nSimulador encerrado.")
