from src.agent.facts import forecast_facts


def test_forecast_facts_include_source_metadata():
    row = {"sku": "S1", "forecast_week": "2024-01-08", "p50": 12, "model_name": "system"}

    facts = forecast_facts(row, source_table="forecast_output")

    assert facts[0] == {
        "metric": "p50",
        "value": 12,
        "source_table": "forecast_output",
        "source_column": "p50",
    }
    assert facts[1]["metric"] == "model_name"
    assert facts[1]["source_column"] == "model_name"
