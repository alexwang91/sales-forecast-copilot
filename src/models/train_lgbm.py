from __future__ import annotations

from datetime import date
from typing import Callable, Protocol

import pandas as pd

from src.models.baseline import FORECAST_COLUMNS, SERIES_COLUMNS


class QuantileBackend(Protocol):
    def fit(self, frame: pd.DataFrame, target: str) -> None: ...
    def predict(self, frame: pd.DataFrame) -> list[float]: ...


class LightGBMQuantileForecaster:
    name = "LightGBMQuantile"

    def __init__(
        self,
        feature_columns: list[str],
        target: str = "sell_out",
        scenario_name: str = "baseline",
        backend_factory: Callable[[float], QuantileBackend] | None = None,
    ) -> None:
        self.feature_columns = feature_columns
        self.target = target
        self.scenario_name = scenario_name
        self.backend_factory = backend_factory
        self._models: dict[float, QuantileBackend] = {}
        self._as_of: date | None = None

    def fit(self, panel: pd.DataFrame, features: pd.DataFrame | None = None, *, as_of: date) -> None:
        if self.backend_factory is None:
            raise ImportError("LightGBM backend is not installed; pass backend_factory or install lightgbm.")
        frame = panel.copy()
        frame["week_start"] = pd.to_datetime(frame["week_start"])
        frame = frame.loc[frame["week_start"] <= pd.Timestamp(as_of)].copy()
        self._validate_columns(frame, [self.target, *self.feature_columns])
        self._models = {}
        for quantile in [0.1, 0.5, 0.9]:
            model = self.backend_factory(quantile)
            model.fit(frame, self.target)
            self._models[quantile] = model
        self._as_of = as_of

    def predict(self, horizon: int, future_covariates: pd.DataFrame | None = None) -> pd.DataFrame:
        if self._as_of is None or not self._models:
            raise RuntimeError("fit must be called before predict")
        if future_covariates is None:
            raise ValueError("future_covariates are required")
        if horizon <= 0:
            raise ValueError("horizon must be positive")
        frame = future_covariates.copy()
        self._validate_columns(frame, [*SERIES_COLUMNS, "forecast_week", "horizon", *self.feature_columns])
        frame = frame.loc[frame["horizon"] <= horizon].copy().reset_index(drop=True)
        predictions = {
            0.1: self._models[0.1].predict(frame),
            0.5: self._models[0.5].predict(frame),
            0.9: self._models[0.9].predict(frame),
        }
        result = frame.loc[:, [*SERIES_COLUMNS, "forecast_week", "horizon"]].copy()
        result["forecast_run_id"] = "lgbm-quantile"
        result["run_date"] = self._as_of
        result["target"] = self.target
        result["p10"] = predictions[0.1]
        result["p50"] = predictions[0.5]
        result["p90"] = predictions[0.9]
        result["model_name"] = self.name
        result["scenario_name"] = self.scenario_name
        return result.loc[:, FORECAST_COLUMNS]

    def _validate_columns(self, frame: pd.DataFrame, columns: list[str]) -> None:
        missing = [column for column in columns if column not in frame.columns]
        if missing:
            raise ValueError("missing columns: " + ", ".join(missing))
