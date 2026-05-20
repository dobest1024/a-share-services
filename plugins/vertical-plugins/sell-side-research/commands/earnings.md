---
description: 季报 / 中报 / 年报分析（含业绩预告 / 快报）
---

# /earnings {标的}

执行个股财报深度分析。

## 工作流
1. 标准化标的
2. 拉最近一期财报（自动识别已披露的最新一期）
3. 触发 `earnings-analysis` skill
4. 触发 `financial-quality-check` 财务质量扫描
5. 输出数据快照 + 超预期分析 + 风险点 + 跟踪问题

## 示例
- `/earnings 比亚迪`
- `/earnings 300750`
