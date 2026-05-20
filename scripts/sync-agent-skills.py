#!/usr/bin/env python3
"""把 vertical-plugins 中的 skills 同步到 agent-plugins/<slug>/skills/。

工作流：
1. 编辑 vertical-plugins/<vertical>/skills/<skill>/SKILL.md
2. 运行 `python3 scripts/sync-agent-skills.py`
3. 提交

每个 agent 引用哪些 skill 在本脚本的 AGENT_SKILLS 字典中维护。
"""
from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGINS = ROOT / "plugins"

AGENT_SKILLS: dict[str, list[str]] = {
    "stock-researcher": [
        "a-share-core/financial-quality-check",
        "a-share-core/industry-classification",
        "a-share-core/market-rules-handbook",
        "a-share-core/comps-analysis",
        "a-share-core/pb-roe-model",
        "event-driven/dragon-tiger-list",
        "event-driven/northbound-flow",
        "event-driven/unlock-calendar",
    ],
    "sector-researcher": [
        "sell-side-research/sector-overview",
        "policy-themes/policy-parser",
        "policy-themes/theme-mapping",
        "a-share-core/industry-classification",
        "a-share-core/comps-analysis",
    ],
    "morning-meeting-host": [
        "sell-side-research/morning-note",
        "sell-side-research/catalyst-calendar",
        "event-driven/dragon-tiger-list",
        "event-driven/northbound-flow",
    ],
    "event-hunter": [
        "event-driven/dragon-tiger-list",
        "event-driven/northbound-flow",
        "event-driven/margin-trading",
        "event-driven/block-trade",
        "event-driven/unlock-calendar",
        "event-driven/regulatory-letter",
        "event-driven/earnings-preview-radar",
        "event-driven/corporate-action",
        "event-driven/limit-up-down-analysis",
    ],
    "policy-analyst": [
        "policy-themes/policy-parser",
        "policy-themes/theme-mapping",
        "policy-themes/policy-calendar",
        "a-share-core/industry-classification",
    ],
    "filing-monitor": [
        "event-driven/regulatory-letter",
        "event-driven/corporate-action",
        "event-driven/earnings-preview-radar",
        "a-share-core/financial-quality-check",
    ],
    "irm-watcher": [],
    "quant-factor-builder": [
        "quant-research/factor-library",
        "quant-research/single-factor-test",
        "quant-research/factor-combination",
        "quant-research/backtest-adapter",
        "quant-research/event-study",
    ],
    "nav-pricer": [
        "nav-ops/nav-calculation",
        "nav-ops/valuation-review",
        "a-share-core/market-rules-handbook",
    ],
    "advisor-meeting-prep": [
        "retail-advisory/client-profiling",
        "retail-advisory/suitability-check",
        "retail-advisory/allocation-framework",
        "retail-advisory/dca-strategy",
        "retail-advisory/monthly-recap",
        "compliance-ops/investor-suitability",
    ],
    "investor-suitability": [
        "retail-advisory/client-profiling",
        "retail-advisory/suitability-check",
        "compliance-ops/investor-suitability",
    ],
}


def main() -> int:
    synced = 0
    missing: list[str] = []
    for agent, skills in AGENT_SKILLS.items():
        target_root = PLUGINS / "agent-plugins" / agent / "skills"
        target_root.mkdir(parents=True, exist_ok=True)
        for s in skills:
            vertical, skill = s.split("/")
            src = PLUGINS / "vertical-plugins" / vertical / "skills" / skill
            dst = target_root / skill
            if not src.is_dir():
                missing.append(f"{agent} → {s} (source not found)")
                continue
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
            synced += 1
    print(f"synced {synced} skill(s) into agent-plugins/")
    if missing:
        for m in missing:
            print(f"  ⚠️ {m}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
