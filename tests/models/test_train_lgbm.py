from datetime import date

import pandas as pd
import pytest

from src.models.baseline import FORECAST_COLUMNS
from src.models.train_lgbm import LightGBMQuantileForecaster


class StubQuantileModel:
    def __init__(self, quantile: float) -> None:
        self.quantile = quantile
        self.fit_called = False

    def fit(self, frame: pd.DataFrame, target: str) -> None:
        self.fit_called = True

    def predict(self, frame: pd.DataFrame) -> list[float]:
        values = {0.1: 10.0, 0.5: 20.0, 0.9: 30.0}
        return [values[self.quantile]] * len(frame)


def test_lgbm_quantile_forecaster_requires_backend():
    model = LightGBMQuantileForecaster(feature_columns=["price"])
    history = pd.DataFrame([
        {"region": "EU", "country": "HU", "channel": "retail", "sku": "S1", "week_start": "2024-01-01", "sell_out": 1, "price": 100},
    ])

    with pytest.raises(ImportError, match="LightGBM"):
        model.fit(history, as_of=date(2024, 1, 1))


def test_lgbm_quantile_forecaster_outputs_forecast_contract_with_injected_backend():
    model = LightGBMQuantileForecaster(
        feature_columns=["price"],
        backend_factory=lambda quantile: StubQuantileModel(quantile),
    )
    history = pd.DataFrame([
        {"region": "EU", "country": "HU", "channel": "retail", "sku": "S1", "week_start": "2024-01-01", "sell_out": 1, "price": 100},
    ])
    future = pd.DataFrame([
        {"region": "EU", "country": "HU", "channel": "retail", "sku": "S1", "forecast_week": "2024-01-08", "horizon": 1, "price": 95},
    ])

    model.fit(history, as_of=date(2024, 1, 1))
    forecast = model.predict(horizon=1, future_covariates=future)

    assert list(forecast.columns) == FORECAST_COLUMNS
    assert forecast.loc[0, "model_name"] == "LightGBMQuantile"
    assert forecast.loc[0, "p10"] == 10.0
    assert forecast.loc[0, "p50"] == 20.0
    assert forecast.loc[0, "p90"] == 30.0
