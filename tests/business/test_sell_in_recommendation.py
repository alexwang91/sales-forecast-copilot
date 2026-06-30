import pandas as pd

from src.business.sell_in_recommendation import recommend_sell_in


def test_recommend_sell_in_replenishes_demand_gap():
    inventory = pd.DataFrame([
        {"sku": "S1", "stock_available": 50},
        {"sku": "S2", "stock_available": 100},
    ])
    forecast = pd.DataFrame([
        {"sku": "S1", "forecast_week": "2024-01-01", "p50": 30},
        {"sku": "S1", "forecast_week": "2024-01-08", "p50": 40},
        {"sku": "S2", "forecast_week": "2024-01-01", "p50": 20},
    ])

    out = recommend_sell_in(inventory, forecast)

    assert out.loc[out["sku"] == "S1", "recommended_sell_in"].iloc[0] == 20
    assert out.loc[out["sku"] == "S2", "recommended_sell_in"].iloc[0] == 0
