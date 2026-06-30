"""Hard data quality gates for forecast input tables."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

import pandas as pd

from src.data.schema import TABLE_SCHEMAS


INPUT_TABLES = (
    "fact_sales_weekly",
    "fact_inventory_weekly",
    "fact_price_promo_weekly",
    "dim_product",
    "dim_channel",
)


@dataclass(frozen=True)
class DataQualityIssue:
    """One blocking data quality problem found during validation."""

    check: str
    table: str
    severity: str
    message: str
    rows: int | None = None


@dataclass(frozen=True)
class DataQualityReport:
    """Validation result. Any issue makes the report fail."""

    issues: tuple[DataQualityIssue, ...]

    @property
    def passed(self) -> bool:
        return len(self.issues) == 0

    def summary(self) -> str:
        if self.passed:
            return "data quality gate passed"
        return "; ".join(f"{issue.check}:{issue.table}:{issue.message}" for issue in self.issues)


def validate_tables(tables: Mapping[str, pd.DataFrame]) -> DataQualityReport:
    """Validate core input tables against schema and hard quality gates."""

    issues: list[DataQualityIssue] = []
    issues.extend(_check_required_tables(tables))
    issues.extend(_check_required_columns(tables))
    issues.extend(_check_unique_keys(tables))
    issues.extend(_check_foreign_keys(tables))
    issues.extend(_check_numeric_legality(tables))
    issues.extend(_check_weekly_continuity(tables))
    return DataQualityReport(tuple(issues))


def assert_valid_tables(tables: Mapping[str, pd.DataFrame]) -> None:
    """Raise ValueError when the data quality gate does not pass."""

    report = validate_tables(tables)
    if not report.passed:
        raise ValueError(report.summary())


def _check_required_tables(tables: Mapping[str, pd.DataFrame]) -> list[DataQualityIssue]:
    missing = [table_name for table_name in INPUT_TABLES if table_name not in tables]
    return [
        DataQualityIssue(
            check="required_table",
            table=table_name,
            severity="error",
            message=f"missing required table {table_name}",
        )
        for table_name in missing
    ]


def _check_required_columns(tables: Mapping[str, pd.DataFrame]) -> list[DataQualityIssue]:
    issues: list[DataQualityIssue] = []
    for table_name, frame in tables.items():
        schema = TABLE_SCHEMAS.get(table_name)
        if schema is None:
            continue
        missing = schema.missing_columns(frame.columns)
        if missing:
            issues.append(
                DataQualityIssue(
                    check="required_columns",
                    table=table_name,
                    severity="error",
                    message=f"missing columns: {', '.join(missing)}",
                )
            )
    return issues


def _check_unique_keys(tables: Mapping[str, pd.DataFrame]) -> list[DataQualityIssue]:
    issues: list[DataQualityIssue] = []
    for table_name, frame in tables.items():
        schema = TABLE_SCHEMAS.get(table_name)
        if schema is None or not set(schema.primary_key).issubset(frame.columns):
            continue
        duplicate_mask = frame.duplicated(list(schema.primary_key), keep=False)
        duplicate_count = int(duplicate_mask.sum())
        if duplicate_count:
            issues.append(
                DataQualityIssue(
                    check="unique_key",
                    table=table_name,
                    severity="error",
                    message=f"primary key has {duplicate_count} duplicate rows",
                    rows=duplicate_count,
                )
            )
    return issues


def _check_foreign_keys(tables: Mapping[str, pd.DataFrame]) -> list[DataQualityIssue]:
    issues: list[DataQualityIssue] = []
    products = tables.get("dim_product")
    channels = tables.get("dim_channel")
    product_keys = set(products["sku"]) if products is not None and "sku" in products.columns else set()
    channel_keys = set(zip(channels.get("country", []), channels.get("channel", []))) if channels is not None else set()

    for table_name in ("fact_sales_weekly", "fact_inventory_weekly", "fact_price_promo_weekly"):
        frame = tables.get(table_name)
        if frame is None:
            continue
        if product_keys and "sku" in frame.columns:
            missing_sku_count = int((~frame["sku"].isin(product_keys)).sum())
            if missing_sku_count:
                issues.append(
                    DataQualityIssue("foreign_key", table_name, "error", f"{missing_sku_count} rows reference missing dim_product sku", missing_sku_count)
                )
        if channel_keys and {"country", "channel"}.issubset(frame.columns):
            row_keys = pd.Series(list(zip(frame["country"], frame["channel"])))
            missing_channel_count = int((~row_keys.isin(channel_keys)).sum())
            if missing_channel_count:
                issues.append(
                    DataQualityIssue("foreign_key", table_name, "error", f"{missing_channel_count} rows reference missing dim_channel country/channel", missing_channel_count)
                )
    return issues


def _check_numeric_legality(tables: Mapping[str, pd.DataFrame]) -> list[DataQualityIssue]:
    issues: list[DataQualityIssue] = []
    checks = {
        "fact_sales_weekly": (("sell_in", ">=", 0), ("sell_out", ">=", 0)),
        "fact_inventory_weekly": (("channel_inventory", ">=", 0), ("stock_available", ">=", 0), ("weeks_of_cover", ">=", 0)),
        "fact_price_promo_weekly": (("retail_price", ">", 0), ("dealer_price", ">", 0), ("discount_rate", "between", (0, 1))),
    }
    for table_name, table_checks in checks.items():
        frame = tables.get(table_name)
        if frame is None:
            continue
        invalid_total = 0
        for column, operator, threshold in table_checks:
            if column not in frame.columns:
                continue
            values = pd.to_numeric(frame[column], errors="coerce")
            if operator == ">=":
                invalid_total += int((values < threshold).sum() + values.isna().sum())
            elif operator == ">":
                invalid_total += int((values <= threshold).sum() + values.isna().sum())
            elif operator == "between":
                lower, upper = threshold
                invalid_total += int((~values.between(lower, upper)).sum() + values.isna().sum())
        invalid_total += _invalid_binary_count(frame, "stockout_flag")
        invalid_total += _invalid_binary_count(frame, "promotion_flag")
        if invalid_total:
            issues.append(DataQualityIssue("numeric_legality", table_name, "error", f"{invalid_total} numeric values violate contract", invalid_total))
    return issues


def _invalid_binary_count(frame: pd.DataFrame, column: str) -> int:
    if column not in frame.columns:
        return 0
    values = pd.to_numeric(frame[column], errors="coerce")
    return int((~values.isin([0, 1])).sum() + values.isna().sum())


def _check_weekly_continuity(tables: Mapping[str, pd.DataFrame]) -> list[DataQualityIssue]:
    issues: list[DataQualityIssue] = []
    for table_name in ("fact_sales_weekly", "fact_inventory_weekly", "fact_price_promo_weekly"):
        frame = tables.get(table_name)
        required = {"week_start", "country", "channel", "sku"}
        if frame is None or not required.issubset(frame.columns):
            continue
        parsed = frame.copy()
        parsed["week_start"] = pd.to_datetime(parsed["week_start"], errors="coerce")
        missing_weeks = 0
        for _, group in parsed.groupby(["country", "channel", "sku"], dropna=False):
            weeks = group["week_start"].sort_values().dropna().drop_duplicates()
            if len(weeks) <= 1:
                continue
            expected = pd.date_range(weeks.iloc[0], weeks.iloc[-1], freq="7D")
            missing_weeks += len(set(expected) - set(weeks))
        if missing_weeks:
            issues.append(DataQualityIssue("weekly_continuity", table_name, "error", f"{missing_weeks} weekly periods are missing", missing_weeks))
    return issues
