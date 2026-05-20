# tushare-mcp

Tushare Pro 数据的 MCP server。作为 `akshare-mcp` 的生产兜底数据源。

## 配置

需要 [Tushare Pro](https://tushare.pro/) 账号与积分。设置环境变量：

```bash
export TUSHARE_TOKEN=<你的 token>
```

## 安装

```bash
pip install mcp tushare pandas
```

## 设计原则

**接口与 `akshare-mcp` 对齐**，调用方在配置层切换数据源即可，不改 agent 逻辑。

## Phase 1 重点

- 高质量财务因子（`fina_indicator`）—— Tushare 已清洗，比 akshare 干净
- 申万行业分类全量映射
- 指数成分与权重
