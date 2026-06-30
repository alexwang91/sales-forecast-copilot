from datetime import date, timedelta

import pandas as pd
import pytest

from src.models.baseline import MovingAverage8w


REQUIRED_FORECAST_COLUMNS = {
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
}


def _single_series_panel(values: list[float]) -> pd.DataFrame:
    start = date(2024, 1, 1)
    return pd.DataFrame(
        [
            {
                "week_start": start + timedelta(weeks=index),
                "region": "CEE",
                "country": "HU",
                "channel": "Retail",
                "sku": "SKU001",
                "sell_in": value + 1,
                "sell_out": value,
            }
            for index, value in enumerate(values)
        ]
    )


def test_moving_average_returns_forecast_output_shape_for_each_horizon():
    panel = _single_series_panel([1, 2, 3, 4, 5, 6, 7, 8])
    forecaster = MovingAverage8w(target="sell_out")
    forecaster.fit(panel, as_of=date(2024, 2, 19))

    forecast = forecaster.predict(horizon=4)

    assert REQUIRED_FORECAST_COLUMNS.issubset(forecast.columns)
    assert len(forecast) == 4
    assert set(forecast["horizon"]) == {1, 2, 3, 4}
    assert set(forecast["target"]) == {"sell_out"}
    assert set(forecast["model_name"]) == {"MovingAverage8w"}


def test_moving_average_p50_uses_last_eight_visible_weeks():
    panel = _single_series_panel([1, 2, 3, 4, 5, 6, 7, 8, 999, 999])
    forecaster = MovingAverage8w(target="sell_out")
    forecaster.fit(panel, as_of=date(2024, 2, 19))

    forecast = forecaster.predict(horizon=2)

    assert forecast["p50"].tolist() == pytest.approx([4.5, 4.5])


def test_moving_average_quantiles_are_ordered():
    panel = _single_series_panel([10, 11, 9, 12, 10, 8, 13, 11])
    forecaster = MovingAverage8w(target="sell_out")
    forecaster.fit(panel, as_of=date(2024, 2, 19))

    forecast = forecaster.predict(horizon=1)

    assert (forecast["p10"] <= forecast["p50"]).all()
    assert (forecast["p50"] <= forecast["p90"]).all()


def test_moving_average_rejects_predict_before_fit():
    forecaster = MovingAverage8w(target="sell_out")

    with pytest.raises(RuntimeError, match="fit"):
        forecaster.predict(horizon=1)


def test_moving_average_rejects_unknown_target():
    panel = _single_series_panel([1, 2, 3, 4, 5, 6, 7, 8])
    forecaster = MovingAverage8w(target="unknown")

    with pytest.raises(ValueError, match="unknown"):
        forecaster.fit(panel, as_of=date(2024, 2, 19))
