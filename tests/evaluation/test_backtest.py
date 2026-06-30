from datetime import date

import pandas as pd
import pytest

from src.data.sample_data import SampleDataConfig, generate_sample_data
from src.evaluation.rolling_backtest import BacktestConfig, run_rolling_backtest
from src.models.baseline import MovingAverage8w


def _sales(weeks=16):
    return generate_sample_data(SampleDataConfig(weeks=weeks, sku_count=2, countries=("HU",), channels=("Retail",)))["fact_sales_weekly"]


def test_backtest_returns_one_row_per_series_origin_and_horizon():
    panel = _sales(16)
    origins = (date(2024, 2, 26), date(2024, 3, 4))

    result = run_rolling_backtest(panel, MovingAverage8w(), BacktestConfig(origins=origins, horizon=4))

    assert {"origin", "horizon", "country", "channel", "sku", "actual", "p50"}.issubset(result.columns)
    assert set(result["origin"].dt.date) == set(origins)
    assert set(result["horizon"]) == {1, 2, 3, 4}
    assert len(result) == len(origins) * 4 * 2


def test_backtest_fails_when_labels_are_missing():
    with pytest.raises(ValueError, match="missing actuals"):
        run_rolling_backtest(_sales(10), MovingAverage8w(), BacktestConfig(origins=(date(2024, 2, 26),), horizon=4))


class RecordingForecaster(MovingAverage8w):
    def __init__(self):
        super().__init__()
        self.max_training_weeks = []

    def fit(self, panel, features=None, *, as_of):
        self.max_training_weeks.append(pd.to_datetime(panel["week_start"]).max())
        super().fit(panel, features, as_of=as_of)


def test_backtest_trains_only_through_origin():
    panel = _sales(16)
    forecaster = RecordingForecaster()
    origins = (date(2024, 2, 26), date(2024, 3, 4))

    run_rolling_backtest(panel, forecaster, BacktestConfig(origins=origins, horizon=2))

    assert forecaster.max_training_weeks == [pd.Timestamp(origin) for origin in origins]
