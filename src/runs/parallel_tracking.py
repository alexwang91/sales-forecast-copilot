import pandas as pd


KEY_COLUMNS = ["sku", "forecast_week"]


def build_parallel_tracking_frame(
    system_snapshot: pd.DataFrame,
    gtm_baseline: pd.DataFrame,
    manual_forecast: pd.DataFrame | None = None,
) -> pd.DataFrame:
    frame = system_snapshot.rename(columns={"snapshot_p50": "system_p50"}).copy()
    frame = frame.merge(gtm_baseline, on=KEY_COLUMNS, how="left")
    if manual_forecast is not None and not manual_forecast.empty:
        manual = manual_forecast.rename(columns={"owner": "manual_owner"})
        frame = frame.merge(
            manual.loc[:, KEY_COLUMNS + ["manual_forecast", "manual_owner"]],
            on=KEY_COLUMNS,
            how="left",
        )
    else:
        frame["manual_forecast"] = pd.NA
        frame["manual_owner"] = pd.NA
    frame["decision_impact"] = False
    frame["mode"] = "parallel_tracking"
    return frame
