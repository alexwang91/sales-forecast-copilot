import pandas as pd

from src.dashboard.workbench import build_workbench_data


def test_build_workbench_data_filters_by_sku():
    history = pd.DataFrame([
        {"week_start": "2024-01-01", "country": "HU", "channel": "Retail", "sku": "S1", "sell_out": 10},
        {"week_start": "2024-01-01", "country": "HU", "channel": "Retail", "sku": "S2", "sell_out": 99},
    ])
    forecast = pd.DataFrame([
        {"forecast_week": "2024-01-08", "country": "HU", "channel": "Retail", "sku": "S1", "p50": 12},
        {"forecast_week": "2024-01-08", "country": "HU", "channel": "Retail", "sku": "S2", "p50": 88},
    ])

    out = build_workbench_data(history, forecast, sku="S1")

    assert out["history"].loc[0, "sku"] == "S1"
    assert out["history"].loc[0, "sell_out"] == 10
    assert out["forecast"].loc[0, "sku"] == "S1"
    assert out["forecast"].loc[0, "p50"] == 12
