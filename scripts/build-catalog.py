#!/usr/bin/env python3
"""Builds the skill catalog from catalog.json.

Writes skills/<stage>/README.md and README.ar.md, and refreshes the block between
<!-- catalog:start --> and <!-- catalog:end --> in README.md and README.ar.md.
Run it after editing catalog.json.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPO = "https://github.com/adeltechtalks/AdelTechTalks-Claude"
DL = f"{REPO}/raw/main/downloads"

catalog = json.loads((ROOT / "catalog.json").read_text(encoding="utf-8"))
stages = catalog["stages"]


def tier(s, ar=False):
    return "Free" if s["tier"] == "free" else "🔒 Pro"


def lang_toggle(ar=False):
    a = "../../docs/assets/"
    en = f"{a}lang-en-{'off' if ar else 'on'}.svg"
    arb = f"{a}lang-ar-{'on' if ar else 'off'}.svg"
    return (f'<p align="center"><a href="README.md"><img src="{en}" alt="English" height="40"></a>&nbsp;&nbsp;'
            f'<a href="README.ar.md"><img src="{arb}" alt="العربية" height="40"></a></p>\n\n')


def table_header(ar=False):
    if ar:
        return ["| الخطوة | الـ Skill | بتعمل إيه | الـ Tier | تحميل |", "|:-:|:--|:--|:-:|:-:|"]
    return ["| Step | Skill | What it does | Tier | Get it |", "|:-:|:--|:--|:-:|:-:|"]


def stage_page(stage, ar=False):
    rows = []
    for s in stage["skills"]:
        if s["status"] == "available":
            page = f"{s['slug']}/" + ("README.ar.md" if ar else "")
            name = f"**[{s['name']}]({page})**"
            action = f"[**⬇ ZIP**]({DL}/{s['slug']}.zip)"
        else:
            name = f"**{s['name']}**"
            action = "قريباً" if ar else "Soon"
        desc = s["desc_ar"] if ar else s["desc"]
        rows.append(f"| {s.get('step', '—')} | {name} | {desc} | {tier(s, ar)} | {action} |")
    if ar:
        lines = [
            f"# {stage['icon']} {stage['name']} · {stage['name_ar']}",
            "",
            '<p dir="rtl"><a href="../../README.ar.md">→ كل الـ Skills</a></p>',
            "",
            '<div dir="rtl">',
            "",
            stage["summary_ar"],
            "",
            f"**المصدر:** {stage['source']}",
            "",
            *table_header(True),
            *rows,
            "",
            "**Free** مجانية للكل، و **🔒 Pro** جزء من الـ [Content Creation OS Pro](../../course/README.ar.md).",
            "",
            "</div>",
            "",
        ]
    else:
        lines = [
            f"# {stage['icon']} {stage['name']}",
            "",
            "[← All skills](../../README.md)",
            "",
            stage["summary"],
            "",
            f"**Source:** {stage['source']}",
            "",
            *table_header(False),
            *rows,
            "",
            "**Free** skills are open to everyone. **🔒 Pro** skills are part of [Content Creation OS Pro](../../course/README.md).",
            "",
        ]
    return "\n".join(lines)


def catalog_block(ar=False):
    out = []
    for st in stages:
        title = f"### {st['icon']} [{st['name']}](skills/{st['id']}/{'README.ar.md' if ar else ''})"
        if ar:
            title += f" · {st['name_ar']}"
        out += [title, "", st["summary_ar"] if ar else st["summary"], "", *table_header(ar)]
        for s in st["skills"]:
            if s["status"] == "available":
                page = f"skills/{st['id']}/{s['slug']}/" + ("README.ar.md" if ar else "")
                name = f"**[{s['name']}]({page})**"
                action = f"[**⬇ ZIP**]({DL}/{s['slug']}.zip)"
            else:
                name = f"**{s['name']}**"
                action = "قريباً" if ar else "Soon"
            desc = s["desc_ar"] if ar else s["desc"]
            out.append(f"| {s.get('step', '—')} | {name} | {desc} | {tier(s, ar)} | {action} |")
        out.append("")
    body = "\n".join(out).rstrip() + "\n"
    return f'<div dir="rtl">\n\n{body}\n</div>\n' if ar else body


for st in stages:
    d = ROOT / "skills" / st["id"]
    d.mkdir(parents=True, exist_ok=True)
    (d / "README.md").write_text(lang_toggle() + stage_page(st), encoding="utf-8")
    (d / "README.ar.md").write_text(lang_toggle(True) + stage_page(st, ar=True), encoding="utf-8")

available = sum(1 for st in stages for s in st["skills"] if s["status"] == "available")
for name, ar in (("README.md", False), ("README.ar.md", True)):
    p = ROOT / name
    text = p.read_text(encoding="utf-8")
    text = re.sub(
        r"(<!-- catalog:start -->\n).*?(<!-- catalog:end -->)",
        lambda m: m.group(1) + "\n" + catalog_block(ar) + "\n" + m.group(2),
        text,
        flags=re.S,
    )
    text = re.sub(r"badge/skills-\d+", f"badge/skills-{available}", text)
    p.write_text(text, encoding="utf-8")

print(f"catalog built: {len(stages)} stages, {available} available skill(s)")
