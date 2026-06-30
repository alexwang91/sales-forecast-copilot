import pandas as pd


def blend_forecasts(forecasts: pd.DataFrame, weights: dict[str, float]) -> pd.DataFrame:
    frame = forecasts.copy()
    total = sum(weights.values())
    norm = {name: value / total for name, value in weights.items()}
    frame["_weight"] = frame["model_name"].map(norm).fillna(0.0)
    group_cols = [column for column in ["sku", "forecast_week"] if column in frame.columns]
    rows = []
    for key, group in frame.groupby(group_cols, dropna=False):
        row = {}
        if group_cols:
            if len(group_cols) == 1:
                row[group_cols[0]] = key
            else:
                row.update(dict(zip(group_cols, key, strict=True)))
        row["p50"] = float((group["p50"] * group["_weight"]).sum())
        row["model_name"] = "WeightedEnsemble"
        rows.append(row)
    return pd.DataFrame(rows)
