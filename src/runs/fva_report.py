import pandas as pd


KEYS = ["sku", "forecast_week"]
SOURCES = [("system", "system_p50"), ("gtm_8w_ma", "gtm_8w_ma"), ("manual", "manual_forecast")]


def build_fva_report(tracking: pd.DataFrame, actuals: pd.DataFrame) -> dict:
    frame = tracking.merge(actuals, on=KEYS, how="inner")
    rows = []
    for name, column in SOURCES:
        err = (frame[column] - frame["actual"]).abs().sum()
        total = frame["actual"].abs().sum()
        rows.append({"forecast_source": name, "wape": round(float(err / total), 10), "n": int(frame[column].notna().sum())})
    scorecard = pd.DataFrame(rows)
    gtm_wape = float(scorecard.loc[scorecard["forecast_source"] == "gtm_8w_ma", "wape"].iloc[0])
    scorecard["fva_vs_gtm_8w_ma"] = (gtm_wape - scorecard["wape"]).round(10)
    winner = str(scorecard.sort_values(["wape", "forecast_source"]).iloc[0]["forecast_source"])
    recommendation = "expand_shadow_pilot" if winner == "system" else "hold_shadow_pilot"
    return {
        "title": "FVA Shadow-mode Report",
        "scorecard": scorecard,
        "winner": winner,
        "recommendation": recommendation,
        "boundary_note": "Shadow-mode report is not a production decision.",
    }
