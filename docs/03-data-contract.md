# 03 · 数据契约与销义语义层

> 系统的地基。表结构沿用 OpenAI 原方案（设计合理），并补充三件原方案缺失但对信任至关重要的东西：
> **(1) sell-out 可得性 fallback、(2) 数据质量门禁、(3) as-of 时点契约（防泄漏）。**

---

## 1. 头号边界问题：到底有没有 sell-out 数据？

> 这是整个方案能否成立的前提，必须在编码前回答（见 `09`）。

"先预测 sell-out 再推导 sell-in" 是本方案的核心逻辑（见 `05`）。但消费电子行业**经常只有 sell-in（出货给渠道），没有或只有脏的 sell-out（渠道真实卖给消费者）**。

三种情形与对应策略：

| 情形 | 策略 |
| --- | --- |
| **A. sell-out 干净可得** | 按主方案：预测 sell-out → 推导 sell-in。 |
| **B. sell-out 部分可得**（部分渠道有 POS/sell-through） | 在有 sell-out 的渠道做主方案；其余渠道用 fallback B'。 |
| **C. 仅有 sell-in** | Fallback：用 `sell-in − Δchannel_inventory` 估算 sell-out（需库存数据）；若库存也缺，则 v1 退化为直接预测 sell-in，并**显式标注这是出货预测而非需求预测**，库存/促销模块相应降级。 |

> **绝不**在情形 C 下假装在预测需求。口径必须对使用者诚实，否则一次"预测了需求其实是出货"的误解就会摧毁信任。

---

## 2. 语义层表结构

以下为 v1 标准表（事实表 `fact_*`，维度表 `dim_*`，输出表）。

### `fact_sales_weekly`
```text
week_start      (date, 周起始, 主键之一)
region          (str)
country         (str)
channel         (str)
sku             (str)
sell_in         (float, 出货)
sell_out        (float, 渠道售出; 情形C下可空/估算)
唯一键: (week_start, country, channel, sku)
```

### `fact_inventory_weekly`
```text
week_start, country, channel, sku
channel_inventory   (float, 渠道库存)
stock_available     (float, 可用库存)
stockout_flag       (0/1)
weeks_of_cover      (float, 库存覆盖周数 = inventory / 近期周均 sell-out)
```

### `fact_price_promo_weekly`
```text
week_start, country, channel, sku
retail_price, dealer_price
discount_rate       (0~1)
promotion_flag      (0/1)
promotion_type      (str: none/discount/bundle/operator_campaign/...)
※ 未来 4–8 周的促销计划单独标注为 known future covariate (见 §4)
```

### `dim_product`
```text
sku, product_name, category, series, price_tier
launch_date, eol_date
predecessor_sku, successor_sku   (新品 Analog 模型依赖)
```

### `dim_channel`
```text
channel, country, region, channel_type, channel_tier
is_operator, is_ecommerce, is_retail_chain
```

### `forecast_output`
```text
forecast_run_id, run_date, forecast_week
region, country, channel, sku
target              (sell_out / sell_in, 显式标注口径)
p10, p50, p90
model_name          (产出该行的模型/ensemble 名)
scenario_name       (基线 / promo_10 / launch / ...)
```

### `forecast_override`（信任的关键表）
```text
forecast_run_id, country, channel, sku, forecast_week
original_p50, override_p50
override_reason     (必填, 自由文本 + 可选枚举)
owner               (谁改的)
timestamp
```
> `forecast_override` 让系统可解释、可追责、可复盘。高层信的是"能复盘的系统"，
> 不是"输出神秘数字的黑盒"。事后用它做 override 的 FVA 分析（见 `06`）。

---

## 3. 数据质量门禁（Data Quality Gate）

> 原方案有"数据质量检查"但未定义门槛。质量门禁必须是**硬门禁**：不过则中止该次 run 并报告，绝不带病预测。

每次导入后强制校验（至少）：

1. **唯一键**：`(week_start, country, channel, sku)` 无重复。
2. **主外键完整性**：fact 表里出现的 sku/channel 必须在 dim 表存在。
3. **时间连续性**：周序列无意外断档（断档要么补 0 要么显式标记，不能静默）。
4. **数值合法性**：销量/库存非负；discount_rate ∈ [0,1]；价格 > 0。
5. **突变检测**：单周环比突变超阈值的点要标记（可能是数据错误或真实事件，需人确认）。
6. **层级口径一致性**：抽样校验 Country 汇总是否 ≈ 其下 SKU 之和（量纲/口径错误的早期信号）。

门禁结果作为 forecast_run 的一部分留痕，并在 Dashboard 的数据质量卡片展示。

---

## 4. As-of 时点契约（防泄漏的契约层定义）

> 数据泄漏是"高层信任"的头号隐形杀手——回测看着很美，上线全崩。必须在数据契约层就约束。

- 每个字段标注其 **可见时点（availability time）**：该信息在现实中**何时**才能被知道。
- 预测 `forecast_week=W` 时，特征只能使用 **截至预测发起时点 `t0`** 可见的信息。
- **known future covariates 白名单**：仅以下字段允许"使用未来值"，且必须是计划性、确定性信息：
  - 未来促销计划（future_promo_flag / future_discount_rate / promotion_type）
  - 日历（节假日、促销季）
  - 已知的价格调整计划、已知的 launch/EOL 日期
- 任何不在白名单的"未来信息"进入特征 = 泄漏 = 该次实验作废。
- 回测时严格用 as-of 重建特征（point-in-time correctness），不得用"今天的全量数据"回填历史特征。

> 详细的回测协议与泄漏自查清单见 `04`。
