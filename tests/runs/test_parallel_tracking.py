import pandas as pd

from src.runs.parallel_tracking import build_parallel_tracking_frame


def test_build_parallel_tracking_frame_records_system_gtm_and_manual_without_decision_impact():
    system = pd.DataFrame([
        {"forecast_run_id": "run_1", "sku": "S1", "forecast_week": "2024-01-08", "snapshot_p50": 100},
    ])
    gtm = pd.DataFrame([
        {"sku": "S1", "forecast_week": "2024-01-08", "gtm_8w_ma": 90},
    ])
    manual = pd.DataFrame([
        {"sku": "S1", "forecast_week": "2024-01-08", "manual_forecast": 110, "owner": "gtm"},
    ])

    out = build_parallel_tracking_frame(system, gtm, manual)

    assert out.loc[0, "forecast_run_id"] == "run_1"
    assert out.loc[0, "sku"] == "S1"
    assert out.loc[0, "system_p50"] == 100
    assert out.loc[0, "gtm_8w_ma"] == 90
    assert out.loc[0, "manual_forecast"] == 110
    assert out.loc[0, "manual_owner"] == "gtm"
    assert not bool(out.loc[0, "decision_impact"])
    assert out.loc[0, "mode"] == "parallel_tracking"
