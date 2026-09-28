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


def catalog_block(ar=False, prefix="skills/"):
    out = []
    for st in stages:
        title = f"### {st['icon']} [{st['name']}]({prefix}{st['id']}/{'README.ar.md' if ar else ''})"
        if ar:
            title += f" · {st['name_ar']}"
        out += [title, "", st["summary_ar"] if ar else st["summary"], "", *table_header(ar)]
        for s in st["skills"]:
            if s["status"] == "available":
                page = f"{prefix}{st['id']}/{s['slug']}/" + ("README.ar.md" if ar else "")
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


def featured_block(ar=False):
    lang = "ar" if ar else "en"
    out = []
    for st in stages:
        for s in st["skills"]:
            if s["status"] != "available":
                continue
            page = f"skills/{st['id']}/{s['slug']}/" + ("README.ar.md" if ar else "")
            hero = ROOT / "docs" / s["slug"] / f"hero-{lang}.svg"
            desc = s["desc_ar"] if ar else s["desc"]
            if hero.exists():
                out.append(f'<a href="{page}"><img src="docs/{s["slug"]}/hero-{lang}.svg" alt="{s["name"]} — {desc}" width="100%"></a>')
                out.append("")
            out.append(f'<p align="center"><a href="{DL}/{s["slug"]}.zip"><img src="docs/assets/btn-download-{lang}.svg" alt="Download" height="48"></a>&nbsp;&nbsp;'
                       f'<a href="{page}"><img src="docs/assets/btn-more-{lang}.svg" alt="How it works" height="48"></a></p>')
            out.append("")
    return "\n".join(out)


def stages_block(ar=False):
    lang = "ar" if ar else "en"
    cells = [f'<td width="50%"><a href="skills/{st["id"]}/{"README.ar.md" if ar else ""}"><img src="docs/assets/stages/{st["id"]}-{lang}.svg" alt="{st["name"]}" width="100%"></a></td>' for st in stages]
    if len(cells) % 2:
        cells.append('<td width="50%"></td>')
    rows = "\n".join(f"<tr>\n{cells[i]}\n{cells[i + 1]}\n</tr>" for i in range(0, len(cells), 2))
    table = f"<table>\n{rows}\n</table>"
    return f'<div dir="rtl">\n\n{table}\n\n</div>\n' if ar else table + "\n"


def all_skills_page(ar=False):
    if ar:
        head = ['<p dir="rtl"><a href="../README.ar.md">→ الصفحة الرئيسية</a></p>', "", "# كل الـ Skills", "",
                '<div dir="rtl">', "", "كل الـ Skills مترتبة بمراحل الـ Content Creation OS. الـ **Free** مفتوحة هنا، والـ **🔒 Pro** جزء من [Content Creation OS Pro](../course/README.ar.md).", "", "</div>", ""]
    else:
        head = ["[← Home](../README.md)", "", "# All skills", "",
                "Every skill, grouped by stage of the Content Creation OS. **Free** skills are open here; **🔒 Pro** skills ship with [Content Creation OS Pro](../course/).", ""]
    return lang_toggle(ar).replace("../../docs", "../docs") + "\n".join(head) + "\n" + catalog_block(ar, prefix="")


for st in stages:
    d = ROOT / "skills" / st["id"]
    d.mkdir(parents=True, exist_ok=True)
    (d / "README.md").write_text(lang_toggle() + stage_page(st), encoding="utf-8")
    (d / "README.ar.md").write_text(lang_toggle(True) + stage_page(st, ar=True), encoding="utf-8")

(ROOT / "skills" / "README.md").write_text(all_skills_page(), encoding="utf-8")
(ROOT / "skills" / "README.ar.md").write_text(all_skills_page(True), encoding="utf-8")

available = sum(1 for st in stages for s in st["skills"] if s["status"] == "available")
blocks = {"featured": featured_block, "stages": stages_block, "catalog": catalog_block}
for name, ar in (("README.md", False), ("README.ar.md", True)):
    p = ROOT / name
    text = p.read_text(encoding="utf-8")
    for key, fn in blocks.items():
        text = re.sub(
            rf"(<!-- {key}:start -->\n).*?(<!-- {key}:end -->)",
            lambda m: m.group(1) + "\n" + fn(ar) + "\n" + m.group(2),
            text,
            flags=re.S,
        )
    text = re.sub(r"badge/skills-\d+", f"badge/skills-{available}", text)
    p.write_text(text, encoding="utf-8")

print(f"catalog built: {len(stages)} stages, {available} available skill(s)")
