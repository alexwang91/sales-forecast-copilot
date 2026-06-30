import pandas as pd


def sum_forecast(frame: pd.DataFrame, by: list[str]) -> pd.DataFrame:
    value_columns = [column for column in ["p10", "p50", "p90"] if column in frame.columns]
    return frame.groupby(by, dropna=False)[value_columns].sum().reset_index()
