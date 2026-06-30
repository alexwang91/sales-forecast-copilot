import pandas as pd

from src.models.selector import select_best_model


def test_select_best_model_chooses_lowest_wape():
    metrics = pd.DataFrame([
        {"model_name": "A", "segment": "HU", "wape": 0.20, "n": 10},
        {"model_name": "B", "segment": "HU", "wape": 0.10, "n": 10},
    ])

    result = select_best_model(metrics, segment_column="segment")

    assert result.loc[0, "segment"] == "HU"
    assert result.loc[0, "model_name"] == "B"
