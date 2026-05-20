---
name: backtest-adapter
description: 回测框架对接 - qlib / backtrader / vnpy 接口适配与标准化报告。
---

# 回测框架对接

## 框架选型

| 框架 | 适合场景 | 数据要求 |
|---|---|---|
| **qlib**（微软）| A 股原生、因子研究、高频回测 | 需提供 qlib 格式数据 |
| **backtrader** | 通用、策略多样 | csv / pandas |
| **vnpy** | 实盘对接、CTP 接口 | tick / 1min 数据 |

默认推荐：**qlib** 用于因子研究，**backtrader** 用于策略原型，**vnpy** 用于实盘前最后一步。

## qlib 标准对接

### 数据准备
```python
# qlib 格式：bin 文件 + instruments + features
import qlib
qlib.init(provider_uri="~/.qlib/qlib_data/cn_data", region="cn")
```

数据准备由 `tushare-mcp` → qlib 格式转换器完成（独立脚本）。

### 因子回测流程
```python
from qlib.workflow import R
from qlib.contrib.workflow import LGBModel

# 1. 定义因子
factor_expr = "Ref($close, -21) / $close - 1"  # 一月动量

# 2. 数据集
dataset = ...

# 3. 模型 / 排序
model = LGBModel(...)
model.fit(dataset)
pred = model.predict(dataset)

# 4. 回测
strategy = TopkDropoutStrategy(topk=50, n_drop=5, signal=pred)
backtest_result = backtest(...)
```

### 输出指标
- 年化收益 / 年化波动 / Sharpe
- 最大回撤 / 卡玛比率
- 信息比率 IR vs 基准
- 换手率
- 净值曲线

## 标准回测报告结构

```
## 回测报告 - {策略名}

### 配置
- 回测期间：YYYY-MM-DD ~ YYYY-MM-DD
- 股票池：{...}
- 基准：沪深 300 / 中证 500 / 中证 1000
- 调仓频率：月频 / 周频
- 持仓数：{Top N}
- 手续费：双边 0.15%（含印花税单边 0.1%）
- 滑点：单边 0.1%

### 业绩指标
- 年化收益：X%
- 基准年化：X%
- 超额年化：X%
- 年化波动：X%
- Sharpe：X.XX
- IR：X.XX（vs 基准）
- 最大回撤：X%（{起点} ~ {终点}）
- 卡玛：X.XX
- 月度胜率：X%

### 分年表现
| 年份 | 策略收益 | 基准收益 | 超额 | 回撤 |

### 持仓特征
- 平均持仓数
- 月均换手率（双边）
- 行业分布（取均值）
- 市值偏好

### 风险暴露
- Barra 风格暴露（动量 / 价值 / 规模 / 波动 / ...）
- 行业偏离度

### 失效区间识别
- 哪些月份策略大幅跑输基准
- 失效原因分析

### 实盘前提示
- 该回测含 / 不含冲击成本
- 该回测假设的容量上限
- 实盘可能差异（停牌处理、涨跌停未成交、限额触发）
```

## 实盘前 checklist

- [ ] 双边手续费按券商真实费率
- [ ] 滑点按标的真实流动性
- [ ] 冲击成本（资金量 > 5000 万必算）
- [ ] 涨跌停 → 未能成交的处理
- [ ] 停牌处理逻辑
- [ ] 调仓时点（开盘 vs 收盘 vs 集合竞价）
- [ ] 数据 lookahead bias 检查
- [ ] 幸存者偏差（退市股不应被排除）
