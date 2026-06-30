"""CSV table loading helpers that enforce the semantic data contract."""

from __future__ import annotations

from datetime import date, datetime
from pathlib import Path

import pandas as pd

from src.data.schema import get_table_schema


def load_table(path: str | Path, table_name: str) -> pd.DataFrame:
    """Load one CSV file and normalize it to the configured table schema."""

    schema = get_table_schema(table_name)
    frame = pd.read_csv(path)
    missing = schema.missing_columns(frame.columns)
    if missing:
        raise ValueError(f"{table_name} is missing required columns: {', '.join(missing)}")

    normalized = frame.copy()
    for column in schema.columns:
        if column.name not in normalized.columns:
            continue
        if _contains_type(column.python_type, date) or _contains_type(column.python_type, datetime):
            normalized[column.name] = pd.to_datetime(normalized[column.name], errors="coerce")
        elif _contains_type(column.python_type, bool):
            normalized[column.name] = normalized[column.name].map(_to_bool)

    ordered_columns = list(schema.column_names)
    extras = [column for column in normalized.columns if column not in ordered_columns]
    return normalized[ordered_columns + extras]


def load_tables(directory: str | Path) -> dict[str, pd.DataFrame]:
    """Load all known input-table CSV files from a directory."""

    root = Path(directory)
    tables: dict[str, pd.DataFrame] = {}
    for table_name in (
        "fact_sales_weekly",
        "fact_inventory_weekly",
        "fact_price_promo_weekly",
        "dim_product",
        "dim_channel",
    ):
        path = root / f"{table_name}.csv"
        if path.exists():
            tables[table_name] = load_table(path, table_name)
    return tables


def _contains_type(type_spec: type | tuple[type, ...], expected: type) -> bool:
    if isinstance(type_spec, tuple):
        return any(type_item is expected for type_item in type_spec)
    return type_spec is expected


def _to_bool(value: object) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    text = str(value).strip().lower()
    if text in {"true", "1", "yes", "y"}:
        return True
    if text in {"false", "0", "no", "n"}:
        return False
    raise ValueError(f"cannot parse boolean value: {value!r}")
