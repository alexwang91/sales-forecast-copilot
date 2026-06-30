from src.data.sample_data import SampleDataConfig, generate_sample_data


def test_generate_sample_data_returns_all_contract_tables():
    tables = generate_sample_data(SampleDataConfig(weeks=12, sku_count=4, countries=("HU",), channels=("Retail",)))

    assert set(tables) == {
        "fact_sales_weekly",
        "fact_inventory_weekly",
        "fact_price_promo_weekly",
        "dim_product",
        "dim_channel",
    }


def test_generated_fact_sales_has_unique_week_country_channel_sku_key():
    tables = generate_sample_data(SampleDataConfig(weeks=12, sku_count=4, countries=("HU",), channels=("Retail",)))
    sales = tables["fact_sales_weekly"]

    key = ["week_start", "country", "channel", "sku"]
    assert not sales.duplicated(key).any()
    assert len(sales) == 12 * 4


def test_generated_sample_respects_basic_quality_gate_inputs():
    tables = generate_sample_data(SampleDataConfig(weeks=12, sku_count=4, countries=("HU",), channels=("Retail",)))
    sales = tables["fact_sales_weekly"]
    inventory = tables["fact_inventory_weekly"]
    promo = tables["fact_price_promo_weekly"]
    products = tables["dim_product"]
    channels = tables["dim_channel"]

    assert (sales[["sell_in", "sell_out"]] >= 0).all().all()
    assert (inventory[["channel_inventory", "stock_available", "weeks_of_cover"]] >= 0).all().all()
    assert promo["discount_rate"].between(0, 1).all()
    assert set(sales["sku"]).issubset(set(products["sku"]))
    assert set(zip(sales["country"], sales["channel"])).issubset(set(zip(channels["country"], channels["channel"])))
