---
description: 政策文件解读 - 输入文件链接或主题
---

# /policy {URL 或主题}

解读政策文件。

## 工作流
1. 识别文件（URL 抓取 / 主题查相关文件）
2. 触发 `policy-parser` skill
3. 触发 `theme-mapping` 映射受益方向
4. 输出文件摘要 + 受益行业 + 落地节奏 + 风险

## 示例
- `/policy https://www.gov.cn/...`
- `/policy 新质生产力`
- `/policy 中特估`
