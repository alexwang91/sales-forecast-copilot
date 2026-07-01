import pandas as pd

from src.business.launch_analog import build_launch_analog_plan


def _analog_rows(sku: str, units: list[int]) -> list[dict]:
    return [
        {
            "analog_sku": sku,
            "launch_week_number": week,
            "units": unit,
            "category": "router",
            "country": "HU",
            "channel": "retail",
            "price_band": "mid",
            "promo_type": "launch",
        }
        for week, unit in enumerate(units, start=1)
    ]


def test_build_launch_analog_plan_returns_forecast_stock_and_rationale():
    candidate = {
        "sku": "NEW1",
        "category": "router",
        "country": "HU",
        "channel": "retail",
        "price_band": "mid",
        "promo_type": "launch",
    }
    analogs = pd.DataFrame(
        _analog_rows("A1", [10, 20, 30, 40])
        + _analog_rows("A2", [12, 22, 32, 42])
        + _analog_rows("A3", [20, 30, 40, 50])
    )

    plan = build_launch_analog_plan(candidate, analogs, weeks=4, max_analogs=3, stock_cover_multiplier=1.2)
    forecast = plan["launch_forecast"]
    selected = plan["selected_analogs"]

    assert plan["title"] == "Launch Analog Plan"
    assert list(selected["analog_sku"]) == ["A1", "A2", "A3"]
    assert selected.loc[0, "similarity_score"] == 5
    assert "category" in selected.loc[0, "similarity_rationale"]
    assert list(forecast["launch_week_number"]) == [1, 2, 3, 4]
    assert forecast.loc[forecast["launch_week_number"] == 1, "p10"].iloc[0] == 10
    assert forecast.loc[forecast["launch_week_number"] == 1, "p50"].iloc[0] == 12
    assert forecast.loc[forecast["launch_week_number"] == 1, "p90"].iloc[0] == 20
    assert plan["recommended_initial_stock"] == 129.6
    assert "analog-based" in plan["caveat"]
