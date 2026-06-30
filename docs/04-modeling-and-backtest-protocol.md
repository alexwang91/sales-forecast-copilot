# 04 · 模型策略与回测协议

> 沿用原方案的"Model Router + Ensemble"思想（正确），但做两处重要修订：
> **(1) Foundation Model 降级为后期挑战者；(2) 把"回测协议 + 防泄漏纪律"前置为先决条件——它比模型选型更重要。**

---

## 1. 先讲回测，再讲模型（顺序刻意如此）

> 原方案把回测放在第 11 项。我把它放到模型之前：**没有可信的回测协议，再多模型都是噪声。**
> 回测协议应在写第一个模型之前就锁定，并最好由他人独立复核。

### 1.1 回测方法：Rolling-origin（滚动起点）

```text
对每个 origin 时点 t0:
    用 ≤ t0 的数据训练 / 构建特征
    预测 t0+1 ... t0+4 周 (P10/P50/P90)
    与真实值比较, 记录指标
t0 沿时间滚动前进, 覆盖多个季节/促销周期
```

- 多个滚动起点 → 避免"挑了一个好窗口"的幸存者偏差。
- 覆盖促销期 + 非促销期 + 季节高/低点，报告**分段表现**而非单一平均。
- 4 周视野逐 horizon 报告（h=1/2/3/4 误差通常递增，要分别看）。

### 1.2 防泄漏自查清单（每个模型上线前过一遍）

- [ ] 特征严格 as-of（见 `03 §4`），无 point-in-time 违规。
- [ ] target 与特征无同周泄漏（例如用本周库存解释本周 sell-out 要谨慎）。
- [ ] rolling/lag 特征的窗口只回看、不前瞻。
- [ ] 标准化/编码的统计量只用训练段拟合，不用全量。
- [ ] known future covariate 仅限白名单字段（`03 §4`）。
- [ ] 回测与上线用**同一套**特征构建代码（避免 train/serve skew）。

### 1.3 必须有的对照基线

每次回测都和这些"诚实基线"对照，否则无法计算 FVA：

- 朴素：SeasonalNaive、去年同期、近 4 周均值。
- 人工：现有人工流程的历史预测（若可得——这是 FVA 的关键对照，见 `06`）。

---

## 2. 模型组合（v1 与后期分清）

### v1 关键路径（必须有）
```text
Baseline:
  - SeasonalNaive
  - AutoETS
  - (可选) AutoARIMA
主预测器:
  - LightGBM Quantile  ← v1 主力
Specialized:
  - Launch Analog Model  (新品, 见 05)
层级一致性:
  - HierarchicalForecast (reconcile)
```

### v1 可选
```text
  - CatBoost Quantile (作为第二棵树模型/对照)
```

### Phase 4 挑战者（默认不在 v1 关键路径）
```text
  - TimesFM (zero-shot / +XReg)
  - Chronos-2 (univariate / covariate-informed)
```

> **为什么把 Foundation Model 降级**（与原方案的主要分歧，详见 `REVIEW`）：
> 1. **信任目标相悖**：它们是黑盒，而 v1 的全部目的是"可解释、可证明"。
> 2. **基础设施风险**：GPU、大模型下载、依赖地狱，会让"给高层现场演示"更容易翻车。
> 3. **边际收益不确定**：在有价格/促销/库存外生变量的零售场景，调好的 LightGBM 往往已很强；Foundation Model 不一定更好。
> 4. **正确时机**：先用 LightGBM + baseline + 校准把信任闭环跑通，**再**把 TimesFM/Chronos 当挑战者拉进回测——若它们真的更好，ensemble 会自动给权重；若没更好，也没赌上 v1 的信誉。

---

## 3. Model Router（场景 → 模型）

不同场景不该用同一个模型。Router 依据序列特征路由：

| 场景 | v1 首选 | 后期可加 |
| --- | --- | --- |
| 成熟稳定 SKU | LightGBM / ETS ensemble | TimesFM |
| 促销频繁 SKU | LightGBM / CatBoost | — |
| 渠道差异大 | CatBoost / LightGBM | — |
| 新品 launch | **Analog Launch Model** | — |
| 低销量/断续需求 | LightGBM Tweedie / Croston / SeasonalNaive | — |
| 有库存约束 | 主预测 + 库存修正（见 `05`） | — |
| 高层汇总层 | 层级校准后的结果 | — |

---

## 4. Ensemble：权重用回测学，不要手拍

```text
final_forecast =
    w1 · LightGBM
  + w2 · (CatBoost / 其它)
  + w3 · SeasonalNaive
  + ...
```

- 权重由**近期 rolling backtest 表现**学出（按 country×channel×SKU 维度记录哪个模型更好）。
- 系统每次回测后自动记录：在哪个 country×channel×SKU 上哪个模型最好 / 谁高估 / 谁低估 / 谁 P90 覆盖不足。
- 这些记录既驱动 ensemble 权重，也喂给 Agent 用于解释（"该 SKU 上 LightGBM 过去 8 次 WAPE 17%、bias +2%"）。

> 注意：v1 可以先用简单稳健的加权（如按近期误差倒数加权 + 上下限裁剪），不必一上来就上复杂的 stacking。
> 简单、稳健、可解释优先于花哨。

---

## 5. 分位数预测（为什么是 P10/P50/P90 而非单点）

- 业务决策需要的是风险，不是一个点：缺货风险用高分位（P75/P90），压货风险用低分位（P40/P50）。详见 `05` 的库存规则。
- 用 LightGBM 的 quantile loss 直接产出分位数；评估时报告 **P90 coverage**（实际落在 ≤P90 的比例是否接近 90%）以验证分位数校准（calibration）是否可信。
- 分位数校准不准会误导库存决策，因此 P90 coverage 是 v1 必报指标（见 `06`）。
