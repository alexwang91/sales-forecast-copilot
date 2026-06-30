import pandas as pd

from src.features.build_features import FeatureConfig, build_time_features


def make_sales(values):
    rows = []
    for index, value in enumerate(values):
        rows.append({
            "week_start": pd.Timestamp("2024-01-01") + pd.Timedelta(days=7 * index),
            "country": "HU",
            "channel": "Retail",
            "sku": "SKU001",
            "sell_out": value,
        })
    return pd.DataFrame(rows)


def test_lag_1_uses_previous_week_value():
    frame = build_time_features(make_sales([10, 20, 30]), FeatureConfig(lags=(1,), rolling_windows=()))

    assert pd.isna(frame.loc[0, "lag_1"])
    assert frame.loc[1, "lag_1"] == 10
    assert frame.loc[2, "lag_1"] == 20


def test_rolling_mean_2_uses_prior_values():
    frame = build_time_features(make_sales([10, 20, 30, 40]), FeatureConfig(lags=(), rolling_windows=(2,)))

    assert pd.isna(frame.loc[0, "rolling_mean_2"])
    assert frame.loc[1, "rolling_mean_2"] == 10
    assert frame.loc[2, "rolling_mean_2"] == 15
    assert frame.loc[3, "rolling_mean_2"] == 25
