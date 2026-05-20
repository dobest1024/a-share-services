---
description: 策略回测 - qlib / backtrader 对接
---

# /backtest {策略配置}

按用户策略配置执行回测。

## 工作流
1. 解析策略配置（股票池 / 因子 / 调仓频率 / 持仓数）
2. 触发 `backtest-adapter` skill
3. 输出业绩指标 + 风险指标 + 分年表现 + 风格暴露 + 实盘前 checklist

## 示例
- `/backtest 沪深300 多因子 月频 Top50`
