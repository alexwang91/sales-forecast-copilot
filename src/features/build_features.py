from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


SERIES_COLUMNS = ["country", "channel", "sku"]
WEEKLY_JOIN_COLUMNS = ["week_start", *SERIES_COLUMNS]


@dataclass(frozen=True)
class FeatureConfig:
    target: str = "sell_out"
    lags: tuple[int, ...] = (1, 2, 4, 8)
    rolling_windows: tuple[int, ...] = (4, 8)


def build_time_features(sales: pd.DataFrame, config: FeatureConfig | None = None) -> pd.DataFrame:
    cfg = config or FeatureConfig()
    frame = sales.copy()
    frame["week_start"] = pd.to_datetime(frame["week_start"])
    frame = frame.sort_values([*SERIES_COLUMNS, "week_start"]).reset_index(drop=True)
    grouped = frame.groupby(SERIES_COLUMNS, dropna=False)[cfg.target]
    for lag in cfg.lags:
        frame[f"lag_{lag}"] = grouped.shift(lag)
    shifted = grouped.shift(1)
    group_keys = [frame[column] for column in SERIES_COLUMNS]
    for window in cfg.rolling_windows:
        frame[f"rolling_mean_{window}"] = shifted.groupby(group_keys, dropna=False).rolling(window, min_periods=1).mean().reset_index(level=SERIES_COLUMNS, drop=True)
        frame[f"rolling_std_{window}"] = shifted.groupby(group_keys, dropna=False).rolling(window, min_periods=2).std(ddof=0).reset_index(level=SERIES_COLUMNS, drop=True)
    return frame


def build_model_frame(sales: pd.DataFrame, inventory=None, price_promo=None, products=None, channels=None, config: FeatureConfig | None = None) -> pd.DataFrame:
    frame = build_time_features(sales, config)
    if inventory is not None:
        inventory_frame = inventory.copy()
        inventory_frame["week_start"] = pd.to_datetime(inventory_frame["week_start"])
        keep = ["week_start", *SERIES_COLUMNS, "channel_inventory", "stock_available", "weeks_of_cover", "stockout_flag"]
        frame = frame.merge(inventory_frame.loc[:, [column for column in keep if column in inventory_frame.columns]], on=WEEKLY_JOIN_COLUMNS, how="left")
    if price_promo is not None:
        promo = price_promo.copy()
        promo["week_start"] = pd.to_datetime(promo["week_start"])
        keep = ["week_start", *SERIES_COLUMNS, "retail_price", "dealer_price", "discount_rate", "promotion_flag", "promotion_type"]
        frame = frame.merge(promo.loc[:, [column for column in keep if column in promo.columns]], on=WEEKLY_JOIN_COLUMNS, how="left")
    if products is not None:
        frame = frame.merge(products, on="sku", how="left")
    if channels is not None:
        frame = frame.merge(channels.drop(columns=["region"], errors="ignore"), on=["country", "channel"], how="left")
    if "launch_date" in frame.columns:
        launch = pd.to_datetime(frame["launch_date"], errors="coerce")
        frame["product_age_weeks"] = ((frame["week_start"] - launch).dt.days // 7).clip(lower=0)
        frame["launch_flag"] = frame["product_age_weeks"].between(0, 4, inclusive="both")
    if "eol_date" in frame.columns:
        eol = pd.to_datetime(frame["eol_date"], errors="coerce")
        frame["weeks_to_eol"] = ((eol - frame["week_start"]).dt.days // 7)
        frame["eol_flag"] = frame["weeks_to_eol"].between(0, 4, inclusive="both")
    return frame
