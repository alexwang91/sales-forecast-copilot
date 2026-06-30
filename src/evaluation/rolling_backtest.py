"""Rolling-origin backtest utilities."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

import pandas as pd

from src.models.base import BaseForecaster


SERIES_COLUMNS = ["country", "channel", "sku"]
ACTUAL_JOIN_COLUMNS = ["forecast_week", "country", "channel", "sku"]


@dataclass(frozen=True)
class BacktestConfig:
    """Configuration for a rolling-origin backtest run."""

    origins: tuple[date, ...]
    horizon: int = 4
    target: str = "sell_out"

    def __post_init__(self) -> None:
        if not self.origins:
            raise ValueError("origins must not be empty")
        if self.horizon <= 0:
            raise ValueError("horizon must be positive")


def run_rolling_backtest(panel: pd.DataFrame, forecaster: BaseForecaster, config: BacktestConfig) -> pd.DataFrame:
    """Run one forecaster across rolling origins and attach observed labels."""

    _require_panel_columns(panel, config.target)
    prepared = panel.copy()
    prepared["week_start"] = pd.to_datetime(prepared["week_start"])

    frames: list[pd.DataFrame] = []
    for origin in config.origins:
        origin_ts = pd.Timestamp(origin)
        train_panel = prepared.loc[prepared["week_start"] <= origin_ts].copy()
        if train_panel.empty:
            raise ValueError(f"no training rows at or before origin {origin}")

        forecaster.fit(train_panel, as_of=origin)
        forecast = forecaster.predict(config.horizon).copy()
        forecast["forecast_week"] = pd.to_datetime(forecast["forecast_week"])
        forecast["origin"] = origin_ts

        actuals = _actuals_for_join(prepared, config.target)
        joined = forecast.merge(actuals, on=ACTUAL_JOIN_COLUMNS, how="left")
        missing = int(joined["actual"].isna().sum())
        if missing:
            raise ValueError(f"missing actuals for {missing} forecast rows")
        frames.append(joined)

    if not frames:
        return pd.DataFrame()
    result = pd.concat(frames, ignore_index=True)
    ordered = [
        "origin",
        "horizon",
        "country",
        "channel",
        "sku",
        "actual",
        "p10",
        "p50",
        "p90",
        "model_name",
        "scenario_name",
    ]
    extras = [column for column in result.columns if column not in ordered]
    return result.loc[:, ordered + extras]


def _require_panel_columns(panel: pd.DataFrame, target: str) -> None:
    required = {"week_start", "country", "channel", "sku", target}
    missing = required - set(panel.columns)
    if missing:
        raise ValueError(f"panel missing columns: {', '.join(sorted(missing))}")


def _actuals_for_join(panel: pd.DataFrame, target: str) -> pd.DataFrame:
    actuals = panel.loc[:, ["week_start", "country", "channel", "sku", target]].copy()
    actuals = actuals.rename(columns={"week_start": "forecast_week", target: "actual"})
    actuals["forecast_week"] = pd.to_datetime(actuals["forecast_week"])
    return actuals
