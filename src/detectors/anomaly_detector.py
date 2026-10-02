"""Regras inclusivas alinhadas às faixas normais do simulador."""
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Iterable

from src.models.sensor_reading import SensorReading


@dataclass(frozen=True)
class RangeRule:
    variable: str
    minimum: float
    maximum: float


DEFAULT_RULES = (
    RangeRule("temperature", 20.0, 30.0),
    RangeRule("humidity", 40.0, 75.0),
    RangeRule("pressure", 1000.0, 1025.0),
)


@dataclass(frozen=True)
class RuleViolation:
    variable: str
    observed_value: float
    minimum: float
    maximum: float
    rule: str


@dataclass(frozen=True)
class DetectionResult:
    event_id: str
    is_anomaly: bool
    violations: tuple[RuleViolation, ...]
    detector_name: str
    detector_version: str
    detected_at: str

    def to_dict(self):
        result = asdict(self)
        result["violations"] = [asdict(v) for v in self.violations]
        return result


class RuleBasedAnomalyDetector:
    detector_name = "rule-based-range"
    detector_version = "1.0.0"

    def __init__(self, rules: Iterable[RangeRule] | None = None):
        self._rules = tuple(DEFAULT_RULES if rules is None else rules)

    def detect(self, reading: SensorReading) -> DetectionResult:
        reading.validate()
        violations = []
        for rule in self._rules:
            value = getattr(reading, rule.variable)
            if value < rule.minimum or value > rule.maximum:
                violations.append(RuleViolation(
                    rule.variable, value, rule.minimum, rule.maximum,
                    "below_minimum" if value < rule.minimum else "above_maximum",
                ))
        return DetectionResult(
            reading.event_id, bool(violations), tuple(violations),
            self.detector_name, self.detector_version,
            datetime.now(timezone.utc).isoformat(),
        )
