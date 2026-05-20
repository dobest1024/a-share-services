---
description: A 股财报质量扫描 - 9 大风险点
---

# /a-share-quality {标的}

对用户给出的标的执行 A 股财报质量风险扫描。

## 工作流
1. 标准化标的
2. 拉近 5 年财报（`akshare-mcp.fundamental_*`）
3. 触发 `financial-quality-check` skill
4. 输出 9 大风险点的触警情况 + 证据 + 追问清单

## 检查的风险点
- 商誉减值
- 应收账款异常
- 关联交易
- 研发资本化激进
- 存货跌价
- 其他应收款黑洞
- 大额非经常性损益
- 货币资金"存贷双高"
- 现金流与净利润背离

## 示例
- `/a-share-quality 中科金财`
- `/a-share-quality 蓝色光标`
