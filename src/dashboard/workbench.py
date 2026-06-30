import pandas as pd


def build_workbench_data(history: pd.DataFrame, forecast: pd.DataFrame, country=None, channel=None, sku=None) -> dict:
    history_frame = _filter(history, country=country, channel=channel, sku=sku).reset_index(drop=True)
    forecast_frame = _filter(forecast, country=country, channel=channel, sku=sku).reset_index(drop=True)
    return {"history": history_frame, "forecast": forecast_frame}


def _filter(frame: pd.DataFrame, country=None, channel=None, sku=None) -> pd.DataFrame:
    result = frame.copy()
    if country is not None and "country" in result.columns:
        result = result.loc[result["country"] == country]
    if channel is not None and "channel" in result.columns:
        result = result.loc[result["channel"] == channel]
    if sku is not None and "sku" in result.columns:
        result = result.loc[result["sku"] == sku]
    return result
