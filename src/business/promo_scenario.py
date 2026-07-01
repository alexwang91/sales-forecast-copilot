import pandas as pd


SERIES_COLUMNS = ["sku"]


def simulate_promo_scenario(
    baseline: pd.DataFrame,
    analogs: pd.DataFrame,
    scenario_name: str,
    stock_available: float,
) -> pd.DataFrame:
    uplift_p10 = float(analogs["uplift"].min())
    uplift_p50 = float(analogs["uplift"].median())
    uplift_p90 = float(analogs["uplift"].max())
    result = baseline.copy()
    result["scenario_name"] = scenario_name
    result["p10"] = (result["p50"] * (1 + uplift_p10)).round(10)
    result["p90"] = (result["p50"] * (1 + uplift_p90)).round(10)
    result["p50"] = (result["p50"] * (1 + uplift_p50)).round(10)
    result["stock_available"] = stock_available
    result["scenario_demand_p50"] = result.groupby(SERIES_COLUMNS, dropna=False)["p50"].transform("sum")
    result["stock_remaining_p50"] = stock_available - result["scenario_demand_p50"]
    result["stockout_risk"] = result["stock_remaining_p50"] < 0
    result["analog_sample_size"] = int(len(analogs))
    result["caveat"] = "Scenario uplift is correlation-based, not causal."
    return result
