"""Command-line P1 backtest runner."""

from __future__ import annotations

from datetime import date

from src.data.sample_data import SampleDataConfig, generate_sample_data
from src.data.validate_data import assert_valid_tables
from src.evaluation.metrics import bias, p90_coverage, wape
from src.evaluation.fva import forecast_value_add
from src.evaluation.rolling_backtest import BacktestConfig, run_rolling_backtest
from src.models.baseline import MovingAverage8w


def run_p1_backtest() -> dict[str, float]:
    """Run the P1 sample-data backtest and return headline metrics."""

    tables = generate_sample_data(SampleDataConfig(weeks=24, sku_count=4, countries=("HU",), channels=("Retail",)))
    assert_valid_tables(tables)
    panel = tables["fact_sales_weekly"]
    config = BacktestConfig(origins=(date(2024, 3, 4), date(2024, 3, 11), date(2024, 3, 18)), horizon=4)
    result = run_rolling_backtest(panel, MovingAverage8w(), config)

    candidate_wape = wape(result["actual"], result["p50"])
    candidate_bias = bias(result["actual"], result["p50"])
    candidate_p90_coverage = p90_coverage(result["actual"], result["p90"])
    baseline_wape = candidate_wape
    return {
        "WAPE": candidate_wape,
        "Bias": candidate_bias,
        "P90 Coverage": candidate_p90_coverage,
        "FVA vs MovingAverage8w": forecast_value_add(baseline_wape, candidate_wape),
    }


def format_metrics(metrics: dict[str, float]) -> str:
    """Format headline metrics as stable CLI output."""

    lines = ["P1 Rolling Backtest Summary"]
    for name in ("WAPE", "Bias", "P90 Coverage", "FVA vs MovingAverage8w"):
        lines.append(f"{name}: {metrics[name]:.4f}")
    return "\n".join(lines)


def main() -> None:
    print(format_metrics(run_p1_backtest()))


if __name__ == "__main__":
    main()
