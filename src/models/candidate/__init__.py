import pandas as pd


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
        rows = []
        future = future_covariates.head(horizon).reset_index(drop=True)
        for index, row in future.iterrows():
            value = self.event if bool(row[self.flag_column]) else self.normal
            rows.append({"p50": value, "model_name": self.name})
        return pd.DataFrame(rows)
