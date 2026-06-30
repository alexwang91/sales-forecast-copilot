import pandas as pd
import pytest

from src.business.forecast_override import apply_forecast_overrides, validate_override


def test_validate_override_requires_reason_and_owner():
    with pytest.raises(ValueError):
        validate_override({"sku": "S1", "forecast_week": "2024-01-01", "p50": 15, "owner": "gtm"})

    with pytest.raises(ValueError):
        validate_override({"sku": "S1", "forecast_week": "2024-01-01", "p50": 15, "reason": "customer commit"})


def test_apply_forecast_overrides_marks_manual_source():
    forecast = pd.DataFrame([
        {"sku": "S1", "forecast_week": "2024-01-01", "p50": 10},
    ])
    overrides = pd.DataFrame([
        {"sku": "S1", "forecast_week": "2024-01-01", "p50": 15, "reason": "customer commit", "owner": "gtm"},
    ])

    out = apply_forecast_overrides(forecast, overrides)

    assert out.loc[0, "p50"] == 15
    assert bool(out.loc[0, "is_overridden"])
    assert out.loc[0, "override_reason"] == "customer commit"
    assert out.loc[0, "override_owner"] == "gtm"
