from datetime import date, timedelta

import pandas as pd
import pytest

from src.models.baseline import SeasonalNaive


def panel(values):
    start = date(2024, 1, 1)
    return pd.DataFrame([
        {"week_start": start + timedelta(weeks=i), "region": "CEE", "country": "HU", "channel": "Retail", "sku": "SKU001", "sell_out": value, "sell_in": value}
        for i, value in enumerate(values)
    ])


def test_seasonal_naive_uses_matching_prior_season_value():
    model = SeasonalNaive(season_length=4)
    model.fit(panel([10, 20, 30, 40, 50, 60, 70, 80]), as_of=date(2024, 2, 19))

    forecast = model.predict(2)

    assert forecast.loc[0, "p50"] == pytest.approx(50)
    assert forecast.loc[1, "p50"] == pytest.approx(60)
    assert set(forecast["model_name"]) == {"SeasonalNaive"}
