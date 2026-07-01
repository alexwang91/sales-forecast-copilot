import pandas as pd


def snapshot_forecast_run(
    forecast: pd.DataFrame,
    as_of: str,
    data_snapshot_id: str,
    information_snapshot_id: str,
) -> pd.DataFrame:
    result = forecast.copy()
    result["forecast_run_id"] = "run_" + as_of + "_" + data_snapshot_id + "_" + information_snapshot_id
    result["as_of"] = as_of
    result["data_snapshot_id"] = data_snapshot_id
    result["information_snapshot_id"] = information_snapshot_id
    for column in ["p10", "p50", "p90"]:
        if column in result.columns:
            result["snapshot_" + column] = result[column]
    return result
