"""
akshare-mcp · A 股开源数据 MCP server

按 namespace 暴露 akshare 的常用接口：stock / fundamental / fund_flow / event / macro / news。

依赖：
    pip install mcp akshare pandas

启动（stdio 模式，由 Claude Code 通过 .mcp.json 自动调起）：
    python3 server.py

⚠️ akshare 数据源不稳定，生产环境用 tushare-mcp 兜底。
"""

from __future__ import annotations

import json
from typing import Any

try:
    from mcp.server.fastmcp import FastMCP
except ImportError as e:
    raise SystemExit("请先安装 mcp: pip install mcp") from e

try:
    import akshare as ak
except ImportError as e:
    raise SystemExit("请先安装 akshare: pip install akshare") from e


mcp = FastMCP("akshare")


def _df_to_json(df) -> str:
    if df is None or df.empty:
        return '{"error": "no data"}'
    return df.to_json(orient="records", force_ascii=False, date_format="iso")


# ============== stock namespace ==============

@mcp.tool()
def stock_code_lookup(query: str) -> dict[str, Any]:
    """名称/代码 → 标准化代码 (`<6 位>.<SH/SZ/BJ>`)，附板块识别。

    Args:
        query: 公司名称或代码片段（"贵州茅台" / "600519" / "000001"）
    """
    df = ak.stock_info_a_code_name()
    q = query.strip()
    if q.isdigit():
        hit = df[df["code"] == q.zfill(6)]
    else:
        hit = df[df["name"].str.contains(q, na=False)]
    if hit.empty:
        return {"error": f"未找到匹配 {query!r} 的 A 股标的"}
    row = hit.iloc[0]
    code = str(row["code"]).zfill(6)
    exchange = "SH" if code.startswith(("60", "68", "9")) else "BJ" if code.startswith(("4", "8")) else "SZ"
    board = (
        "star" if code.startswith("688") else
        "chinext" if code.startswith("30") else
        "beijing" if exchange == "BJ" else
        "main"
    )
    limit = 0.20 if board in ("star", "chinext") else 0.30 if board == "beijing" else 0.10
    return {
        "code": f"{code}.{exchange}",
        "raw_code": code,
        "name": str(row["name"]),
        "exchange": exchange,
        "board": board,
        "price_limit": limit,
    }


@mcp.tool()
def stock_daily(code: str, start_date: str, end_date: str, adjust: str = "qfq") -> str:
    """个股日线行情。

    Args:
        code: 6 位代码
        start_date: 起始 YYYYMMDD
        end_date: 截止 YYYYMMDD
        adjust: "qfq" 前复权 / "hfq" 后复权 / "" 不复权
    """
    df = ak.stock_zh_a_hist(symbol=code, period="daily", start_date=start_date, end_date=end_date, adjust=adjust)
    return _df_to_json(df)


@mcp.tool()
def stock_profile(code: str) -> str:
    """公司简介、所属行业、上市日期、总股本、流通股本。"""
    df = ak.stock_individual_info_em(symbol=code)
    return _df_to_json(df)


@mcp.tool()
def stock_holders(code: str) -> str:
    """主要股东与近期变动（前十大流通股东）。"""
    df = ak.stock_circulate_stock_holder(symbol=code)
    return _df_to_json(df)


@mcp.tool()
def stock_valuation(code: str) -> dict[str, Any]:
    """PE-TTM / PB / PS / 股息率 + 历史分位。"""
    try:
        pe_df = ak.stock_a_pe(symbol=code)
        latest = pe_df.iloc[-1].to_dict() if not pe_df.empty else {}
        return {"code": code, "latest": latest}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def stock_news(code: str) -> str:
    """个股相关新闻（近期）。"""
    df = ak.stock_news_em(symbol=code)
    return _df_to_json(df)


@mcp.tool()
def stock_irm_qa(code: str) -> str:
    """互动平台问答（深交所互动易）。"""
    try:
        df = ak.stock_irm_cninfo(symbol=code)
        return _df_to_json(df)
    except Exception as e:
        return json.dumps({"error": str(e)})


# ============== fundamental namespace ==============

@mcp.tool()
def fundamental_income(code: str) -> str:
    """利润表（近 5 期）。"""
    df = ak.stock_financial_report_sina(stock=code, symbol="利润表")
    return _df_to_json(df)


@mcp.tool()
def fundamental_balance(code: str) -> str:
    """资产负债表（近 5 期）。"""
    df = ak.stock_financial_report_sina(stock=code, symbol="资产负债表")
    return _df_to_json(df)


@mcp.tool()
def fundamental_cashflow(code: str) -> str:
    """现金流量表（近 5 期）。"""
    df = ak.stock_financial_report_sina(stock=code, symbol="现金流量表")
    return _df_to_json(df)


@mcp.tool()
def fundamental_earnings_preview(year: str = "2024") -> str:
    """业绩预告（年度，全市场）。

    Args:
        year: 年份，如 "2024"
    """
    df = ak.stock_yjyg_em(date=f"{year}1231")
    return _df_to_json(df)


@mcp.tool()
def fundamental_earnings_express(year: str = "2024") -> str:
    """业绩快报（年度，全市场）。"""
    df = ak.stock_yjkb_em(date=f"{year}1231")
    return _df_to_json(df)


@mcp.tool()
def fundamental_dividend_history(code: str) -> str:
    """分红历史。"""
    df = ak.stock_history_dividend_detail(symbol=code, indicator="分红")
    return _df_to_json(df)


# ============== fund_flow namespace ==============

@mcp.tool()
def fund_flow_dragon_tiger(date: str) -> str:
    """当日龙虎榜（全市场）。

    Args:
        date: YYYYMMDD
    """
    df = ak.stock_lhb_detail_em(start_date=date, end_date=date)
    return _df_to_json(df)


@mcp.tool()
def fund_flow_northbound_top10() -> str:
    """北向资金 Top 10 活跃股（当日）。"""
    try:
        df = ak.stock_hsgt_north_net_flow_in_em(symbol="沪股通")
        return _df_to_json(df)
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
def fund_flow_northbound_holdings(code: str) -> str:
    """个股北向持股历史。"""
    try:
        df = ak.stock_hsgt_individual_em(stock=code)
        return _df_to_json(df)
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
def fund_flow_margin_stock(code: str) -> str:
    """个股融资融券余额历史。"""
    exchange = "sh" if code.startswith(("60", "68")) else "sz"
    df = ak.stock_margin_detail_szse(symbol=code) if exchange == "sz" else ak.stock_margin_detail_sse(symbol=code)
    return _df_to_json(df)


@mcp.tool()
def fund_flow_block_trade(date: str) -> str:
    """当日大宗交易（全市场）。"""
    df = ak.stock_dzjy_sctj()
    return _df_to_json(df)


@mcp.tool()
def fund_flow_limit_up_pool(date: str) -> str:
    """当日涨停股池。"""
    df = ak.stock_zt_pool_em(date=date)
    return _df_to_json(df)


# ============== event namespace ==============

@mcp.tool()
def event_unlock_calendar(start_date: str, end_date: str) -> str:
    """限售解禁日历。

    Args:
        start_date: YYYYMMDD
        end_date: YYYYMMDD
    """
    df = ak.stock_restricted_release_queue_em()
    return _df_to_json(df)


@mcp.tool()
def event_repurchase() -> str:
    """全市场近期回购公告。"""
    df = ak.stock_repurchase_em()
    return _df_to_json(df)


@mcp.tool()
def event_reduction(code: str | None = None) -> str:
    """股东减持公告（可指定个股）。"""
    df = ak.stock_share_change_cninfo() if code is None else ak.stock_share_hold_change_bse(symbol=code)
    return _df_to_json(df)


# ============== macro namespace ==============

@mcp.tool()
def macro_cpi() -> str:
    """CPI 历史。"""
    df = ak.macro_china_cpi()
    return _df_to_json(df)


@mcp.tool()
def macro_pmi() -> str:
    """PMI 历史。"""
    df = ak.macro_china_pmi()
    return _df_to_json(df)


@mcp.tool()
def macro_gdp() -> str:
    """GDP 历史。"""
    df = ak.macro_china_gdp()
    return _df_to_json(df)


@mcp.tool()
def macro_bond_yield_10y() -> str:
    """10 年期国债收益率（DCF 估值用）。"""
    df = ak.bond_china_yield()
    return _df_to_json(df)


# ============== index namespace ==============

@mcp.tool()
def index_daily(code: str, start_date: str, end_date: str) -> str:
    """指数日线（沪深 300 / 中证 500 / 中证 1000 / 创业板指等）。

    Args:
        code: "000300" 沪深300 / "000905" 中证500 / "000852" 中证1000 / "399006" 创业板指 / "000688" 科创50
    """
    df = ak.stock_zh_index_daily(symbol=code)
    return _df_to_json(df)


@mcp.tool()
def sw_industry_list(level: int = 1) -> str:
    """申万行业列表。

    Args:
        level: 1 一级 / 2 二级 / 3 三级
    """
    if level == 1:
        df = ak.sw_index_first_info()
    elif level == 2:
        df = ak.sw_index_second_info()
    else:
        df = ak.sw_index_third_info()
    return _df_to_json(df)


@mcp.tool()
def sw_index_valuation(code: str) -> str:
    """申万行业指数估值（PE / PB / 股息率）。"""
    df = ak.sw_index_daily_indicator(symbol=code)
    return _df_to_json(df)


if __name__ == "__main__":
    mcp.run()
