---
description: A 股可比公司分析 - 按申万二/三级行业取同行，输出估值矩阵
---

# /a-share-comps {标的}

对用户给出的标的执行可比公司分析。

## 参数
- 必须：标的（公司名或 6 位代码）
- 可选：行业层级（默认申万二级）

## 工作流
1. 用 `akshare-mcp.stock_code_lookup` 标准化标的
2. 用 `akshare-mcp.stock_profile` 拿申万行业
3. 按申万二级取同行（5-15 家）
4. 触发 `comps-analysis` skill
5. 输出估值矩阵 + 分位 + 参考观点

## 示例
- `/a-share-comps 贵州茅台`
- `/a-share-comps 600519`
- `/a-share-comps 宁德时代`

输出末尾必有合规提示。
