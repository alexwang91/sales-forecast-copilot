import pandas as pd


def recommend_sell_in(inventory: pd.DataFrame, forecast: pd.DataFrame, demand_column: str = "p50") -> pd.DataFrame:
    demand = forecast.groupby("sku", dropna=False)[demand_column].sum().reset_index(name="forecast_demand")
    frame = inventory.merge(demand, on="sku", how="left")
    frame["forecast_demand"] = frame["forecast_demand"].fillna(0.0)
    frame["recommended_sell_in"] = (frame["forecast_demand"] - frame["stock_available"]).clip(lower=0)
    return frame.loc[:, ["sku", "forecast_demand", "stock_available", "recommended_sell_in"]]
