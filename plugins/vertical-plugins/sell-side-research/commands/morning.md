---
description: 生成晨会纪要（卖方版默认）
---

# /morning [version=sell|buy]

生成早晨 8:00 前的晨会纪要。

## 工作流
1. 拉隔夜外盘
2. 拉前日 A 股复盘
3. 触发 `catalyst-calendar` 拿今日关键事件
4. 选 3-5 重点行业 / 公司
5. 按 `morning-note` 结构输出

## 示例
- `/morning`（默认卖方版）
- `/morning version=buy`（买方版，需提供持仓清单）
