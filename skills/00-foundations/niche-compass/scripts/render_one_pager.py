#!/usr/bin/env python3
"""Render a One Pager JSON into a designed, printable HTML page (and a PDF when Chromium is available).

Usage:
    python scripts/render_one_pager.py one-pager.json --out out
Writes out/one-pager.html, and out/one-pager.pdf if a Chromium/Chrome binary is found.
Only the Python standard library is needed.
"""
import argparse
import html
import json
import shutil
import subprocess
from pathlib import Path

L = {
    "ar": {"who": "مين", "what": "بيعمل إيه", "why": "موجود ليه", "aud": "بيكلّم مين", "pillars": "الـ Pillars",
           "q": "بيجاوب على", "types": "أنواع المحتوى", "filter": "فلتر الأفكار", "filter_hint": "الفكرة لازم تعدّي على الـ 3",
           "off": "ممنوع دلوقتي", "commit": "الالتزام", "months": "شهور من غير مواضيع جديدة", "money": "الفلوس",
           "focus": "ابدأ هنا", "kdp": "هتكمّل · هتسيب · هتأجّل", "keep": "هتكمّل", "drop": "هتسيب", "post": "هتأجّل",
           "starter": "ابدأ بكرة", "ideas": "أول 10 أفكار (عدّوا على الفلتر)", "week": "أول أسبوع", "bios": "الـ Bios",
           "chars": "حرف", "ref": "ده المرجع: أي فكرة جديدة تتقارن بالصفحة دي قبل ما تتعمل.",
           "vision": "الرؤية: رايح فين", "y1": "بعد سنة", "y5": "بعد 5 سنين", "brand": "البراند", "btype": "النوع",
           "tagline": "الـ Tagline", "pending": "لسه محتاجة قرار", "channels": "القنوات", "platforms": "المنصات",
           "langmkt": "اللغة والسوق", "rhythm": "هتشتغل إزاي", "hours": "الوقت في الأسبوع", "cadence": "النشر", "workflow": "الطريقة"},
    "en": {"who": "Who", "what": "What", "why": "Why here", "aud": "Who we talk to", "pillars": "Pillars",
           "q": "Answers", "types": "Content types", "filter": "Idea filter", "filter_hint": "An idea must pass all 3",
           "off": "Off-limits for now", "commit": "Commitment", "months": "months with no new topics", "money": "Money",
           "focus": "Start here", "kdp": "Keep · Drop · Postpone", "keep": "Keep", "drop": "Drop", "post": "Postpone",
           "starter": "Start tomorrow", "ideas": "First 10 ideas (all pass the filter)", "week": "First week", "bios": "Bios",
           "chars": "chars", "ref": "This is the reference: every new idea is checked against this page before it gets made.",
           "vision": "Vision: where this goes", "y1": "In 1 year", "y5": "In 5 years", "brand": "Brand", "btype": "Type",
           "tagline": "Tagline", "pending": "Still to decide", "channels": "Channels", "platforms": "Platforms",
           "langmkt": "Language & market", "rhythm": "How you'll work", "hours": "Time per week", "cadence": "Posting", "workflow": "Workflow"},
}

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@600;800&family=Readex+Pro:wght@400;500;700&display=swap" rel="stylesheet">')


def e(s):
    return html.escape(str(s or ""))


def render(d):
    lang = d.get("lang", "en")
    t = L["ar" if lang == "ar" else "en"]
    rtl = d.get("dir", "rtl" if lang == "ar" else "ltr") == "rtl"
    b = {"primary": "#2563EB", "deep": "#1746A2", "accent": "#2DD4A8", "dark": "#171A1F", "muted": "#667085",
         "paper": "#FAFAF8", "line": "#E6E8EC", "ice": "#DCEBFF", **d.get("brand", {})}
    f = d.get("filter", {})
    s = d.get("starter", {})

    lq, rq = ("«", "»") if lang == "ar" else ("“", "”")
    pillars = "".join(
        f'<div class="pillar"><div class="num">{i}</div><h3>{e(p["name"])}</h3>'
        f'<p class="q">{lq}{e(p.get("question"))}{rq}</p><p class="types">{e(p.get("types"))}</p></div>'
        for i, p in enumerate(d.get("pillars", []), 1))
    questions = "".join(f"<li>{e(q)}</li>" for q in f.get("questions", []))
    examples = "".join(
        f'<tr><td class="mark {"ok" if x.get("ok") else "no"}">{"✓" if x.get("ok") else "✕"}</td>'
        f'<td>{e(x["idea"])}</td><td class="note">{e(x.get("note"))}</td></tr>' for x in f.get("examples", []))
    money = "".join(
        f'<div class="step{" focus" if m.get("focus") else ""}"><div class="sn">{i}</div><div><b>{e(m["step"])}</b>'
        f'<span>{e(m.get("what"))}</span></div><div class="price" dir="ltr">{e(m.get("price"))}</div>'
        f'{"<div class=tag>" + t["focus"] + "</div>" if m.get("focus") else ""}</div>'
        for i, m in enumerate(d.get("money", []), 1))
    kdp = d.get("kdp", {})
    col = lambda items: "".join(f"<li>{e(x)}</li>" for x in items)
    postpone = "".join(f'<li>{e(x["item"])} <i>({e(x.get("when"))})</i></li>' if isinstance(x, dict) else f"<li>{e(x)}</li>"
                       for x in kdp.get("postpone", []))
    ideas = "".join(f'<li><span class="pp">P{e(i.get("pillar"))}</span>{e(i["title"])}</li>' for i in s.get("ideas", []))
    week = "".join(f'<div class="day"><b>{e(w["day"])}</b><span>{e(w["post"])}</span></div>' for w in s.get("week", []))
    bios = "".join(
        f'<div class="bio"><div class="bh"><b>{e(k)}</b><span>{len(v.encode("utf-16-le")) // 2} {t["chars"]}</span></div><pre dir="auto">{e(v)}</pre></div>'
        for k, v in d.get("bios", {}).items())
    aud = "".join(f"<li>{e(a)}</li>" for a in d.get("audience", []))
    v = d.get("vision", {})
    vision = (f'<section class="vision"><h2>{t["vision"]}</h2><div class="vgrid"><div class="vbox"><b>{t["y1"]}</b><p>{e(v.get("year1"))}</p></div>'
              f'<div class="vbox far"><b>{t["y5"]}</b><p>{e(v.get("year5"))}</p></div></div></section>') if v else ""
    idn = d.get("identity", {})
    if idn:
        tl = idn.get("tagline")
        opts = "".join(f'<span class="opt{" on" if o == tl else ""}" dir="auto">{e(o)}</span>' for o in idn.get("tagline_options", []))
        tag_html = f'<div class="tl" dir="auto">{e(tl)}</div>' if tl else f'<div class="tlp">{t["pending"]}</div>'
        chans = "".join(f'<li><b>{e(c["name"])}</b> · {e(c.get("role"))}</li>' for c in idn.get("channels", []))
        plats = "".join(f'<span class="chip">{e(x)}</span>' for x in idn.get("platforms", []))
        identity = (f'<section><h2>{t["brand"]}</h2><div class="grid4">'
                    f'<div class="box"><h3>{t["btype"]}</h3><p><b>{e(idn.get("type"))}</b></p><p class="sub">{e(idn.get("name"))} · <span dir="ltr">{e(idn.get("handle"))}</span></p><p class="sub">{e(idn.get("why"))}</p></div>'
                    f'<div class="box"><h3>{t["tagline"]}</h3>{tag_html}<div class="opts">{opts}</div></div>'
                    f'<div class="box"><h3>{t["channels"]}</h3><ul>{chans}</ul></div>'
                    f'<div class="box"><h3>{t["langmkt"]}</h3><p>{e(idn.get("language"))}</p><p class="sub">{e(idn.get("market"))}</p><div class="meta">{plats}</div></div>'
                    f'</div></section>')
    else:
        identity = ""
    r = d.get("rhythm", {})
    rhythm = (f'<section><h2>{t["rhythm"]}</h2><div class="rgrid"><div class="box"><h3>{t["hours"]}</h3><p class="big">{e(r.get("hours"))}</p></div>'
              f'<div class="box"><h3>{t["cadence"]}</h3><p class="big">{e(r.get("cadence"))}</p></div>'
              f'<div class="box"><h3>{t["workflow"]}</h3><p>{e(r.get("workflow"))}</p></div></div></section>') if r else ""
    commit = f.get("commit_months")

    css = f"""
:root{{--p:{b['primary']};--d:{b['deep']};--a:{b['accent']};--k:{b['dark']};--m:{b['muted']};--paper:{b['paper']};--line:{b['line']};--ice:{b['ice']}}}
*{{box-sizing:border-box}}body{{margin:0;background:#EEF0F3;color:var(--k);font:400 15px/1.6 'Readex Pro','Montserrat',system-ui,sans-serif}}
.page{{max-width:900px;margin:24px auto;background:var(--paper);border-radius:22px;overflow:hidden;box-shadow:0 10px 40px rgba(23,26,31,.08)}}
header{{background:linear-gradient(135deg,var(--p),var(--d));color:#fff;padding:36px 40px 32px}}
.eyebrow{{font:600 12px Montserrat,sans-serif;letter-spacing:2px;opacity:.8;text-transform:uppercase}}
h1{{font:800 34px/1.2 Montserrat,'Readex Pro',sans-serif;margin:8px 0 4px}}.handle{{opacity:.85}}
.line{{margin-top:18px;background:rgba(255,255,255,.12);border-inline-start:4px solid var(--a);padding:14px 18px;border-radius:12px;font-size:19px;font-weight:500}}
section{{padding:26px 40px;border-top:1px solid var(--line)}}h2{{font:700 13px Montserrat,'Readex Pro',sans-serif;letter-spacing:1.5px;color:var(--p);text-transform:uppercase;margin:0 0 14px}}
.grid4{{display:grid;grid-template-columns:repeat(2,1fr);gap:14px}}.box{{background:#fff;border:1px solid var(--line);border-radius:14px;padding:14px 16px}}
.box h3{{margin:0 0 4px;font-size:13px;color:var(--m);font-weight:500}}.box p,.box ul{{margin:0}}.box ul{{padding-inline-start:18px}}
.pillars{{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}}.pillar{{background:#fff;border:1px solid var(--line);border-radius:16px;padding:18px;position:relative}}
.pillar .num{{width:30px;height:30px;border-radius:50%;background:var(--p);color:#fff;display:grid;place-items:center;font:800 14px Montserrat}}
.pillar h3{{margin:10px 0 6px;font-size:17px}}.pillar .q{{color:var(--d);margin:0 0 8px;font-size:14px}}.pillar .types{{color:var(--m);font-size:13px;margin:0}}
.filter{{display:grid;grid-template-columns:1fr 1.6fr;gap:18px}}.qs{{background:var(--ice);border-radius:14px;padding:14px 16px}}.qs ol{{margin:6px 0 0;padding-inline-start:20px}}.qs li{{margin:6px 0;font-weight:500}}
table{{width:100%;border-collapse:collapse;font-size:14px}}td{{padding:7px 6px;border-bottom:1px solid var(--line);vertical-align:top}}
.mark{{width:26px;font-weight:800;text-align:center}}.ok{{color:#0B8A6A}}.no{{color:#C0392B}}.note{{color:var(--m);font-size:13px}}
.meta{{display:flex;gap:10px;flex-wrap:wrap;margin-top:12px}}.chip{{background:#fff;border:1px solid var(--line);border-radius:999px;padding:5px 12px;font-size:13px}}
.step{{display:flex;align-items:center;gap:14px;background:#fff;border:1px solid var(--line);border-radius:14px;padding:10px 14px;margin-bottom:8px;position:relative}}
.step .sn{{font:800 14px Montserrat;color:var(--m);width:22px}}.step b{{display:block}}.step span{{color:var(--m);font-size:13px}}.step .price{{margin-inline-start:auto;font:600 13px Montserrat,'Readex Pro';white-space:nowrap}}
.step.focus{{border:2px solid var(--a);background:#F0FCF8}}.tag{{position:absolute;top:-10px;inset-inline-end:14px;background:var(--a);color:var(--k);font-size:11px;font-weight:700;padding:2px 10px;border-radius:999px}}
.kdp{{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}}.kdp .box h3{{font-size:14px;color:var(--k);font-weight:700}}.kdp ul{{padding-inline-start:18px;margin:6px 0 0}}.kdp i{{color:var(--m);font-style:normal;font-size:12px}}
.k1{{border-top:4px solid var(--a)}}.k2{{border-top:4px solid #C0392B}}.k3{{border-top:4px solid #F2B705}}
.starter{{background:linear-gradient(180deg,#fff,var(--ice))}}.ideas{{columns:2;gap:22px;padding:0;margin:0;list-style:none}}.ideas li{{break-inside:avoid;margin:0 0 9px;display:flex;gap:8px;align-items:baseline}}
.pp{{background:var(--p);color:#fff;font:700 10px Montserrat;border-radius:6px;padding:2px 6px;flex:none}}
.week{{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-top:16px}}.day{{background:#fff;border-radius:12px;padding:12px 14px;border:1px solid var(--line)}}.day b{{display:block;color:var(--p);font-size:13px}}.day span{{font-size:14px}}
.bios{{display:grid;grid-template-columns:repeat(2,1fr);gap:12px}}.bio{{background:#fff;border:1px solid var(--line);border-radius:14px;padding:12px 14px}}
.bh{{display:flex;justify-content:space-between;font-size:13px}}.bh span{{color:var(--m)}}pre{{white-space:pre-wrap;margin:8px 0 0;font:400 14px/1.6 'Readex Pro',sans-serif}}
.vision{{background:var(--k);color:#fff}}.vision h2{{color:var(--a)}}.vgrid{{display:grid;grid-template-columns:1fr 1fr;gap:14px}}
.vbox{{background:rgba(255,255,255,.07);border-radius:14px;padding:14px 16px}}.vbox b{{color:var(--a);font-size:13px}}.vbox p{{margin:4px 0 0;font-size:16px}}.vbox.far{{border:1px solid var(--a)}}
.sub{{color:var(--m);font-size:13px;margin-top:4px!important}}.tl{{font:800 20px/1.3 Montserrat,'Readex Pro',sans-serif;color:var(--p)}}.tlp{{color:#B45309;font-weight:700}}
.opts{{display:flex;flex-wrap:wrap;gap:6px;margin-top:8px}}.opt{{border:1px dashed var(--line);border-radius:999px;padding:3px 10px;font-size:12px;color:var(--m)}}.opt.on{{border:1px solid var(--p);color:var(--p)}}
.rgrid{{display:grid;grid-template-columns:1fr 1fr 2fr;gap:14px}}.big{{font:800 22px Montserrat,'Readex Pro',sans-serif;margin:0}}
footer{{padding:16px 40px 26px;color:var(--m);font-size:13px;border-top:1px solid var(--line)}}
@media (max-width:700px){{header,section,footer{{padding-inline:18px}}.grid4,.pillars,.filter,.kdp,.week,.bios,.vgrid,.rgrid{{grid-template-columns:1fr}}.ideas{{columns:1}}h1{{font-size:26px}}}}
@media print{{body{{background:#fff}}.page{{margin:0;box-shadow:none;border-radius:0;max-width:none}}section{{break-inside:avoid}}}}
"""
    return f"""<!doctype html><html lang="{e(lang)}" dir="{'rtl' if rtl else 'ltr'}"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>{e(d.get('name'))} · One Pager</title>{FONTS}<style>{css}</style></head>
<body><div class="page">
<header><div class="eyebrow">One Pager</div><h1>{e(d.get('name'))}</h1><div class="handle"><bdi>{e(d.get('handle'))}</bdi></div>
<div class="line">{e(d.get('line'))}</div></header>
<section><div class="grid4"><div class="box"><h3>{t['who']}</h3><p>{e(d.get('who'))}</p></div>
<div class="box"><h3>{t['what']}</h3><p>{e(d.get('what'))}</p></div>
<div class="box"><h3>{t['why']}</h3><p>{e(d.get('why'))}</p></div>
<div class="box"><h3>{t['aud']}</h3><ul>{aud}</ul></div></div></section>
{vision}{identity}<section><h2>{t['pillars']}</h2><div class="pillars">{pillars}</div></section>
<section><h2>{t['filter']}</h2><div class="filter"><div class="qs"><b>{t['filter_hint']}</b><ol>{questions}</ol></div>
<table>{examples}</table></div><div class="meta">{f'<span class="chip">⏳ {t["commit"]}: {e(commit)} {t["months"]}</span>' if commit else ''}
{f'<span class="chip">🚫 {t["off"]}: {e(f.get("off_limits"))}</span>' if f.get("off_limits") else ''}</div></section>
<section class="starter"><h2>{t['starter']}</h2><b>{t['ideas']}</b><ol class="ideas" style="margin-top:10px">{ideas}</ol>
<div class="week">{week}</div></section>
{rhythm}<section><h2>{t['money']}</h2>{money}</section>
<section><h2>{t['kdp']}</h2><div class="kdp"><div class="box k1"><h3>{t['keep']}</h3><ul>{col(kdp.get('keep', []))}</ul></div>
<div class="box k2"><h3>{t['drop']}</h3><ul>{col(kdp.get('drop', []))}</ul></div><div class="box k3"><h3>{t['post']}</h3><ul>{postpone}</ul></div></div></section>
<section><h2>{t['bios']}</h2><div class="bios">{bios}</div></section>
<footer>{t['ref']}</footer></div></body></html>"""


def chromium():
    for name in ("chromium", "chromium-browser", "google-chrome", "chrome"):
        if shutil.which(name):
            return shutil.which(name)
    hits = sorted(Path("/opt/pw-browsers").glob("chromium-*/chrome-linux/chrome")) if Path("/opt/pw-browsers").exists() else []
    return str(hits[-1]) if hits else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("json")
    ap.add_argument("--out", default="out")
    a = ap.parse_args()
    data = json.loads(Path(a.json).read_text(encoding="utf-8"))
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    page = out / "one-pager.html"
    page.write_text(render(data), encoding="utf-8")
    print(f"wrote {page}")
    exe = chromium()
    if exe:
        pdf = out / "one-pager.pdf"
        subprocess.run([exe, "--headless", "--no-sandbox", "--disable-gpu", "--virtual-time-budget=4000",
                        "--no-pdf-header-footer", f"--print-to-pdf={pdf.resolve()}", page.resolve().as_uri()],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=90)
        if pdf.exists():
            print(f"wrote {pdf}")


if __name__ == "__main__":
    main()
