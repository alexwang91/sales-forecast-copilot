import pandas as pd

from src.business.promo_scenario import simulate_promo_scenario


BOUNDARY_NOTE = "Promotion scenarios are correlation-based, not causal forecasts."


def build_promotion_simulator_page(
    baseline: pd.DataFrame,
    analogs_by_scenario: dict[str, pd.DataFrame],
    stock_available: float,
) -> dict:
    scenario_frames = [
        simulate_promo_scenario(
            baseline,
            analogs,
            scenario_name=scenario_name,
            stock_available=stock_available,
        )
        for scenario_name, analogs in analogs_by_scenario.items()
    ]
    scenarios = pd.concat(scenario_frames, ignore_index=True) if scenario_frames else pd.DataFrame()
    stockout_scenarios = _stockout_scenarios(scenarios)
    return {
        "title": "Promotion Simulator",
        "boundary_note": BOUNDARY_NOTE,
        "cards": {
            "scenario_count": int(len(analogs_by_scenario)),
            "stockout_scenarios": stockout_scenarios,
            "max_p50": 0.0 if scenarios.empty else float(scenarios["p50"].max()),
        },
        "next_actions": _next_actions(stockout_scenarios),
        "scenarios": scenarios,
    }


def _stockout_scenarios(scenarios: pd.DataFrame) -> int:
    if scenarios.empty:
        return 0
    return int(scenarios.groupby("scenario_name", dropna=False)["stockout_risk"].max().sum())


def _next_actions(stockout_scenarios: int) -> list[str]:
    if stockout_scenarios:
        label = "scenario" if stockout_scenarios == 1 else "scenarios"
        return [f"Review stockout risk in {stockout_scenarios} promotion {label}"]
    return ["No immediate promotion inventory risk"]
