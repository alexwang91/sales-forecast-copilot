def forecast_facts(row: dict, source_table: str) -> list[dict]:
    facts = []
    for metric in ["p50", "model_name"]:
        if metric in row:
            facts.append({
                "metric": metric,
                "value": row[metric],
                "source_table": source_table,
                "source_column": metric,
            })
    return facts
