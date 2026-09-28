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


def lang_button(lang, active):
    """Pill used by the English / العربية switch at the top of every page."""
    W, H = 148, 44
    fill, fg = (BLUE, "#FFFFFF") if active else (GRAPHITE, "#C9CED6")
    stroke = BLUE if active else "#3A404A"
    if lang == "ar":
        label = "العربية"
        text = f'<text x="{W / 2}" y="29" text-anchor="middle" font-family="R" font-weight="600" font-size="18" fill="{fg}">{label}</text>'
    else:
        label = "English"
        text = f'<text x="{W / 2}" y="28.5" text-anchor="middle" font-family="M" font-weight="700" font-size="16" fill="{fg}">{label}</text>'
    body = f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="{(H - 2) / 2}" fill="{fill}" stroke="{stroke}"/>{text}'
    return svg(W, H, font_css(label, {"M", "R"}), body, label)


# ---------- step cards: "How it works" and "Install" as illustrated, animated cards ----------

CARD_W, CARD_H, CARD_GAP, CARD_Y = 436, 460, 96, 30


def _card_x(i, rtl, W=1600):
    total = 3 * CARD_W + 2 * CARD_GAP
    x0 = (W - total) / 2
    c = 2 - i if rtl else i
    return x0 + c * (CARD_W + CARD_GAP)


def _img(path, w=None):
    return "data:image/jpeg;base64," + base64.b64encode(path.read_bytes()).decode()


def _card(i, rtl, title, caption, art, delay):
    x = _card_x(i, rtl)
    y = CARD_Y
    pad = 32
    tx = x + CARD_W - pad if rtl else x + pad
    anc = "start" if rtl else "start"
    dir_ = ' direction="rtl"' if rtl else ""
    num = f"{i + 1:02d}"
    out = [f'<g class="fu" style="{d(delay)}">',
           f'<rect x="{x:.1f}" y="{y}" width="{CARD_W}" height="{CARD_H}" rx="22" fill="#FFFFFF" stroke="{SOFT}"/>',
           f'<rect x="{x + 16:.1f}" y="{y + 16}" width="{CARD_W - 32}" height="270" rx="14" fill="#F4F6FA"/>',
           art(x, y),
           f'<text x="{tx:.1f}" y="{y + 336}" text-anchor="{"end" if rtl else "start"}" font-family="J" font-weight="500" font-size="16" fill="{BLUE}">{num}</text>',
           f'<text x="{tx:.1f}" y="{y + 372}" text-anchor="{anc}"{dir_} font-family="{"R" if rtl else "M"}" font-weight="{600 if rtl else 700}" font-size="{25 if rtl else 24}" fill="{GRAPHITE}">{escape(title)}</text>']
    for k, line in enumerate(caption):
        ltr = not any('\u0600' <= c <= '\u08FF' for c in line)
        if rtl and ltr:
            out.append(f'<text x="{tx:.1f}" y="{y + 408 + k * 26}" text-anchor="end" font-family="R" font-weight="400" font-size="17" fill="{SLATE}">{escape(line)}</text>')
        else:
            out.append(f'<text x="{tx:.1f}" y="{y + 408 + k * 26}" text-anchor="start"{dir_} font-family="R" font-weight="400" font-size="17" fill="{SLATE}">{escape(line)}</text>')
    out.append("</g>")
    return "".join(out)


def _arrows(rtl, delay):
    out = []
    for i in range(2):
        xa = _card_x(i, rtl) + (0 if rtl else CARD_W)
        xb = _card_x(i + 1, rtl) + (CARD_W if rtl else 0)
        x1, x2 = (xa - 22, xb + 22) if rtl else (xa + 22, xb - 22)
        cy = CARD_Y + 151
        hd = 9 if rtl else -9
        out.append(f'<g class="fi" style="{d(delay + i * 0.35)}"><line class="draw" style="--len:60;{d(delay + i * 0.35)}" x1="{x1:.1f}" y1="{cy}" x2="{x2:.1f}" y2="{cy}" stroke="{BLUE}" stroke-width="3" stroke-linecap="round" stroke-dasharray="60"/>'
                   f'<path d="M{x2 + hd:.1f} {cy - 9} L{x2:.1f} {cy} L{x2 + hd:.1f} {cy + 9}" fill="none" stroke="{BLUE}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/></g>')
    return "".join(out)


STEP_CSS = """
.pop{animation:pop .7s cubic-bezier(.2,.8,.2,1.1) both;transform-box:fill-box;transform-origin:center}
@keyframes pop{from{opacity:0;transform:scale(.9)}to{opacity:1;transform:none}}
.bob{animation:bob 1.8s ease-in-out infinite both}
@keyframes bob{0%,100%{transform:translateY(0)}50%{transform:translateY(8px)}}
.knob{animation:knob 3.2s ease-in-out infinite both}
@keyframes knob{0%,30%{transform:translateX(0)}42%,100%{transform:translateX(26px)}}
.track{animation:track 3.2s ease-in-out infinite both}
@keyframes track{0%,30%{fill:#C9CED6}42%,100%{fill:#2563EB}}
.drop{animation:drop 3.6s cubic-bezier(.4,0,.2,1) infinite both}
@keyframes drop{0%,10%{transform:translate(0,-70px);opacity:0}25%{opacity:1}45%,100%{transform:translate(0,0);opacity:1}}
.row{animation:row 3.6s ease-out infinite both}
@keyframes row{0%,48%{opacity:0}58%,100%{opacity:1}}
"""


def _pick_css(n, cyc=6.0):
    frames = []
    for i in range(n):
        a, b = i / n * 100, (i + 0.8) / n * 100
        frames.append(f"{a:.1f}%,{b:.1f}%{{transform:translateX({i * 74}px)}}")
    frames.append("100%{transform:translateX(0)}")
    return f".pick{{animation:pick {cyc}s cubic-bezier(.4,0,.2,1) infinite both;animation-delay:1.4s}}@keyframes pick{{{''.join(frames)}}}"


def _cycle_css(name, n, cyc):
    on = 100 / n
    return (f".{name}{{animation:{name} {cyc}s ease-in-out infinite both}}"
            f"@keyframes {name}{{0%{{opacity:0}}3%{{opacity:1}}{on - 3:.1f}%{{opacity:1}}{on:.1f}%{{opacity:0}}100%{{opacity:0}}}}")


def how_it_works(lang):
    rtl = lang == "ar"
    W, H = 1600, 520
    root = ROOT / "docs" / "social-cover-studio"
    before, after = _img(root / "before.jpg"), _img(root / "after.jpg")
    thumbs = [_img(root / "thumbs" / f"t{k}.jpg") for k in range(5)]

    if rtl:
        titles = ["ابعت الصورة", "اختار Template", "خد كل المقاسات"]
        caps = [["ومعاها الكلمة الكبيرة، واسم الـ Product،", "وكلمة قصيرة."], ["الـ 5 جنب بعض، بألوان", "الـ Brand والـ Fonts بتاعتك."], ["Instagram · TikTok", "Facebook · YouTube"]]
        bubble = ["الكلمة: GLACIER", "الـ Product: iPhone 18", "الكلمة القصيرة: لوني المفضل"]
    else:
        titles = ["Send a photo", "Pick a template", "Get every size"]
        caps = [["Add a big word, the product name", "and a short keyword."], ["See all 5 side by side,", "in your colours and fonts."], ["Instagram · TikTok", "Facebook · YouTube"]]
        bubble = ["Big word: GLACIER", "Product: iPhone 18", "Keyword: my favourite"]

    def art1(x, y):
        cx = x + CARD_W / 2
        px, bx = (cx + 40, cx - 190) if rtl else (cx - 170, cx - 30)
        s = [f'<clipPath id="p1"><rect x="{px}" y="{y + 44}" width="130" height="226" rx="12"/></clipPath>',
             f'<image clip-path="url(#p1)" href="{before}" x="{px}" y="{y + 44}" width="130" height="226" preserveAspectRatio="xMidYMid slice"/>',
             f'<g class="pop" style="{d(0.9)}"><rect x="{bx}" y="{y + 70}" width="220" height="150" rx="16" fill="{ICE}"/>']
        for k, line in enumerate(bubble):
            tx = bx + 220 - 18 if rtl else bx + 18
            attrs = 'text-anchor="start" direction="rtl"' if rtl else 'text-anchor="start"'
            s.append(f'<text class="fi" style="{d(1.2 + k * 0.35)}" x="{tx}" y="{y + 112 + k * 38}" {attrs} font-family="R" font-weight="500" font-size="15" fill="{DEEP}">{escape(line)}</text>')
        s.append("</g>")
        return "".join(s)

    def art2(x, y):
        cx = x + CARD_W / 2
        tw, th, gap = 64, 114, 10
        x0 = cx - (5 * tw + 4 * gap) / 2
        s = []
        for k in range(5):
            tx = x0 + k * (tw + gap)
            s.append(f'<clipPath id="tp{k}"><rect x="{tx}" y="{y + 96}" width="{tw}" height="{th}" rx="8"/></clipPath>'
                     f'<image class="pop" style="{d(0.9 + k * 0.1)}" clip-path="url(#tp{k})" href="{thumbs[k]}" x="{tx}" y="{y + 96}" width="{tw}" height="{th}" preserveAspectRatio="xMidYMid slice"/>')
        ring_x = x0 - 4 if not rtl else x0 - 4
        s.append(f'<g class="pick"><rect x="{ring_x}" y="{y + 92}" width="{tw + 8}" height="{th + 8}" rx="11" fill="none" stroke="{BLUE}" stroke-width="3"/>'
                 f'<circle cx="{ring_x + tw + 8}" cy="{y + 92}" r="11" fill="{BLUE}"/><path d="M{ring_x + tw + 3} {y + 92} l4 4 l7 -8" fill="none" stroke="#fff" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/></g>')
        return "".join(s)

    def art3(x, y):
        cx = x + CARD_W / 2
        frames = [("9:16", 72, 128), ("4:5", 104, 130), ("16:9", 176, 99)]
        total = sum(f[1] for f in frames) + 2 * 18
        order = list(reversed(frames)) if rtl else frames
        fx = cx - total / 2
        base = y + 214
        s = []
        for k, (lab, fw, fh) in enumerate(order):
            s.append(f'<clipPath id="f{k}"><rect x="{fx}" y="{base - fh}" width="{fw}" height="{fh}" rx="8"/></clipPath>'
                     f'<g class="pop" style="{d(1.0 + k * 0.25)}"><image clip-path="url(#f{k})" href="{after}" x="{fx}" y="{base - fh}" width="{fw}" height="{fh}" preserveAspectRatio="xMidYMid slice"/>'
                     f'<rect class="sz{k}" style="{d(2.0 + k * 1.2)}" x="{fx - 3}" y="{base - fh - 3}" width="{fw + 6}" height="{fh + 6}" rx="10" fill="none" stroke="{BLUE}" stroke-width="3" opacity="0"/>'
                     f'<text x="{fx + fw / 2}" y="{base + 30}" text-anchor="middle" font-family="J" font-weight="500" font-size="15" fill="{SLATE}">{lab}</text></g>')
            fx += fw + 18
        return "".join(s)

    arts = [art1, art2, art3]
    parts = [f'<rect width="{W}" height="{H}" fill="{WARM}"/>']
    for i in range(3):
        parts.append(_card(i, rtl, titles[i], caps[i], arts[i], 0.1 + i * 0.25))
    parts.append(_arrows(rtl, 0.7))
    extra = STEP_CSS + _pick_css(5)
    for k in range(3):
        extra += _cycle_css(f"sz{k}", 3, 3.6).replace(f".sz{k}{{", f".sz{k}{{").replace("infinite both}", "infinite both}", 1)
    # stagger the size rings so they light up one after another
    text = "".join(titles) + "".join("".join(c) for c in caps) + "".join(bubble) + "0123456789:"
    css = font_css(text, {"M", "R", "J"}) + BASE_CSS + extra
    return svg(W, H, css, "".join(parts), "How it works" if not rtl else "بتشتغل إزاي")


def install_steps(lang, skill="social-cover-studio"):
    rtl = lang == "ar"
    W, H = 1600, 520
    if rtl:
        titles = ["حمّل ملف الـ ZIP", "شغّل Code execution", "ارفع الـ Skill"]
        caps = [["ملف واحد، ومن غير ما تفكه."], ["Settings → Capabilities"], ["Customize → Skills → +"]]
        uploaded = "اترفعت"
    else:
        titles = ["Download the ZIP", "Turn on code execution", "Upload the skill"]
        caps = [["One file. Don't unzip it."], ["Settings → Capabilities"], ["Customize → Skills → +"]]
        uploaded = "Added"
    fname = f"{skill}.zip"

    def art1(x, y):
        cx = x + CARD_W / 2
        return (f'<g class="bob"><path d="M{cx} {y + 50} v34 m-14 -14 l14 14 l14 -14" fill="none" stroke="{BLUE}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/></g>'
                f'<g class="pop" style="{d(0.8)}"><rect x="{cx - 70}" y="{y + 104}" width="140" height="150" rx="16" fill="#FFFFFF" stroke="{SOFT}" stroke-width="2"/>'
                f'<rect x="{cx - 70}" y="{y + 104}" width="140" height="40" rx="16" fill="{BLUE}"/><rect x="{cx - 70}" y="{y + 124}" width="140" height="20" fill="{BLUE}"/>'
                + "".join(f'<rect x="{cx - 5}" y="{y + 150 + k * 12}" width="10" height="6" rx="2" fill="{SLATE}" opacity=".55"/>' for k in range(4))
                + f'<text x="{cx}" y="{y + 130}" text-anchor="middle" font-family="M" font-weight="800" font-size="18" fill="#FFFFFF">ZIP</text>'
                f'<text x="{cx}" y="{y + 278}" text-anchor="middle" font-family="J" font-weight="500" font-size="13" fill="{SLATE}">{fname}</text></g>')

    def art2(x, y):
        px, pw = x + 36, CARD_W - 72
        label = "Code execution and file creation"
        if rtl:
            tgx, lx, la = px + 22, px + pw - 22, "end"
        else:
            tgx, lx, la = px + pw - 22 - 56, px + 22, "start"
        return (f'<g class="pop" style="{d(0.8)}"><rect x="{px}" y="{y + 110}" width="{pw}" height="92" rx="14" fill="#FFFFFF" stroke="{SOFT}" stroke-width="2"/>'
                f'<text x="{lx}" y="{y + 148}" text-anchor="{la}" font-family="R" font-weight="500" font-size="15" fill="{GRAPHITE}">{label}</text>'
                f'<text x="{lx}" y="{y + 172}" text-anchor="{la}" font-family="R" font-weight="400" font-size="13" fill="{SLATE}">Settings → Capabilities</text>'
                f'<rect class="track" x="{tgx}" y="{y + 141}" width="56" height="30" rx="15" fill="#C9CED6"/>'
                f'<circle class="knob" cx="{tgx + 15}" cy="{y + 156}" r="11" fill="#FFFFFF"/></g>')

    def art3(x, y):
        px, pw = x + 36, CARD_W - 72
        hx, ha = (px + pw - 20, "end") if rtl else (px + 20, "start")
        plus_x = px + 30 if rtl else px + pw - 30
        row_tx, row_a = (px + pw - 44, "end") if rtl else (px + 44, "start")
        dot_x = px + pw - 26 if rtl else px + 26
        return (f'<g class="pop" style="{d(0.8)}"><rect x="{px}" y="{y + 70}" width="{pw}" height="190" rx="14" fill="#FFFFFF" stroke="{SOFT}" stroke-width="2"/>'
                f'<text x="{hx}" y="{y + 106}" text-anchor="{ha}" font-family="M" font-weight="700" font-size="18" fill="{GRAPHITE}">Skills</text>'
                f'<circle cx="{plus_x}" cy="{y + 100}" r="15" fill="{BLUE}"/><path d="M{plus_x - 7} {y + 100} h14 M{plus_x} {y + 93} v14" stroke="#fff" stroke-width="2.6" stroke-linecap="round"/>'
                f'<line x1="{px + 16}" y1="{y + 124}" x2="{px + pw - 16}" y2="{y + 124}" stroke="{SOFT}"/>'
                f'<g class="drop"><rect x="{px + pw / 2 - 90}" y="{y + 146}" width="180" height="40" rx="10" fill="{ICE}"/>'
                f'<text x="{px + pw / 2}" y="{y + 171}" text-anchor="middle" font-family="J" font-weight="500" font-size="13" fill="{DEEP}">{fname}</text></g>'
                f'<g class="row"><circle cx="{dot_x}" cy="{y + 220}" r="6" fill="{MINT}"/>'
                f'<text x="{row_tx}" y="{y + 225}" text-anchor="{row_a}" font-family="J" font-weight="500" font-size="14" fill="{GRAPHITE}">{skill}</text>'
                f'<text x="{px + 20 if rtl else px + pw - 20}" y="{y + 225}" text-anchor="{"start" if rtl else "end"}" font-family="R" font-weight="600" font-size="14" fill="#12A37F">{uploaded} ✓</text></g></g>')

    arts = [art1, art2, art3]
    parts = [f'<rect width="{W}" height="{H}" fill="{WARM}"/>']
    for i in range(3):
        parts.append(_card(i, rtl, titles[i], caps[i], arts[i], 0.1 + i * 0.25))
    parts.append(_arrows(rtl, 0.7))
    text = "".join(titles) + "".join("".join(c) for c in caps) + fname + skill + uploaded + " ✓" + "Code execution and file creationSettings → CapabilitiesSkillsZIP0123456789"
    css = font_css(text, {"M", "R", "J"}) + BASE_CSS + STEP_CSS
    return svg(W, H, css, "".join(parts), "Install in three steps" if not rtl else "التسطيب في 3 خطوات")


# ---------- main page pieces ----------

def _wrap(text, file, size, max_w):
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if width(file, trial, size) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def width_mixed(text, size, weight=400):
    ar = f"readex-pro-arabic-{weight}-normal.woff2"
    lat = f"readex-pro-latin-{min(weight, 600)}-normal.woff2"
    return sum(width(ar if "\u0600" <= c <= "\u08FF" else lat, c, size) for c in text)


def _wrap_ar(text, size, max_w):
    # Arabic glyph widths are measured on isolated forms, so keep a safety margin
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if width_mixed(trial, size) <= max_w * 0.9 or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def stage_card(stage, lang):
    rtl = lang == "ar"
    W, H = 560, 236
    skills = stage["skills"]
    ready = sum(1 for s in skills if s["status"] == "available")
    soon = len(skills) - ready
    pad = 30
    X = W - pad if rtl else pad
    num = stage["id"][:2]
    name = stage["name"]
    summary = stage["summary_ar"] if rtl else stage["summary"]
    lines = (_wrap_ar(summary, 16, W - 2 * pad) if rtl else _wrap(summary, "readex-pro-latin-400-normal.woff2", 16, W - 2 * pad))[:2]
    parts = [f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="18" fill="#FFFFFF" stroke="{SOFT}" stroke-width="2"/>']
    if ready:
        parts.append(f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="18" fill="none" stroke="{BLUE}" stroke-width="2"/>')
    nx = X
    parts.append(f'<text x="{nx}" y="{pad + 22}" text-anchor="{"end" if rtl else "start"}" font-family="J" font-weight="500" font-size="18" fill="{BLUE}">{num}</text>')
    title = name if not rtl else f"{name} · {stage['name_ar']}"
    if rtl:
        parts.append(f'<text x="{X}" y="{pad + 62}" text-anchor="start" direction="rtl" font-family="R" font-weight="600" font-size="25" fill="{GRAPHITE}">{escape(title)}</text>')
    else:
        parts.append(f'<text x="{X}" y="{pad + 62}" font-family="M" font-weight="700" font-size="25" fill="{GRAPHITE}">{escape(title)}</text>')
    for k, line in enumerate(lines):
        dirattr = ' direction="rtl"' if rtl else ""
        parts.append(f'<text x="{X}" y="{pad + 96 + k * 24}" text-anchor="start"{dirattr} font-family="R" font-weight="400" font-size="16" fill="{SLATE}">{escape(line)}</text>')
    # status pills
    pills = []
    if ready:
        pills.append((f"{ready} ready" if not rtl else f"{ready} جاهزة", MINT, "#0B5E49", True))
    pills.append((f"{soon} coming" if not rtl else f"{soon} قريباً", "#EEF1F5", SLATE, False))
    x = X
    for label, bg, fg, live in pills:
        f = "readex-pro-arabic-600-normal.woff2" if rtl else "montserrat-latin-600-normal.woff2"
        lw = (width_mixed(label, 14, 600) if rtl else width(f, label, 14)) + (18 if live else 0)
        pw = lw + 28
        x0 = x - pw if rtl else x
        dot = ""
        if live:
            dx = x0 + pw - 18 if rtl else x0 + 16
            dot = f'<circle class="pulse" cx="{dx}" cy="{H - pad - 15}" r="4.5" fill="#0B5E49"/>'
        tx = x0 + pw - 14 - (18 if live else 0) if rtl else x0 + 14 + (18 if live else 0)
        ta = 'text-anchor="start" direction="rtl"' if rtl else ""
        parts.append(f'<rect x="{x0:.1f}" y="{H - pad - 30}" width="{pw:.1f}" height="30" rx="15" fill="{bg if live else bg}" opacity="{".35" if live else "1"}"/>{dot}'
                     f'<text x="{tx:.1f}" y="{H - pad - 10}" {ta} font-family="{"R" if rtl else "M"}" font-weight="600" font-size="14" fill="{fg}">{escape(label)}</text>')
        x = x0 - 10 if rtl else x0 + pw + 10
    arrow_x = pad + 6 if rtl else W - pad - 6
    arrow = f'M{arrow_x + 8} {pad + 12} L{arrow_x} {pad + 20} L{arrow_x + 8} {pad + 28}' if rtl else f'M{arrow_x - 8} {pad + 12} L{arrow_x} {pad + 20} L{arrow_x - 8} {pad + 28}'
    parts.append(f'<path d="{arrow}" fill="none" stroke="{SLATE}" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/>')
    text = num + title + "".join(lines) + "".join(p[0] for p in pills)
    css = font_css(text, {"M", "R", "J"}) + BASE_CSS
    return svg(W, H, css, "".join(parts), title)


def button(label, kind, lang, icon=None):
    rtl = lang == "ar"
    f = "readex-pro-arabic-600-normal.woff2" if rtl and any("؀" <= c <= "ࣿ" for c in label) else "montserrat-latin-700-normal.woff2"
    tw = width(f, label, 16)
    ic = 26 if icon else 0
    W, H = int(tw + 48 + ic), 48
    fill, fg, stroke = {"primary": (BLUE, "#FFFFFF", BLUE), "dark": (GRAPHITE, "#FFFFFF", GRAPHITE), "ghost": ("#FFFFFF", GRAPHITE, "#D0D5DD")}[kind]
    parts = [f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="{(H - 2) / 2}" fill="{fill}" stroke="{stroke}"/>']
    cx = W / 2 + (ic / 2 if not rtl else -ic / 2)
    if icon == "star":
        sx = 24 if not rtl else W - 24
        pts = []
        import math
        for k in range(10):
            r = 8 if k % 2 == 0 else 3.6
            a = -math.pi / 2 + k * math.pi / 5
            pts.append(f"{sx + r * math.cos(a):.1f},{24 + r * math.sin(a):.1f}")
        parts.append(f'<polygon points="{" ".join(pts)}" fill="{"#F5B301" if kind != "primary" else "#FFFFFF"}"/>')
    elif icon == "down":
        sx = 24 if not rtl else W - 24
        parts.append(f'<path d="M{sx} 15 v14 m-6 -6 l6 6 l6 -6 M{sx - 8} 33 h16" fill="none" stroke="{fg}" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/>')
    elif icon == "grid":
        sx = 18 if not rtl else W - 30
        parts.append("".join(f'<rect x="{sx + (k % 2) * 7}" y="{17 + (k // 2) * 7}" width="5" height="5" rx="1" fill="{fg}"/>' for k in range(4)))
    fam = "R" if f.startswith("readex") else "M"
    parts.append(f'<text x="{cx:.1f}" y="30" text-anchor="middle" font-family="{fam}" font-weight="{600 if fam == "R" else 700}" font-size="16" fill="{fg}">{escape(label)}</text>')
    css = font_css(label, {"M", "R"})
    return svg(W, H, css, "".join(parts), label)


def principles(lang):
    rtl = lang == "ar"
    W, H = 1600, 250
    items = ([("The AI suggests. You decide.", "Nothing is published without your approval."),
              ("Real over generated.", "Real photos, tests and numbers."),
              ("One source, many formats.", "Write once; every platform gets its cut."),
              ("Verified before published.", "Checked against official sources.")] if not rtl else
             [("الـ AI يقترح، وإنت تقرر.", "مفيش حاجة بتتنشر من غير موافقتك."),
              ("الحقيقي قبل المتولّد.", "صور وتجارب وأرقام حقيقية."),
              ("مصدر واحد، وفورماتات كتير.", "بتكتبها مرة، وكل منصة تاخد نسختها."),
              ("بنراجع قبل ما ننشر.", "من المصادر الرسمية.")])
    gap, n = 20, 4
    cw = (W - 100 - gap * (n - 1)) / n
    parts = [f'<rect width="{W}" height="{H}" fill="{WARM}"/>']
    for i, (tt, sub) in enumerate(items):
        c = (n - 1 - i) if rtl else i
        x = 50 + c * (cw + gap)
        X = x + cw - 26 if rtl else x + 26
        a = 'text-anchor="start" direction="rtl"' if rtl else ""
        tfam, tw_ = ("R", 600) if rtl else ("M", 700)
        tl = _wrap_ar(tt, 21, cw - 52) if rtl else _wrap(tt, "montserrat-latin-700-normal.woff2", 21, cw - 52)
        sl = _wrap_ar(sub, 16, cw - 52) if rtl else _wrap(sub, "readex-pro-latin-400-normal.woff2", 16, cw - 52)
        g = [f'<rect x="{x:.1f}" y="30" width="{cw:.1f}" height="{H - 60}" rx="18" fill="#FFFFFF" stroke="{SOFT}"/>',
             f'<rect x="{(x + cw - 26 - 30) if rtl else (x + 26):.1f}" y="56" width="30" height="4" rx="2" fill="{BLUE if i else MINT}"/>']
        for k, l in enumerate(tl[:2]):
            g.append(f'<text x="{X:.1f}" y="{100 + k * 28}" {a} font-family="{tfam}" font-weight="{tw_}" font-size="21" fill="{GRAPHITE}">{escape(l)}</text>')
        y0 = 100 + len(tl[:2]) * 28 + 10
        for k, l in enumerate(sl[:2]):
            g.append(f'<text x="{X:.1f}" y="{y0 + k * 23}" {a} font-family="R" font-weight="400" font-size="16" fill="{SLATE}">{escape(l)}</text>')
        parts.append(f'<g class="fu" style="{d(0.1 + i * 0.12)}">' + "".join(g) + "</g>")
    text = "".join(a + b for a, b in items)
    css = font_css(text, {"M", "R"}) + BASE_CSS
    return svg(W, H, css, "".join(parts), "Principles" if not rtl else "المبادئ")


def skill_card(stage, skill, lang):
    """Compact card for 'Available now' on the main page (light, so it never competes with the hero)."""
    rtl = lang == "ar"
    W, H, pad = 560, 236, 22
    thumb_path = ROOT / "docs" / skill["slug"] / "after.jpg"
    tw, th = 112, H - 2 * pad
    tx = W - pad - tw if rtl else pad
    X = tx - 24 if rtl else tx + tw + 24
    a = 'text-anchor="start" direction="rtl"' if rtl else ""
    anchor_end = 'text-anchor="end"' if rtl else ""
    parts = [f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="18" fill="#FFFFFF" stroke="{BLUE}" stroke-width="2"/>']
    if thumb_path.exists():
        img = "data:image/jpeg;base64," + base64.b64encode(thumb_path.read_bytes()).decode()
        parts.append(f'<clipPath id="th"><rect x="{tx}" y="{pad}" width="{tw}" height="{th}" rx="12"/></clipPath>'
                     f'<image clip-path="url(#th)" href="{img}" x="{tx}" y="{pad}" width="{tw}" height="{th}" preserveAspectRatio="xMidYMid slice"/>'
                     f'<g clip-path="url(#th)"><rect class="shine" x="{tx + tw / 2 - 20}" y="{pad - 30}" width="40" height="{th + 60}" fill="#FFFFFF" opacity=".22"/></g>')
    step = f" · STEP {skill['step']}" if skill.get("step") else ""
    eyebrow = f"{stage['id'][:2]} · {stage['name'].upper()}{step}"
    parts.append(f'<text x="{X}" y="{pad + 24}" {anchor_end} font-family="J" font-weight="500" font-size="13" letter-spacing="1.4" fill="{BLUE}">{escape(eyebrow)}</text>')
    parts.append(f'<text x="{X}" y="{pad + 62}" {anchor_end} font-family="M" font-weight="700" font-size="26" fill="{GRAPHITE}">{escape(skill["name"])}</text>')
    desc = skill["desc_ar"] if rtl else skill["desc"]
    avail = W - 2 * pad - tw - 24
    lines = (_wrap_ar(desc, 16, avail) if rtl else _wrap(desc, "readex-pro-latin-400-normal.woff2", 16, avail))[:3]
    for k, line in enumerate(lines):
        parts.append(f'<text x="{X}" y="{pad + 96 + k * 23}" {a} font-family="R" font-weight="400" font-size="16" fill="{SLATE}">{escape(line)}</text>')
    pills = [("Free" if skill["tier"] == "free" else "Pro", "#DCF8EF", "#0B5E49", True), ("Ready" if not rtl else "جاهزة", "#EEF1F5", SLATE, False)]
    x = X
    for label, bg, fg, live in pills:
        f = "readex-pro-arabic-600-normal.woff2" if any("؀" <= c <= "ࣿ" for c in label) else "montserrat-latin-600-normal.woff2"
        lw = (width_mixed(label, 14, 600) if f.startswith("readex") else width(f, label, 14)) + (16 if live else 0)
        pw = lw + 26
        x0 = x - pw if rtl else x
        dot = ""
        if live:
            dx = x0 + pw - 16 if rtl else x0 + 15
            dot = f'<circle class="pulse" cx="{dx}" cy="{H - pad - 15}" r="4.5" fill="#12A37F"/>'
        tx2 = x0 + pw - 13 - (16 if live else 0) if rtl else x0 + 13 + (16 if live else 0)
        ta = 'text-anchor="start" direction="rtl"' if rtl else ""
        fam = "R" if f.startswith("readex") else "M"
        parts.append(f'<rect x="{x0:.1f}" y="{H - pad - 30}" width="{pw:.1f}" height="30" rx="15" fill="{bg}"/>{dot}'
                     f'<text x="{tx2:.1f}" y="{H - pad - 10}" {ta} font-family="{fam}" font-weight="600" font-size="14" fill="{fg}">{escape(label)}</text>')
        x = x0 - 10 if rtl else x0 + pw + 10
    text = eyebrow + skill["name"] + "".join(lines) + "".join(p[0] for p in pills)
    css_extra = (".shine{animation:shine 4.5s ease-in-out infinite both;animation-delay:1s}"
                 f"@keyframes shine{{0%{{transform:translateX(-{tw + 60}px) skewX(-18deg)}}35%,100%{{transform:translateX({tw + 60}px) skewX(-18deg)}}}}")
    css = font_css(text, {"M", "R", "J"}) + BASE_CSS + css_extra
    return svg(W, H, css, "".join(parts), f"{skill['name']} — {desc}")


def coming_card(catalog, lang):
    rtl = lang == "ar"
    W, H, pad = 560, 236, 26
    nxt = [s["name"] for st in catalog["stages"] for s in st["skills"] if s["status"] != "available" and s["tier"] == "free"][:3]
    X = W - pad if rtl else pad
    a = 'text-anchor="start" direction="rtl"' if rtl else ""
    ae = 'text-anchor="end"' if rtl else ""
    parts = [f'<rect x="1.5" y="1.5" width="{W - 3}" height="{H - 3}" rx="18" fill="#FAFAF8" stroke="#C9CED6" stroke-width="2" stroke-dasharray="7 7"/>']
    eyebrow = "COMING NEXT"
    title = "Next free skills" if not rtl else "الـ Skills المجانية الجاية"
    sub = "Watch → Releases to get them first." if not rtl else "اعمل Watch ← Releases عشان توصلك أول ما تنزل."
    parts.append(f'<text x="{X}" y="{pad + 22}" {ae} font-family="J" font-weight="500" font-size="13" letter-spacing="1.4" fill="{SLATE}">{eyebrow}</text>')
    if rtl:
        parts.append(f'<text x="{X}" y="{pad + 58}" {a} font-family="R" font-weight="600" font-size="24" fill="{GRAPHITE}">{escape(title)}</text>')
    else:
        parts.append(f'<text x="{X}" y="{pad + 58}" font-family="M" font-weight="700" font-size="24" fill="{GRAPHITE}">{escape(title)}</text>')
    for k, name in enumerate(nxt):
        cy = pad + 92 + k * 30
        dx = X - 6 if rtl else X + 6
        parts.append(f'<g class="fi" style="{d(0.3 + k * 0.25)}"><circle cx="{dx}" cy="{cy - 5}" r="5" fill="none" stroke="{BLUE}" stroke-width="2"/>'
                     f'<text x="{X - 22 if rtl else X + 22}" y="{cy}" {ae} font-family="M" font-weight="600" font-size="17" fill="{GRAPHITE}">{escape(name)}</text></g>')
    parts.append(f'<text x="{X}" y="{H - pad + 2}" {a} font-family="R" font-weight="400" font-size="15" fill="{SLATE}">{escape(sub)}</text>')
    text = eyebrow + title + sub + "".join(nxt)
    css = font_css(text, {"M", "R", "J"}) + BASE_CSS
    return svg(W, H, css, "".join(parts), title)


def build_main_page_art():
    import json
    catalog = json.loads((ROOT / "catalog.json").read_text(encoding="utf-8"))
    stages_dir = OUT / "stages"
    stages_dir.mkdir(parents=True, exist_ok=True)
    skills_dir = OUT / "skills"
    skills_dir.mkdir(parents=True, exist_ok=True)
    for st in catalog["stages"]:
        for lang in ("en", "ar"):
            (stages_dir / f"{st['id']}-{lang}.svg").write_text(stage_card(st, lang), encoding="utf-8")
            for sk in st["skills"]:
                if sk["status"] == "available":
                    (skills_dir / f"{sk['slug']}-{lang}.svg").write_text(skill_card(st, sk, lang), encoding="utf-8")
    for lang in ("en", "ar"):
        (skills_dir / f"coming-{lang}.svg").write_text(coming_card(catalog, lang), encoding="utf-8")
    btns = {
        "en": [("download", "Download ZIP", "primary", "down"), ("more", "How it works", "ghost", None), ("guide", "Guide PDF", "ghost", None), ("watch", "Get notified", "dark", None),
               ("browse", "Browse skills", "primary", "grid"), ("install", "Install", "ghost", "down"), ("star", "Star the repo", "ghost", "star")],
        "ar": [("download", "حمّل الـ ZIP", "primary", "down"), ("more", "اعرف أكتر", "ghost", None), ("guide", "الدليل PDF", "ghost", None), ("watch", "وصّلني الجديد", "dark", None),
               ("browse", "تصفّح الـ Skills", "primary", "grid"), ("install", "التسطيب", "ghost", "down"), ("star", "Star للريبو", "ghost", "star")],
    }
    for lang, items in btns.items():
        for key, label, kind, icon in items:
            (OUT / f"btn-{key}-{lang}.svg").write_text(button(label, kind, lang, icon), encoding="utf-8")
    for lang in ("en", "ar"):
        (OUT / f"principles-{lang}.svg").write_text(principles(lang), encoding="utf-8")
        (OUT / f"install-{lang}.svg").write_text(install_steps(lang, "any-skill"), encoding="utf-8")
    print(f"built main page art: {len(catalog['stages'])} stage cards, buttons, principles, install cards")


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    build_main_page_art()
    for name, content in (("banner-en.svg", banner("en")), ("banner-ar.svg", banner("ar")),
                          ("flow-en.svg", flow("en")), ("flow-ar.svg", flow("ar"))):
        (OUT / name).write_text(content, encoding="utf-8")
        print(f"built docs/assets/{name} ({len(content.encode()) // 1024} KB)")
    for lang in ("en", "ar"):
        for active in (True, False):
            name = f"lang-{lang}-{'on' if active else 'off'}.svg"
            (OUT / name).write_text(lang_button(lang, active), encoding="utf-8")
            print(f"built docs/assets/{name}")
    for lang in ("en", "ar"):
        for name, fn in (("how", how_it_works), ("install", install_steps)):
            target = ROOT / "docs" / "social-cover-studio" / f"{name}-{lang}.svg"
            content = fn(lang)
            target.write_text(content, encoding="utf-8")
            print(f"built docs/social-cover-studio/{name}-{lang}.svg ({len(content.encode()) // 1024} KB)")
    for lang in ("en", "ar"):
        target = ROOT / "docs" / "social-cover-studio" / f"hero-{lang}.svg"
        content = cover_hero(lang)
        target.write_text(content, encoding="utf-8")
        print(f"built docs/social-cover-studio/hero-{lang}.svg ({len(content.encode()) // 1024} KB)")
