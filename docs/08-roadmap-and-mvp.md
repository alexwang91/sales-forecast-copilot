# 08 · 路线图与 MVP

> 与原方案的关键差异：**按"信任里程碑"分期，而非按"功能堆叠"分期。**
> 每个 Phase 的退出标准都是"是否更值得被信任 / 更被采用"，而不是"功能是否做完"。

---

## 1. 分期总览（每期一个信任里程碑）

| Phase | 里程碑（退出标准） | 交付的能力 |
| --- | --- | --- |
| **Phase 0** | **"我们能测量'更好'"** | 数据契约 + 质量门禁 + 回测骨架 + FVA 基线（量化现状） |
| **Phase 1** | **"系统比现状准，且各级数字一致"** | LightGBM + 统计 baseline + 层级校准 + Executive Overview + Workbench |
| **Phase 2** | **"预测能变成补货行动，且人能改并被记录"** | 库存/sell-in 建议 + override 审计闭环 + Inventory 页面 |
| **Phase 3** | **"能做场景与新品规划"** | 促销模拟器（相关性，带护栏）+ 新品 Analog + Launch/Promotion 页面 |
| **Phase 4** | **"挑战者与解释力"** | TimesFM/Chronos 作为挑战者拉进回测；Agent 解释层与周报成熟 |

> 顺序的核心逻辑：**先证明"能测量好坏"（P0）→ 再证明"我们更好"（P1）→ 再把好预测变成行动（P2）
> → 再扩展场景（P3）→ 最后才碰重型/黑盒组件（P4）。** 信任是逐级累加的，不能跳级。

---

## 2. MVP 范围（= Phase 0 + Phase 1，刻意砍小）

> 一个人做，第一版不要做全量平台。把范围砍到"足以产出一份有说服力的 FVA 对照报告"。

### MVP 数据范围
```text
1 个 Region
2–3 个国家
2–3 个渠道
~10 个 SKU
周粒度, 预测未来 4 周
输出 P10 / P50 / P90
```

### MVP 必须有
```text
数据上传 + 数据质量门禁
LightGBM quantile forecast
SeasonalNaive / AutoETS baseline
rolling backtest
WAPE / Bias / P90 coverage / FVA
层级校准 (各级一致)
库存覆盖周数 + sell-in recommendation (若 sell-out 数据可得)
Streamlit dashboard (Executive Overview + Workbench 起步)
Agent summary (基于结构化事实)
```

### MVP 先不做（= 原方案 Non-Goal + 本项目 Non-Goal）
```text
TimesFM / Chronos (Phase 4 再作为挑战者)
复杂权限系统 / 自动审批流
实时数据流
复杂 MLOps
严肃因果 promotion uplift
完整新品 launch 自动化
多 Agent 自主决策
```

> 注意：MVP 把 **FVA 和层级校准列为必须**——因为它们是"可证明 + 数字一致"的信任基础，
> 而把 **Foundation Model 排除**——因为它是 v1 的风险项而非价值项（见 `04`/`REVIEW`）。

---

## 3. 与 Shadow Mode 试点的衔接

- MVP（P0+P1）跑通后，**不直接上线替换**，而是进入 `01 §3` 的 shadow-mode 试点：在 1 个友好国家并行运行 6–8 周。
- 试点产出的 FVA 对照报告 = 向高层汇报的弹药。
- 试点 FVA 为正且销售愿意参考 → 进入 Phase 2/3 扩展；为负 → 回到数据/特征/模型迭代，不强推。

---

## 4. 建议的目录骨架（实现期参考，当前不创建）

> 仅作为 Phase 0 开始编码时的参考结构。**当前阶段不创建任何实现文件**（遵循"先定边界"原则）。

```text
sales-forecast-copilot/
  app/
    streamlit_app.py
    pages/
      executive_overview.py
      forecast_workbench.py
      inventory_recommendation.py
      promotion_simulator.py
      launch_planner.py
  src/
    data/        schema.py  load_data.py  validate_data.py
    features/    build_features.py
    models/      baseline.py  train_lgbm.py  ensemble.py  predict_timesfm.py(后期)
    evaluation/  rolling_backtest.py  metrics.py  fva.py
    hierarchy/   build_hierarchy.py  reconcile.py
    business/    sell_in_recommendation.py  promo_scenario.py  launch_analog.py
    agent/       explain_forecast.py  weekly_summary.py
  docs/          (本设计文档集)
```

> 编码顺序建议：`data/` → `evaluation/`（回测骨架）→ `models/baseline` → `models/train_lgbm`
> → `hierarchy/` → `business/` → `app/` → `agent/`。
> **先有数据与评估骨架，再写模型**——这与 `04 §1` 的"先回测后模型"一致。
