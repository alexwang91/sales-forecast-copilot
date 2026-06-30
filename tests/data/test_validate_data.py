import pandas as pd
import pytest

from src.data.sample_data import SampleDataConfig, generate_sample_data
from src.data.validate_data import assert_valid_tables, validate_tables


def _sample_tables():
    return generate_sample_data(SampleDataConfig(weeks=12, sku_count=3, countries=("HU",), channels=("Retail",)))


def _checks(report):
    return {issue.check for issue in report.issues}


def test_validate_tables_passes_generated_sample_data():
    report = validate_tables(_sample_tables())

    assert report.passed
    assert report.issues == ()


def test_validate_tables_reports_missing_required_columns():
    tables = _sample_tables()
    tables["fact_sales_weekly"] = tables["fact_sales_weekly"].drop(columns=["sell_out"])

    report = validate_tables(tables)

    assert not report.passed
    assert "required_columns" in _checks(report)


def test_validate_tables_reports_duplicate_primary_keys():
    tables = _sample_tables()
    duplicate = tables["fact_sales_weekly"].iloc[[0]]
    tables["fact_sales_weekly"] = pd.concat([tables["fact_sales_weekly"], duplicate], ignore_index=True)

    report = validate_tables(tables)

    assert not report.passed
    assert "unique_key" in _checks(report)


def test_validate_tables_reports_sku_foreign_key_errors():
    tables = _sample_tables()
    tables["fact_sales_weekly"].loc[0, "sku"] = "UNKNOWN"

    report = validate_tables(tables)

    assert not report.passed
    assert "foreign_key" in _checks(report)


def test_validate_tables_reports_channel_foreign_key_errors():
    tables = _sample_tables()
    tables["fact_inventory_weekly"].loc[0, "channel"] = "Unknown Channel"

    report = validate_tables(tables)

    assert not report.passed
    assert "foreign_key" in _checks(report)


def test_validate_tables_reports_numeric_legality_errors():
    tables = _sample_tables()
    tables["fact_sales_weekly"].loc[0, "sell_out"] = -1
    tables["fact_inventory_weekly"].loc[0, "channel_inventory"] = -1
    tables["fact_price_promo_weekly"].loc[0, "retail_price"] = 0
    tables["fact_price_promo_weekly"].loc[1, "discount_rate"] = 1.2

    report = validate_tables(tables)

    assert not report.passed
    assert "numeric_legality" in _checks(report)


def test_validate_tables_reports_weekly_continuity_errors():
    tables = _sample_tables()
    sales = tables["fact_sales_weekly"]
    series_mask = (sales["country"] == "HU") & (sales["channel"] == "Retail") & (sales["sku"] == "SKU001")
    removed_index = sales.loc[series_mask].index[4]
    tables["fact_sales_weekly"] = sales.drop(index=removed_index).reset_index(drop=True)

    report = validate_tables(tables)

    assert not report.passed
    assert "weekly_continuity" in _checks(report)


def test_assert_valid_tables_raises_with_blocking_issue_summary():
    tables = _sample_tables()
    tables["fact_sales_weekly"] = tables["fact_sales_weekly"].drop(columns=["sell_out"])

    with pytest.raises(ValueError, match="required_columns"):
        assert_valid_tables(tables)
