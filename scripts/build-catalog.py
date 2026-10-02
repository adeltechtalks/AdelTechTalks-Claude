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


def is_out(s):
    """Downloadable: released or still in testing."""
    return s["status"] in ("available", "testing")


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
        if is_out(s):
            page = f"{s['slug']}/" + ("README.ar.md" if ar else "")
            name = f"**[{s['name']}]({page})**"
            action = f"[**⬇ ZIP**]({DL}/{s['slug']}.zip)" + (" · 🧪" if s["status"] == "testing" else "")
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
            if is_out(s):
                page = f"{prefix}{st['id']}/{s['slug']}/" + ("README.ar.md" if ar else "")
                name = f"**[{s['name']}]({page})**"
                action = f"[**⬇ ZIP**]({DL}/{s['slug']}.zip)" + (" · 🧪" if s["status"] == "testing" else "")
            else:
                name = f"**{s['name']}**"
                action = "قريباً" if ar else "Soon"
            desc = s["desc_ar"] if ar else s["desc"]
            out.append(f"| {s.get('step', '—')} | {name} | {desc} | {tier(s, ar)} | {action} |")
        out.append("")
    body = "\n".join(out).rstrip() + "\n"
    return f'<div dir="rtl">\n\n{body}\n</div>\n' if ar else body


def featured_block(ar=False, up="", pages="skills/"):
    lang = "ar" if ar else "en"
    cells = []
    for st in stages:
        for s in st["skills"]:
            if not is_out(s):
                continue
            page = f"{pages}{st['id']}/{s['slug']}/" + ("README.ar.md" if ar else "")
            cells.append(f'<td width="50%" valign="top"><a href="{page}"><img src="{up}docs/assets/skills/{s["slug"]}-{lang}.svg" alt="{s["name"]}" width="100%"></a>'
                         f'<p align="center"><a href="{DL}/{s["slug"]}.zip"><img src="{up}docs/assets/btn-download-{lang}.svg" alt="Download ZIP" height="40"></a>&nbsp;'
                         f'<a href="{page}"><img src="{up}docs/assets/btn-more-{lang}.svg" alt="How it works" height="40"></a></p></td>')
    if len(cells) % 2:
        watch = "https://github.com/adeltechtalks/AdelTechTalks-Claude/subscription"
        cells.append(f'<td width="50%" valign="top"><a href="{watch}"><img src="{up}docs/assets/skills/coming-{lang}.svg" alt="Coming next" width="100%"></a>'
                     f'<p align="center"><a href="{watch}"><img src="{up}docs/assets/btn-watch-{lang}.svg" alt="Get notified" height="40"></a></p></td>')
    rows = "\n".join(f"<tr>\n{cells[i]}\n{cells[i + 1]}\n</tr>" for i in range(0, len(cells), 2))
    table = f"<table>\n{rows}\n</table>"
    return f'<div dir="rtl">\n\n{table}\n\n</div>\n' if ar else table + "\n"


def stages_block(ar=False):
    lang = "ar" if ar else "en"
    cells = [f'<td width="50%"><a href="skills/{st["id"]}/{"README.ar.md" if ar else ""}"><img src="docs/assets/stages/{st["id"]}-{lang}.svg" alt="{st["name"]}" width="100%"></a></td>' for st in stages]
    if len(cells) % 2:
        cells.append('<td width="50%"></td>')
    rows = "\n".join(f"<tr>\n{cells[i]}\n{cells[i + 1]}\n</tr>" for i in range(0, len(cells), 2))
    table = f"<table>\n{rows}\n</table>"
    return f'<div dir="rtl">\n\n{table}\n\n</div>\n' if ar else table + "\n"


def stage_rows(ar=False):
    """Browse page: one row per stage — the stage card next to its skill list."""
    lang = "ar" if ar else "en"
    rows = []
    for st in stages:
        items = []
        for s in st["skills"]:
            ready = is_out(s)
            testing = s["status"] == "testing"
            mark = "🧪" if testing else "✅" if ready else ("🔒" if s["tier"] == "pro" else "⏳")
            name = f'<a href="{st["id"]}/{s["slug"]}/{"README.ar.md" if ar else ""}"><b>{s["name"]}</b></a>' if ready else f"<b>{s['name']}</b>"
            step = f"Step {s['step']} · " if s.get("step") else ""
            tier = "Free" if s["tier"] == "free" else "Pro"
            state = ("تجريبية" if ar else "Testing") if testing else ("جاهزة" if ar else "Ready") if ready else ("قريباً" if ar else "Soon")
            desc = s["desc_ar"] if ar else s["desc"]
            items.append(f"{mark} {name} <sub>· {step}{tier} · {state}</sub><br><sub>{desc}</sub>")
        card = f'<a href="{st["id"]}/{"README.ar.md" if ar else ""}"><img src="../docs/assets/stages/{st["id"]}-{lang}.svg" alt="{st["name"]}" width="100%"></a>'
        body = "<br><br>\n".join(items)
        if ar:
            body = f'<div dir="rtl" align="right">\n{body}\n</div>'
        rows.append(f'<tr>\n<td width="44%" valign="top">{card}</td>\n<td valign="top">\n\n' + body + "\n\n</td>\n</tr>")
    table = "<table>\n" + "\n".join(rows) + "\n</table>"
    return f'<div dir="rtl">\n\n{table}\n\n</div>\n' if ar else table + "\n"


def all_skills_page(ar=False):
    lang = "ar" if ar else "en"
    toggle = lang_toggle(ar).replace("../../docs", "../docs")
    if ar:
        return (toggle + '<p dir="rtl"><a href="../README.ar.md">→ الصفحة الرئيسية</a></p>\n\n'
                '<div dir="rtl">\n\n# كل الـ Skills\n\nكل الـ Skills مترتبة بمراحل الـ Content Creation OS.\n\n'
                '✅ جاهزة للتحميل · 🧪 تجريبية، حمّلها وقولنا رأيك · ⏳ Free وجاية قريب · 🔒 Pro، جزء من [Content Creation OS Pro](../course/README.ar.md)\n\n---\n\n## متاحة دلوقتي\n\n</div>\n\n'
                + featured_block(True, up="../", pages="") +
                '\n---\n\n<div dir="rtl">\n\n## حسب المرحلة\n\nدوس على كارت المرحلة عشان تفتح صفحتها.\n\n</div>\n\n' + stage_rows(True))
    return (toggle + "[← Home](../README.md)\n\n# All skills\n\nEvery skill, grouped by stage of the Content Creation OS.\n\n"
            "✅ Ready to download · 🧪 Testing, download and send feedback · ⏳ Free, coming soon · 🔒 Pro, part of [Content Creation OS Pro](../course/)\n\n---\n\n## Available now\n\n"
            + featured_block(False, up="../", pages="") +
            "\n---\n\n## By stage\n\nTap a stage card to open its page.\n\n" + stage_rows(False))


for st in stages:
    d = ROOT / "skills" / st["id"]
    d.mkdir(parents=True, exist_ok=True)
    (d / "README.md").write_text(lang_toggle() + stage_page(st), encoding="utf-8")
    (d / "README.ar.md").write_text(lang_toggle(True) + stage_page(st, ar=True), encoding="utf-8")

(ROOT / "skills" / "README.md").write_text(all_skills_page(), encoding="utf-8")
(ROOT / "skills" / "README.ar.md").write_text(all_skills_page(True), encoding="utf-8")

available = sum(1 for st in stages for s in st["skills"] if is_out(s))
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
