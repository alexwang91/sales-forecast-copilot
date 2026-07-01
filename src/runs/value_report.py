import pandas as pd


METHODS = [("system", "system_p50"), ("gtm_8w_ma", "gtm_8w_ma"), ("manual", "manual_forecast")]


def build_value_report(tracking: pd.DataFrame) -> dict:
    rows = []
    for method, column in METHODS:
        if column not in tracking.columns:
            continue
        valid = tracking.loc[tracking[column].notna()]
        if valid.empty:
            continue
        err = (valid["actual"] - valid[column]).abs().sum()
        den = valid["actual"].abs().sum()
        rows.append({"method": method, "wape": round(float(err / den), 10)})
    scorecard = pd.DataFrame(rows).sort_values(["wape", "method"]).reset_index(drop=True)
    winner = str(scorecard.loc[0, "method"])
    recommendation = "expand_shadow_pilot" if winner == "system" else "continue_shadow_pilot"
    values = {row["method"]: row["wape"] for row in scorecard.to_dict("records")}
    summary = f"system vs gtm_8w_ma: {values.get('system')} vs {values.get('gtm_8w_ma')} WAPE"
    return {"title": "Shadow-mode Value Report", "scorecard": scorecard, "winner": winner, "recommendation": recommendation, "summary": summary}
