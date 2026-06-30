import pandas as pd


FORECAST_COLUMNS = [
    "forecast_run_id",
    "run_date",
    "forecast_week",
    "region",
    "country",
    "channel",
    "sku",
    "target",
    "p10",
    "p50",
    "p90",
    "model_name",
    "scenario_name",
    "horizon",
]


class EventLiftBaseline:
    name = "EventLiftBaseline"

    def __init__(self, flag_column="event_flag", target="sell_out", scenario_name="baseline"):
        self.flag_column = flag_column
        self.target = target
        self.scenario_name = scenario_name
        self.as_of = None
        self.normal = 0.0
        self.event = 0.0

    def fit(self, panel, features=None, *, as_of):
        self.as_of = pd.Timestamp(as_of).date()
        normal = panel.loc[~panel[self.flag_column].astype(bool), self.target]
        event = panel.loc[panel[self.flag_column].astype(bool), self.target]
        self.normal = float(normal.mean())
        self.event = float(event.mean()) if len(event) else self.normal

    def predict(self, horizon, future_covariates=None):
        if self.as_of is None:
            raise RuntimeError("fit must be called before predict")
        if future_covariates is None:
            raise ValueError("future_covariates is required")
        rows = []
        future = future_covariates.head(horizon).reset_index(drop=True)
        for index, row in future.iterrows():
            value = self.event if bool(row[self.flag_column]) else self.normal
            rows.append({
                "forecast_run_id": "event-lift",
                "run_date": self.as_of,
                "forecast_week": pd.Timestamp(row["forecast_week"]).date(),
                "region": row["region"],
                "country": row["country"],
                "channel": row["channel"],
                "sku": row["sku"],
                "target": self.target,
                "p10": value * 0.9,
                "p50": value,
                "p90": value * 1.1,
                "model_name": self.name,
                "scenario_name": self.scenario_name,
                "horizon": index + 1,
            })
        return pd.DataFrame(rows).loc[:, FORECAST_COLUMNS]
