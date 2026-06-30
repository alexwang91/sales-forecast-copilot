"""Forecast evaluation metrics for the P1 backtest spine."""

from __future__ import annotations

from collections.abc import Iterable

import numpy as np


def wape(actual: Iterable[float], predicted: Iterable[float]) -> float:
    """Return weighted absolute percentage error: sum(abs(err)) / sum(actual)."""

    actual_values, predicted_values = _aligned_arrays(actual, predicted)
    denominator = float(np.sum(np.abs(actual_values)))
    numerator = float(np.sum(np.abs(actual_values - predicted_values)))
    if denominator == 0:
        if numerator == 0:
            return 0.0
        raise ValueError("actual sum is zero while forecast error is nonzero")
    return numerator / denominator


def weighted_wape(actual: Iterable[float], predicted: Iterable[float], weights: Iterable[float]) -> float:
    """Return WAPE after applying explicit non-negative row weights."""

    actual_values, predicted_values = _aligned_arrays(actual, predicted)
    weight_values = _as_float_array(weights, "weights")
    if len(weight_values) != len(actual_values):
        raise ValueError("weights length must match actual length")
    if np.any(weight_values < 0):
        raise ValueError("weights must be non-negative")
    denominator = float(np.sum(np.abs(actual_values) * weight_values))
    numerator = float(np.sum(np.abs(actual_values - predicted_values) * weight_values))
    if denominator == 0:
        if numerator == 0:
            return 0.0
        raise ValueError("weighted actual sum is zero while forecast error is nonzero")
    return numerator / denominator


def bias(actual: Iterable[float], predicted: Iterable[float]) -> float:
    """Return signed bias. Positive means over-forecasting."""

    actual_values, predicted_values = _aligned_arrays(actual, predicted)
    denominator = float(np.sum(actual_values))
    if denominator == 0:
        if float(np.sum(predicted_values - actual_values)) == 0:
            return 0.0
        raise ValueError("actual sum is zero while bias is nonzero")
    return float(np.sum(predicted_values - actual_values) / denominator)


def p90_coverage(actual: Iterable[float], p90: Iterable[float]) -> float:
    """Return the share of actual values below or equal to predicted P90."""

    actual_values, p90_values = _aligned_arrays(actual, p90)
    if len(actual_values) == 0:
        raise ValueError("coverage requires at least one value")
    return float(np.mean(actual_values <= p90_values))


def pinball_loss(actual: Iterable[float], predicted_quantile: Iterable[float], *, quantile: float) -> float:
    """Return average pinball loss for one quantile forecast."""

    if quantile <= 0 or quantile >= 1:
        raise ValueError("quantile must be between 0 and 1")
    actual_values, predicted_values = _aligned_arrays(actual, predicted_quantile)
    if len(actual_values) == 0:
        raise ValueError("pinball loss requires at least one value")
    residual = actual_values - predicted_values
    losses = np.maximum(quantile * residual, (quantile - 1) * residual)
    return float(np.mean(losses))


def _aligned_arrays(actual: Iterable[float], predicted: Iterable[float]) -> tuple[np.ndarray, np.ndarray]:
    actual_values = _as_float_array(actual, "actual")
    predicted_values = _as_float_array(predicted, "predicted")
    if len(actual_values) != len(predicted_values):
        raise ValueError("actual and predicted must have the same length")
    return actual_values, predicted_values


def _as_float_array(values: Iterable[float], name: str) -> np.ndarray:
    array = np.asarray(list(values), dtype=float)
    if array.ndim != 1:
        raise ValueError(f"{name} must be one-dimensional")
    if np.any(~np.isfinite(array)):
        raise ValueError(f"{name} must contain only finite numeric values")
    return array
