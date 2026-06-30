import subprocess
import sys


def test_run_backtest_cli_prints_p1_metrics():
    result = subprocess.run(
        [sys.executable, "-m", "src.evaluation.run_backtest"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "WAPE" in result.stdout
    assert "Bias" in result.stdout
    assert "P90 Coverage" in result.stdout
    assert "FVA vs MovingAverage8w" in result.stdout
