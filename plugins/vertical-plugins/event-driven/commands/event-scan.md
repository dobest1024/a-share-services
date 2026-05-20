---
description: 当日 / 当周事件驱动综合扫描
---

# /event-scan [window=daily|weekly]

执行 event-hunter agent 工作流，输出综合事件扫描报告。

## 工作流
1. 并行扫描龙虎榜 / 北向 / 两融 / 大宗 / 解禁 / 业绩预告 / 监管文书 / 公司行动 / 涨跌停
2. 识别异动（单事件高强度 + 多事件叠加 + 主题联动）
3. 输出今日热点 + 个股异动 + 主题联动 + 风险信号 + 跟踪清单

## 示例
- `/event-scan`（默认日度）
- `/event-scan window=weekly`
