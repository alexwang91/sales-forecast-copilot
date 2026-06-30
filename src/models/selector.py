import pandas as pd


def select_best_model(metrics: pd.DataFrame, segment_column: str = "segment") -> pd.DataFrame:
    ordered = metrics.sort_values([segment_column, "wape", "model_name"]).reset_index(drop=True)
    best = ordered.groupby(segment_column, dropna=False).head(1).reset_index(drop=True)
    return best.loc[:, [segment_column, "model_name", "wape", "n"]]
