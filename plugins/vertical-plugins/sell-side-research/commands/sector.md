---
description: 行业综述 - 按申万一级 / 二级输出空间、产业链、竞争、政策、估值、公司清单
---

# /sector {行业}

输出 A 股行业综述。

## 工作流
1. 确认行业边界（申万一级 / 二级，或转主题）
2. 触发 `sector-overview` skill
3. 触发 `policy-parser`（行业相关政策）
4. 触发 `industry-classification`（同行对比）
5. 输出 8 段式综述

## 示例
- `/sector 电力设备`
- `/sector 创新药`
- `/sector 新质生产力`（主题，先转受益行业）
