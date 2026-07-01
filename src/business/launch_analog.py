import pandas as pd


SIMILARITY_COLUMNS = ["category", "country", "channel", "price_band", "promo_type"]


def build_launch_analog_plan(
    candidate: dict,
    analogs: pd.DataFrame,
    weeks: int = 4,
    max_analogs: int = 5,
    stock_cover_multiplier: float = 1.0,
) -> dict:
    selected = _select_analogs(candidate, analogs, max_analogs=max_analogs)
    selected_rows = analogs.loc[
        analogs["analog_sku"].isin(selected["analog_sku"])
        & (analogs["launch_week_number"] <= weeks)
    ].copy()
    forecast = (
        selected_rows.groupby("launch_week_number", dropna=False)["units"]
        .agg(p10="min", p50="median", p90="max")
        .reset_index()
        .sort_values("launch_week_number")
        .reset_index(drop=True)
    )
    forecast[["p10", "p50", "p90"]] = forecast[["p10", "p50", "p90"]].round(10)
    recommended_initial_stock = round(float(forecast["p50"].sum() * stock_cover_multiplier), 10)
    return {
        "title": "Launch Analog Plan",
        "candidate_sku": candidate.get("sku"),
        "launch_forecast": forecast,
        "selected_analogs": selected,
        "recommended_initial_stock": recommended_initial_stock,
        "caveat": "Launch plan is analog-based and should be reviewed before execution.",
    }


def _select_analogs(candidate: dict, analogs: pd.DataFrame, max_analogs: int) -> pd.DataFrame:
    rows = []
    for analog_sku, group in analogs.groupby("analog_sku", dropna=False):
        first = group.iloc[0]
        matched = [column for column in SIMILARITY_COLUMNS if first.get(column) == candidate.get(column)]
        rows.append(
            {
                "analog_sku": analog_sku,
                "similarity_score": len(matched),
                "similarity_rationale": ", ".join(matched) if matched else "no exact attribute matches",
            }
        )
    return (
        pd.DataFrame(rows)
        .sort_values(["similarity_score", "analog_sku"], ascending=[False, True])
        .head(max_analogs)
        .reset_index(drop=True)
    )
