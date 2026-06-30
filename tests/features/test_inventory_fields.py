import pandas as pd

from src.features.build_features import FeatureConfig, build_model_frame


def test_inventory_fields_are_joined_by_week():
    sales = pd.DataFrame([
        {"week_start": "2024-01-01", "country": "HU", "channel": "Retail", "sku": "SKU001", "sell_out": 10},
        {"week_start": "2024-01-08", "country": "HU", "channel": "Retail", "sku": "SKU001", "sell_out": 20},
    ])
    inventory = pd.DataFrame([
        {"week_start": "2024-01-01", "country": "HU", "channel": "Retail", "sku": "SKU001", "channel_inventory": 100, "stock_available": 80},
        {"week_start": "2024-01-08", "country": "HU", "channel": "Retail", "sku": "SKU001", "channel_inventory": 90, "stock_available": 70},
    ])

    frame = build_model_frame(sales, inventory=inventory, config=FeatureConfig(lags=(1,), rolling_windows=()))

    assert frame.loc[1, "channel_inventory"] == 90
    assert frame.loc[1, "stock_available"] == 70
