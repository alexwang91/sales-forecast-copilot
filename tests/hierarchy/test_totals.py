import pandas as pd

from src.hierarchy.totals import sum_forecast


def test_sum_forecast_adds_p50_by_level():
    frame = pd.DataFrame([
        {"region": "CEE", "country": "HU", "channel": "Retail", "sku": "S1", "forecast_week": "2024-01-01", "p50": 10},
        {"region": "CEE", "country": "HU", "channel": "Retail", "sku": "S2", "forecast_week": "2024-01-01", "p50": 20},
    ])

    out = sum_forecast(frame, by=["region", "country", "channel", "forecast_week"])

    assert out.loc[0, "p50"] == 30
    assert out.loc[0, "channel"] == "Retail"
