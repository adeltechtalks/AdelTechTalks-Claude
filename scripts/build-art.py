#!/usr/bin/env python3
"""Builds the animated README art in docs/assets/ from the AdelTechTalks brand tokens.

Outputs banner-en.svg, banner-ar.svg, flow-en.svg and flow-ar.svg. Fonts are subset and
embedded, so the SVGs render the same everywhere GitHub shows them. Motion is CSS inside
the SVG (GitHub strips scripts from READMEs but plays SVG animation) and switches off for
viewers who prefer reduced motion.

Requires: pip install fonttools brotli
"""
import base64
import io
from pathlib import Path
from xml.sax.saxutils import escape

from fontTools.subset import Options, Subsetter
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parent.parent
FONTS = Path(__file__).resolve().parent / "fonts"
OUT = ROOT / "docs" / "assets"

# Brand tokens (AdelTechTalks design system)
BLUE, DEEP, ICE, MINT = "#2563EB", "#1746A2", "#DCEBFF", "#2DD4A8"
GRAPHITE, SLATE, WARM, SOFT = "#171A1F", "#667085", "#FAFAF8", "#E6E8EC"

ARABIC_RANGE = "U+0600-06FF, U+0750-077F, U+08A0-08FF, U+200C-200F, U+FB50-FDFF, U+FE70-FEFF"
FACES = [  # (family, weight, file, unicode-range)
    ("M", 600, "montserrat-latin-600-normal.woff2", None),
    ("M", 700, "montserrat-latin-700-normal.woff2", None),
    ("M", 800, "montserrat-latin-800-normal.woff2", None),
    ("R", 400, "readex-pro-latin-400-normal.woff2", None),
    ("R", 500, "readex-pro-latin-500-normal.woff2", None),
    ("R", 600, "readex-pro-latin-600-normal.woff2", None),
    ("R", 400, "readex-pro-arabic-400-normal.woff2", ARABIC_RANGE),
    ("R", 600, "readex-pro-arabic-600-normal.woff2", ARABIC_RANGE),
    ("R", 700, "readex-pro-arabic-700-normal.woff2", ARABIC_RANGE),
    ("J", 500, "jetbrains-mono-latin-500-normal.woff2", None),
]

_fonts = {}


def font(file):
    if file not in _fonts:
        _fonts[file] = TTFont(FONTS / file)
    return _fonts[file]


def width(file, text, size, spacing=0.0):
    f = font(file)
    cmap, hmtx, upm = f.getBestCmap(), f["hmtx"], f["head"].unitsPerEm
    adv = sum(hmtx[cmap[ord(c)]][0] for c in text if ord(c) in cmap)
    return adv / upm * size + spacing * len(text)


def font_css(text, families):
    css = []
    for fam, weight, file, urange in FACES:
        if fam not in families:
            continue
        f = TTFont(FONTS / file)
        chars = {c for c in text if ord(c) in f.getBestCmap()}
        if not chars:
            continue
        opts = Options()
        opts.layout_features = ["*"]
        opts.flavor = "woff2"
        sub = Subsetter(opts)
        sub.populate(text="".join(chars))
        sub.subset(f)
        f.flavor = "woff2"
        buf = io.BytesIO()
        f.save(buf)
        data = base64.b64encode(buf.getvalue()).decode()
        rng = f";unicode-range:{urange}" if urange else ""
        css.append(f"@font-face{{font-family:{fam};font-weight:{weight};src:url(data:font/woff2;base64,{data}) format('woff2'){rng}}}")
    return "".join(css)


BASE_CSS = """
.fu{animation:fu .7s cubic-bezier(.2,.7,.2,1) both}
@keyframes fu{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:none}}
.fi{animation:fi .8s ease-out both}
@keyframes fi{from{opacity:0}to{opacity:1}}
.pulse{animation:pulse 2.4s ease-in-out infinite;transform-box:fill-box;transform-origin:center}
@keyframes pulse{0%,100%{transform:scale(1);opacity:1}50%{transform:scale(1.35);opacity:.55}}
.blink{animation:blink 1.1s steps(1) infinite}
@keyframes blink{0%,49%{opacity:1}50%,100%{opacity:0}}
.type{transform-box:fill-box;animation:type 1.1s steps(35) both;animation-delay:.2s}
@keyframes type{from{transform:scaleX(0)}to{transform:scaleX(1)}}
.draw{animation:draw 1s cubic-bezier(.2,.7,.2,1) both}
@keyframes draw{from{stroke-dashoffset:var(--len)}to{stroke-dashoffset:0}}
@media (prefers-reduced-motion:reduce){*{animation:none!important}.runin{display:none}}
"""


def svg(w, h, css, body, title):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="{escape(title)}">'
        f"<title>{escape(title)}</title><style>{css}</style>{body}</svg>\n"
    )


def d(s):
    return f"animation-delay:{s:.2f}s"


STAGES = ["Foundations", "Ideas", "Pre-Production", "Production", "Publish & Grow", "Lanes", "Money"]
STEP = 1.4  # seconds each stage stays highlighted
CYCLE = STEP * len(STAGES)


def stage_css():
    on = STEP / CYCLE * 100
    return (
        f".st{{animation:st {CYCLE:.1f}s ease-in-out infinite both}}"
        f"@keyframes st{{0%{{fill:#8A93A3}}2%{{fill:{WARM}}}{on - 1.5:.1f}%{{fill:{WARM}}}{on + 1:.1f}%{{fill:#8A93A3}}100%{{fill:#8A93A3}}}}"
        f".ul{{animation:ul {CYCLE:.1f}s ease-in-out infinite both}}"
        f"@keyframes ul{{0%{{opacity:0}}2%{{opacity:1}}{on - 1.5:.1f}%{{opacity:1}}{on + 1:.1f}%{{opacity:0}}100%{{opacity:0}}}}"
    )


def stages_row(y, rtl, start):
    num_f, lab_f = "jetbrains-mono-latin-500-normal.woff2", "montserrat-latin-600-normal.woff2"
    items = []
    for i, name in enumerate(STAGES):
        nw, lw = width(num_f, f"{i:02d}", 15), width(lab_f, name, 17)
        items.append((i, name, nw, lw, nw + 7 + lw))
    sep_w, gap = width(lab_f, "/", 17), 15
    out, x = [], (1192 if rtl else 88)
    for i, name, nw, lw, iw in items:
        x0 = x - iw if rtl else x
        delay = start + 0.9 + i * STEP
        out.append(
            f'<g class="fu" style="{d(start + i * 0.07)}">'
            f'<text x="{x0:.1f}" y="{y}" font-family="J" font-weight="500" font-size="15" fill="{BLUE}">{i:02d}</text>'
            f'<text class="st" fill="#8A93A3" style="{d(delay)}" x="{x0 + nw + 7:.1f}" y="{y}" font-family="M" font-weight="600" font-size="17">{escape(name)}</text>'
            f'<rect class="ul" opacity="0" style="{d(delay)}" x="{x0 + nw + 7:.1f}" y="{y + 12}" width="{lw:.1f}" height="3" rx="1.5" fill="{MINT}"/>'
            "</g>"
        )
        if i < len(items) - 1:
            sx = x0 - gap - sep_w if rtl else x0 + iw + gap
            out.append(f'<text class="fu" style="{d(start + i * 0.07)}" x="{sx:.1f}" y="{y}" font-family="M" font-weight="600" font-size="17" fill="#475467">/</text>')
            x = sx - gap if rtl else sx + sep_w + gap
    return "".join(out)


def banner(lang):
    rtl = lang == "ar"
    W, H, L, R = 1280, 640, 88, 1192
    eyebrow = "CONTENT CREATION OS · CLAUDE SKILLS"
    ew = width("jetbrains-mono-latin-500-normal.woff2", eyebrow, 17, 2.7)
    brand, curated = "AdelTechTalks", ("Curated by Adel" if not rtl else "Curated by Adel")
    bw = width("montserrat-latin-700-normal.woff2", brand, 22)
    cw = width("readex-pro-latin-400-normal.woff2", curated, 16)
    tag = "Experience it. Don't just consume it."

    parts = [f'<rect width="{W}" height="{H}" fill="{GRAPHITE}"/>']
    # faint brand grid, top corner only
    gx = R - 300 if not rtl else L
    parts.append(f'<g opacity=".06"><g class="fi" style="{d(0.2)}">' + "".join(
        f'<circle cx="{gx + c * 30}" cy="{150 + r * 30}" r="1.6" fill="{WARM}"/>' for r in range(8) for c in range(11)) + "</g></g>")

    # eyebrow with typing reveal
    ex = R - ew if rtl else L
    origin = "right" if rtl else "left"
    parts.append(f'<clipPath id="type"><rect class="type" style="transform-origin:{origin}" x="{ex - 2:.1f}" y="70" width="{ew + 6:.1f}" height="40"/></clipPath>')
    parts.append(f'<text clip-path="url(#type)" x="{ex:.1f}" y="100" font-family="J" font-weight="500" font-size="17" letter-spacing="2.7" fill="{MINT}">{escape(eyebrow)}</text>')

    # brand lockup
    if rtl:
        bx = L + 18
        parts.append(f'<g class="fi" style="{d(0.3)}"><circle class="pulse" cx="{L + 6}" cy="93" r="6" fill="{BLUE}"/>'
                     f'<text x="{bx}" y="101" font-family="M" font-weight="700" font-size="22" fill="{WARM}">{brand}</text>'
                     f'<text x="{bx + bw + 12:.1f}" y="100" font-family="R" font-weight="400" font-size="16" fill="#98A2B3">{curated}</text></g>')
    else:
        cx = R - cw
        bx = cx - 12 - bw
        parts.append(f'<g class="fi" style="{d(0.3)}"><circle class="pulse" cx="{bx - 12:.1f}" cy="93" r="6" fill="{BLUE}"/>'
                     f'<text x="{bx:.1f}" y="101" font-family="M" font-weight="700" font-size="22" fill="{WARM}">{brand}</text>'
                     f'<text x="{cx:.1f}" y="100" font-family="R" font-weight="400" font-size="16" fill="#98A2B3">{curated}</text></g>')

    h1f = "montserrat-latin-800-normal.woff2"
    if rtl:
        parts.append(f'<text class="fu" style="{d(0.5)}" x="{R}" y="238" text-anchor="end" font-family="M" font-weight="800" font-size="82" letter-spacing="-2.4" fill="{WARM}">Claude Skills</text>')
        parts.append(f'<text class="fu" style="{d(0.75)}" x="{R}" y="334" text-anchor="start" direction="rtl" font-family="R" font-weight="700" font-size="88" fill="{BLUE}">لصنّاع المحتوى</text>')
        subs = ["Skills و Agents لكل خطوة في الـ Flow،", "من أول فكرة لحد تحليل اللي نجح."]
        for k, line in enumerate(subs):
            parts.append(f'<text class="fu" style="{d(1.0 + k * 0.08)}" x="{R}" y="{398 + k * 40}" text-anchor="start" direction="rtl" font-family="R" font-weight="400" font-size="27" fill="#C9CED6">{escape(line)}</text>')
    else:
        parts.append(f'<text class="fu" style="{d(0.5)}" x="{L}" y="240" font-family="M" font-weight="800" font-size="82" letter-spacing="-2.4" fill="{WARM}">Claude Skills</text>')
        parts.append(f'<text class="fu" style="{d(0.75)}" x="{L}" y="325" font-family="M" font-weight="800" font-size="82" letter-spacing="-2.4" fill="{WARM}">for <tspan fill="{BLUE}">Content Creators</tspan></text>')
        caret_x = L + width(h1f, "for Content Creators", 82, -2.4) + 14
        parts.append(f'<rect class="blink" x="{caret_x:.1f}" y="262" width="7" height="70" rx="2" fill="{BLUE}"/>')
        subs = ["Skills and agents for every step of the flow — from the first idea to", "the analysis of what worked."]
        for k, line in enumerate(subs):
            parts.append(f'<text class="fu" style="{d(1.0 + k * 0.08)}" x="{L}" y="{392 + k * 38}" font-family="R" font-weight="400" font-size="26" fill="#C9CED6">{escape(line)}</text>')

    # rule draws in
    ln = R - L
    parts.append(f'<line class="draw" style="--len:{ln};{d(1.3)}" x1="{R if rtl else L}" y1="522" x2="{L if rtl else R}" y2="522" stroke="#2C313A" stroke-width="1" stroke-dasharray="{ln}"/>')
    parts.append(stages_row(566, rtl, 1.6))
    parts.append(f'<text class="fi" style="{d(2.2)}" x="{L if rtl else R}" y="616" text-anchor="{"start" if rtl else "end"}" font-family="R" font-weight="400" font-size="14" fill="{SLATE}">{escape(tag)}</text>')

    body = "".join(parts)
    text = eyebrow + brand + curated + tag + "Claude Skills for Content Creators0123456789/" + "".join(STAGES) + "لصنّاع المحتوى" + "".join(subs)
    css = font_css(text, {"M", "R", "J"}) + BASE_CSS + stage_css()
    title = "Claude Skills for Content Creators — AdelTechTalks" if not rtl else "Claude Skills لصنّاع المحتوى — AdelTechTalks"
    return svg(W, H, css, body, title)


FLOW = [  # (num, name, part_en, part_ar, output_en, output_ar)
    ("00", "Capture", "Ideas", "الأفكار", ["Idea card"], ["Idea card"]),
    ("01", "Idea Gate", "Ideas", "الأفكار", ["Go · Park · Kill"], ["Go · Park · Kill"]),
    ("02", "Research", "Ideas", "الأفكار", ["References + a", "better plan"], ["References", "وخطة أحسن"]),
    ("03", "Brief", "Ideas", "الأفكار", ["One-page brief"], ["Brief في صفحة"]),
    ("04", "Hook & Script", "Pre-Production", "قبل التصوير", ["Ready script"], ["Script جاهز"]),
    ("05", "Shot List", "Pre-Production", "قبل التصوير", ["Checked shot list"], ["Shot list متعلّمة"]),
    ("06", "Setup & Gear", "Pre-Production", "قبل التصوير", ["Defined setup"], ["Setup محدد"]),
    ("07", "Shoot", "Production", "التصوير", ["Footage + backup"], ["Footage و Backup"]),
    ("08", "Ingest", "Production", "التصوير", ["Project folder"], ["Project folder"]),
    ("09", "Edit", "Production", "التصوير", ["Final cut"], ["Final cut"]),
    ("10", "Publish Gate", "Publish & Grow", "النشر والنمو", ["Approve or", "back to edit"], ["Approve أو", "Back to edit"]),
    ("11", "Package & Publish", "Publish & Grow", "النشر والنمو", ["Live + scheduled"], ["Live و Scheduled"]),
    ("12", "Engage", "Publish & Grow", "النشر والنمو", ["New ideas in", "the inbox"], ["أفكار جديدة", "في الـ Inbox"]),
    ("13", "Analyze", "Publish & Grow", "النشر والنمو", ["Day 1 · 7 · 30", "+ one lesson"], ["أرقام يوم 1 و 7 و 30", "ودرس واحد"]),
]


def flow(lang):
    rtl = lang == "ar"
    W, H, L = 1600, 720, 72
    R = W - L
    cols, gap, ch = 7, 16, 180
    cw = (R - L - gap * (cols - 1)) / cols
    rows_y = [236, 236 + ch + 18]
    parts = [f'<rect width="{W}" height="{H}" fill="{WARM}"/>']

    eyebrow = "CONTENT CREATION OS · THE FLOW"
    anchor = "end" if rtl else "start"
    X = R if rtl else L
    parts.append(f'<text class="fi" style="{d(0.1)}" x="{X}" y="84" text-anchor="{anchor}" font-family="J" font-weight="500" font-size="15" letter-spacing="2.4" fill="{DEEP}">{eyebrow}</text>')
    if rtl:
        parts.append(f'<text class="fu" style="{d(0.2)}" x="{X}" y="152" text-anchor="start" direction="rtl" font-family="R" font-weight="700" font-size="54" fill="{GRAPHITE}">من الفكرة <tspan fill="{BLUE}">للتحليل</tspan></text>')
        sub = "كل فكرة بتمشي في نفس الـ 14 خطوة، وكل خطوة ليها Skill."
        parts.append(f'<text class="fu" style="{d(0.3)}" x="{X}" y="194" text-anchor="start" direction="rtl" font-family="R" font-weight="400" font-size="21" fill="{SLATE}">{escape(sub)}</text>')
    else:
        parts.append(f'<text class="fu" style="{d(0.2)}" x="{X}" y="150" font-family="M" font-weight="800" font-size="52" letter-spacing="-1" fill="{GRAPHITE}">From Idea <tspan fill="{BLUE}">to Analysis</tspan></text>')
        sub = "Every idea walks the same 14 steps. Every step has a skill."
        parts.append(f'<text class="fu" style="{d(0.3)}" x="{X}" y="190" font-family="R" font-weight="400" font-size="21" fill="{SLATE}">{escape(sub)}</text>')

    pos = []
    for i, (num, name, p_en, p_ar, o_en, o_ar) in enumerate(FLOW):
        r, c = divmod(i, cols)
        cx = L + ((cols - 1 - c) if rtl else c) * (cw + gap)
        y = rows_y[r]
        pos.append((cx, y))
        tx = cx + cw - 18 if rtl else cx + 18
        dirattr = ' direction="rtl"' if rtl else ""
        part = p_ar if rtl else p_en.upper()
        outs = o_ar if rtl else o_en
        pf, ps, pls = ("R", 12.5, 0) if rtl else ("R", 11.5, 1.2)
        g = [f'<rect x="{cx:.1f}" y="{y}" width="{cw:.1f}" height="{ch}" rx="14" fill="#FFFFFF" stroke="{SOFT}"/>',
             f'<text x="{tx:.1f}" y="{y + 32}" text-anchor="{"start" if rtl else anchor}"{dirattr} font-family="{pf}" font-weight="500" font-size="{ps}" letter-spacing="{pls}" fill="{SLATE}">{escape(part)}</text>',
             f'<text x="{tx:.1f}" y="{y + 72}" text-anchor="{anchor}" font-family="J" font-weight="500" font-size="27" fill="{BLUE}">{num}</text>']
        title_lines = ["Package &", "Publish"] if name == "Package & Publish" else [name]
        for k, tl in enumerate(title_lines):
            g.append(f'<text x="{tx:.1f}" y="{y + 102 + k * 23}" text-anchor="{anchor}" font-family="M" font-weight="700" font-size="19" fill="{GRAPHITE}">{escape(tl)}</text>')
        base = y + ch - 20 - (len(outs) - 1) * 19
        for k, ol in enumerate(outs):
            g.append(f'<text x="{tx:.1f}" y="{base + k * 19}" text-anchor="{"start" if rtl else anchor}"{dirattr} font-family="R" font-weight="400" font-size="14.5" fill="{SLATE}">{escape(ol)}</text>')
        parts.append(f'<g class="fu" style="{d(0.45 + i * 0.06)}">' + "".join(g) + "</g>")

    # the runner: a blue ring that walks the 14 steps
    n, hold = len(FLOW), 0.9
    cyc = n * hold
    frames = []
    for i, (x, y) in enumerate(pos):
        a, b = i / n * 100, (i + 0.78) / n * 100
        frames.append(f"{a:.2f}%,{b:.2f}%{{transform:translate({x:.1f}px,{y}px)}}")
    frames.append(f"100%{{transform:translate({pos[0][0]:.1f}px,{pos[0][1]}px)}}")
    css_runner = (f".run{{animation:run {cyc:.1f}s cubic-bezier(.4,0,.2,1) infinite both;animation-delay:1.6s}}"
                  f"@keyframes run{{{''.join(frames)}}}"
                  f".runin{{animation:fi .6s ease-out both;animation-delay:1.6s}}")
    dot_x = 16 if rtl else cw - 16
    parts.append(f'<g class="runin"><g class="run"><rect x="0" y="0" width="{cw:.1f}" height="{ch}" rx="14" fill="none" stroke="{BLUE}" stroke-width="2.5"/>'
                 f'<circle class="pulse" cx="{dot_x:.1f}" cy="16" r="5" fill="{MINT}"/></g></g>')

    loop_y = rows_y[1] + ch + 56
    if rtl:
        txt = "أسئلة الـ Engage ودروس الـ Analyze بترجع على طول للـ Capture."
        parts.append(f'<g class="fi" style="{d(1.4)}"><circle class="pulse" cx="{R - 5}" cy="{loop_y - 6}" r="5" fill="{MINT}"/>'
                     f'<text x="{R - 20}" y="{loop_y}" text-anchor="start" direction="rtl" font-family="R" font-weight="400" font-size="18" fill="{GRAPHITE}"><tspan font-weight="600">الـ Loop:</tspan> {escape(txt)}</text></g>')
    else:
        txt = "questions from Engage and lessons from Analyze go straight back into Capture."
        parts.append(f'<g class="fi" style="{d(1.4)}"><circle class="pulse" cx="{L + 5}" cy="{loop_y - 6}" r="5" fill="{MINT}"/>'
                     f'<text x="{L + 20}" y="{loop_y}" font-family="R" font-weight="400" font-size="18" fill="{GRAPHITE}"><tspan font-family="M" font-weight="700">The loop:</tspan> {escape(txt)}</text></g>')

    body = "".join(parts)
    alltext = eyebrow + sub + txt + "From Idea to AnalysisThe loop:الـ Loop:من الفكرة للتحليل" + "".join(
        f[0] + f[1] + f[2].upper() + f[3] + "".join(f[4]) + "".join(f[5]) for f in FLOW) + "Package &Publish"
    css = font_css(alltext, {"M", "R", "J"}) + BASE_CSS + css_runner
    title = "From Idea to Analysis — the 14-step flow" if not rtl else "من الفكرة للتحليل — 14 خطوة"
    return svg(W, H, css, body, title)


def cover_hero(lang):
    """Hero for the Social Cover Studio page: title on one side, before → after on the other."""
    rtl = lang == "ar"
    W, H, L = 1600, 680, 88
    R = W - L
    img_dir = ROOT / "docs" / "social-cover-studio"
    b64 = {k: base64.b64encode((img_dir / f"{k}.jpg").read_bytes()).decode() for k in ("before", "after")}

    bw, bh, aw, ah = 270, 486, 290, 522
    if rtl:
        ax, arrow_x0, arrow_x1 = L, L + aw + 48, L + aw + 12
        bx = L + aw + 60
    else:
        bx = R - aw - 60 - bw
        arrow_x0, arrow_x1 = bx + bw + 12, bx + bw + 48
        ax = R - aw
    by, ay = (H - bh) // 2 - 14, (H - ah) // 2 - 14
    cy = ay + ah / 2

    css_extra = (
        ".pop{animation:pop .8s cubic-bezier(.2,.8,.2,1.1) both;transform-box:fill-box;transform-origin:center}"
        "@keyframes pop{from{opacity:0;transform:scale(.92)}to{opacity:1;transform:none}}"
        ".ring{animation:ring 2.6s ease-in-out infinite both}"
        "@keyframes ring{0%,100%{opacity:1}50%{opacity:.35}}"
        f".shine{{animation:shine 4.5s ease-in-out infinite both;animation-delay:2.2s}}"
        f"@keyframes shine{{0%{{transform:translateX(-{aw + 160}px) skewX(-18deg)}}35%,100%{{transform:translateX({aw + 160}px) skewX(-18deg)}}}}"
    )

    parts = [f'<rect width="{W}" height="{H}" fill="{GRAPHITE}"/>',
             f'<defs><clipPath id="cb"><rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="18"/></clipPath>'
             f'<clipPath id="ca"><rect x="{ax}" y="{ay}" width="{aw}" height="{ah}" rx="20"/></clipPath></defs>']

    # before
    parts.append(f'<g class="fu" style="{d(0.4)}"><image clip-path="url(#cb)" href="data:image/jpeg;base64,{b64["before"]}" x="{bx}" y="{by}" width="{bw}" height="{bh}" preserveAspectRatio="xMidYMid slice"/>'
                 f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="18" fill="none" stroke="#2C313A"/>'
                 + (f'<text x="{bx + bw / 2}" y="{ay + ah + 44}" text-anchor="middle" font-family="R" font-weight="600" font-size="18" fill="#98A2B3">قبل</text>' if rtl else
                    f'<text x="{bx + bw / 2}" y="{ay + ah + 44}" text-anchor="middle" font-family="J" font-weight="500" font-size="14" letter-spacing="2.4" fill="#98A2B3">BEFORE</text>')
                 + "</g>")
    # arrow
    head = f"M{arrow_x1 + (8 if rtl else -8)} {cy - 8} L{arrow_x1} {cy} L{arrow_x1 + (8 if rtl else -8)} {cy + 8}"
    parts.append(f'<g class="fi" style="{d(1.0)}"><line class="draw" style="--len:40;{d(1.0)}" x1="{arrow_x0}" y1="{cy}" x2="{arrow_x1}" y2="{cy}" stroke="{BLUE}" stroke-width="3" stroke-linecap="round" stroke-dasharray="40"/>'
                 f'<path d="{head}" fill="none" stroke="{BLUE}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/></g>')
    # after
    parts.append(f'<g class="pop" style="{d(1.3)}"><image clip-path="url(#ca)" href="data:image/jpeg;base64,{b64["after"]}" x="{ax}" y="{ay}" width="{aw}" height="{ah}" preserveAspectRatio="xMidYMid slice"/>'
                 f'<g clip-path="url(#ca)"><rect class="shine" x="{ax + aw / 2 - 40}" y="{ay - 40}" width="80" height="{ah + 80}" fill="#FFFFFF" opacity=".16"/></g>'
                 f'<rect class="ring" style="{d(2.0)}" x="{ax - 5}" y="{ay - 5}" width="{aw + 10}" height="{ah + 10}" rx="24" fill="none" stroke="{BLUE}" stroke-width="3"/>'
                 + (f'<text x="{ax + aw / 2}" y="{ay + ah + 44}" text-anchor="middle" font-family="R" font-weight="600" font-size="18" fill="{BLUE}">بعد</text>' if rtl else
                    f'<text x="{ax + aw / 2}" y="{ay + ah + 44}" text-anchor="middle" font-family="J" font-weight="500" font-size="14" letter-spacing="2.4" fill="{BLUE}">AFTER</text>')
                 + "</g>")

    # text column
    X = R if rtl else L
    anc = "end" if rtl else "start"
    eyebrow = "PUBLISH & GROW · STEP 11 · FREE"
    parts.append(f'<text class="fi" style="{d(0.1)}" x="{X}" y="168" text-anchor="{anc}" font-family="J" font-weight="500" font-size="16" letter-spacing="2.5" fill="{MINT}">{escape(eyebrow)}</text>')
    parts.append(f'<text class="fu" style="{d(0.2)}" x="{X}" y="262" text-anchor="{anc}" font-family="M" font-weight="800" font-size="80" letter-spacing="-2.2" fill="{WARM}">Social Cover</text>')
    parts.append(f'<text class="fu" style="{d(0.35)}" x="{X}" y="350" text-anchor="{anc}" font-family="M" font-weight="800" font-size="80" letter-spacing="-2.2" fill="{BLUE}">Studio</text>')
    if rtl:
        subs = ["صورة واحدة تدخل،", "و Cover بالـ Brand بتاعك لكل منصة يطلع."]
        for k, s in enumerate(subs):
            parts.append(f'<text class="fu" style="{d(0.5 + k * 0.08)}" x="{X}" y="{418 + k * 40}" text-anchor="start" direction="rtl" font-family="R" font-weight="400" font-size="26" fill="#C9CED6">{escape(s)}</text>')
    else:
        subs = ["One photo in. A branded cover", "for every platform out."]
        for k, s in enumerate(subs):
            parts.append(f'<text class="fu" style="{d(0.5 + k * 0.08)}" x="{X}" y="{416 + k * 38}" font-family="R" font-weight="400" font-size="26" fill="#C9CED6">{escape(s)}</text>')

    chips = [("9:16", "Reels · TikTok"), ("4:5", "Feed"), ("16:9", "YouTube")]
    jf, mf = "jetbrains-mono-latin-500-normal.woff2", "montserrat-latin-600-normal.woff2"
    x, cyp = X, 512
    for i, (ratio, label) in enumerate(chips):
        rw, lw = width(jf, ratio, 15), width(mf, label, 16)
        pw = 18 + rw + 10 + lw + 18
        x0 = x - pw if rtl else x
        parts.append(f'<g class="fu" style="{d(0.7 + i * 0.08)}"><rect x="{x0:.1f}" y="{cyp}" width="{pw:.1f}" height="44" rx="22" fill="#1E2229" stroke="#2C313A"/>'
                     f'<text x="{x0 + 18:.1f}" y="{cyp + 28}" font-family="J" font-weight="500" font-size="15" fill="{BLUE}">{ratio}</text>'
                     f'<text x="{x0 + 18 + rw + 10:.1f}" y="{cyp + 28}" font-family="M" font-weight="600" font-size="16" fill="{WARM}">{escape(label)}</text></g>')
        x = x0 - 12 if rtl else x0 + pw + 12

    body = "".join(parts)
    text = eyebrow + "Social CoverStudio" + "".join(subs) + "".join(a + b for a, b in chips) + "BEFOREAFTERقبلبعد"
    css = font_css(text, {"M", "R", "J"}) + BASE_CSS + css_extra
    title = "Social Cover Studio — one photo in, a branded cover for every platform out"
    return svg(W, H, css, body, title)


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for name, content in (("banner-en.svg", banner("en")), ("banner-ar.svg", banner("ar")),
                          ("flow-en.svg", flow("en")), ("flow-ar.svg", flow("ar"))):
        (OUT / name).write_text(content, encoding="utf-8")
        print(f"built docs/assets/{name} ({len(content.encode()) // 1024} KB)")
    for lang in ("en", "ar"):
        target = ROOT / "docs" / "social-cover-studio" / f"hero-{lang}.svg"
        content = cover_hero(lang)
        target.write_text(content, encoding="utf-8")
        print(f"built docs/social-cover-studio/hero-{lang}.svg ({len(content.encode()) // 1024} KB)")
