import pandas as pd

from src.dashboard.decision_package import build_decision_package


def test_build_decision_package_summarizes_p4_decisions_for_users():
    inventory = pd.DataFrame([
        {"sku": "S1", "stock_available": 10},
    ])
    forecast = pd.DataFrame([
        {"sku": "S1", "forecast_week": "2024-01-01", "p50": 20},
        {"sku": "S1", "forecast_week": "2024-01-08", "p50": 20},
    ])
    overrides = pd.DataFrame([
        {
            "sku": "S1",
            "forecast_week": "2024-01-01",
            "p50": 25,
            "reason": "customer commit",
            "owner": "gtm",
            "created_at": "2024-01-02T09:00:00",
        },
    ])

    package = build_decision_package(inventory, forecast, overrides=overrides, horizon_weeks=2)

    assert package["title"] == "Inventory & Sell-in Decision Package"
    assert package["cards"]["stockout_skus"] == 1
    assert package["cards"]["total_recommended_sell_in"] == 30
    assert package["cards"]["manual_overrides"] == 1
    assert "Review 1 stockout SKU" in package["next_actions"]
    assert package["recommendations"].loc[0, "recommended_sell_in"] == 30
    assert package["override_audit"].loc[0, "change_summary"] == "S1 2024-01-01 p50: 20 -> 25"
