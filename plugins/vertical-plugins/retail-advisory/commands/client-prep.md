---
description: 投顾客户会议准备（持牌投顾使用）
---

# /client-prep {客户编号}

为持牌投顾准备客户会议材料。

## ⚠️ 前提
- 调用方必须是持牌投资顾问机构
- 客户画像已完成

## 工作流
1. 拉取客户画像 + 持仓
2. 计算与目标配置偏离
3. 触发 `monthly-recap`、`allocation-framework`
4. 输出会议材料 + 风险揭示 + 签字位

## 示例
- `/client-prep C00123`
