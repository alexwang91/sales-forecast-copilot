import pandas as pd

from src.dashboard.override_audit import build_override_audit_view


def test_build_override_audit_view_shows_who_why_and_change():
    forecast = pd.DataFrame([
        {"sku": "S1", "forecast_week": "2024-01-01", "p50": 10},
    ])
    overrides = pd.DataFrame([
        {
            "sku": "S1",
            "forecast_week": "2024-01-01",
            "p50": 15,
            "reason": "customer commit",
            "owner": "gtm",
            "created_at": "2024-01-02T09:00:00",
        },
    ])

    out = build_override_audit_view(forecast, overrides)

    assert out.loc[0, "sku"] == "S1"
    assert out.loc[0, "forecast_week"] == "2024-01-01"
    assert out.loc[0, "old_p50"] == 10
    assert out.loc[0, "new_p50"] == 15
    assert out.loc[0, "owner"] == "gtm"
    assert out.loc[0, "reason"] == "customer commit"
    assert out.loc[0, "change_summary"] == "S1 2024-01-01 p50: 10 -> 15"
