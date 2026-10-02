#!/usr/bin/env python3
"""Checks that every released skill follows the repo structure, so all skill pages look and work the same.

Run before every commit that adds or changes a skill:
    python3 scripts/check-skills.py
Exits non-zero and lists what's missing. "Released" means status "available" or "testing" in catalog.json.
"""
import json
import re
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
catalog = json.loads((ROOT / "catalog.json").read_text(encoding="utf-8"))
market = json.loads((ROOT / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8"))
market_paths = {p for pl in market["plugins"] for p in pl.get("skills", [])}

# Sections every skill page must have, in this order.
PAGE = {
    "README.md": ["docs/{slug}/hero-en.svg", "[← All skills]", "btn-download-en.svg", "| You give |",
                  "## How it works", "docs/{slug}/how-en.svg", "## Get started", "### 1 · Install — once, 5 minutes",
                  "docs/{slug}/install-en.svg", "<details>", "MIT License"],
    "README.ar.md": ["docs/{slug}/hero-ar.svg", "→ كل الـ Skills", "btn-download-ar.svg", "| بتدّيه |",
                     "## بتشتغل إزاي", "docs/{slug}/how-ar.svg", "## ابدأ", "### 1 · Install: مرة واحدة، 5 دقايق",
                     "docs/{slug}/install-ar.svg", "<details>", "MIT License"],
}
TESTING = {"README.md": "🧪 **Testing.**", "README.ar.md": "🧪 **تجريبية.**"}

errors = []
for st in catalog["stages"]:
    for s in st["skills"]:
        if s["status"] not in ("available", "testing"):
            continue
        slug = s["slug"]
        sk = ROOT / "skills" / st["id"] / slug
        err = lambda m: errors.append(f"{slug}: {m}")

        md = sk / "SKILL.md"
        if not md.exists():
            err("missing SKILL.md")
        else:
            head = md.read_text(encoding="utf-8").split("---")[1] if md.read_text(encoding="utf-8").startswith("---") else ""
            if not re.search(rf"^name:\s*{re.escape(slug)}\s*$", head, re.M):
                err("SKILL.md `name` must equal the folder name")
            if "description:" not in head:
                err("SKILL.md has no description")

        for page, needles in PAGE.items():
            f = sk / page
            if not f.exists():
                err(f"missing {page}")
                continue
            text = f.read_text(encoding="utf-8")
            pos = 0
            for n in needles:
                n = n.format(slug=slug)
                i = text.find(n, pos)
                if i < 0:
                    err(f"{page}: missing or out of order: {n}")
                else:
                    pos = i
            if s["status"] == "testing" and TESTING[page] not in text:
                err(f"{page}: testing skills need the 🧪 note")
            if "[!NOTE]" in text and TESTING[page] not in text:
                err(f"{page}: unexpected note")

        docs = ROOT / "docs" / slug
        for name in [f"{k}-{l}.svg" for k in ("hero", "how", "install") for l in ("en", "ar")] + ["after.jpg"]:
            if not (docs / name).exists():
                err(f"missing docs/{slug}/{name}")
        for l in ("en", "ar"):
            if not (ROOT / "docs" / "assets" / "skills" / f"{slug}-{l}.svg").exists():
                err(f"missing card docs/assets/skills/{slug}-{l}.svg (run scripts/build-art.py)")

        z = ROOT / "downloads" / f"{slug}.zip"
        if not z.exists():
            err("missing ZIP (run scripts/build-zips.sh)")
        else:
            names = zipfile.ZipFile(z).namelist()
            if f"{slug}/SKILL.md" not in names:
                err("ZIP must hold <slug>/SKILL.md at the top level")
            if any(re.fullmatch(rf"{re.escape(slug)}/README(\.\w+)?\.md", n) for n in names):
                err("ZIP must not include the README pages")

        if f"./skills/{st['id']}/{slug}" not in market_paths:
            err("not listed in .claude-plugin/marketplace.json")

if errors:
    print("Skill structure check failed:\n  " + "\n  ".join(errors))
    sys.exit(1)
print("All released skills follow the structure.")
