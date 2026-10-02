from src.detectors.anomaly_detector import RuleBasedAnomalyDetector
from src.collectors import simulator as simulator_module
from src.collectors.simulator import SensorSimulator


def test_generate_reading_uses_configured_sensor_and_normal_measurements(
    monkeypatch,
):
    values = iter([24.123, 60.456, 1010.789])
    monkeypatch.setattr(simulator_module.random, "choice", lambda items: items[0])
    monkeypatch.setattr(simulator_module.random, "uniform", lambda *_: next(values))
    monkeypatch.setattr(simulator_module.random, "random", lambda: 1.0)
    simulator = SensorSimulator(sensor_ids=["sensor-test"], anomaly_probability=0)

    reading = simulator.generate_reading()

    assert reading.sensor_id == "sensor-test"
    assert reading.temperature == 24.12
    assert reading.humidity == 60.46
    assert reading.pressure == 1010.79
    assert reading.source == "simulator"
    reading.validate()
    assert not RuleBasedAnomalyDetector().detect(reading).is_anomaly


def test_generate_reading_can_select_each_anomaly_branch(monkeypatch):
    anomaly_values = {"temperature": 75.0, "humidity": 95.0, "pressure": 900.0}

    for branch, expected in anomaly_values.items():
        values = iter([25.0, 50.0, 1010.0, expected])
        choices = iter(["sensor-test", branch])
        monkeypatch.setattr(simulator_module.random, "choice", lambda _: next(choices))
        monkeypatch.setattr(simulator_module.random, "uniform", lambda *_: next(values))
        monkeypatch.setattr(simulator_module.random, "random", lambda: 0.0)

        reading = SensorSimulator(anomaly_probability=1).generate_reading()

        assert getattr(reading, branch) == expected
        result = RuleBasedAnomalyDetector().detect(reading)
        assert [v.variable for v in result.violations] == [branch]


def test_normal_range_endpoints(monkeypatch):
    for index in (0, 1):
        monkeypatch.setattr(simulator_module.random, "uniform", lambda low, high: (low, high)[index])
        reading = SensorSimulator(anomaly_probability=0).generate_reading()
        reading.validate()
        assert not RuleBasedAnomalyDetector().detect(reading).is_anomaly
