import pandas as pd

from src.business.promo_scenario import simulate_promo_scenario


def test_simulate_promo_scenario_returns_quantiles_risk_and_caveat():
    baseline = pd.DataFrame([
        {"sku": "S1", "forecast_week": "2024-01-01", "p50": 100},
    ])
    analogs = pd.DataFrame([
        {"sku": "A1", "uplift": 0.10},
        {"sku": "A2", "uplift": 0.20},
        {"sku": "A3", "uplift": 0.30},
    ])

    out = simulate_promo_scenario(
        baseline,
        analogs,
        scenario_name="15% discount",
        stock_available=110,
    )

    assert out.loc[0, "scenario_name"] == "15% discount"
    assert out.loc[0, "p50"] == 120
    assert out.loc[0, "p10"] == 110
    assert out.loc[0, "p90"] == 130
    assert out.loc[0, "stock_remaining_p50"] == -10
    assert bool(out.loc[0, "stockout_risk"])
    assert out.loc[0, "analog_sample_size"] == 3
    assert "not causal" in out.loc[0, "caveat"]
