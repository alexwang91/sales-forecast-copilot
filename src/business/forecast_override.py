import pandas as pd


def validate_override(record: dict) -> dict:
    if not record.get("reason"):
        raise ValueError("override reason is required")
    if not record.get("owner"):
        raise ValueError("override owner is required")
    return record


def apply_forecast_overrides(forecast: pd.DataFrame, overrides: pd.DataFrame) -> pd.DataFrame:
    for record in overrides.to_dict("records"):
        validate_override(record)

    override_frame = overrides.rename(columns={
        "p50": "override_p50",
        "reason": "override_reason",
        "owner": "override_owner",
    })
    result = forecast.merge(
        override_frame.loc[:, ["sku", "forecast_week", "override_p50", "override_reason", "override_owner"]],
        on=["sku", "forecast_week"],
        how="left",
    )
    result["is_overridden"] = result["override_p50"].notna()
    result.loc[result["is_overridden"], "p50"] = result.loc[result["is_overridden"], "override_p50"]
    return result.drop(columns=["override_p50"])
