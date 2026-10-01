import json

import pytest

from src.models.sensor_reading import SensorReading


def make_reading(**overrides):
    values = {
        "sensor_id": "sensor-001",
        "timestamp": "2026-01-02T03:04:05+00:00",
        "temperature": 21.5,
        "humidity": 55.0,
        "pressure": 1012.0,
        "source": "unit-test",
    }
    values.update(overrides)
    return SensorReading(**values)


def test_create_converts_measurements_to_float():
    reading = SensorReading.create("sensor-001", 21, 55, 1012)

    assert reading.sensor_id == "sensor-001"
    assert isinstance(reading.temperature, float)
    assert isinstance(reading.humidity, float)
    assert isinstance(reading.pressure, float)
    assert reading.source == "simulator"


def test_json_round_trip_preserves_reading():
    original = make_reading(sensor_id="sensor-é")

    restored = SensorReading.from_json(original.to_json())

    assert restored == original


@pytest.mark.parametrize(
    "field", ["sensor_id", "timestamp", "source"]
)
def test_validate_rejects_blank_required_text(field):
    reading = make_reading(**{field: "   "})

    with pytest.raises(ValueError):
        reading.validate()


@pytest.mark.parametrize(
    "payload, error",
    [
        ("{invalid", json.JSONDecodeError),
        ('{"sensor_id":"sensor-001"}', TypeError),
        (
            '{"sensor_id":null,"timestamp":"t","temperature":1,'
            '"humidity":2,"pressure":3}',
            (AttributeError, TypeError),
        ),
    ],
)
def test_from_json_rejects_invalid_payload(payload, error):
    with pytest.raises(error):
        SensorReading.from_json(payload)
