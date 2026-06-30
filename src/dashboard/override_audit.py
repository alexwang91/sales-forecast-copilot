import pandas as pd


def build_override_audit_view(forecast: pd.DataFrame, overrides: pd.DataFrame) -> pd.DataFrame:
    joined = overrides.merge(
        forecast.loc[:, ["sku", "forecast_week", "p50"]].rename(columns={"p50": "old_p50"}),
        on=["sku", "forecast_week"],
        how="left",
    )
    joined = joined.rename(columns={"p50": "new_p50"})
    joined["change_summary"] = joined.apply(
        lambda row: f"{row['sku']} {row['forecast_week']} p50: {row['old_p50']} -> {row['new_p50']}",
        axis=1,
    )
    columns = [
        "created_at",
        "sku",
        "forecast_week",
        "old_p50",
        "new_p50",
        "owner",
        "reason",
        "change_summary",
    ]
    keep = [column for column in columns if column in joined.columns]
    return joined.loc[:, keep].sort_values(keep[:1] or ["sku"], ascending=False).reset_index(drop=True)
