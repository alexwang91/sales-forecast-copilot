import pandas as pd

from src.business.inventory_risk import derive_inventory_risk
from src.business.sell_in_recommendation import recommend_sell_in


def build_inventory_recommendation(
    inventory: pd.DataFrame,
    forecast: pd.DataFrame,
    horizon_weeks: int = 4,
) -> pd.DataFrame:
    recommendation = recommend_sell_in(inventory, forecast)
    frame = recommendation.copy()
    frame["weekly_demand"] = frame["forecast_demand"] / horizon_weeks
    return derive_inventory_risk(frame)
