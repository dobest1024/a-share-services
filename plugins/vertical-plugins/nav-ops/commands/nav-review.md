---
description: 净值核算复核
---

# /nav-review {基金代码}

执行 nav-pricer agent 工作流。

## 工作流
1. 拉持仓 + 当日行情
2. 触发 `nav-calculation` + `valuation-review` skills
3. 输出复核报告 + 异常清单

## 示例
- `/nav-review 519005`
