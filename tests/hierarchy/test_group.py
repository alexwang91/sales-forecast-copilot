import pandas as pd

from src.hierarchy.group import group_sum


def test_group_sum_adds_p50():
    frame = pd.DataFrame([
        {"country": "HU", "p50": 10},
        {"country": "HU", "p50": 20},
    ])

    out = group_sum(frame, keys=["country"])

    assert out.loc[0, "country"] == "HU"
    assert out.loc[0, "p50"] == 30
