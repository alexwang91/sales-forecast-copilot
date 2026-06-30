"""Forecast Value Add helpers."""

from __future__ import annotations

from collections.abc import Iterable

from src.evaluation.metrics import wape


def forecast_value_add(baseline_wape: float, candidate_wape: float) -> float:
    """Return FVA as baseline WAPE minus candidate WAPE."""

    return float(baseline_wape - candidate_wape)


def fva_from_predictions(actual: Iterable[float], baseline: Iterable[float], candidate: Iterable[float]) -> float:
    """Compute FVA directly from actual, baseline, and candidate predictions."""

    return forecast_value_add(wape(actual, baseline), wape(actual, candidate))
