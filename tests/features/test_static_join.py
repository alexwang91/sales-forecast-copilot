from src.features.build_features import FeatureConfig


def test_feature_config_defaults():
    config = FeatureConfig()
    assert config.target == "sell_out"
    assert config.lags == (1, 2, 4, 8)
