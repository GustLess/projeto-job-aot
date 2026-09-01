from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any
import json


@dataclass
class SensorReading:
    """Representa uma medição produzida por um sensor."""

    sensor_id: str
    timestamp: str
    temperature: float
    humidity: float
    pressure: float
    source: str = "simulator"

    @classmethod
    def create(
        cls,
        sensor_id: str,
        temperature: float,
        humidity: float,
        pressure: float,
        source: str = "simulator",
    ) -> "SensorReading":
        """Cria uma leitura usando o horário UTC atual."""

        return cls(
            sensor_id=sensor_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            temperature=float(temperature),
            humidity=float(humidity),
            pressure=float(pressure),
            source=source,
        )

    def validate(self) -> None:
        """Valida os campos obrigatórios da leitura."""

        if not self.sensor_id.strip():
            raise ValueError("sensor_id não pode ser vazio")

        if not self.timestamp.strip():
            raise ValueError("timestamp não pode ser vazio")

        if not self.source.strip():
            raise ValueError("source não pode ser vazio")

    def to_dict(self) -> dict[str, Any]:
        """Converte a leitura para um dicionário."""

        self.validate()
        return asdict(self)

    def to_json(self) -> str:
        """Converte a leitura para JSON."""

        return json.dumps(self.to_dict(), ensure_ascii=False)

    @classmethod
    def from_json(cls, message: str) -> "SensorReading":
        """Cria uma leitura a partir de uma mensagem JSON."""

        data = json.loads(message)
        reading = cls(**data)
        reading.validate()
        return reading