"""Semantic data contract for the Sales Forecast Decision Copilot.

The schemas mirror docs/03-data-contract.md. They stay deliberately small:
validation and loading live in separate modules so the contract can remain a
stable interface for data, forecasting, evaluation, and dashboard code.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import Any


@dataclass(frozen=True)
class ColumnSpec:
    """Column metadata used by quality gates and loaders."""

    name: str
    python_type: type[Any] | tuple[type[Any], ...]
    nullable: bool = False


@dataclass(frozen=True)
class TableSchema:
    """Table contract with ordered columns and primary key columns."""

    name: str
    columns: tuple[ColumnSpec, ...]
    primary_key: tuple[str, ...]

    @property
    def column_names(self) -> tuple[str, ...]:
        return tuple(column.name for column in self.columns)

    def missing_columns(self, row_or_columns: dict[str, Any] | set[str] | list[str] | tuple[str, ...]) -> tuple[str, ...]:
        if isinstance(row_or_columns, dict):
            available = set(row_or_columns)
        else:
            available = set(row_or_columns)
        return tuple(column for column in self.column_names if column not in available)


def _cols(*specs: tuple[str, type[Any] | tuple[type[Any], ...], bool]) -> tuple[ColumnSpec, ...]:
    return tuple(ColumnSpec(*spec) for spec in specs)


TABLE_SCHEMAS: dict[str, TableSchema] = {
    "fact_sales_weekly": TableSchema(
        name="fact_sales_weekly",
        columns=_cols(
            ("week_start", date, False),
            ("region", str, False),
            ("country", str, False),
            ("channel", str, False),
            ("sku", str, False),
            ("sell_in", (int, float), False),
            ("sell_out", (int, float), False),
        ),
        primary_key=("week_start", "country", "channel", "sku"),
    ),
    "fact_inventory_weekly": TableSchema(
        name="fact_inventory_weekly",
        columns=_cols(
            ("week_start", date, False),
            ("country", str, False),
            ("channel", str, False),
            ("sku", str, False),
            ("channel_inventory", (int, float), False),
            ("stock_available", (int, float), False),
            ("stockout_flag", int, False),
            ("weeks_of_cover", (int, float), False),
        ),
        primary_key=("week_start", "country", "channel", "sku"),
    ),
    "fact_price_promo_weekly": TableSchema(
        name="fact_price_promo_weekly",
        columns=_cols(
            ("week_start", date, False),
            ("country", str, False),
            ("channel", str, False),
            ("sku", str, False),
            ("retail_price", (int, float), False),
            ("dealer_price", (int, float), False),
            ("discount_rate", (int, float), False),
            ("promotion_flag", int, False),
            ("promotion_type", str, False),
        ),
        primary_key=("week_start", "country", "channel", "sku"),
    ),
    "dim_product": TableSchema(
        name="dim_product",
        columns=_cols(
            ("sku", str, False),
            ("product_name", str, False),
            ("category", str, False),
            ("series", str, False),
            ("price_tier", str, False),
            ("launch_date", date, False),
            ("eol_date", date, True),
            ("predecessor_sku", str, True),
            ("successor_sku", str, True),
        ),
        primary_key=("sku",),
    ),
    "dim_channel": TableSchema(
        name="dim_channel",
        columns=_cols(
            ("channel", str, False),
            ("country", str, False),
            ("region", str, False),
            ("channel_type", str, False),
            ("channel_tier", str, False),
            ("is_operator", bool, False),
            ("is_ecommerce", bool, False),
            ("is_retail_chain", bool, False),
        ),
        primary_key=("channel", "country"),
    ),
    "forecast_output": TableSchema(
        name="forecast_output",
        columns=_cols(
            ("forecast_run_id", str, False),
            ("run_date", date, False),
            ("forecast_week", date, False),
            ("region", str, False),
            ("country", str, False),
            ("channel", str, False),
            ("sku", str, False),
            ("target", str, False),
            ("p10", (int, float), False),
            ("p50", (int, float), False),
            ("p90", (int, float), False),
            ("model_name", str, False),
            ("scenario_name", str, False),
        ),
        primary_key=("forecast_run_id", "country", "channel", "sku", "forecast_week", "model_name", "scenario_name"),
    ),
    "forecast_override": TableSchema(
        name="forecast_override",
        columns=_cols(
            ("forecast_run_id", str, False),
            ("country", str, False),
            ("channel", str, False),
            ("sku", str, False),
            ("forecast_week", date, False),
            ("original_p50", (int, float), False),
            ("override_p50", (int, float), False),
            ("override_reason", str, False),
            ("owner", str, False),
            ("timestamp", datetime, False),
        ),
        primary_key=("forecast_run_id", "country", "channel", "sku", "forecast_week"),
    ),
}


FORECAST_TARGETS = {"sell_out", "sell_in"}
PROMOTION_TYPES = {"none", "discount", "bundle", "operator_campaign"}


def get_table_schema(table_name: str) -> TableSchema:
    """Return one named table schema or raise a clear KeyError."""

    try:
        return TABLE_SCHEMAS[table_name]
    except KeyError as exc:
        known = ", ".join(sorted(TABLE_SCHEMAS))
        raise KeyError(f"Unknown table schema '{table_name}'. Known schemas: {known}") from exc
