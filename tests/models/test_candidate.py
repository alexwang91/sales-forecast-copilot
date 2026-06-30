import pandas as pd

from src.models.candidate import EventLiftBaseline


def test_event_lift_model_uses_future_flag():
    train = pd.DataFrame([
        {"week_start": "2024-01-01", "region": "CEE", "country": "HU", "channel": "Retail", "sku": "SKU001", "sell_out": 10, "event_flag": False},
        {"week_start": "2024-01-08", "region": "CEE", "country": "HU", "channel": "Retail", "sku": "SKU001", "sell_out": 20, "event_flag": True},
    ])
    future = pd.DataFrame([
        {"forecast_week": "2024-01-15", "region": "CEE", "country": "HU", "channel": "Retail", "sku": "SKU001", "event_flag": False},
        {"forecast_week": "2024-01-22", "region": "CEE", "country": "HU", "channel": "Retail", "sku": "SKU001", "event_flag": True},
    ])
    model = EventLiftBaseline(flag_column="event_flag")
    model.fit(train, as_of="2024-01-08")

    out = model.predict(2, future_covariates=future)

    assert out.loc[0, "p50"] == 10
    assert out.loc[1, "p50"] == 20
