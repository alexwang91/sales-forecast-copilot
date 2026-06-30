import pytest

from src.evaluation.fva import forecast_value_add, fva_from_predictions


def test_forecast_value_add_is_baseline_wape_minus_candidate_wape():
    assert forecast_value_add(0.30, 0.22) == pytest.approx(0.08)


def test_forecast_value_add_can_be_negative_when_candidate_is_worse():
    assert forecast_value_add(0.20, 0.25) == pytest.approx(-0.05)


def test_fva_from_predictions_computes_wape_delta():
    actual = [100, 50]
    baseline = [80, 70]
    candidate = [90, 60]

    assert fva_from_predictions(actual, baseline, candidate) == pytest.approx(20 / 150)
