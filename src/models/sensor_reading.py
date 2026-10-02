from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import uuid4
import json
import math


@dataclass
class SensorReading:
    """Evento v1; valores extremos finitos são válidos, não necessariamente normais."""

    sensor_id: str
    timestamp: str
    temperature: float
    humidity: float
    pressure: float
    source: str = "simulator"
    event_id: str = field(default_factory=lambda: str(uuid4()))
    schema_version: int = 1

    @classmethod
    def create(cls, sensor_id, temperature, humidity, pressure, source="simulator"):
        reading = cls(
            sensor_id=sensor_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            temperature=temperature, humidity=humidity, pressure=pressure, source=source,
        )
        reading.validate()
        reading.temperature = float(temperature)
        reading.humidity = float(humidity)
        reading.pressure = float(pressure)
        return reading

    def validate(self) -> None:
        for name in ("sensor_id", "event_id", "source", "timestamp"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} deve ser texto não vazio")
        try:
            timestamp = datetime.fromisoformat(self.timestamp.replace("Z", "+00:00"))
        except ValueError as error:
            raise ValueError("timestamp deve ser ISO 8601 UTC") from error
        if timestamp.utcoffset() != timedelta(0):
            raise ValueError("timestamp deve incluir fuso UTC (Z ou +00:00)")
        if type(self.schema_version) is not int or self.schema_version != 1:
            raise ValueError("schema_version suportada: 1")
        for name in ("temperature", "humidity", "pressure"):
            value = getattr(self, name)
            if type(value) not in (int, float):
                raise ValueError(f"{name} deve ser numérico e finito")
            try:
                finite = math.isfinite(value)
            except OverflowError:
                finite = False
            if not finite:
                raise ValueError(f"{name} deve ser numérico e finito")

    def to_dict(self) -> dict[str, Any]:
        self.validate()
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, allow_nan=False)

    @classmethod
    def from_json(cls, message: str) -> "SensorReading":
        data = json.loads(message)
        if not isinstance(data, dict):
            raise ValueError("evento deve ser um objeto JSON")
        required = set(cls.__dataclass_fields__)
        if required - data.keys():
            raise ValueError(f"campos obrigatórios ausentes: {sorted(required - data.keys())}")
        reading = cls(**data)
        reading.validate()
        return reading
