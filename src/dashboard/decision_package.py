import pandas as pd

from src.dashboard.inventory_recommendation import build_inventory_recommendation
from src.dashboard.override_audit import build_override_audit_view


def build_decision_package(
    inventory: pd.DataFrame,
    forecast: pd.DataFrame,
    overrides: pd.DataFrame | None = None,
    horizon_weeks: int = 4,
) -> dict:
    recommendations = build_inventory_recommendation(inventory, forecast, horizon_weeks=horizon_weeks)
    override_audit = _build_audit(forecast, overrides)
    stockout_skus = int(recommendations["stockout_risk"].sum())
    total_recommended_sell_in = float(recommendations["recommended_sell_in"].sum())
    manual_overrides = int(len(override_audit))
    return {
        "title": "Inventory & Sell-in Decision Package",
        "cards": {
            "stockout_skus": stockout_skus,
            "total_recommended_sell_in": total_recommended_sell_in,
            "manual_overrides": manual_overrides,
        },
        "next_actions": _next_actions(stockout_skus, manual_overrides),
        "recommendations": recommendations,
        "override_audit": override_audit,
    }


def _build_audit(forecast: pd.DataFrame, overrides: pd.DataFrame | None) -> pd.DataFrame:
    if overrides is None or overrides.empty:
        return pd.DataFrame()
    return build_override_audit_view(forecast, overrides)


def _next_actions(stockout_skus: int, manual_overrides: int) -> list[str]:
    actions = []
    if stockout_skus:
        label = "SKU" if stockout_skus == 1 else "SKUs"
        actions.append(f"Review {stockout_skus} stockout {label}")
    if manual_overrides:
        label = "override" if manual_overrides == 1 else "overrides"
        actions.append(f"Review {manual_overrides} manual {label}")
    if not actions:
        actions.append("No immediate inventory action required")
    return actions
