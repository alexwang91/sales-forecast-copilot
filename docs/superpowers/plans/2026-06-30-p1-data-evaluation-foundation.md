# P1 Data and Evaluation Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the smallest trustworthy P1 foundation: data contract, deterministic sample data, data quality gates, baseline forecasting, rolling backtest, and FVA against the 8-week moving average.

**Architecture:** Keep the first implementation boring and testable. `src.data` owns contracts and generated inputs, `src.evaluation` owns metrics/FVA/backtest, and `src.models` owns the `BaseForecaster` protocol plus the first moving-average baseline. Dashboard, business, hierarchy, and agent directories exist only as integration targets for later PRs.

**Tech Stack:** Python 3.11+, pandas, pytest. Add duckdb/lightgbm/streamlit only in later PRs when the evaluation spine is green.

## Global Constraints

- Use RED-GREEN-REFACTOR for every behavior change: failing test first, verify it fails, minimal code, verify it passes, then commit.
- Keep the trust order: data contract → quality gate → metrics/FVA → model interface → rolling backtest → dashboard.
- FVA baseline is the GTM current-process proxy: 8-week moving average.
- Forecast horizon is 4 weeks; target is `sell_out` unless a caller explicitly chooses `sell_in`.
- Backtest features and model fitting must use only data visible at the origin date.
- The sample dataset must not require real company data, external APIs, GPU, or paid services.
- Any failure of the data quality gate must stop the run and report exact blocking checks.

---

## PR Breakdown

| PR | Branch suggestion | Review gate | Deliverable |
| --- | --- | --- | --- |
| PR-00 | `codex/p1-superpowers-tdd-plan` | Unit tests green, plan saved | Superpowers TDD/PR plan, repo skeleton, schema contract, deterministic sample data |
| PR-01 | `codex/p1-data-quality-gate` | Invalid fixtures fail for the right reason | CSV loader and hard data quality gate |
| PR-02 | `codex/p1-evaluation-metrics` | Metric edge cases pass | WAPE, weighted WAPE, bias, P90 coverage, pinball loss, FVA |
| PR-03 | `codex/p1-baseline-models` | Baseline predictions match hand-calculated windows | `BaseForecaster` protocol and `MovingAverage8w` baseline |
| PR-04 | `codex/p1-rolling-backtest` | Backtest rejects leakage fixtures | Rolling-origin backtest with horizon-level FVA report |
| PR-05 | `codex/p1-make-backtest` | `make backtest` green from clean checkout | CLI/report wrapper for full P1 DoD |

---

## File Structure

- `pyproject.toml`: package metadata, runtime/dev dependencies, pytest config.
- `Makefile`: stable developer commands: `test`, `data`, `backtest`, `app`.
- `.github/workflows/ci.yml`: PR/push test workflow.
- `app/streamlit_app.py`: importable placeholder for later P3 dashboard work.
- `src/data/schema.py`: table schema definitions and primary-key contracts.
- `src/data/sample_data.py`: deterministic synthetic panel data generator and CSV writer.
- `src/data/load_data.py`: PR-01 CSV/DuckDB loader.
- `src/data/validate_data.py`: PR-01 data quality gate.
- `src/evaluation/metrics.py`: PR-02 metric functions.
- `src/evaluation/fva.py`: PR-02 FVA helpers.
- `src/models/base.py`: PR-03 forecaster protocol and `QuantileForecast` shape.
- `src/models/baseline.py`: PR-03 `MovingAverage8w` baseline.
- `src/evaluation/rolling_backtest.py`: PR-04 rolling-origin backtest.

---

## Task 1: Repo skeleton, schema contract, and deterministic sample data

**Files:**
- Create: `pyproject.toml`, `Makefile`, `.gitignore`, `.github/workflows/ci.yml`
- Create: `app/streamlit_app.py`, `app/pages/.gitkeep`
- Create: `src/__init__.py`, `src/data/__init__.py`, `src/data/schema.py`, `src/data/sample_data.py`
- Create: `src/features/__init__.py`, `src/models/__init__.py`, `src/evaluation/__init__.py`, `src/hierarchy/__init__.py`, `src/business/__init__.py`, `src/agent/__init__.py`
- Test: `tests/data/test_schema.py`, `tests/data/test_sample_data.py`

**Interfaces:**
- Produces: `TABLE_SCHEMAS: dict[str, TableSchema]`
- Produces: `get_table_schema(table_name: str) -> TableSchema`
- Produces: `SampleDataConfig`
- Produces: `generate_sample_data(config: SampleDataConfig | None = None) -> dict[str, pandas.DataFrame]`
- Produces: `write_sample_data(output_dir: str | Path = "data/sample", config: SampleDataConfig | None = None) -> Mapping[str, Path]`

- [x] **Step 1: Write failing schema tests**

Run: `python -m pytest tests/data/test_schema.py -q`

Expected before implementation: import failure for `src.data.schema`.

- [x] **Step 2: Write failing sample-data tests**

Run: `python -m pytest tests/data/test_sample_data.py -q`

Expected before implementation: import failure for `src.data.sample_data`.

- [x] **Step 3: Implement minimal schema module**

Create declarative table contracts for `fact_sales_weekly`, `fact_inventory_weekly`, `fact_price_promo_weekly`, `dim_product`, `dim_channel`, `forecast_output`, and `forecast_override`.

- [x] **Step 4: Implement deterministic sample data generator**

Generate sales, inventory, promo, product, and channel tables with weekly grain, non-negative demand/inventory, valid discounts, and consistent fact-to-dimension keys.

- [x] **Step 5: Run tests to verify green**

Run: `python -m pytest`

Expected after implementation: all Task 1 tests pass.

- [x] **Step 6: Verify sample CSV writer**

Run: `python -m src.data.sample_data`

Expected after implementation: five CSV paths printed under `data/sample/`.

---

## Task 2: CSV loader and hard data quality gate

**Files:**
- Create: `src/data/load_data.py`
- Create: `src/data/validate_data.py`
- Test: `tests/data/test_load_data.py`
- Test: `tests/data/test_validate_data.py`

**Interfaces:**
- Consumes: `TABLE_SCHEMAS`, `get_table_schema`, `generate_sample_data`
- Produces: `load_table(path: str | Path, table_name: str) -> pandas.DataFrame`
- Produces: `load_tables(directory: str | Path) -> dict[str, pandas.DataFrame]`
- Produces: `DataQualityIssue(check: str, table: str, severity: str, message: str, rows: int | None = None)`
- Produces: `DataQualityReport(issues: tuple[DataQualityIssue, ...], passed: bool)`
- Produces: `validate_tables(tables: Mapping[str, pandas.DataFrame]) -> DataQualityReport`
- Produces: `assert_valid_tables(tables: Mapping[str, pandas.DataFrame]) -> None`

- [ ] **Step 1: RED missing required column**: remove `sell_out`; expect `check="required_columns"`.
- [ ] **Step 2: GREEN required column check**: scan all `TableSchema.column_names`.
- [ ] **Step 3: RED duplicate primary key**: append duplicate sales row; expect `check="unique_key"`.
- [ ] **Step 4: GREEN primary-key uniqueness check**: detect duplicates for every schema primary key.
- [ ] **Step 5: RED foreign-key integrity**: replace one SKU with `UNKNOWN`; expect `check="foreign_key"`.
- [ ] **Step 6: GREEN SKU/channel foreign-key checks**: check fact rows against `dim_product` and `dim_channel`.
- [ ] **Step 7: RED numeric legality**: negative sales, negative inventory, zero price, and discount > 1 must block.
- [ ] **Step 8: GREEN numeric legality checks**: implement non-negative, positive price, discount range, and binary flag checks.
- [ ] **Step 9: RED weekly continuity**: remove one week for one `(country, channel, sku)` group; expect `check="weekly_continuity"`.
- [ ] **Step 10: GREEN weekly continuity check**: verify weekly frequency per series.
- [ ] **Step 11: RED CSV loader schema enforcement**: missing contract column raises `ValueError`.
- [ ] **Step 12: GREEN CSV loader**: parse CSV, coerce dates/bools, normalize schema column order.
- [ ] **Step 13: Run and commit**: `python -m pytest tests/data -q`.

---

## Task 3: Metrics and FVA functions

**Files:**
- Create: `src/evaluation/metrics.py`
- Create: `src/evaluation/fva.py`
- Test: `tests/evaluation/test_metrics.py`
- Test: `tests/evaluation/test_fva.py`

**Interfaces:**
- Produces: `wape(actual, predicted) -> float`
- Produces: `weighted_wape(actual, predicted, weights) -> float`
- Produces: `bias(actual, predicted) -> float`
- Produces: `p90_coverage(actual, p90) -> float`
- Produces: `pinball_loss(actual, predicted_quantile, quantile: float) -> float`
- Produces: `forecast_value_add(baseline_wape: float, system_wape: float) -> float`

- [ ] **Step 1: RED WAPE hand calculation**: `actual=[100,50]`, `predicted=[90,60]`, expected `20/150`.
- [ ] **Step 2: GREEN WAPE**: implement defensive numeric conversion and zero-denominator behavior.
- [ ] **Step 3: RED bias sign convention**: over-forecasting should return positive bias.
- [ ] **Step 4: GREEN bias**: implement `sum(predicted - actual) / sum(actual)`.
- [ ] **Step 5: RED coverage and pinball loss**: add hand-calculated examples.
- [ ] **Step 6: GREEN coverage and pinball loss**: implement quantile helpers.
- [ ] **Step 7: RED FVA**: baseline WAPE `0.30`, system WAPE `0.22`, expected `0.08`.
- [ ] **Step 8: GREEN FVA**: implement `baseline_wape - system_wape`.
- [ ] **Step 9: Run and commit**: `python -m pytest tests/evaluation/test_metrics.py tests/evaluation/test_fva.py -q`.

---

## Task 4: Base forecaster contract and MovingAverage8w baseline

**Files:**
- Create: `src/models/base.py`
- Create: `src/models/baseline.py`
- Test: `tests/models/test_baseline.py`

**Interfaces:**
- Produces: `BaseForecaster.fit(panel: pandas.DataFrame, features: pandas.DataFrame | None = None, *, as_of: date) -> None`
- Produces: `BaseForecaster.predict(horizon: int, future_covariates: pandas.DataFrame | None = None) -> pandas.DataFrame`
- Produces: `MovingAverage8w(target: str = "sell_out")`

- [ ] **Step 1: RED contract columns**: prediction returns one row per series per horizon and all forecast output columns.
- [ ] **Step 2: GREEN contract and baseline**: fit on rows with `week_start <= as_of`; P50 is last-8-week average.
- [ ] **Step 3: RED quantile spread**: assert `P10 <= P50 <= P90`.
- [ ] **Step 4: GREEN quantile spread**: use recent standard deviation with a floor.
- [ ] **Step 5: RED as-of protection**: future spike after `as_of` must not change prediction.
- [ ] **Step 6: GREEN as-of filtering**: store and enforce `as_of`.
- [ ] **Step 7: Run and commit**: `python -m pytest tests/models/test_baseline.py -q`.

---

## Task 5: Rolling-origin backtest and leakage assertions

**Files:**
- Create: `src/evaluation/rolling_backtest.py`
- Test: `tests/evaluation/test_rolling_backtest.py`

**Interfaces:**
- Produces: `BacktestConfig(origins: tuple[date, ...], horizon: int = 4, target: str = "sell_out")`
- Produces: `run_rolling_backtest(panel: pandas.DataFrame, forecaster: BaseForecaster, config: BacktestConfig) -> pandas.DataFrame`
- Produces report columns: `origin`, `horizon`, `country`, `channel`, `sku`, `actual`, `p10`, `p50`, `p90`, `model_name`, `scenario_name`.

- [ ] **Step 1: RED horizon-level result shape**: 2 origins × 4 horizons must contain horizons `1..4`.
- [ ] **Step 2: GREEN rolling-origin loop**: fit as-of each origin, predict horizon, join actuals.
- [ ] **Step 3: RED missing actuals**: origin too close to end raises `ValueError`.
- [ ] **Step 4: GREEN missing-actual guard**: fail with affected origin/horizon counts.
- [ ] **Step 5: RED leakage guard**: test forecaster records max training week `<= origin`.
- [ ] **Step 6: GREEN as-of assertion**: enforce before each fit.
- [ ] **Step 7: Run and commit**: `python -m pytest tests/evaluation/test_rolling_backtest.py -q`.

---

## Task 6: `make backtest` P1 integration

**Files:**
- Modify: `Makefile`
- Create: `src/evaluation/run_backtest.py`
- Test: `tests/evaluation/test_run_backtest.py`

**Interfaces:**
- Produces CLI: `python -m src.evaluation.run_backtest`
- Produces console output containing `WAPE`, `Bias`, `P90 Coverage`, and `FVA vs MovingAverage8w`.

- [ ] **Step 1: RED CLI output contract**: subprocess stdout must include required metric labels.
- [ ] **Step 2: GREEN CLI wrapper**: generate sample data, validate tables, run baseline backtest, compute metrics, print compact table.
- [ ] **Step 3: RED Makefile target**: `make backtest` exits non-zero until wired.
- [ ] **Step 4: GREEN Makefile target**: wire `backtest` to `python -m src.evaluation.run_backtest`.
- [ ] **Step 5: Run all P1 tests and commit**: `make test && make data && make backtest`.

---

## Self-Review

**Spec coverage:** Covers P1 DoD: schema/sample data, quality gates, evaluation metrics, FVA, baseline model, rolling backtest, and `make backtest`. It intentionally excludes LightGBM, hierarchy reconciliation, dashboard, sell-in recommendations, promotions, launch analog, and Agent explanations.

**Placeholder scan:** No task contains `TBD`, `TODO`, or undefined module names. Future tasks define exact paths, interfaces, test intent, commands, and commit messages.

**Type consistency:** Later tasks consume earlier symbols: `TABLE_SCHEMAS`, `generate_sample_data`, `validate_tables`, metric functions, `BaseForecaster`, and `MovingAverage8w`.
