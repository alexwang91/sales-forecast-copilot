import pandas as pd

from src.business.inventory_risk import derive_inventory_risk


def test_derive_inventory_risk_flags_stockout_and_overstock():
    frame = pd.DataFrame([
        {"sku": "S1", "stock_available": 10, "weekly_demand": 20},
        {"sku": "S2", "stock_available": 100, "weekly_demand": 20},
    ])

    out = derive_inventory_risk(frame, stockout_threshold=1.0, overstock_threshold=4.0)

    assert out.loc[out["sku"] == "S1", "weeks_of_cover"].iloc[0] == 0.5
    assert out.loc[out["sku"] == "S1", "stockout_risk"].iloc[0]
    assert not out.loc[out["sku"] == "S1", "overstock_risk"].iloc[0]
    assert out.loc[out["sku"] == "S2", "weeks_of_cover"].iloc[0] == 5.0
    assert out.loc[out["sku"] == "S2", "overstock_risk"].iloc[0]
