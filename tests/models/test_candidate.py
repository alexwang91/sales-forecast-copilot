import pandas as pd
import pytest

from src.models.candidate import EventLiftBaseline


EXPECTED_COLUMNS = [
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


def train_frame():
    return pd.DataFrame([
        {"week_start": "2024-01-01", "region": "CEE", "country": "HU", "channel": "Retail", "sku": "SKU001", "sell_out": 10, "event_flag": False},
        {"week_start": "2024-01-08", "region": "CEE", "country": "HU", "channel": "Retail", "sku": "SKU001", "sell_out": 20, "event_flag": True},
    ])


def future_frame():
    return pd.DataFrame([
        {"forecast_week": "2024-01-15", "region": "CEE", "country": "HU", "channel": "Retail", "sku": "SKU001", "event_flag": False},
        {"forecast_week": "2024-01-22", "region": "CEE", "country": "HU", "channel": "Retail", "sku": "SKU001", "event_flag": True},
    ])


def test_event_lift_model_uses_future_flag():
    model = EventLiftBaseline(flag_column="event_flag")
    model.fit(train_frame(), as_of="2024-01-08")

    out = model.predict(2, future_covariates=future_frame())

    assert out.loc[0, "p50"] == 10
    assert out.loc[1, "p50"] == 20


def test_event_lift_model_outputs_forecast_schema():
    model = EventLiftBaseline(flag_column="event_flag")
    model.fit(train_frame(), as_of="2024-01-08")

    out = model.predict(2, future_covariates=future_frame())

    assert out.columns.tolist() == EXPECTED_COLUMNS
    assert out.loc[0, "horizon"] == 1
    assert out.loc[1, "horizon"] == 2
    assert out.loc[0, "model_name"] == "EventLiftBaseline"


def test_event_lift_model_requires_fit_before_predict():
    model = EventLiftBaseline(flag_column="event_flag")

    with pytest.raises(RuntimeError):
        model.predict(1, future_covariates=future_frame())


def test_event_lift_model_requires_future_covariates():
    model = EventLiftBaseline(flag_column="event_flag")
    model.fit(train_frame(), as_of="2024-01-08")

    with pytest.raises(ValueError):
        model.predict(1)
