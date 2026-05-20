#!/usr/bin/env python3
"""a-share-services 校验脚本。

校验内容：
1. 每个 plugin.json 合法（含 name / version / description）
2. agent-plugins/<slug>/agents/<slug>.md 存在
3. agent.yaml 引用的 system.file / skills.path 路径解析得到
4. agent-plugins/<slug>/skills/ 的 bundled 副本与 vertical-plugins 源一致
5. marketplace.json 引用的 source 目录存在
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None

ROOT = Path(__file__).resolve().parents[1]
PLUGINS = ROOT / "plugins"
COOKBOOKS = ROOT / "managed-agent-cookbooks"
MARKETPLACE = ROOT / ".claude-plugin" / "marketplace.json"

errors: list[str] = []


def fail(msg: str) -> None:
    errors.append(msg)


# 1) plugin.json
plugin_jsons = list(PLUGINS.glob("**/.claude-plugin/plugin.json"))
for p in plugin_jsons:
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:
        fail(f"{p}: invalid JSON: {e}")
        continue
    for key in ("name", "version", "description"):
        if key not in d:
            fail(f"{p}: missing key {key!r}")

# 2) agents/<slug>.md
for plugin in (PLUGINS / "agent-plugins").iterdir():
    if not plugin.is_dir():
        continue
    slug = plugin.name
    agent_md = plugin / "agents" / f"{slug}.md"
    if not agent_md.exists():
        fail(f"agent-plugins/{slug}: missing agents/{slug}.md")

# 3) agent.yaml refs
if COOKBOOKS.exists() and yaml is not None:
    for cb in COOKBOOKS.iterdir():
        if not cb.is_dir():
            continue
        yfile = cb / "agent.yaml"
        if not yfile.exists():
            continue
        try:
            data = yaml.safe_load(yfile.read_text(encoding="utf-8"))
        except Exception as e:
            fail(f"{yfile}: invalid YAML: {e}")
            continue
        sys_file = data.get("system", {}).get("file")
        if sys_file:
            target = (yfile.parent / sys_file).resolve()
            if not target.exists():
                fail(f"{yfile}: system.file not resolved: {sys_file}")
        for s in data.get("skills") or []:
            spath = s.get("path") if isinstance(s, dict) else None
            if spath:
                target = (yfile.parent / spath).resolve()
                if not target.exists():
                    fail(f"{yfile}: skill path not found: {spath}")

# 4) bundled skill consistency
src_by_name = {p.name: p for p in (PLUGINS / "vertical-plugins").glob("*/skills/*") if p.is_dir()}
for bundled in (PLUGINS / "agent-plugins").glob("*/skills/*"):
    if not bundled.is_dir():
        continue
    name = bundled.name
    src = src_by_name.get(name)
    if src is None:
        fail(f"{bundled}: no source in vertical-plugins/*/skills/{name}")
        continue
    src_skill = (src / "SKILL.md").read_text(encoding="utf-8") if (src / "SKILL.md").exists() else ""
    bundled_skill = (bundled / "SKILL.md").read_text(encoding="utf-8") if (bundled / "SKILL.md").exists() else ""
    if src_skill != bundled_skill:
        fail(f"{bundled}/SKILL.md drift from vertical source")

# 5) marketplace.json
if MARKETPLACE.exists():
    try:
        mp = json.loads(MARKETPLACE.read_text(encoding="utf-8"))
    except Exception as e:
        fail(f"{MARKETPLACE}: invalid JSON: {e}")
    else:
        for p in mp.get("plugins", []):
            src = ROOT / p["source"].lstrip("./")
            if not src.exists():
                fail(f"marketplace.json: {p['name']} source not found: {p['source']}")

# Summary
total = sum([
    len(plugin_jsons),
    sum(1 for _ in (PLUGINS / "agent-plugins").glob("*/agents/*.md")),
    sum(1 for _ in (PLUGINS / "agent-plugins").glob("*/skills/*/SKILL.md")),
    sum(1 for _ in (PLUGINS / "vertical-plugins").glob("*/skills/*/SKILL.md")),
])

if errors:
    print(f"FAIL — {len(errors)} issue(s):")
    for e in errors:
        print(f"  {e}")
    sys.exit(1)
print(f"OK — {total} file(s) checked, 0 issues.")
