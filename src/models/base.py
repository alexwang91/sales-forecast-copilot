"""Forecast model interfaces used by evaluation and later ensembles."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date

import pandas as pd


FORECAST_OUTPUT_COLUMNS = (
    "forecast_run_id",
    "run_date",
    "forecast_week",
    "region",
    "country",
    "channel",
    "sku",
    "target",
    "p10",
    "p50",
    "p90",
    "model_name",
    "scenario_name",
    "horizon",
)


@dataclass(frozen=True)
class QuantileForecast:
    """Lightweight wrapper for schema-shaped quantile forecast rows."""

    frame: pd.DataFrame

    def to_frame(self) -> pd.DataFrame:
        missing = set(FORECAST_OUTPUT_COLUMNS) - set(self.frame.columns)
        if missing:
            missing_text = ", ".join(sorted(missing))
            raise ValueError(f"forecast output missing columns: {missing_text}")
        return self.frame.loc[:, list(FORECAST_OUTPUT_COLUMNS)].copy()


class BaseForecaster(ABC):
    """Minimal pluggable forecaster interface for P1 and later model adapters."""

    name: str

    @abstractmethod
    def fit(self, panel: pd.DataFrame, features: pd.DataFrame | None = None, *, as_of: date) -> None:
        """Fit using only rows visible at or before `as_of`."""

    @abstractmethod
    def predict(self, horizon: int, future_covariates: pd.DataFrame | None = None) -> pd.DataFrame:
        """Return forecast rows shaped like the `forecast_output` contract."""
