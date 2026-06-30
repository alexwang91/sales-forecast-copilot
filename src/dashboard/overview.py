import pandas as pd


def build_overview(metrics: pd.DataFrame, baseline: str) -> dict:
    ordered = metrics.sort_values(["wape", "model_name"]).reset_index(drop=True)
    best = ordered.iloc[0]
    baseline_row = metrics.loc[metrics["model_name"] == baseline].iloc[0]
    return {
        "best_model": best["model_name"],
        "baseline_model": baseline,
        "best_wape": float(best["wape"]),
        "baseline_wape": float(baseline_row["wape"]),
        "fva_vs_baseline": round(float(baseline_row["wape"] - best["wape"]), 10),
    }
