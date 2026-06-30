import pandas as pd

from src.dashboard.overview import build_overview


def test_build_overview_selects_best_model_and_fva():
    metrics = pd.DataFrame([
        {"model_name": "baseline", "wape": 0.20, "bias": 0.05},
        {"model_name": "system", "wape": 0.15, "bias": -0.02},
    ])

    overview = build_overview(metrics, baseline="baseline")

    assert overview["best_model"] == "system"
    assert overview["baseline_model"] == "baseline"
    assert overview["best_wape"] == 0.15
    assert overview["fva_vs_baseline"] == 0.05
