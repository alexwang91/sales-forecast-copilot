import pandas as pd

from src.dashboard.inventory_recommendation import build_inventory_recommendation


def test_build_inventory_recommendation_combines_sell_in_and_risk():
    inventory = pd.DataFrame([
        {"sku": "S1", "stock_available": 10},
    ])
    forecast = pd.DataFrame([
        {"sku": "S1", "forecast_week": "2024-01-01", "p50": 20},
        {"sku": "S1", "forecast_week": "2024-01-08", "p50": 20},
    ])

    out = build_inventory_recommendation(inventory, forecast, horizon_weeks=2)

    assert out.loc[0, "sku"] == "S1"
    assert out.loc[0, "forecast_demand"] == 40
    assert out.loc[0, "recommended_sell_in"] == 30
    assert out.loc[0, "weeks_of_cover"] == 0.5
    assert out.loc[0, "stockout_risk"]
