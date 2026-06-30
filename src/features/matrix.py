from __future__ import annotations

import pandas as pd


def build_training_matrix(frame: pd.DataFrame, target: str = "sell_out"):
    rows = frame.loc[frame[target].notna()].copy()
    x = build_prediction_matrix(rows).drop(columns=[target], errors="ignore")
    y = rows[target].astype(float).reset_index(drop=True)
    return x, y


def build_prediction_matrix(frame: pd.DataFrame):
    keep = []
    for column in frame.columns:
        if column in {"week_start", "region", "country", "channel", "sku", "sell_in", "sell_out"}:
            continue
        if pd.api.types.is_numeric_dtype(frame[column]) or pd.api.types.is_bool_dtype(frame[column]):
            keep.append(column)
    return frame.loc[:, sorted(keep)].reset_index(drop=True)
