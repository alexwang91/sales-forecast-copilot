"""Generate deterministic sample data for local development and tests."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import Mapping

import pandas as pd


@dataclass(frozen=True)
class SampleDataConfig:
    start_week: date = date(2024, 1, 1)
    weeks: int = 104
    region: str = "CEE"
    countries: tuple[str, ...] = ("HU", "CZ", "PL")
    channels: tuple[str, ...] = ("Retail", "Operator", "Ecom")
    sku_count: int = 10
    random_seed: int = 42


def generate_sample_data(config: SampleDataConfig | None = None) -> dict[str, pd.DataFrame]:
    cfg = config or SampleDataConfig()
    if cfg.weeks <= 0:
        raise ValueError("weeks must be positive")
    if cfg.sku_count <= 0:
        raise ValueError("sku_count must be positive")
    if not cfg.countries or not cfg.channels:
        raise ValueError("countries and channels must not be empty")

    weeks = [cfg.start_week + timedelta(weeks=i) for i in range(cfg.weeks)]
    skus = [f"SKU{i:03d}" for i in range(1, cfg.sku_count + 1)]
    products = _build_products(cfg, skus)
    channels = _build_channels(cfg)
    sales_rows: list[dict[str, object]] = []
    inventory_rows: list[dict[str, object]] = []
    promo_rows: list[dict[str, object]] = []

    for week_index, week_start in enumerate(weeks):
        seasonal = 1.0 + ((week_index % 52) / 52.0) * 0.18
        for country_index, country in enumerate(cfg.countries):
            for channel_index, channel in enumerate(cfg.channels):
                for sku_index, sku in enumerate(skus):
                    promo_flag = int((week_index + sku_index + channel_index) % 11 == 0)
                    discount_rate = 0.15 if promo_flag else 0.0
                    base = 40 + sku_index * 5 + country_index * 4 + channel_index * 3
                    sell_out = round(base * seasonal * (1.25 if promo_flag else 1.0), 2)
                    sell_in = round(sell_out * (1.03 + (week_index % 3) * 0.01), 2)
                    channel_inventory = round(sell_out * (4.0 + channel_index * 0.4), 2)
                    stock_available = round(channel_inventory - sell_out * 0.25, 2)
                    weeks_of_cover = round(channel_inventory / max(sell_out, 1.0), 2)
                    retail_price = float(129 + sku_index * 10)
                    sales_rows.append({"week_start": week_start, "region": cfg.region, "country": country, "channel": channel, "sku": sku, "sell_in": sell_in, "sell_out": sell_out})
                    inventory_rows.append({"week_start": week_start, "country": country, "channel": channel, "sku": sku, "channel_inventory": channel_inventory, "stock_available": stock_available, "stockout_flag": int(weeks_of_cover < 1.0), "weeks_of_cover": weeks_of_cover})
                    promo_rows.append({"week_start": week_start, "country": country, "channel": channel, "sku": sku, "retail_price": retail_price, "dealer_price": round(retail_price * 0.74, 2), "discount_rate": discount_rate, "promotion_flag": promo_flag, "promotion_type": _promotion_type(channel, promo_flag)})

    return {
        "fact_sales_weekly": pd.DataFrame(sales_rows),
        "fact_inventory_weekly": pd.DataFrame(inventory_rows),
        "fact_price_promo_weekly": pd.DataFrame(promo_rows),
        "dim_product": products,
        "dim_channel": channels,
    }


def write_sample_data(output_dir: str | Path = "data/sample", config: SampleDataConfig | None = None) -> Mapping[str, Path]:
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    paths: dict[str, Path] = {}
    for table_name, frame in generate_sample_data(config).items():
        path = destination / f"{table_name}.csv"
        frame.to_csv(path, index=False)
        paths[table_name] = path
    return paths


def _build_products(cfg: SampleDataConfig, skus: list[str]) -> pd.DataFrame:
    return pd.DataFrame([
        {"sku": sku, "product_name": f"Device {i + 1}", "category": "CPE" if i % 2 == 0 else "Wearable", "series": f"Series {1 + i // 3}", "price_tier": ("entry", "mid", "premium")[i % 3], "launch_date": cfg.start_week - timedelta(weeks=max(0, 52 - i * 3)), "eol_date": pd.NaT, "predecessor_sku": skus[i - 1] if i > 0 and i % 5 == 0 else None, "successor_sku": None}
        for i, sku in enumerate(skus)
    ])


def _build_channels(cfg: SampleDataConfig) -> pd.DataFrame:
    return pd.DataFrame([
        {"channel": channel, "country": country, "region": cfg.region, "channel_type": "operator" if channel == "Operator" else "retail", "channel_tier": "tier_1" if channel in {"Retail", "Operator"} else "tier_2", "is_operator": channel == "Operator", "is_ecommerce": channel == "Ecom", "is_retail_chain": channel == "Retail"}
        for country in cfg.countries
        for channel in cfg.channels
    ])


def _promotion_type(channel: str, promo_flag: int) -> str:
    if not promo_flag:
        return "none"
    if channel == "Operator":
        return "operator_campaign"
    if channel == "Ecom":
        return "bundle"
    return "discount"


if __name__ == "__main__":
    for table_name, path in write_sample_data().items():
        print(f"{table_name}: {path}")
