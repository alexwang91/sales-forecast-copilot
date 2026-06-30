from src.data.schema import TABLE_SCHEMAS, get_table_schema


def test_schema_contains_contract_tables_and_primary_keys():
    expected = {
        "fact_sales_weekly": ("week_start", "country", "channel", "sku"),
        "fact_inventory_weekly": ("week_start", "country", "channel", "sku"),
        "fact_price_promo_weekly": ("week_start", "country", "channel", "sku"),
        "dim_product": ("sku",),
        "dim_channel": ("channel", "country"),
        "forecast_output": ("forecast_run_id", "country", "channel", "sku", "forecast_week", "model_name", "scenario_name"),
        "forecast_override": ("forecast_run_id", "country", "channel", "sku", "forecast_week"),
    }

    assert set(expected).issubset(TABLE_SCHEMAS)
    for table_name, primary_key in expected.items():
        assert get_table_schema(table_name).primary_key == primary_key


def test_fact_sales_weekly_matches_sell_out_contract():
    columns = get_table_schema("fact_sales_weekly").column_names

    assert columns == (
        "week_start",
        "region",
        "country",
        "channel",
        "sku",
        "sell_in",
        "sell_out",
    )


def test_schemas_do_not_define_duplicate_columns():
    for schema in TABLE_SCHEMAS.values():
        assert len(schema.column_names) == len(set(schema.column_names)), schema.name
