import pandas as pd


def compare_model_metrics(forecasts: pd.DataFrame, actuals: pd.DataFrame, target: str = "sell_out") -> pd.DataFrame:
    left = forecasts.copy()
    left["forecast_week"] = pd.to_datetime(left["forecast_week"])
    right = actuals.copy()
    right["week_start"] = pd.to_datetime(right["week_start"])
    joined = left.merge(right, left_on=["sku", "forecast_week"], right_on=["sku", "week_start"], how="inner")
    rows = []
    for model_name, group in joined.groupby("model_name", dropna=False):
        error = (group["p50"] - group[target]).abs().sum()
        actual = group[target].abs().sum()
        wape = 0.0 if actual == 0 else float(error / actual)
        bias = 0.0 if actual == 0 else float((group["p50"] - group[target]).sum() / actual)
        rows.append({"model_name": model_name, "wape": wape, "bias": bias, "n": int(len(group))})
    return pd.DataFrame(rows).sort_values("model_name").reset_index(drop=True)
