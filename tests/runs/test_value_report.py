import pandas as pd

from src.runs.value_report import build_value_report


def test_build_value_report_compares_three_methods_with_recommendation():
    tracking = pd.DataFrame([
        {"sku": "S1", "forecast_week": "2024-01-08", "system_p50": 100, "gtm_8w_ma": 80, "manual_forecast": 90, "actual": 100},
        {"sku": "S2", "forecast_week": "2024-01-08", "system_p50": 50, "gtm_8w_ma": 40, "manual_forecast": 55, "actual": 50},
    ])

    report = build_value_report(tracking)
    scorecard = report["scorecard"]

    assert report["title"] == "Shadow-mode Value Report"
    assert report["winner"] == "system"
    assert report["recommendation"] == "expand_shadow_pilot"
    assert scorecard.loc[scorecard["method"] == "system", "wape"].iloc[0] == 0.0
    assert scorecard.loc[scorecard["method"] == "gtm_8w_ma", "wape"].iloc[0] == 0.2
    assert scorecard.loc[scorecard["method"] == "manual", "wape"].iloc[0] == 0.1
    assert "system vs gtm_8w_ma" in report["summary"]


def test_build_value_report_omits_method_with_no_prediction_coverage():
    tracking = pd.DataFrame([
        {"sku": "S1", "forecast_week": "2024-01-08", "system_p50": 100, "gtm_8w_ma": 80, "manual_forecast": pd.NA, "actual": 100},
    ])

    report = build_value_report(tracking)

    assert list(report["scorecard"]["method"]) == ["system", "gtm_8w_ma"]
    assert report["winner"] == "system"
