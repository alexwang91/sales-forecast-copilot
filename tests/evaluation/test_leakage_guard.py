import pandas as pd
import pytest

from src.evaluation.leakage_guard import assert_as_of_safe_features


def test_assert_as_of_safe_features_rejects_non_whitelisted_future_source():
    frame = pd.DataFrame([
        {
            "sku": "S1",
            "as_of_week": "2024-01-01",
            "lag_1": 10,
            "lag_1_source_week": "2024-01-08",
        }
    ])

    with pytest.raises(ValueError, match="lag_1"):
        assert_as_of_safe_features(frame, {"lag_1": "lag_1_source_week"})


def test_assert_as_of_safe_features_allows_known_future_covariate_whitelist():
    frame = pd.DataFrame([
        {
            "sku": "S1",
            "as_of_week": "2024-01-01",
            "future_promo": 1,
            "future_promo_source_week": "2024-01-08",
        }
    ])

    assert assert_as_of_safe_features(
        frame,
        {"future_promo": "future_promo_source_week"},
        known_future_features={"future_promo"},
    )
