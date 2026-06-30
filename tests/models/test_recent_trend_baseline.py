from datetime import date, timedelta

import pandas as pd

from src.models.baseline import RecentTrendBaseline


def panel(values):
    start = date(2024, 1, 1)
    rows = []
    for i, value in enumerate(values):
        rows.append({"week_start": start + timedelta(weeks=i), "region": "CEE", "country": "HU", "channel": "Retail", "sku": "SKU001", "sell_out": value, "sell_in": value})
    return pd.DataFrame(rows)


def test_recent_trend_projects_average_recent_delta():
    model = RecentTrendBaseline(window=4)
    model.fit(panel([10, 20, 30, 40, 50]), as_of=date(2024, 1, 29))

    forecast = model.predict(2)

    assert forecast.loc[0, "p50"] == 60
    assert forecast.loc[1, "p50"] == 70
    assert set(forecast["model_name"]) == {"RecentTrendBaseline"}
