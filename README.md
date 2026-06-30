# Sales Forecast Decision Copilot（消费电子销售预测决策系统）

> 用多模型预测未来 4 周 **sell-out**，用库存约束生成 **sell-in 建议**，
> 用促销 / 新品模块做场景模拟，用层级校准保证 Region/Country/Channel/SKU 数字一致，
> 用 Agent 把预测变成销售可执行的建议——并且**用 Forecast Value Add 证明它比现有人工流程更好**。

---

## 这是什么 / 这不是什么

**是**：一个面向销售、供应链、区域负责人和经营高层的**销售决策系统**。模型只是其中一个零件。
**不是**：一个"更先进的预测模型"。我们不靠模型先进度赢得信任，靠**可解释、可追责、可复盘、可证明更优**的闭环赢得信任。

> 核心判断：高层不信预测，几乎从来不是因为模型不够先进，
> 而是因为系统回答不了"为什么这么预测""比人工好多少""哪里会缺货""谁改了什么"。
> 本项目的第一目标，就是把这些问题做成产品功能。

---

## 当前状态

**阶段：方案设计（Design）。** 本仓库目前只包含设计与边界文档，**尚未编写实现代码**——这是刻意的。
我们遵循"先定方案边界、再写实现"的原则。在 [`docs/09-open-questions-for-stakeholders.md`](docs/09-open-questions-for-stakeholders.md)
中的关键边界问题（尤其是 sell-out 数据可得性）得到确认之前，不进入编码阶段。

---

## 文档导航

| 文档 | 内容 | 读者 |
| --- | --- | --- |
| [`docs/00-vision-scope-and-nongoals.md`](docs/00-vision-scope-and-nongoals.md) | 愿景、北极星指标、明确的 Non-Goals、范围边界 | 所有人 / 高层 |
| [`docs/01-decision-framing-and-trust-strategy.md`](docs/01-decision-framing-and-trust-strategy.md) | 我们改进哪些**决策**、给谁用、现状流程、如何赢得信任（shadow mode） | 高层 / 业务 |
| [`docs/02-architecture.md`](docs/02-architecture.md) | 修订后的系统架构与分层 | 技术 |
| [`docs/03-data-contract.md`](docs/03-data-contract.md) | 销售语义层、表结构、数据契约与质量门槛 | 技术 / 数据 |
| [`docs/04-modeling-and-backtest-protocol.md`](docs/04-modeling-and-backtest-protocol.md) | 模型组合、Model Router、**回测协议与防泄漏纪律** | 技术 |
| [`docs/05-business-decision-logic.md`](docs/05-business-decision-logic.md) | sell-out → sell-in 逻辑、库存规则、促销诚实边界、新品 Analog | 业务 / 技术 |
| [`docs/06-evaluation-trust-and-override-loop.md`](docs/06-evaluation-trust-and-override-loop.md) | FVA、指标体系、人工 override 审计闭环 | 高层 / 业务 |
| [`docs/07-dashboard-and-agent.md`](docs/07-dashboard-and-agent.md) | 5 个 Dashboard 页面、Agent 的硬性护栏 | 业务 / 技术 |
| [`docs/08-roadmap-and-mvp.md`](docs/08-roadmap-and-mvp.md) | 按"信任里程碑"而非功能堆叠排期的路线图 | 所有人 |
| [`docs/09-open-questions-for-stakeholders.md`](docs/09-open-questions-for-stakeholders.md) | 编码前必须和干系人敲定的边界问题 | 所有人 |
| [`docs/REVIEW-of-openai-plan.md`](docs/REVIEW-of-openai-plan.md) | 对 OpenAI 原始方案的逐点评审：同意什么、改什么、为什么 | 决策记录 |

---

## 北极星指标（North Star）

**Forecast Value Add (FVA)**：本系统相对**现有人工/朴素流程**的预测误差改进，并换算成业务价值（避免的缺货 + 避免的压货）。
不是 WAPE 的绝对值——是"比你们现在的做法好多少"。这是赢得高层信任的唯一硬通货，详见
[`docs/06-evaluation-trust-and-override-loop.md`](docs/06-evaluation-trust-and-override-loop.md)。

---

## 与 OpenAI 原方案的主要差异（摘要）

1. **FVA 升为北极星**，而不是把 WAPE 当主指标。
2. **Foundation Model（TimesFM/Chronos）从"核心"降级为"Phase 4 挑战者"**——它们带来基础设施风险且是黑盒，与"建立信任"目标相悖。先用 LightGBM + 统计 baseline + 层级校准把闭环跑通。
3. **先解决数据现实边界**：到底有没有干净的 sell-out 数据？没有就需要 fallback 方案。这是第一优先级的开放问题。
4. **抬高 override + 审计闭环的权重，并采用 shadow-mode 试点**——在一个友好国家并行运行、不改任何决策，6–8 周后用 FVA 说话。
5. **促销模拟器在 v1 明确标注为"相关性场景探索"而非因果 uplift**，避免过度承诺。
6. **路线图按信任里程碑分期**，并写明 Non-Goals。

完整评审见 [`docs/REVIEW-of-openai-plan.md`](docs/REVIEW-of-openai-plan.md)。
