import pandas as pd


def derive_inventory_risk(
    frame: pd.DataFrame,
    stockout_threshold: float = 1.0,
    overstock_threshold: float = 4.0,
) -> pd.DataFrame:
    result = frame.copy()
    result["weeks_of_cover"] = result["stock_available"] / result["weekly_demand"]
    result["stockout_risk"] = result["weeks_of_cover"] < stockout_threshold
    result["overstock_risk"] = result["weeks_of_cover"] > overstock_threshold
    return result
