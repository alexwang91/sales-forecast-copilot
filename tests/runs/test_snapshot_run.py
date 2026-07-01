import pandas as pd

from src.runs.snapshot_run import snapshot_forecast_run


def test_snapshot_forecast_run_adds_run_id_and_snapshot_metadata():
    forecast = pd.DataFrame([
        {"sku": "S1", "forecast_week": "2024-01-08", "p10": 8, "p50": 10, "p90": 12, "model_name": "baseline"},
        {"sku": "S2", "forecast_week": "2024-01-08", "p10": 4, "p50": 5, "p90": 6, "model_name": "baseline"},
    ])

    out = snapshot_forecast_run(
        forecast,
        as_of="2024-01-01",
        data_snapshot_id="sellout_2024w01",
        information_snapshot_id="visible_2024w01",
    )

    assert out["forecast_run_id"].nunique() == 1
    assert out.loc[0, "forecast_run_id"] == "run_2024-01-01_sellout_2024w01_visible_2024w01"
    assert set(out["as_of"]) == {"2024-01-01"}
    assert set(out["data_snapshot_id"]) == {"sellout_2024w01"}
    assert set(out["information_snapshot_id"]) == {"visible_2024w01"}
    assert list(out["snapshot_p50"]) == [10, 5]
