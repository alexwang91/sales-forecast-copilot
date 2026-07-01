import pandas as pd

from src.business.launch_analog import build_launch_analog_plan


BOUNDARY_NOTE = "Launch plans are analog-based and should be reviewed before execution."


def build_launch_planner_page(
    candidate: dict,
    analogs: pd.DataFrame,
    weeks: int = 4,
    stock_cover_multiplier: float = 1.0,
) -> dict:
    plan = build_launch_analog_plan(
        candidate,
        analogs,
        weeks=weeks,
        stock_cover_multiplier=stock_cover_multiplier,
    )
    forecast = plan["launch_forecast"]
    selected_analogs = plan["selected_analogs"]
    return {
        "title": "Launch Planner",
        "boundary_note": BOUNDARY_NOTE,
        "cards": {
            "analog_count": int(len(selected_analogs)),
            "recommended_initial_stock": float(plan["recommended_initial_stock"]),
            "week_1_p50": _week_1_p50(forecast),
        },
        "next_actions": _next_actions(len(selected_analogs)),
        "forecast": forecast,
        "selected_analogs": selected_analogs,
    }


def _week_1_p50(forecast: pd.DataFrame) -> float:
    if forecast.empty:
        return 0.0
    return float(forecast.sort_values("launch_week_number").iloc[0]["p50"])


def _next_actions(analog_count: int) -> list[str]:
    if analog_count:
        return [f"Review analog rationale for {analog_count} selected SKUs"]
    return ["Add analog SKUs before using launch plan"]
