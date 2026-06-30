def build_weekly_summary(overview: dict, risks: list[dict] | None = None) -> dict:
    risks = risks or []
    risk_skus = [item["sku"] for item in risks if "sku" in item]
    payload = {
        "best_model": overview.get("best_model"),
        "fva_vs_baseline": overview.get("fva_vs_baseline"),
        "risk_skus": risk_skus,
    }
    markdown = (
        "# Weekly Forecast Summary\n\n"
        f"Best model: {payload['best_model']}\n\n"
        f"FVA vs baseline: {payload['fva_vs_baseline']}\n\n"
        f"Risk SKUs: {', '.join(risk_skus) if risk_skus else 'None'}"
    )
    return {"json": payload, "markdown": markdown}
