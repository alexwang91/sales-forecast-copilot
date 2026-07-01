import pandas as pd


def assert_as_of_safe_features(
    frame: pd.DataFrame,
    feature_source_columns: dict[str, str],
    as_of_column: str = "as_of_week",
    known_future_features: set[str] | None = None,
) -> bool:
    allowed = known_future_features or set()
    as_of = pd.to_datetime(frame[as_of_column])
    violations = []
    for feature, source_column in feature_source_columns.items():
        if feature in allowed:
            continue
        source_week = pd.to_datetime(frame[source_column])
        if bool((source_week > as_of).any()):
            violations.append(feature)
    if violations:
        names = ", ".join(sorted(violations))
        raise ValueError(f"as-of feature leakage detected: {names}")
    return True
