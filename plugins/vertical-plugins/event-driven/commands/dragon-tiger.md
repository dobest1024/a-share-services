---
description: 当日龙虎榜分析 - 席位识别、资金主导力度、风格判断
---

# /dragon-tiger [date=today]

分析指定日期的龙虎榜。

## 工作流
1. 拉龙虎榜（`akshare-mcp.fund_flow_dragon_tiger`）
2. 触发 `dragon-tiger-list` skill
3. 输出主线、机构席位、知名游资席位特征、次日观察清单

## 示例
- `/dragon-tiger`（今日）
- `/dragon-tiger date=20250515`
