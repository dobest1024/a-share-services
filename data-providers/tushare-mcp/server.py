"""
tushare-mcp · Tushare Pro 数据 MCP server

作为 akshare-mcp 的生产兜底数据源。重点：清洗过的财务因子、申万/中信行业分类、指数成分。

环境变量：
    TUSHARE_TOKEN  — Tushare Pro token（必填）

依赖：
    pip install mcp tushare pandas
"""

from __future__ import annotations

import os
from typing import Any

try:
    from mcp.server.fastmcp import FastMCP
except ImportError as e:
    raise SystemExit("请先安装 mcp: pip install mcp") from e

try:
    import tushare as ts
except ImportError as e:
    raise SystemExit("请先安装 tushare: pip install tushare") from e


TOKEN = os.environ.get("TUSHARE_TOKEN")
if not TOKEN:
    raise SystemExit("请设置环境变量 TUSHARE_TOKEN")

ts.set_token(TOKEN)
pro = ts.pro_api()

mcp = FastMCP("tushare")


def _df_to_json(df) -> str:
    if df is None or df.empty:
        return '{"error": "no data"}'
    return df.to_json(orient="records", force_ascii=False)


# ============== 基础行情 ==============

@mcp.tool()
def stock_daily(ts_code: str, start_date: str, end_date: str) -> str:
    """个股日线行情（Tushare 高质量数据）。

    Args:
        ts_code: "600519.SH"
        start_date: YYYYMMDD
        end_date: YYYYMMDD
    """
    df = pro.daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
    return _df_to_json(df)


@mcp.tool()
def stock_basic() -> str:
    """A 股全市场股票基本信息（含上市状态、申万行业）。"""
    df = pro.stock_basic(exchange="", list_status="L", fields="ts_code,symbol,name,area,industry,market,list_date")
    return _df_to_json(df)


@mcp.tool()
def stock_daily_basic(ts_code: str, trade_date: str) -> str:
    """每日基本面（PE / PB / PS / 股息率 / 总市值 / 自由流通市值 / 换手率）。

    Args:
        ts_code: "600519.SH"
        trade_date: YYYYMMDD
    """
    df = pro.daily_basic(ts_code=ts_code, trade_date=trade_date)
    return _df_to_json(df)


# ============== 财务因子（核心）==============

@mcp.tool()
def fina_indicator(ts_code: str, period: str = "") -> str:
    """财务指标（Tushare 已清洗，比 akshare 干净）。

    Args:
        ts_code: "600519.SH"
        period: 报告期 YYYYMMDD，留空取全部
    """
    df = pro.fina_indicator(ts_code=ts_code, period=period)
    return _df_to_json(df)


@mcp.tool()
def income_statement(ts_code: str, period: str = "") -> str:
    """利润表。"""
    df = pro.income(ts_code=ts_code, period=period)
    return _df_to_json(df)


@mcp.tool()
def balance_sheet(ts_code: str, period: str = "") -> str:
    """资产负债表。"""
    df = pro.balancesheet(ts_code=ts_code, period=period)
    return _df_to_json(df)


@mcp.tool()
def cashflow_statement(ts_code: str, period: str = "") -> str:
    """现金流量表。"""
    df = pro.cashflow(ts_code=ts_code, period=period)
    return _df_to_json(df)


@mcp.tool()
def forecast(ts_code: str = "", ann_date: str = "") -> str:
    """业绩预告。"""
    df = pro.forecast(ts_code=ts_code, ann_date=ann_date)
    return _df_to_json(df)


@mcp.tool()
def express(ts_code: str = "", ann_date: str = "") -> str:
    """业绩快报。"""
    df = pro.express(ts_code=ts_code, ann_date=ann_date)
    return _df_to_json(df)


# ============== 行业分类 ==============

@mcp.tool()
def sw_industry_classify(level: str = "L1") -> str:
    """申万行业分类。

    Args:
        level: L1 一级 / L2 二级 / L3 三级
    """
    df = pro.index_classify(level=level, src="SW2021")
    return _df_to_json(df)


@mcp.tool()
def sw_industry_members(index_code: str) -> str:
    """申万行业成分股。

    Args:
        index_code: 申万行业指数代码
    """
    df = pro.index_member(index_code=index_code)
    return _df_to_json(df)


# ============== 指数 ==============

@mcp.tool()
def index_daily(ts_code: str, start_date: str, end_date: str) -> str:
    """指数日线（沪深 300 / 中证 500 / 中证 1000）。

    Args:
        ts_code: "000300.SH" / "000905.SH" / "000852.SH"
    """
    df = pro.index_daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
    return _df_to_json(df)


@mcp.tool()
def index_weight(index_code: str, trade_date: str) -> str:
    """指数成分股权重。

    Args:
        index_code: "000300.SH"
        trade_date: YYYYMMDD
    """
    df = pro.index_weight(index_code=index_code, trade_date=trade_date)
    return _df_to_json(df)


# ============== 资金流 ==============

@mcp.tool()
def moneyflow_hsgt(start_date: str, end_date: str) -> str:
    """北向资金每日净买入。"""
    df = pro.moneyflow_hsgt(start_date=start_date, end_date=end_date)
    return _df_to_json(df)


@mcp.tool()
def hk_hold(ts_code: str = "", trade_date: str = "") -> str:
    """沪深港通持股明细（北向持股）。"""
    df = pro.hk_hold(ts_code=ts_code, trade_date=trade_date)
    return _df_to_json(df)


# ============== 一致预期（部分接口需高积分）==============

@mcp.tool()
def consensus_estimate(ts_code: str) -> str:
    """一致预期（卖方分析师汇总）。需 Tushare 高积分账户。"""
    try:
        df = pro.report_rc(ts_code=ts_code)
        return _df_to_json(df)
    except Exception as e:
        return f'{{"error": "{e}"}}'


if __name__ == "__main__":
    mcp.run()
