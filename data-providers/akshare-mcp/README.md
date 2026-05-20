# akshare-mcp

A 股开源数据的 MCP server。包装 [akshare](https://akshare.akfamily.xyz/)，按 namespace 暴露常用接口。

## 安装

```bash
pip install mcp akshare pandas
```

## 启动

由 Claude Code 通过 `.mcp.json` 自动以 stdio 方式调起。手动测试：

```bash
python3 server.py
```

## 当前 tool（Phase 0）

| Tool | 说明 |
|---|---|
| `stock_code_lookup` | 名称/代码 → 标准化代码（`600519.SH`） |
| `stock_daily` | 个股日线行情（含复权） |

## Phase 1 待补

- `stock`: profile / holders / valuation / index
- `fundamental`: income / balance / cashflow / earnings_preview
- `fund_flow`: dragon_tiger / northbound / margin / block_trade
- `event`: unlock_calendar / repurchase / reduction
- `macro`: gdp / cpi / pmi / interest_rate
- `news`: stock_news / research_report / irm

## 注意

akshare 数据源不稳定，生产环境需用 `tushare-mcp` 兜底。建议双源校验关键指标。
