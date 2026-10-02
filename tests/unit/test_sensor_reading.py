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
        ('{"sensor_id":"sensor-001"}', ValueError),
        (
            '{"sensor_id":null,"timestamp":"t","temperature":1,'
            '"humidity":2,"pressure":3}',
            (AttributeError, ValueError),
        ),
    ],
)
def test_from_json_rejects_invalid_payload(payload, error):
    with pytest.raises(error):
        SensorReading.from_json(payload)


def test_complete_contract_and_unique_ids():
    from datetime import datetime, timedelta
    from uuid import UUID
    first = SensorReading.create('s', 25, 50, 1010)
    second = SensorReading.create('s', 25, 50, 1010)
    assert first.event_id != second.event_id
    assert UUID(first.event_id).version == 4
    assert first.schema_version == 1
    assert datetime.fromisoformat(first.timestamp).utcoffset() == timedelta(0)
    assert set(first.to_dict()) == {'event_id', 'sensor_id', 'timestamp', 'temperature',
                                    'humidity', 'pressure', 'source', 'schema_version'}
    reading = make_reading(event_id='external-event', timestamp='2026-01-02T03:04:05Z')
    assert SensorReading.from_json(reading.to_json()) == reading


@pytest.mark.parametrize('field,value', [
    ('event_id', ''), ('event_id', None), ('sensor_id', 123), ('source', []),
    ('timestamp', 'invalid'), ('timestamp', '2026-01-02T03:04:05'),
    ('timestamp', '2026-01-02T03:04:05+03:00'),
    ('schema_version', 2), ('schema_version', True), ('schema_version', '1'),
    ('temperature', '25'), ('humidity', True), ('pressure', None),
    ('temperature', float('nan')), ('humidity', float('inf')),
    ('pressure', float('-inf')),
])
def test_invalid_fields(field, value):
    with pytest.raises(ValueError):
        make_reading(**{field: value}).validate()


@pytest.mark.parametrize('field', list(SensorReading.__dataclass_fields__))
def test_wire_contract_requires_all_fields(field):
    data = make_reading().to_dict()
    del data[field]
    with pytest.raises(ValueError, match='campos obrigatórios'):
        SensorReading.from_json(json.dumps(data))


@pytest.mark.parametrize('payload', ['null', '[]', '42', '"text"'])
def test_wire_contract_requires_object(payload):
    with pytest.raises(ValueError):
        SensorReading.from_json(payload)


def test_extreme_finite_measurements_are_valid():
    make_reading(temperature=-999, humidity=200, pressure=0).validate()


@pytest.mark.parametrize('value', [True, '25', None, float('nan')])
def test_create_does_not_coerce_invalid_measurements(value):
    with pytest.raises(ValueError):
        SensorReading.create('s', value, 50, 1010)
