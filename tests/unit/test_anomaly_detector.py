from datetime import datetime, timedelta

import pytest

from src.detectors.anomaly_detector import DEFAULT_RULES, RuleBasedAnomalyDetector
from src.models.sensor_reading import SensorReading


@pytest.mark.parametrize('values,variables', [
    ((25, 50, 1010), []),
    ((75, 50, 1010), ['temperature']),
    ((25, 95, 1010), ['humidity']),
    ((25, 50, 900), ['pressure']),
    ((75, 95, 900), ['temperature', 'humidity', 'pressure']),
    ((20, 40, 1000), []),
    ((30, 75, 1025), []),
])
def test_classification_and_result(values, variables):
    reading = SensorReading.create('sensor-test', *values)
    result = RuleBasedAnomalyDetector().detect(reading)
    assert result.event_id == reading.event_id
    assert result.is_anomaly == bool(variables)
    assert [v.variable for v in result.violations] == variables
    assert result.detector_name == 'rule-based-range'
    assert result.detector_version == '1.0.0'
    assert datetime.fromisoformat(result.detected_at).utcoffset() == timedelta(0)
    assert len(result.to_dict()['violations']) == len(variables)
    for violation in result.violations:
        assert violation.observed_value == getattr(reading, violation.variable)
        assert violation.minimum < violation.maximum
        assert violation.rule in ('below_minimum', 'above_maximum')


@pytest.mark.parametrize('rule', DEFAULT_RULES)
@pytest.mark.parametrize('side', ['below', 'above'])
def test_each_side_outside_bounds(rule, side):
    reading = SensorReading.create('s', 25, 50, 1010)
    setattr(reading, rule.variable, rule.minimum - 0.01 if side == 'below' else rule.maximum + 0.01)
    result = RuleBasedAnomalyDetector().detect(reading)
    assert len(result.violations) == 1
    assert result.violations[0].rule == ('below_minimum' if side == 'below' else 'above_maximum')


def test_detector_rejects_invalid_reading():
    reading = SensorReading.create('s', 25, 50, 1010)
    reading.temperature = True
    with pytest.raises(ValueError):
        RuleBasedAnomalyDetector().detect(reading)


def test_custom_rules_are_copied_and_replace_defaults():
    from src.detectors.anomaly_detector import RangeRule
    rules = [RangeRule('temperature', 0, 80)]
    detector = RuleBasedAnomalyDetector(rules)
    rules.clear()
    reading = SensorReading.create('s', 75, 95, 900)
    assert not detector.detect(reading).is_anomaly
    reading.temperature = 81
    result = detector.detect(reading)
    assert [v.variable for v in result.violations] == ['temperature']
    assert result.violations[0].maximum == 80


def test_empty_custom_rules_do_not_fall_back_to_defaults():
    reading = SensorReading.create('s', 75, 95, 900)
    assert not RuleBasedAnomalyDetector([]).detect(reading).is_anomaly
    assert RuleBasedAnomalyDetector().detect(reading).is_anomaly
