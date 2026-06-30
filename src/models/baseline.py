from __future__ import annotations

from datetime import date, timedelta

import pandas as pd


SERIES_COLUMNS = ["region", "country", "channel", "sku"]
FORECAST_COLUMNS = [
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
]


def _forecast_frame(rows: list[dict]) -> pd.DataFrame:
    return pd.DataFrame(rows).loc[:, FORECAST_COLUMNS]


def _quantiles(value: float) -> tuple[float, float, float]:
    p50 = max(0.0, float(value))
    return max(0.0, p50 * 0.9), p50, p50 * 1.1


class SeasonalNaive:
    name = "SeasonalNaive"

    def __init__(self, season_length: int = 52, target: str = "sell_out", scenario_name: str = "baseline") -> None:
        if season_length <= 0:
            raise ValueError("season_length must be positive")
        self.season_length = season_length
        self.target = target
        self.scenario_name = scenario_name
        self._history: pd.DataFrame | None = None
        self._as_of: date | None = None

    def fit(self, panel: pd.DataFrame, features: pd.DataFrame | None = None, *, as_of: date) -> None:
        if self.target not in panel.columns:
            raise ValueError(f"target column not found: {self.target}")
        frame = panel.copy()
        frame["week_start"] = pd.to_datetime(frame["week_start"])
        frame = frame.loc[frame["week_start"] <= pd.Timestamp(as_of)].copy()
        self._history = frame.sort_values([*SERIES_COLUMNS, "week_start"]).reset_index(drop=True)
        self._as_of = as_of

    def predict(self, horizon: int, future_covariates: pd.DataFrame | None = None) -> pd.DataFrame:
        if self._history is None or self._as_of is None:
            raise RuntimeError("fit must be called before predict")
        if horizon <= 0:
            raise ValueError("horizon must be positive")

        rows = []
        for key, group in self._history.groupby(SERIES_COLUMNS, dropna=False):
            ordered = group.sort_values("week_start").reset_index(drop=True)
            for step in range(1, horizon + 1):
                index = len(ordered) - self.season_length + step - 1
                if index < 0 or index >= len(ordered):
                    value = ordered[self.target].tail(1).iloc[0]
                else:
                    value = ordered[self.target].iloc[index]
                p10, p50, p90 = _quantiles(float(value))
                series_values = dict(zip(SERIES_COLUMNS, key, strict=True))
                rows.append({
                    "forecast_run_id": "seasonal-naive",
                    "run_date": self._as_of,
                    "forecast_week": self._as_of + timedelta(weeks=step),
                    **series_values,
                    "target": self.target,
                    "p10": p10,
                    "p50": p50,
                    "p90": p90,
                    "model_name": self.name,
                    "scenario_name": self.scenario_name,
                    "horizon": step,
                })
        return _forecast_frame(rows)


class RecentTrendBaseline:
    name = "RecentTrendBaseline"

    def __init__(self, window: int = 8, target: str = "sell_out", scenario_name: str = "baseline") -> None:
        if window <= 1:
            raise ValueError("window must be greater than 1")
        self.window = window
        self.target = target
        self.scenario_name = scenario_name
        self._history: pd.DataFrame | None = None
        self._as_of: date | None = None

    def fit(self, panel: pd.DataFrame, features: pd.DataFrame | None = None, *, as_of: date) -> None:
        if self.target not in panel.columns:
            raise ValueError(f"target column not found: {self.target}")
        frame = panel.copy()
        frame["week_start"] = pd.to_datetime(frame["week_start"])
        frame = frame.loc[frame["week_start"] <= pd.Timestamp(as_of)].copy()
        self._history = frame.sort_values([*SERIES_COLUMNS, "week_start"]).reset_index(drop=True)
        self._as_of = as_of

    def predict(self, horizon: int, future_covariates: pd.DataFrame | None = None) -> pd.DataFrame:
        if self._history is None or self._as_of is None:
            raise RuntimeError("fit must be called before predict")
        if horizon <= 0:
            raise ValueError("horizon must be positive")

        rows = []
        for key, group in self._history.groupby(SERIES_COLUMNS, dropna=False):
            ordered = group.sort_values("week_start").reset_index(drop=True)
            recent = ordered[self.target].tail(self.window).astype(float)
            last_value = float(recent.iloc[-1])
            average_delta = 0.0 if len(recent) < 2 else float(recent.diff().dropna().mean())
            for step in range(1, horizon + 1):
                value = last_value + average_delta * step
                p10, p50, p90 = _quantiles(value)
                series_values = dict(zip(SERIES_COLUMNS, key, strict=True))
                rows.append({
                    "forecast_run_id": "recent-trend",
                    "run_date": self._as_of,
                    "forecast_week": self._as_of + timedelta(weeks=step),
                    **series_values,
                    "target": self.target,
                    "p10": p10,
                    "p50": p50,
                    "p90": p90,
                    "model_name": self.name,
                    "scenario_name": self.scenario_name,
                    "horizon": step,
                })
        return _forecast_frame(rows)
