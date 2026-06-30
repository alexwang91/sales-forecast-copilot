import pandas as pd

from src.evaluation.model_comparison import compare_model_metrics


def test_compare_model_metrics_reports_wape_by_model():
    forecasts = pd.DataFrame([
        {"model_name": "A", "sku": "S1", "forecast_week": "2024-01-01", "p50": 90},
        {"model_name": "A", "sku": "S1", "forecast_week": "2024-01-08", "p50": 110},
        {"model_name": "B", "sku": "S1", "forecast_week": "2024-01-01", "p50": 100},
        {"model_name": "B", "sku": "S1", "forecast_week": "2024-01-08", "p50": 100},
    ])
    actuals = pd.DataFrame([
        {"sku": "S1", "week_start": "2024-01-01", "sell_out": 100},
        {"sku": "S1", "week_start": "2024-01-08", "sell_out": 100},
    ])

    result = compare_model_metrics(forecasts, actuals, target="sell_out")

    assert result.loc[result["model_name"] == "A", "wape"].iloc[0] == 0.10
    assert result.loc[result["model_name"] == "B", "wape"].iloc[0] == 0.0
