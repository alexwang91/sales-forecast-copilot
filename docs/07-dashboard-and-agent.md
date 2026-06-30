# 07 · Dashboard 与 Agent 解释层

> 沿用原方案的 5 页结构（合理）。补强两点：**(1) 每页的"成功 = 服务一个角色的一个决策"；
> (2) Agent 的硬性架构护栏——Agent 只把结构化事实翻译成人话，不做任何运算、不做任何决策。**

---

## 1. 五个 Dashboard 页面

| 页面 | 服务角色 | 核心决策 | 关键内容 |
| --- | --- | --- | --- |
| **1. Executive Overview** | 高层 / 区域负责人 | 整体态势与信任 | Region/Country 总预测、Top growth/risk SKU、缺货/压货风险、本周 forecast 变化、override 记录、**FVA 对照表（信任核心）** |
| **2. Forecast Workbench** | 销售 / 产品 | 这条线未来怎么走 | 选 Country/Channel/SKU；历史 sell-out/sell-in/inventory；P10/P50/P90；多模型对比；各模型误差与 bias |
| **3. Inventory & Sell-in** | 供应链 / 分货 | 这周补多少 | 当前库存、未来 4 周需求、weeks_of_cover、建议 sell-in、缺货/压货风险 |
| **4. Promotion Simulator** | 销售 / GTM | 促销怎么选 | 无促销 / 10% / 15% / 20% / bundle / operator campaign 场景对比；预计 sell-out、库存消化、缺货风险、建议补货量 |
| **5. Launch Planner** | 新品上市 | 新品铺多少 | 输入新品信息、选 predecessor、选国家/渠道/促销；首 4 周预测；首批铺货建议；**展示所用类比 SKU** |

> 页面 4 必须带"相关性而非因果"的显式声明（见 `05 §3`）。
> 页面 5 必须展示类比 SKU 的选择依据，让产品经理可认同/否决（见 `05 §4`）。
> 起步用 Streamlit 验证业务闭环；闭环验证后再评估是否迁移 Next.js。

---

## 2. Agent 层：只解释，不决策（硬性边界）

### Agent 可以做
```text
解释预测为什么涨/跌
总结本周风险
生成高层周报
回答 "匈牙利某 SKU 未来 4 周怎么看"
解释促销场景
列出需要人工确认的异常
```

### Agent 不能做（硬性 Non-Goal）
```text
自己改预测
自己决定发货 / 促销
编造竞品 / 宏观 / 任何无数据支撑的因素
绕过 override 审计
自己做算术 (见 §3 的关键规则)
```

---

## 3. 关键架构规则：Agent 不碰数字，只翻译事实

> 这是防止"AI 一本正经地胡说一个数字"的核心护栏，也是让高层敢信 Agent 输出的前提。

```text
模型/业务层输出结构化结果 (JSON 事实)
  ↓
规则引擎生成"事实 bullet" (含每个数字的字段来源)
  ↓
Agent 只把事实 bullet 写成通顺人话, 零运算、零新增数字
  ↓
每条结论都带字段级来源, 可点开追溯
```

**硬性规则：**
1. **Agent 输入只能是预先算好的结构化事实**，不得拿到原始数据自己聚合/计算。
2. **Agent 输出里出现的每个数字，都必须来自输入事实**——不允许 Agent 生成任何新数字。
3. **每条结论带字段级来源**（哪张表、哪个 forecast_run、哪个指标）。
4. Agent 不确定或事实缺失时，应说"数据不支持该结论"，而不是编造。

### 示例（达到的效果）
```text
Hungary / Channel A / SKU X 未来 4 周 P50 下降 18%。
主要原因:
1. 近 4 周 sell-out rolling mean 下降 12%。           [来源: fact_sales_weekly]
2. 当前库存覆盖 8.4 周, 高于目标 5 周。               [来源: fact_inventory_weekly]
3. 上周促销结束, promotion_flag 由 1 → 0。            [来源: fact_price_promo_weekly]
4. 该 SKU 上模型近 8 次回测 WAPE 17%、Bias +2%。      [来源: backtest/metrics]
```

> 这比"AI 认为会下降"可信得多——因为每句话都能被点开核对。**可核对，才可信。**

---

## 4. 周报（Agent 的高价值产出）

- 每周自动生成各 Country 的风险摘要 + 本周预测变化解释 + 需人工确认的异常清单。
- 周报同样遵守 §3 规则：所有数字来自结构化事实，带来源。
- 周报是 Executive Overview 的"叙事版"，让高层不用自己读图也能掌握态势——降低高层使用门槛本身就是采用率的关键。
