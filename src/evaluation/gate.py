import pandas as pd


def assert_positive_fva(metrics: pd.DataFrame, baseline: str, system: str) -> dict:
    baseline_wape = float(metrics.loc[metrics["model_name"] == baseline, "wape"].iloc[0])
    system_wape = float(metrics.loc[metrics["model_name"] == system, "wape"].iloc[0])
    fva = round(baseline_wape - system_wape, 10)
    if fva <= 0:
        raise ValueError("FVA gate failed")
    return {"baseline_wape": baseline_wape, "system_wape": system_wape, "fva": fva}
