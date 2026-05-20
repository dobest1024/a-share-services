# cninfo-mcp

巨潮资讯网（cninfo.com.cn）公告数据的 MCP server。A 股上市公司公告的官方披露平台。

## ⚠️ 法律提醒

巨潮没有开放 API。本仓库的实现方式有三种路径，**生产部署前必须明确选哪一种**：

1. **公开查询接口**（POC 阶段）— 使用 cninfo 公开的网页查询接口。可能违反 ToS，仅供研究开发。
2. **正式数据授权**（生产推荐）— 与巨潮申请数据合作。
3. **第三方持牌数据商**（折中）— 通过同花顺 / Wind / Choice 等持牌商访问公告数据。

当前骨架默认走路径 1，需在配置中显式切换。

## Phase 0 状态

骨架已就位，`filings_list` / `filing_text` 是占位实现。

## Phase 1 实现要点

- 公告检索：`http://www.cninfo.com.cn/new/hisAnnouncement/query`
- 分类映射：监管函 / 问询函 / 业绩预告 / 业绩快报 / 回购 / 减持 / 定增 / 重组
- PDF 下载与文本抽取（pypdf）
- 增量缓存（按公司+日期）
