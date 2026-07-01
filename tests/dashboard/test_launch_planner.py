import pandas as pd

from src.dashboard.launch_planner import build_launch_planner_page


def test_build_launch_planner_page_summarizes_plan_with_boundary_note():
    candidate = {"sku": "NEW1", "category": "router", "country": "HU", "channel": "retail", "price_band": "mid", "promo_type": "launch"}
    curves = {"A1": [10, 20, 30, 40], "A2": [12, 22, 32, 42], "A3": [20, 30, 40, 50]}
    rows = []
    for sku, units in curves.items():
        for week, unit in enumerate(units, start=1):
            rows.append({"analog_sku": sku, "launch_week_number": week, "units": unit, "category": "router", "country": "HU", "channel": "retail", "price_band": "mid", "promo_type": "launch"})
    analogs = pd.DataFrame(rows)

    page = build_launch_planner_page(candidate, analogs, weeks=4, stock_cover_multiplier=1.2)

    assert page["title"] == "Launch Planner"
    assert "analog-based" in page["boundary_note"]
    assert page["cards"]["analog_count"] == 3
    assert page["cards"]["recommended_initial_stock"] == 129.6
    assert page["cards"]["week_1_p50"] == 12.0
    assert "Review analog rationale for 3 selected SKUs" in page["next_actions"]
    assert page["forecast"].loc[0, "p50"] == 12
    assert list(page["selected_analogs"]["analog_sku"]) == ["A1", "A2", "A3"]
    assert "category" in page["selected_analogs"].loc[0, "similarity_rationale"]
