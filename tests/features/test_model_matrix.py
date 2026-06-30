import pandas as pd

from src.features.matrix import build_prediction_matrix, build_training_matrix


def feature_frame():
    return pd.DataFrame([
        {"week_start": "2024-01-01", "country": "HU", "channel": "Retail", "sku": "A", "sell_out": 10.0, "lag_1": 8.0, "rolling_mean_4": 7.0, "promotion_flag": False, "category": "Router"},
        {"week_start": "2024-01-08", "country": "HU", "channel": "Retail", "sku": "A", "sell_out": None, "lag_1": 10.0, "rolling_mean_4": 8.0, "promotion_flag": True, "category": "Router"},
    ])


def test_training_matrix_drops_rows_with_missing_target():
    x, y = build_training_matrix(feature_frame(), target="sell_out")

    assert len(x) == 1
    assert y.tolist() == [10.0]
    assert "sell_out" not in x.columns


def test_prediction_matrix_keeps_rows_without_target_and_matches_columns():
    train_x, _ = build_training_matrix(feature_frame(), target="sell_out")
    predict_x = build_prediction_matrix(feature_frame())

    assert len(predict_x) == 2
    assert predict_x.columns.tolist() == train_x.columns.tolist()
    assert predict_x.columns.tolist() == ["lag_1", "promotion_flag", "rolling_mean_4"]
