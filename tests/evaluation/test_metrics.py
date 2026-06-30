import pytest

from src.evaluation.metrics import bias, p90_coverage, pinball_loss, wape, weighted_wape


def test_wape_uses_absolute_error_over_total_actual():
    assert wape([100, 50], [90, 60]) == pytest.approx(20 / 150)


def test_wape_returns_zero_when_actual_and_prediction_are_all_zero():
    assert wape([0, 0], [0, 0]) == 0.0


def test_wape_rejects_zero_actual_with_nonzero_prediction():
    with pytest.raises(ValueError, match="actual sum is zero"):
        wape([0, 0], [0, 3])


def test_weighted_wape_uses_explicit_weights():
    assert weighted_wape([100, 50], [90, 65], [2, 1]) == pytest.approx(35 / 250)


def test_bias_is_positive_for_over_forecast():
    assert bias([100, 100], [110, 120]) == pytest.approx(30 / 200)


def test_p90_coverage_counts_actual_values_below_or_equal_to_p90():
    assert p90_coverage([10, 20, 40, 50], [11, 19, 40, 60]) == pytest.approx(3 / 4)


def test_pinball_loss_matches_hand_calculation_for_p90():
    assert pinball_loss([110, 90], [100, 100], quantile=0.9) == pytest.approx(5.0)


def test_pinball_loss_rejects_invalid_quantile():
    with pytest.raises(ValueError, match="quantile"):
        pinball_loss([1], [1], quantile=1.5)
