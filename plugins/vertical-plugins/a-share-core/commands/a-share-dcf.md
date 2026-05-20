---
description: A 股 DCF 估值（中国语境的 WACC、永续增长率、自由现金流）
---

# /a-share-dcf {标的}

对用户给出的非金融、非周期顶部公司执行 DCF 估值。

## 参数
- 必须：标的
- 可选：显性期年数（默认 5）、永续增长率（默认 2.5%）

## 工作流
1. 标准化标的
2. 用 `akshare-mcp.macro_bond_yield_10y` 取无风险利率
3. 触发 `dcf-model` skill
4. 输出企业价值 + 股权价值 + 每股价值参考 + WACC × g 敏感性矩阵

## 不适用情形
- 金融行业（用 PB-ROE）
- 周期股顶部
- 亏损公司

## 示例
- `/a-share-dcf 海天味业`
- `/a-share-dcf 美的集团`
