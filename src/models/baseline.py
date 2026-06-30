"""Simple baseline forecasters for P1 backtesting."""

from __future__ import annotations

from datetime import date, timedelta

import pandas as pd

from src.models.base import BaseForecaster, FORECAST_OUTPUT_COLUMNS, QuantileForecast


SERIES_COLUMNS = ["region", "country", "channel", "sku"]


class MovingAverage8w(BaseForecaster):
    """Flat quantile forecast using each series' last 8 visible weeks."""

    name = "MovingAverage8w"

    def __init__(self, target: str = "sell_out", scenario_name: str = "baseline") -> None:
        self.target = target
        self.scenario_name = scenario_name
        self._as_of: date | None = None
        self._summary: pd.DataFrame | None = None

    def fit(self, panel: pd.DataFrame, features: pd.DataFrame | None = None, *, as_of: date) -> None:
        if self.target not in panel.columns:
            raise ValueError(f"unknown target column: {self.target}")
        required = {"week_start", *SERIES_COLUMNS, self.target}
        missing = required - set(panel.columns)
        if missing:
            raise ValueError(f"panel missing columns: {', '.join(sorted(missing))}")

        visible = panel.copy()
        visible["week_start"] = pd.to_datetime(visible["week_start"])
        visible = visible.loc[visible["week_start"] <= pd.Timestamp(as_of)].copy()
        if visible.empty:
            raise ValueError("no visible rows at or before as_of")

        rows: list[dict[str, object]] = []
        for key, group in visible.groupby(SERIES_COLUMNS, dropna=False):
            recent = group.sort_values("week_start").tail(8)
            values = pd.to_numeric(recent[self.target], errors="coerce")
            if values.isna().any():
                raise ValueError("target contains non-numeric values")
            p50 = float(values.mean())
            std = float(values.std(ddof=0)) if len(values) > 1 else 0.0
            spread = max(std, p50 * 0.10, 1.0)
            row = dict(zip(SERIES_COLUMNS, key, strict=True))
            row.update({"p50": p50, "spread": spread})
            rows.append(row)

        self._summary = pd.DataFrame(rows)
        self._as_of = as_of

    def predict(self, horizon: int, future_covariates: pd.DataFrame | None = None) -> pd.DataFrame:
        if self._summary is None or self._as_of is None:
            raise RuntimeError("fit must be called before predict")
        if horizon <= 0:
            raise ValueError("horizon must be positive")

        output: list[dict[str, object]] = []
        for _, series in self._summary.iterrows():
            p50 = float(series["p50"])
            spread = float(series["spread"])
            for step in range(1, horizon + 1):
                output.append(
                    {
                        "forecast_run_id": "moving-average-8w",
                        "run_date": self._as_of,
                        "forecast_week": self._as_of + timedelta(weeks=step),
                        "region": series["region"],
                        "country": series["country"],
                        "channel": series["channel"],
                        "sku": series["sku"],
                        "target": self.target,
                        "p10": max(0.0, p50 - spread),
                        "p50": p50,
                        "p90": p50 + spread,
                        "model_name": self.name,
                        "scenario_name": self.scenario_name,
                        "horizon": step,
                    }
                )
        return QuantileForecast(pd.DataFrame(output)).to_frame().loc[:, list(FORECAST_OUTPUT_COLUMNS)]
