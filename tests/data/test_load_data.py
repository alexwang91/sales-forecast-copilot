from pathlib import Path

import pandas as pd
import pytest

from src.data.load_data import load_table, load_tables
from src.data.sample_data import SampleDataConfig, write_sample_data


def test_load_table_parses_dates_and_orders_schema_columns(tmp_path: Path):
    paths = write_sample_data(tmp_path, SampleDataConfig(weeks=4, sku_count=2, countries=("HU",), channels=("Retail",)))

    frame = load_table(paths["fact_sales_weekly"], "fact_sales_weekly")

    assert list(frame.columns) == ["week_start", "region", "country", "channel", "sku", "sell_in", "sell_out"]
    assert str(frame["week_start"].dtype).startswith("datetime64")


def test_load_table_rejects_missing_contract_columns(tmp_path: Path):
    path = tmp_path / "fact_sales_weekly.csv"
    pd.DataFrame([
        {"week_start": "2024-01-01", "region": "CEE", "country": "HU", "channel": "Retail", "sku": "SKU001", "sell_in": 10}
    ]).to_csv(path, index=False)

    with pytest.raises(ValueError, match="sell_out"):
        load_table(path, "fact_sales_weekly")


def test_load_tables_loads_all_csvs_from_directory(tmp_path: Path):
    write_sample_data(tmp_path, SampleDataConfig(weeks=4, sku_count=2, countries=("HU",), channels=("Retail",)))

    tables = load_tables(tmp_path)

    assert set(tables) == {
        "fact_sales_weekly",
        "fact_inventory_weekly",
        "fact_price_promo_weekly",
        "dim_product",
        "dim_channel",
    }
