import pandas as pd
import pytest

from src.evaluation.gate import assert_positive_fva


def test_assert_positive_fva_passes_when_system_wape_is_lower():
    metrics = pd.DataFrame([
        {"model_name": "baseline", "wape": 0.20},
        {"model_name": "system", "wape": 0.15},
    ])

    result = assert_positive_fva(metrics, baseline="baseline", system="system")

    assert result["fva"] == 0.05


def test_assert_positive_fva_fails_when_system_wape_is_not_lower():
    metrics = pd.DataFrame([
        {"model_name": "baseline", "wape": 0.20},
        {"model_name": "system", "wape": 0.25},
    ])

    with pytest.raises(ValueError):
        assert_positive_fva(metrics, baseline="baseline", system="system")
