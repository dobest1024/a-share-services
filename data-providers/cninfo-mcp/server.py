"""
cninfo-mcp · 巨潮资讯网公告 MCP server

巨潮资讯（cninfo.com.cn）是 A 股上市公司公告的官方披露平台。本 server 暴露公告检索与 PDF
文本抽取能力。

⚠️ 法律提醒：cninfo 没有公开 API。当前实现走其公开网页查询接口，仅供研究/开发使用。
生产部署前请评估法务风险或与巨潮申请正式数据合作。

依赖：
    pip install mcp httpx pypdf
"""

from __future__ import annotations

import io
from datetime import datetime
from typing import Any

try:
    from mcp.server.fastmcp import FastMCP
except ImportError as e:
    raise SystemExit("请先安装 mcp: pip install mcp") from e

try:
    import httpx
except ImportError as e:
    raise SystemExit("请先安装 httpx: pip install httpx") from e


mcp = FastMCP("cninfo")

CNINFO_QUERY_URL = "http://www.cninfo.com.cn/new/hisAnnouncement/query"

# 公告分类（巨潮枚举码）
CATEGORY_MAP = {
    "annual_report": "category_ndbg_szsh",
    "interim_report": "category_bndbg_szsh",
    "q3_report": "category_sjdbg_szsh",
    "q1_report": "category_yjdbg_szsh",
    "earnings_preview": "category_yjygjxz_szsh",
    "earnings_express": "category_yjkb_szsh",
    "repurchase": "category_hgjg_szsh",
    "reduction": "category_jcjh_szsh",
    "increase": "category_zjjh_szsh",
    "regulatory_letter": "category_jgcfgg_szsh",
    "restructuring": "category_zjzc_szsh",
}


@mcp.tool()
def filings_list(stock_code: str, start_date: str, end_date: str, category: str | None = None) -> dict[str, Any]:
    """检索某股票在指定时间段内的公告。

    Args:
        stock_code: 6 位代码（如 "600519"）
        start_date: 起始日期 YYYY-MM-DD
        end_date: 截止日期 YYYY-MM-DD
        category: 公告分类筛选键（annual_report / earnings_preview / regulatory_letter / ...）

    Returns:
        {"filings": [{"title": ..., "ann_date": ..., "url": ..., "category": ...}]}
    """
    plate = "sh" if stock_code.startswith(("60", "68")) else "sz"
    payload = {
        "stock": f"{stock_code},{plate}",
        "tabName": "fulltext",
        "pageSize": 30,
        "pageNum": 1,
        "column": plate,
        "category": CATEGORY_MAP.get(category, "") if category else "",
        "seDate": f"{start_date}~{end_date}",
        "isHLtitle": "true",
    }
    try:
        r = httpx.post(CNINFO_QUERY_URL, data=payload, timeout=15.0)
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        return {"filings": [], "error": str(e)}

    filings = []
    for ann in data.get("announcements") or []:
        ts = ann.get("announcementTime")
        d = datetime.fromtimestamp(ts / 1000).strftime("%Y-%m-%d") if ts else ""
        filings.append({
            "title": ann.get("announcementTitle"),
            "ann_date": d,
            "url": f"http://static.cninfo.com.cn/{ann.get('adjunctUrl')}",
            "category": category or "all",
        })
    return {"filings": filings, "count": len(filings)}


@mcp.tool()
def filing_text(url: str, max_pages: int = 20) -> dict[str, Any]:
    """下载公告 PDF 并抽取文本。

    Args:
        url: PDF 链接
        max_pages: 最多抽取页数（避免超大年报）
    """
    try:
        from pypdf import PdfReader
    except ImportError:
        return {"error": "pypdf not installed, run: pip install pypdf"}

    try:
        r = httpx.get(url, timeout=30.0)
        r.raise_for_status()
        reader = PdfReader(io.BytesIO(r.content))
        n = min(len(reader.pages), max_pages)
        text = "\n".join(reader.pages[i].extract_text() or "" for i in range(n))
        return {"text": text, "pages_read": n, "total_pages": len(reader.pages)}
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    mcp.run()
