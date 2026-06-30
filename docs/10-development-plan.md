# 10 · 开发计划（Development Plan）

> 前置边界已确认（见 `09` 顶部）：sell-out 干净可得（情形 A）、库存可得、模型训练由内部 AI 承担、
> 现状基线 = GTM 的 8 周移动平均 + 经验、FVA 阈值暂缓。**可进入编码。**
>
> 本计划面向**单人开发 + 内部 AI 负责训练**的现实，按"构建顺序"组织——
> 不是按页面/功能堆叠，而是按 `04 §1` 的纪律：**先有数据与评估骨架，再有模型，最后才是界面与场景。**

---

## 1. 三条贯穿全程的原则

1. **数据 → 评估 → 模型 → 界面 → 业务 → 场景 → 试点**，顺序不可颠倒。先能"测量好坏"，才谈"做得更好"。
2. **模型层可插拔**：内部 AI 训练出的模型，通过统一的 `BaseForecaster` 接口（§4）接入，本仓库提供一个 LightGBM 参考实现作为兜底/对照，不与内部训练算力竞争。
3. **FVA 对照对象明确**：每次回测都和 **8 周移动平均**（= GTM 现状）对比，这是 v1 必须打败的基线。若能拿到 GTM 历史预测原值（`09 B2`），再加一列"人工 vs 系统"。

---

## 2. 阶段总览（单人节奏，周为单位，估时仅供参考）

| 阶段 | 目标（Definition of Done） | 估时 | 依赖 |
| --- | --- | --- | --- |
| **P1 架构骨架 + 数据层 + 评估骨架** | 能加载（样例）数据、过质量门禁、把一个朴素模型跑完整 rolling backtest 并算出 WAPE/Bias/P90cov/**FVA(vs 8周MA)** | ~2 周 | 无（先行） |
| **P2 模型层（baseline + 主模型 + 校准）** | LightGBM 分位数预测 + 统计 baseline + ensemble + 层级校准；回测显示 ensemble 优于 8 周 MA，且各级数字一致 | ~2–3 周 | P1 |
| **P3 Dashboard 起步 + Agent 摘要** | Streamlit 跑起来，Executive Overview（含 **FVA 对照表**）+ Forecast Workbench 两页可用；Agent 基于结构化事实出解释 | ~2 周 | P2 |
| **P4 业务层：sell-in 建议 + override 闭环** | Inventory & Sell-in 页可用；建议 sell-in + 缺货/压货风险；可 override（带原因+owner）并入审计 | ~2 周 | P2, P3 |
| **P5 场景：促销模拟 + 新品 Analog** | Promotion Simulator（相关性+护栏）+ Launch Planner 两页可用 | ~2 周 | P2, P3 |
| **P6 Shadow-mode 试点 + 挑战者** | 每周冻结、与 GTM 并行运行 6–8 周；产出 FVA 对照报告；（可选）内部 AI 把 TimesFM/Chronos 当挑战者拉进回测 | 6–8 周（并行运行） | P1–P5 |

> 关键门：**P2 结束有一道 FVA 门** —— 若 ensemble 在干净回测下打不过 8 周移动平均，停下来查数据/特征/泄漏，不要带病往下做界面。

---

## 3. 任务分解（Task Breakdown）

### P1 · 架构骨架 + 数据层 + 评估骨架（先行，最重要）

**3.1 仓库骨架与工程基建**
- [ ] 按 `08 §4` 目录结构建空骨架（`app/`、`src/{data,features,models,evaluation,hierarchy,business,agent}/`）。
- [ ] `pyproject.toml`/`requirements.txt`：pandas/polars、duckdb、mlforecast、statsforecast、hierarchicalforecast、lightgbm、streamlit、pydantic。
- [ ] `Makefile`/任务脚本：`make data`（生成样例）、`make backtest`、`make app`。
- [ ] `.github` SessionStart hook（可选）：保证 web session 能跑 lint/test。

**3.2 数据层（src/data/）**
- [ ] `schema.py`：用 pydantic/dataclass 定义 `03` 的 6 张表（fact_sales/inventory/price_promo、dim_product/channel、forecast_output、forecast_override），含字段类型与唯一键。
- [ ] `load_data.py`：CSV/Excel/DuckDB 加载，落地到 DuckDB 单文件。
- [ ] `validate_data.py`：实现 `03 §3` 硬门禁（唯一键/主外键/时间连续性/数值合法/突变/层级口径一致），不过则中止并产出报告。
- [ ] **`sample_data.py`（关键，避免被真实数据交付卡住）**：按 schema 生成可控的合成数据（含季节性、促销、库存、新品/EOL、若干"陷阱"），供全程开发与单测使用。

**3.3 评估骨架（src/evaluation/）— 在写模型之前完成**
- [ ] `metrics.py`：WAPE、Weighted WAPE、Bias、P90 Coverage、Pinball/Quantile loss。
- [ ] `fva.py`：FVA = WAPE(baseline) − WAPE(system)，baseline 默认 **8 周移动平均**，可扩展加入 GTM 历史预测列。
- [ ] `rolling_backtest.py`：rolling-origin 回测（`04 §1`），逐 horizon（h=1..4）、分场景（促销/平销）报告；含 **as-of 防泄漏**重建特征。
- [ ] **泄漏自查**：把 `04 §1.2` 清单做成可跑的断言/单测。

**3.4 Model 接口契约（src/models/base.py）— 让内部 AI 可插拔**
- [ ] 定义 `BaseForecaster`（见 §4），先用一个 `NaiveSeasonal` / `MovingAverage8w` 实现把整条回测链路打通。

**P1 DoD**：`make backtest` 能跑：加载样例 → 门禁 → 朴素模型 → rolling backtest → 打印 WAPE/Bias/P90cov/FVA(vs 8周MA)。**此时一行模型代码都不"先进"，但闭环已成立。**

---

### P2 · 模型层（baseline + 主模型 + ensemble + 层级校准）

**3.5 特征工程（src/features/build_features.py）**
- [ ] 时间特征：lag_{1,2,4,8,13,26,52}、rolling_mean/std/max。
- [ ] 价格促销：retail/dealer price、discount_rate、promotion_flag/type、future_promo（known future covariate 白名单，`03 §4`）。
- [ ] 库存：channel_inventory、weeks_of_cover、inventory_pressure、stockout/overstock_risk 派生。
- [ ] 生命周期：product_age_weeks、launch/eol_flag、weeks_to_eol、predecessor/successor。
- [ ] 层级类别特征：region/country/channel/category/price_tier。
- [ ] **所有特征严格 as-of**，与回测共用同一份构建代码（防 train/serve skew）。

**3.6 模型（src/models/）**
- [ ] `baseline.py`：SeasonalNaive、AutoETS（StatsForecast）。
- [ ] `train_lgbm.py`：LightGBM **分位数**（P10/P50/P90）参考实现（MLForecast）。*— 内部 AI 若提供训练好的模型，按 §4 接口替换即可。*
- [ ] `ensemble.py`：Model Router（`04 §3` 场景→模型）+ 简单稳健加权（近期误差倒数 + 上下限裁剪）。

**3.7 层级校准（src/hierarchy/）**
- [ ] `build_hierarchy.py`：构建 Region→Country→Channel→SKU 层级。
- [ ] `reconcile.py`：HierarchicalForecast（BottomUp/MinTrace），保证各级数字一致。

**P2 DoD（含 FVA 门）**：回测中 ensemble 的 WAPE 显著低于 8 周移动平均（FVA 为正），且校准后各级汇总一致。**不过门则停下排查，不进入 P3。**

---

### P3 · Dashboard 起步 + Agent 摘要

**3.8 Streamlit 应用（app/）**
- [ ] `streamlit_app.py` 外壳 + 导航。
- [ ] `executive_overview.py`：总预测、Top growth/risk、缺货/压货风险、本周变化、**FVA 对照表（信任核心，`06 §3`）**、override 记录。
- [ ] `forecast_workbench.py`：选 Country/Channel/SKU；历史 sell-out/sell-in/inventory；P10/P50/P90；多模型对比；误差与 bias。

**3.9 Agent 解释层（src/agent/）**
- [ ] `explain_forecast.py`：规则引擎产出"事实 bullet（带字段级来源）" → Agent 只翻译成人话（`07 §3` 硬护栏：不运算、不造数、带来源）。
- [ ] `weekly_summary.py`：各 Country 周报。
- [ ] **合规注意（`09 F1`）**：销售数据是否可进外部 LLM 待定；接口设计成 LLM-provider 可切换，优先支持内部 AI/本地模型。

**P3 DoD**：GTM 能打开看板，一眼看到"系统 vs 自己的 8 周 MA 好多少"，并能点开每条解释看到来源。

---

### P4 · 业务层：sell-in 建议 + override 闭环

- [ ] `business/sell_in_recommendation.py`：实现 `05 §1/2` 公式与库存规则（缺货用 P75/P90、压货用 P40/P50、EOL 限补、促销前提前补）。
- [ ] 派生 weeks_of_cover、stockout_risk、overstock_risk。
- [ ] `inventory_recommendation.py` 页面：当前库存、未来 4 周需求、覆盖周数、建议 sell-in、风险。
- [ ] override：`forecast_override` 写入 + UI（必填 reason/owner）+ 审计视图；override 永不被系统静默覆盖（`06 §4`）。

**P4 DoD**：页面给出可执行的补货建议与风险；GTM 可 override 并留痕。

---

### P5 · 场景：促销模拟 + 新品 Analog

- [ ] `business/promo_scenario.py`：相关性场景（无促销/10/15/20%/bundle/operator），输出 P10/P50/P90 + 库存消化 + 风险 + **类比样本量与不确定性**；UI 明示"非因果"（`05 §3`）。
- [ ] `business/launch_analog.py`：找 3–5 个相似旧品 → launch curve × 国家/渠道/价带/促销修正；输出首 4 周 P10/P50/P90 + 铺货建议；**展示所用类比 SKU 及相似依据**（`05 §4`）。
- [ ] `promotion_simulator.py` / `launch_planner.py` 页面。

**P5 DoD**：两页可用且都带诚实边界标注。

---

### P6 · Shadow-mode 试点 + 挑战者

- [ ] 每周固定一次 forecast_run，冻结当周预测与可见信息（带 forecast_run_id + 数据快照）。
- [ ] 与 GTM 的 8 周 MA + 经验预测**并行**记录，不改任何真实决策（`01 §3`）。
- [ ] 运行 6–8 周（至少覆盖一次促销），产出 **FVA 对照报告**（系统 vs 8周MA vs 若有的人工原值）。
- [ ] （可选）内部 AI 把 TimesFM/Chronos 训练/接入为**挑战者**，按 §4 接口拉进回测；更优则 ensemble 自动加权（`04 §2`）。

**P6 DoD**：一份可向高层汇报的 FVA 对照报告 + 是否扩展的建议。

---

## 4. Model 接口契约（让内部 AI 训练的模型可插拔）

> 因为模型训练交给内部 AI，本仓库不绑定具体训练栈，而是**约定一个最小接口**。
> 任何模型（LightGBM 参考实现、内部 AI 产物、TimesFM/Chronos 挑战者）只要实现它，就能进 Router/Ensemble/回测。

```python
# src/models/base.py  (契约示意, P1 落地)
class BaseForecaster:
    name: str

    def fit(self, panel, features, *, as_of) -> None:
        """用 <= as_of 的数据训练。可为 no-op（如已由内部 AI 离线训练好）。"""

    def predict(self, horizon: int, future_covariates) -> "QuantileForecast":
        """返回每个 (country, channel, sku, week) 的 P10/P50/P90。"""
        # 必须输出 forecast_output 约定的 schema (见 03)
```

- **内部 AI 训练好的模型** → 包一层适配器实现 `predict`（`fit` 可为空），即接入。
- 所有模型输出统一落到 `forecast_output`（带 model_name），回测/ensemble/校准/看板对模型来源无感。
- 这样：训练在哪、用什么栈，都不影响系统其余部分——**模型可替换是架构的硬要求，不是事后适配。**

---

## 5. 风险检查点（Gate）

| 检查点 | 位置 | 不过怎么办 |
| --- | --- | --- |
| **数据泄漏审查** | P1 末 / P2 中 | 由非作者复核 `04 §1.2` 清单；发现泄漏则该实验作废重做 |
| **FVA 门** | P2 末 | ensemble 打不过 8 周 MA → 停做界面，回查数据/特征/模型 |
| **层级一致性** | P2 末 | 各级汇总不一致 → 修 reconcile，再继续 |
| **分位数校准** | P2 末 | P90 coverage 明显偏离 90% → 重标定分位数，否则库存决策会被误导 |
| **促销过度承诺** | P5 | UI 未标"非因果" / 未给样本量 → 不上线该页 |

---

## 6. 立即可做的第一步（P1 的前两个 commit）

1. **commit 1**：仓库骨架 + 依赖 + `schema.py` + `sample_data.py`（能生成一份合成面板数据）。
2. **commit 2**：`validate_data.py`（质量门禁）+ `metrics.py` + `rolling_backtest.py` + `MovingAverage8w` 基线，跑通 `make backtest` 打印 FVA。

> 这两步做完，"能测量好坏"的骨架就立起来了——之后所有模型/界面都长在这根骨架上。

---

## 7. 与既有文档的对应

| 本计划阶段 | 设计依据 |
| --- | --- |
| P1 数据/评估 | `03`（数据契约）、`04 §1`（回测协议）、`06`（指标/FVA） |
| P2 模型/校准 | `04 §2-§5`（模型/Router/ensemble/分位数）、`02`（架构）、`05`（特征对应业务） |
| P3 看板/Agent | `07`（页面与 Agent 护栏）、`06 §3`（FVA 表） |
| P4 业务/override | `05 §1-2`（sell-in/库存）、`06 §4`（override 闭环）、`03`（override 表） |
| P5 场景 | `05 §3`（促销诚实）、`05 §4`（新品 Analog） |
| P6 试点 | `01 §3`（shadow mode）、`08 §3`、`04 §2`（挑战者） |
