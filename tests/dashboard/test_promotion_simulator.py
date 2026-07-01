import pandas as pd

from src.dashboard.promotion_simulator import build_promotion_simulator_page


def test_build_promotion_simulator_page_summarizes_scenarios_with_boundary_note():
    baseline = pd.DataFrame([
        {"sku": "S1", "forecast_week": "2024-01-01", "p50": 100},
    ])
    analogs_by_scenario = {
        "15% discount": pd.DataFrame([
            {"analog_sku": "A1", "uplift": 0.10},
            {"analog_sku": "A2", "uplift": 0.20},
            {"analog_sku": "A3", "uplift": 0.30},
        ])
    }

    page = build_promotion_simulator_page(
        baseline,
        analogs_by_scenario,
        stock_available=110,
    )
    scenarios = page["scenarios"]

    assert page["title"] == "Promotion Simulator"
    assert "not causal" in page["boundary_note"]
    assert page["cards"] == {
        "scenario_count": 1,
        "stockout_scenarios": 1,
        "max_p50": 120.0,
    }
    assert "Review stockout risk in 1 promotion scenario" in page["next_actions"]
    assert scenarios.loc[0, "scenario_name"] == "15% discount"
    assert scenarios.loc[0, "p50"] == 120
    assert scenarios.loc[0, "analog_sample_size"] == 3
