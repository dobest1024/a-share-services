# stock-researcher · Managed Agent 部署

## 安全等级

**T2** — 输出前需人工复核，**禁止**直接面向终端投资者发布。

## 数据依赖

- `akshare-mcp`（主力）
- `tushare-mcp`（可选，akshare 故障时兜底，需 `TUSHARE_TOKEN`）
- `cninfo-mcp`（可选，公告原文检索）

## Handoff

Phase 0 骨架不调用其他 agent。Phase 2 起可 handoff 给：
- `event-hunter`：补充事件维度
- `filing-monitor`：拉公告全文

## 合规

输出统一使用 `reference-data/compliance-templates.md` 中的话术。
