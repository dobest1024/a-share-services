# Claude for A 股市场

面向 A 股市场的 Claude 服务参考实现 — 个股研究、行业研究、事件驱动、政策主题、量化因子、买方组合、投顾合规。

> [!IMPORTANT]
> 本仓库提供的 agent 与 skill 仅为**分析辅助工具**，输出的所有内容**不构成任何投资建议**。所有结论需由具备相应资质的专业人士复核。使用者需自行遵守中国证监会、交易所及相关法律法规。

## 它是什么

`anthropics/financial-services` 的 A 股本地化版本。复用其"一份源 + 双发"（Cowork 插件 + Claude Managed Agent）机制，但**数据源、估值惯例、监管语境、行业分类、agent 工作流**全部按 A 股市场重写。

## 11 个 Agent

| 用户 | Agent | 用途 |
|---|---|---|
| 卖方研究 | **stock-researcher** | 个股研究 - 季报/中报/年报 + 业绩预告/快报，输出研究框架 |
| | **sector-researcher** | 行业综述 - 申万一级 + 政策维度 |
| | **morning-meeting-host** | 晨会纪要 - 卖方/买方两版 |
| 买方 / 量化 | **quant-factor-builder** | 因子构造、检验、合成、回测对接 qlib / backtrader |
| | **nav-pricer** | 公募/私募净值核算与估值复核 |
| 事件驱动 | **event-hunter** | 龙虎榜 / 北向 / 两融 / 解禁 / 业绩预告 / 监管函综合扫描 |
| | **filing-monitor** | 公告与监管文书监控，分级告警 |
| | **irm-watcher** | 上证 e 互动 / 深交所互动易回复监控 |
| 政策研究 | **policy-analyst** | 政策文件 → 受益主题 / 行业 / 公司映射 |
| 投顾 (持牌) | **advisor-meeting-prep** | 客户会议简报 |
| | **investor-suitability** | 投资者适当性管理 |

## 9 个 Vertical Plugin

`a-share-core` · `sell-side-research` · `buy-side-pm` · `quant-research` · `event-driven` · `policy-themes` · `retail-advisory` · `nav-ops` · `compliance-ops`

共 **38 个 skill**，覆盖 A 股本地化的估值、财务质量、行业分类、因子库、事件分析、政策解读、投顾合规等领域。

## 20 个 Slash 命令

| 命令 | 用途 |
|---|---|
| `/a-share-comps` `/a-share-dcf` `/a-share-quality` | 估值与财务质量扫描 |
| `/earnings` `/sector` `/morning` `/catalysts` `/screen` | 研究 |
| `/dragon-tiger` `/northbound` `/event-scan` | 事件驱动 |
| `/policy` `/theme` | 政策与主题 |
| `/factor-test` `/backtest` | 量化 |
| `/ic-memo` | 投资决策备忘 |
| `/client-prep` `/dca` | 投顾 |
| `/nav-review` `/suitability` | 合规与运营 |

## 数据基础设施（自建 MCP）

| Server | 说明 |
|---|---|
| `data-providers/akshare-mcp/` | 开源数据起步主力（25+ tools, namespace: stock / fundamental / fund_flow / event / macro / index） |
| `data-providers/tushare-mcp/` | 付费稳定数据兜底（财务因子、申万分类、指数成分） |
| `data-providers/cninfo-mcp/` | 巨潮公告检索 + PDF 文本抽取（含法律提醒） |

## 仓库结构

```
a-share-services/
├── plugins/
│   ├── agent-plugins/            # 11 个命名 agent
│   ├── vertical-plugins/         # 9 个垂直插件
│   └── partner-built/            # 留位：Wind / 同花顺 / Choice 商业数据
├── managed-agent-cookbooks/      # 11 份 CMA 部署模板
├── data-providers/               # 3 个自建 MCP server
├── reference-data/               # 行业分类映射、合规话术、政策主题词表
├── scripts/                      # check.py · sync-agent-skills.py
└── .claude-plugin/marketplace.json
```

## 安装

```bash
# 从 GitHub 添加 marketplace
claude plugin marketplace add dobest1024/a-share-services

# 或本地开发时
# claude plugin marketplace add /path/to/a-share-services

# 核心 + 必装
claude plugin install a-share-core@claude-for-a-share

# 按需安装垂直
claude plugin install sell-side-research@claude-for-a-share
claude plugin install quant-research@claude-for-a-share
claude plugin install event-driven@claude-for-a-share

# 命名 agent
claude plugin install stock-researcher@claude-for-a-share
claude plugin install event-hunter@claude-for-a-share
```

## Managed Agent 部署

```bash
export ANTHROPIC_API_KEY=sk-ant-...
export TUSHARE_TOKEN=...  # Tushare Pro 数据 token
../scripts/deploy-managed-agent.sh stock-researcher
```

## 开发约定

- **Skills 源**在 `plugins/vertical-plugins/<vertical>/skills/`。编辑后：

  ```bash
  python3 scripts/sync-agent-skills.py
  ```

- **校验**：

  ```bash
  python3 scripts/check.py
  ```

- **Agent 系统 prompt** 在 `plugins/agent-plugins/<slug>/agents/<slug>.md`，被 Cowork 插件和 Managed Agent cookbook 共同引用。
- **合规话术** 集中在 `reference-data/compliance-templates.md`，所有 agent 输出必须使用。

## 合规边界

| 用户 | 业务边界 |
|---|---|
| 量化 / 自研 | 因子研究、回测、信号生成 — 实盘前自行评估冲击成本与合规 |
| 买方持牌机构 | 组合管理、风险归因、IC memo — 输出经合规审核后内部使用 |
| 卖方研究所 | 研报底稿生成 — 必须经合规与质控人工审核后才能对外发布 |
| 持牌投顾 | `retail-advisory` 仅对持牌机构开放，输出仅为大类配置框架，不指定个股权重 |
| 个人投资者 | 个人用户使用本仓库 agent 须自行判断；agent 输出不构成投资建议 |

## 设计方案

完整方案见 [`../claudedocs/a-share-adaptation-plan.md`](../claudedocs/a-share-adaptation-plan.md)。
