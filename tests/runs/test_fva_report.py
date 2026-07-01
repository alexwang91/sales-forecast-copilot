import pandas as pd

from src.runs.fva_report import build_fva_report


def test_build_fva_report_compares_system_gtm_and_manual_against_actuals():
    tracking = pd.DataFrame([
        {"sku": "S1", "forecast_week": "2024-01-08", "system_p50": 100, "gtm_8w_ma": 80, "manual_forecast": 90},
        {"sku": "S2", "forecast_week": "2024-01-08", "system_p50": 50, "gtm_8w_ma": 10, "manual_forecast": 30},
    ])
    actuals = pd.DataFrame([
        {"sku": "S1", "forecast_week": "2024-01-08", "actual": 100},
        {"sku": "S2", "forecast_week": "2024-01-08", "actual": 50},
    ])

    report = build_fva_report(tracking, actuals)
    scorecard = report["scorecard"]

    assert report["title"] == "FVA Shadow-mode Report"
    assert report["winner"] == "system"
    assert report["recommendation"] == "expand_shadow_pilot"
    assert scorecard.loc[scorecard["forecast_source"] == "system", "wape"].iloc[0] == 0.0
    assert scorecard.loc[scorecard["forecast_source"] == "gtm_8w_ma", "wape"].iloc[0] == 0.4
    assert scorecard.loc[scorecard["forecast_source"] == "manual", "wape"].iloc[0] == 0.2
    assert scorecard.loc[scorecard["forecast_source"] == "system", "fva_vs_gtm_8w_ma"].iloc[0] == 0.4
    assert "not a production decision" in report["boundary_note"]
