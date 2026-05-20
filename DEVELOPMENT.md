# 开发指南

逐目录、逐文件解释 `a-share-services/` 里每个东西**是什么、怎么动**。

---

## 顶层目录

```
a-share-services/
├── .claude-plugin/        # 仓库级 marketplace 配置
├── .gitignore             # Git 忽略规则（__pycache__/ / .env / .DS_Store 等）
├── README.md              # 用户视角的介绍（功能 / 安装 / 使用）
├── DEVELOPMENT.md         # 本文件 —— 开发者视角
├── plugins/               # 所有 Claude Code 插件
│   ├── agent-plugins/     # 命名 agent（端到端工作流，含完整 system prompt）
│   ├── vertical-plugins/  # 垂直插件（skill + command + MCP 的集合）
│   └── partner-built/     # 留位 —— 给商业数据合作方（Wind / 同花顺）
├── managed-agent-cookbooks/ # Claude Managed Agent API 的部署模板
├── data-providers/        # 自建 MCP server（数据接入层）
├── reference-data/        # 跨插件共享的静态数据
└── scripts/               # 维护脚本（check.py / sync-agent-skills.py）
```

**两种交付形态共享一份源**：
- 一个 agent 既是 `plugins/agent-plugins/<slug>/`（Cowork / Claude Code 插件），也是 `managed-agent-cookbooks/<slug>/`（API 部署）。
- 两者都引用同一份 `agents/<slug>.md` 作为 system prompt，所以改 prompt 只改一处。

---

## `.claude-plugin/marketplace.json`

仓库根的"插件商店清单"。Claude Code `claude plugin marketplace add dobest1024/a-share-services` 时读这个文件，看仓库里有哪些可安装的插件。

```json
{
  "name": "claude-for-a-share",        // marketplace 标识符
  "owner": { "name": "...", "url": "..." },
  "plugins": [
    {
      "name": "a-share-core",
      "source": "./plugins/vertical-plugins/a-share-core",
      "description": "..."
    },
    ...
  ]
}
```

**何时改**：新增 / 删除一个插件时，必须同步更新这里的 `plugins[]` 数组。`source` 是相对仓库根的路径。

---

## `plugins/agent-plugins/<slug>/`

一个命名 agent。例：`stock-researcher`、`event-hunter`。

每个 agent 的目录长这样：

```
<slug>/
├── .claude-plugin/
│   └── plugin.json        # 插件元数据
├── agents/
│   └── <slug>.md          # ⭐ 该 agent 的完整 system prompt（核心文件）
└── skills/                # 该 agent 引用的 skill 副本（由 sync 脚本生成）
    ├── financial-quality-check/
    │   └── SKILL.md
    └── ...
```

### `.claude-plugin/plugin.json`

```json
{
  "name": "stock-researcher",
  "version": "0.0.1",
  "description": "个股研究 - 季报/中报/年报联动业绩预告/快报",
  "author": { "name": "dobest1024", "url": "https://github.com/dobest1024/a-share-services" }
}
```

`version` 在每次发改动时手动 bump（patch），用户安装更新时 Claude Code 看版本号决定是否拉新。

### `agents/<slug>.md` ⭐

**最重要的文件**。这是 agent 启动后注入到 Claude 的 system prompt。结构上一般包含：

```markdown
# Agent 名 · 一句话角色

## 角色
（agent 是谁、解决什么问题、给谁用）

## 核心约束
（合规底线 / 不可做的事 / 必须做的事 —— 例如"非投资建议"、"数据可追溯"）

## 工作流
（step 1 / step 2 / ... —— agent 应该按什么顺序调用 skill 和 MCP）

## 引用 Skills
（列出该 agent 用到的 skill，便于 sync-agent-skills.py 维护映射）

## 引用 MCP
（声明该 agent 依赖哪些 MCP server）

## 输出末尾固定
（合规免责模板的引用）
```

**改这个文件 = 改 agent 的行为**。Cowork 插件运行时和 Managed Agent API 部署时都读这同一份。

### `skills/` 子目录

**不要手动编辑这里**。这是 `vertical-plugins/<v>/skills/<s>/` 的副本，由 `scripts/sync-agent-skills.py` 复制过来。

为什么要复制？因为：
- 插件是自包含的：用户只装 `stock-researcher` 而不装 `a-share-core` 时，agent 仍要能用 skill
- Cowork / Managed Agent 部署时按目录打包，跨插件引用不可靠

**`check.py` 会校验副本与源是否一致**。漂移即报错。

---

## `plugins/vertical-plugins/<vertical>/`

垂直插件，按业务条线打包 skill + command + MCP 引用。例：`a-share-core`、`event-driven`、`quant-research`。

```
<vertical>/
├── .claude-plugin/
│   └── plugin.json
├── .mcp.json              # 该垂直插件挂载的 MCP server（仅 a-share-core 有）
├── README.md              # 该垂直插件的简介
├── skills/                # ⭐ skill 源（编辑这里！）
│   ├── <skill-name>/
│   │   └── SKILL.md       # ⭐ skill 定义
│   └── ...
└── commands/              # 用户显式触发的 slash 命令
    ├── earnings.md
    └── ...
```

### `.mcp.json`（仅 `a-share-core/` 有）

```json
{
  "mcpServers": {
    "akshare": {
      "type": "stdio",
      "command": "python3",
      "args": ["${PLUGIN_DIR}/../../../data-providers/akshare-mcp/server.py"]
    },
    "tushare": { ... "env": { "TUSHARE_TOKEN": "${TUSHARE_TOKEN}" } },
    "cninfo":  { ... }
  }
}
```

声明该插件需要启动哪些 MCP server。Claude Code 加载插件时按此自动起 server。`${PLUGIN_DIR}` 由 Claude Code 替换为插件目录。

### `skills/<skill-name>/SKILL.md` ⭐

Skill = 一份 markdown 知识 + 工作流。Claude 在 agent 运行时**自动**根据 SKILL.md 的 `description` 字段判断是否相关、按需调取。

格式：

```markdown
---
name: financial-quality-check
description: A 股财报质量扫描 - 商誉减值、应收账款、关联交易... 当分析个股财务时必触发。
---

# 标题

（详细工作流、表格、清单、输出结构）
```

**`description` 字段决定何时被触发**。写得越具体（"当分析个股财务时必触发"），越能精确激活。

**永远在 `vertical-plugins/<v>/skills/<s>/` 这里编辑 skill**。改完跑：

```bash
python3 scripts/sync-agent-skills.py
```

会把改动同步到所有引用了这个 skill 的 `agent-plugins/*/skills/<s>/`。

### `commands/<command>.md`

用户在 Claude Code 里输入 `/earnings 贵州茅台` 时触发。文件格式：

```markdown
---
description: 季报 / 中报 / 年报分析（含业绩预告 / 快报）
---

# /earnings {标的}

## 工作流
1. ...
2. ...

## 示例
- `/earnings 比亚迪`
```

文件名 = 命令名（去掉 `.md`）。用户调用 `/<plugin>:<command>` 或直接 `/<command>`（如果命名不冲突）。

---

## `managed-agent-cookbooks/<slug>/`

把 agent 部署到 Claude Managed Agent API（headless 服务化）的模板。与 `agent-plugins/<slug>/` 一一对应。

```
<slug>/
├── agent.yaml      # ⭐ 部署描述
├── README.md       # 部署说明 / 安全等级
└── subagents/      # 子 agent（当前为空，留位给 callable_agents 多层编排）
```

### `agent.yaml` ⭐

```yaml
name: stock-researcher
description: A 股个股研究 agent
system:
  file: ../../plugins/agent-plugins/stock-researcher/agents/stock-researcher.md
  # ↑ 指向插件目录下的 system prompt —— 两种部署共享一份源
model: claude-opus-4-7
skills:
  - path: ../../plugins/agent-plugins/stock-researcher/skills/financial-quality-check
  - path: ../../plugins/agent-plugins/stock-researcher/skills/comps-analysis
  ...
mcp_servers:
  - name: akshare
    command: python3
    args: [../../data-providers/akshare-mcp/server.py]
callable_agents: []     # 该 agent 可调用的其他 agent
security_tier: T2       # T1/T2/T3 安全等级
```

**`security_tier`**：
- **T1** — 低风险，可直接对外
- **T2** — 输出需人工复核，不可直接面向终端客户（卖方研究 / 行业分析）
- **T3** — 高敏感（量化实盘 / 投顾业务 / 净值核算），需严格合规

### 部署

```bash
export ANTHROPIC_API_KEY=sk-ant-...
export TUSHARE_TOKEN=...
# 用上层仓库 anthropics/financial-services 的 deploy-managed-agent.sh
# 或自己写部署脚本调 Anthropic /v1/agents
```

---

## `data-providers/<server>/`

自建 MCP server。**这是数据接入层 —— 所有 agent 的数据都从这里来**。

```
<server>/
├── server.py       # ⭐ MCP server 实现
└── README.md       # 该 server 的接口、依赖、限制说明
```

### `akshare-mcp/server.py`

主力数据源（开源、免费、覆盖广，但偶尔反爬）。

按 namespace 切分 tool：
- `stock_*`：行情、profile、持股、估值、新闻、互动平台
- `fundamental_*`：三大报表、业绩预告 / 快报、分红
- `fund_flow_*`：龙虎榜、北向、两融、大宗、涨停池
- `event_*`：解禁、回购、减持
- `macro_*`：CPI / PMI / GDP / 10 年国债
- `index_*` / `sw_*`：指数 / 申万行业分类与估值

新增 tool 时遵循：
```python
@mcp.tool()
def stock_xxx(code: str, ...) -> str:
    """一句话说明。用于：xxx 场景。"""
    df = ak.xxx(...)
    return _df_to_json(df)
```

### `tushare-mcp/server.py`

生产兜底（付费、稳定，需 Tushare Pro Token）。

接口尽量与 `akshare-mcp` 对齐 —— agent 通过参数切换数据源时不改逻辑。

### `cninfo-mcp/server.py`

巨潮公告检索 + PDF 文本抽取。

⚠️ 法律提醒：cninfo 没有公开 API，当前用其公开网页查询接口，**生产前需走正式授权或持牌第三方**。

---

## `reference-data/`

跨插件共享的静态数据。

```
reference-data/
├── industry-map.csv          # 申万 ↔ 中信 ↔ 证监会 ↔ GICS 行业分类映射
├── policy-keywords.yaml      # 政策主题 → 受益申万行业的映射
└── compliance-templates.md   # ⭐ 标准合规话术 / 措辞替换表 / 免责模板
```

### `compliance-templates.md` ⭐

**所有 agent 的输出必须引用本文件的话术**。包含：
- 标准免责声明
- 禁用 / 允许的措辞替换表（如"建议买入"→"关注要点"）
- 个人投资者 / 投顾客户输出额外规则
- 数据引用规范
- 输出末尾固定段落模板

新增 agent 时检查：system prompt 是否引用了本文件的免责段。

### `industry-map.csv`

当前是占位 schema。Phase 1 需要填实。维护原则：按季度更新。

### `policy-keywords.yaml`

主题 → 受益行业映射。`policy-analyst` agent 用这个把政策文件落到行业上。新增主题时在这里增条目。

---

## `scripts/`

```
scripts/
├── check.py              # ⭐ 校验脚本（每次提交前跑）
└── sync-agent-skills.py  # ⭐ skill 同步脚本
```

### `check.py`

校验 5 件事：
1. 所有 `plugin.json` 含 `name / version / description`
2. 每个 `agent-plugins/<slug>/agents/<slug>.md` 存在
3. `agent.yaml` 引用的 `system.file` / `skills.path` 路径都能解析
4. `agent-plugins/*/skills/<s>/SKILL.md` 与 `vertical-plugins/*/skills/<s>/SKILL.md` 内容一致（防漂移）
5. `marketplace.json` 引用的 `source` 目录都存在

提交前必跑：

```bash
python3 scripts/check.py
# OK — 131 file(s) checked, 0 issues.
```

### `sync-agent-skills.py`

把 `vertical-plugins/<v>/skills/<s>/` 复制到所有需要的 `agent-plugins/<a>/skills/<s>/`。

agent → skills 的映射写死在脚本里的 `AGENT_SKILLS` 字典中。新增 agent 或调整 skill 引用时改这个字典。

```bash
python3 scripts/sync-agent-skills.py
# synced 51 skill(s) into agent-plugins/
```

---

## 常见开发场景速查

### 场景 1：改 skill 的内容

```bash
# 1. 编辑源
vim plugins/vertical-plugins/event-driven/skills/dragon-tiger-list/SKILL.md

# 2. 同步到 agent 包
python3 scripts/sync-agent-skills.py

# 3. 校验
python3 scripts/check.py

# 4. bump version（修改的 vertical-plugin 的 plugin.json）
# 5. commit
```

### 场景 2：新增 agent

```bash
# 1. 建目录
mkdir -p plugins/agent-plugins/new-agent/{.claude-plugin,agents,skills}
mkdir -p managed-agent-cookbooks/new-agent/subagents

# 2. 写 system prompt
vim plugins/agent-plugins/new-agent/agents/new-agent.md

# 3. plugin.json
vim plugins/agent-plugins/new-agent/.claude-plugin/plugin.json

# 4. cookbook
vim managed-agent-cookbooks/new-agent/agent.yaml

# 5. 注册到 marketplace
vim .claude-plugin/marketplace.json   # 在 plugins[] 加一项

# 6. 如果该 agent 引用了 skill，在 scripts/sync-agent-skills.py 的 AGENT_SKILLS
#    字典里加映射，然后跑同步
python3 scripts/sync-agent-skills.py

# 7. 校验 + commit
python3 scripts/check.py
```

### 场景 3：新增 skill

```bash
# 1. 在合适的 vertical 下建目录
mkdir plugins/vertical-plugins/event-driven/skills/new-skill

# 2. 写 SKILL.md（注意 frontmatter 的 name / description）
vim plugins/vertical-plugins/event-driven/skills/new-skill/SKILL.md

# 3. 决定哪些 agent 要引用这个 skill，更新 sync 脚本
vim scripts/sync-agent-skills.py   # AGENT_SKILLS 字典

# 4. 同步 + 校验
python3 scripts/sync-agent-skills.py
python3 scripts/check.py
```

### 场景 4：新增 MCP tool

```bash
# 1. 编辑 server.py
vim data-providers/akshare-mcp/server.py
# 加 @mcp.tool() 函数

# 2. 更新 README.md 的 tool 清单
vim data-providers/akshare-mcp/README.md

# 3. 如果需要在 agent 中使用，更新对应的 SKILL.md 或 agent system prompt
```

### 场景 5：新增 slash command

```bash
# 在对应的 vertical 下加 markdown 文件
vim plugins/vertical-plugins/sell-side-research/commands/new-command.md

# frontmatter 描述 + 工作流说明
# 用户输入 /new-command 即触发
```

---

## 关键约定

1. **永远在 `vertical-plugins/<v>/skills/` 编辑 skill 源** —— agent 包里的副本由脚本生成，不要手改。
2. **`agents/<slug>.md` 是 agent 行为的单一真相** —— 改 prompt 只改这一处。
3. **合规话术统一在 `reference-data/compliance-templates.md`** —— 所有 agent 引用这里，不要每个 agent 各写一套免责。
4. **每次改动 plugin 前 bump version** —— `plugin.json` 的 `version` 字段（patch 即可），Claude Code 据此推更新。
5. **`check.py` 必过** —— 否则 CI / 用户安装会出问题。
6. **数据接口对齐** —— `akshare-mcp` 和 `tushare-mcp` 的 tool 签名尽量对齐，方便切换数据源。
7. **agent 安全等级 T2/T3 分级** —— cookbook 的 `security_tier` 字段决定部署后输出是否需要人工 gate。

---

## 文件命名约定

| 元素 | 命名 | 例 |
|---|---|---|
| Vertical / Agent 目录 | `kebab-case` | `sell-side-research/` `stock-researcher/` |
| Skill 目录 | `kebab-case` | `financial-quality-check/` |
| Skill 文件 | `SKILL.md`（固定大写）| — |
| Command 文件 | `kebab-case.md` | `earnings.md` `dragon-tiger.md` |
| MCP tool | `snake_case` | `stock_daily` `fund_flow_dragon_tiger` |
| MCP server 子目录 | `<name>-mcp/` | `akshare-mcp/` |

---

## 调试技巧

### Skill 没被触发？
- 检查 `SKILL.md` frontmatter 的 `description`，加上"当 XXX 时使用"的明确触发条件
- 确认该 skill 在 agent 的 `引用 Skills` 列表里
- 跑 `sync-agent-skills.py` 确保已同步进 agent 包

### MCP tool 没被调用？
- 确认 `.mcp.json` 中 server 已注册
- 检查 `server.py` 的 `@mcp.tool()` 装饰器和函数 docstring（Claude 据此决定何时调用）
- 在终端手动起 server 看是否报错：`python3 data-providers/akshare-mcp/server.py`

### check.py 报错？
- "missing key X"：补 `plugin.json` 字段
- "skill path not found"：跑 `sync-agent-skills.py`
- "drift from vertical source"：bundled 副本与源不一致，跑 `sync-agent-skills.py` 重新同步

---

## 路线图

参考 [`../claudedocs/a-share-adaptation-plan.md`](../claudedocs/a-share-adaptation-plan.md)。

当前完成 Phase 0-4 全部骨架与 skill 内容。后续重点：
- akshare-mcp 在反爬时切 tushare-mcp 的鲁棒性测试
- cninfo 数据合规路径决策
- 实际跑 stock-researcher / event-hunter 端到端，根据输出迭代 skill 话术
- 行业分类映射表 `industry-map.csv` 填实
- 量化回测框架选型（qlib / backtrader / vnpy）落地
