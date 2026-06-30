import pandas as pd

from src.models.blend import blend_forecasts


def test_blend_forecasts_combines_values():
    data = pd.DataFrame([
        {"model_name": "A", "sku": "S1", "forecast_week": "2024-01-01", "p50": 10},
        {"model_name": "B", "sku": "S1", "forecast_week": "2024-01-01", "p50": 20},
    ])

    out = blend_forecasts(data, weights={"A": 0.25, "B": 0.75})

    assert out.loc[0, "p50"] == 17.5
    assert out.loc[0, "model_name"] == "WeightedEnsemble"
