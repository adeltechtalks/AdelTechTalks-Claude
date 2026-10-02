"""AdelTechTalks — Morphing UI template: 'how to make a motion video with Claude' (30s, 9:16)"""
import sys, math, subprocess, time, glob
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # skill root, so the engine package is importable
from engine import config
from PIL import Image, ImageDraw, ImageFilter
from engine.plib import UP, txt, CAIRO, MONT, READ, MONO, GRAPH, WHITE, CORAL

W, H, FPS, DUR = 1080, 1920, 30, 32.0
BG = (246, 246, 244); SIG = (37, 99, 235); BLUE4 = (91, 142, 244); MINT = (45, 212, 168)
SLATE = (102, 112, 133); LIGHTB = (232, 234, 238); CX, CY = 540, 960

def clamp(v, a, b): return max(a, min(b, v))
def prog(t, s, d): return clamp((t - s) / d, 0, 1)
def ease(p): return 1 - (1 - p) ** 3
def spring(p): return 1 - math.exp(-7 * p) * math.cos(8 * p) if p < 1 else 1.0
def lerp(a, b, p): return a + (b - a) * p
def lerpc(a, b, p): return tuple(int(lerp(x, y, p)) for x, y in zip(a, b))
def fit(im, w=None, h=None):
    r = (w / im.width) if w else (h / im.height)
    return im.resize((max(1, int(im.width * r)), max(1, int(im.height * r))), Image.LANCZOS)
def recolor(im, col):
    o = Image.new('RGBA', im.size, col + (255,)); o.putalpha(im.split()[3]); return o
def put(f, spr, cx, cy, a=1.0, s=1.0):
    if a <= 0.01 or s <= 0.01: return
    im = spr if abs(s - 1) < 0.003 else spr.resize((max(1, int(spr.width * s)), max(1, int(spr.height * s))), Image.BICUBIC)
    if a < 0.999: im = im.copy(); im.putalpha(im.split()[3].point(lambda v: int(v * a)))
    f.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2)))
def put_r(f, spr, rx, cy, a=1.0):  # right-aligned (for RTL text)
    put(f, spr, rx - spr.width / 2, cy, a)
def put_l(f, spr, lx, cy, a=1.0):
    put(f, spr, lx + spr.width / 2, cy, a)

def box(f, cx, cy, w, h, r, col, shadow=True, alpha=1.0):
    w, h = int(w), int(h)
    if w < 4 or h < 4 or alpha <= 0.01: return
    r = min(r, w / 2, h / 2); x0, y0 = int(cx - w / 2), int(cy - h / 2)
    if shadow:
        q = 4; sw, sh = w // q + 20, h // q + 20
        m = Image.new('L', (sw, sh), 0)
        ImageDraw.Draw(m).rounded_rectangle((10, 10, 10 + w // q, 10 + h // q), int(r / q), fill=int(70 * alpha))
        m = m.filter(ImageFilter.GaussianBlur(6)).resize((sw * q, sh * q), Image.BICUBIC)
        sl = Image.new('RGBA', m.size, (20, 26, 40, 255)); sl.putalpha(m); f.alpha_composite(sl, (x0 - 40, y0 - 40 + 22))
    s = 2; im = Image.new('RGBA', (w * s, h * s), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle((0, 0, w * s - 1, h * s - 1), int(r * s), fill=col + (int(255 * alpha),))
    f.alpha_composite(im.resize((w, h), Image.LANCZOS), (x0, y0))

def vis(t, t_in, t_out, delay=0.2, dur=0.3):
    a = ease(prog(t, t_in + delay, dur)) * (1 - prog(t, t_out - 0.18, 0.18)); return a, 24 * (1 - ease(prog(t, t_in + delay, dur)))

# ---------- assets ----------
MARK = recolor(fit(Image.open(config.asset('atc-mark-white-1024.png')).convert('RGBA'), w=64), GRAPH)
MARK_W = fit(Image.open(config.asset('atc-mark-white-1024.png')).convert('RGBA'), w=54)
RES = [fr for fr in config.input_frames('result')]

def words(line, size, col=GRAPH, hi=(), hi_col=SIG, font=CAIRO):
    out = []
    for w_ in line.split(' '):
        out.append(txt(w_, font(size), hi_col if w_ in hi else col, rtl=True))
    return out
H1 = words('ينفع تعمل موشن جرافيك', 70)
H2 = words('من غير ولا برنامج؟', 70, hi=('برنامج؟', 'ولا'))
def kinetic(f, t, ws, cy, t0, t_out, gap=26, stagger=0.12):
    total = sum(w.width for w in ws) + gap * (len(ws) - 1); x = CX + total / 2
    a_out = 1 - prog(t, t_out, 0.2)
    for i, w_ in enumerate(ws):
        p = prog(t, t0 + i * stagger, 0.35)
        if p > 0:
            e = ease(p); put_r(f, w_, x, cy + 40 * (1 - e) - 30 * prog(t, t_out, 0.2), min(1, p * 2.5) * a_out)
        x -= w_.width + gap

PILL_T = txt('Motion Graphics', MONT(46), GRAPH)
CHAT_TITLE = txt('Claude', MONT(34), WHITE)
TYPE_WORDS = 'اعملي ريل 30 ثانية لكود الخصم بتاعي'.split(' ')
TYPE_SPR = [txt(w_, READ(38, 500), WHITE, rtl=True) for w_ in TYPE_WORDS]
BUBBLE_T = txt('اعملي ريل 30 ثانية لكود الخصم بتاعي', READ(36, 500), WHITE, rtl=True)
HEAD3 = txt('ابعتله ريفرنس وصورك', CAIRO(70), GRAPH, rtl=True)
CHIPS = [txt(s_, MONT(36), SIG) for s_ in ('reel.mp4', 'photo.jpg', 'logos.png')]
PLUS = txt('+', MONT(60), GRAPH)
UPL = txt('ارفع ملفاتك هنا', READ(40, 500), SLATE, rtl=True)
HEAD4 = txt('Claude بيكتب الكود ويرندر', CAIRO(66), GRAPH, rtl=True)
HEAD4b = txt('Claude', MONT(64), SIG)
CODE = [
    [('scene', WHITE), (' = ', SLATE), ('Paper', BLUE4), ('(style=', WHITE), ('"collage"', MINT), (')', WHITE)],
    [('scene', WHITE), ('.add(', WHITE), ('photo', BLUE4), (', code=', WHITE), ('"ATT001"', MINT), (')', WHITE)],
    [('scene', WHITE), ('.sfx(', WHITE), ('"paper"', MINT), (', ', WHITE), ('"pop"', MINT), (')', WHITE)],
    [('render', BLUE4), ('(', WHITE), ('"reel.mp4"', MINT), (', fps=', WHITE), ('30', CORAL if False else (255, 196, 120)), (')', WHITE)],
]
MF = MONO(32)
def code_line(parts):
    total = sum(MF.getlength(p) for p, _ in parts)
    out = Image.new('RGBA', (int(total) + 20, 56), (0, 0, 0, 0)); d = ImageDraw.Draw(out); x = 0
    for s_, c in parts:
        d.text((x, 8), s_, font=MF, fill=c); x += MF.getlength(s_)
    return out
CODE_SPR = [code_line(l) for l in CODE]
HEAD5 = txt('مش عاجبك؟ قوله يعدّل', CAIRO(70), GRAPH, rtl=True)
BUBS = [('r', 'الألوان باهتة شوية'), ('l', 'تمام، شلت الشادوز وظبطت الألوان'), ('r', 'تحفة!')]
BUB_SPR = [(side, txt(s_, READ(38, 500), WHITE if side == 'r' else GRAPH, rtl=True)) for side, s_ in BUBS]
HEAD6 = txt('والنتيجة', CAIRO(76), GRAPH, rtl=True)
HEAD7 = txt('بالحركة والـ SFX كمان', READ(56, 700), GRAPH, rtl=True)
TRACKS = [('Motion', SIG), ('SFX', MINT), ('Music', (255, 176, 66))]
TRK_L = [txt(n, MONO(30), SLATE) for n, _ in TRACKS]
HEAD8 = txt('عايز نفس السكيل؟', CAIRO(80), GRAPH, rtl=True)
H4W = [txt(w_, CAIRO(66), SIG if w_ == 'Claude' else GRAPH, rtl=True) for w_ in 'Claude بيكتب الكود ويرندر'.split(' ')]
H8W = [txt(w_, CAIRO(80), GRAPH, rtl=True) for w_ in 'عايز نفس السكيل؟'.split(' ')]
CTA_T = txt('تابع AdelTechTalks', CAIRO(54), WHITE, rtl=True)
from PIL import ImageOps
_src = ImageOps.exif_transpose(config.input_image('photo.jpg', (2000, 2100), 'the portrait photo')).convert('RGB').crop((610, 310, 1510, 1210)).resize((176, 176), Image.LANCZOS)
_m = Image.new('L', (528, 528), 0); ImageDraw.Draw(_m).ellipse((0, 0, 527, 527), fill=255)
AVATAR = _src.convert('RGBA'); AVATAR.putalpha(_m.resize((176, 176), Image.LANCZOS))
NAME = txt('AdelTechTalks', MONT(52), GRAPH)
# comment card: [اكتب] [SKILL box] [في الكومنتات] + small promise line
_c1 = txt('اكتب', CAIRO(52), GRAPH, rtl=True); _c2 = txt('في الكومنتات', CAIRO(52), GRAPH, rtl=True)
_c3 = txt('وهبعتلك السكيل كاملة بالشرح', READ(32, 500), SLATE, rtl=True)
_kw_w = int(MONT(54).getlength('SKILL')) + 60
_cw = _c1.width + _kw_w + _c2.width + 140; CMT_CARD = Image.new('RGBA', (_cw * 2, 400), (0, 0, 0, 0))
ImageDraw.Draw(CMT_CARD).rounded_rectangle((0, 0, _cw * 2 - 1, 399), 60, fill=(255, 255, 255, 255))
CMT_CARD = CMT_CARD.resize((_cw, 200), Image.LANCZOS)
_x = _cw - 50 - _c1.width; CMT_CARD.alpha_composite(_c1, (_x, 34))
_bx1 = _x - 20; _bx0 = _bx1 - _kw_w
_d = ImageDraw.Draw(CMT_CARD); _d.rounded_rectangle((_bx0, 26, _bx1, 106), 22, fill=SIG + (255,))
CMT_CARD.alpha_composite(_c2, (_bx0 - 20 - _c2.width, 34))
CMT_CARD.alpha_composite(_c3, ((_cw - _c3.width) // 2, 128))
KW_X = (_bx0 + _bx1) / 2 - _cw / 2
_sh = Image.new('RGBA', (CMT_CARD.width + 60, CMT_CARD.height + 70), (0, 0, 0, 0)); _m = CMT_CARD.split()[3].point(lambda v: v * 60 // 255)
_k = Image.new('RGBA', CMT_CARD.size, (20, 26, 40, 255)); _k.putalpha(_m); _sh.alpha_composite(_k, (30, 44)); _sh = _sh.filter(ImageFilter.GaussianBlur(14)); _sh.alpha_composite(CMT_CARD, (30, 30)); CMT_CARD = _sh
LOGO_END = recolor(fit(Image.open(config.asset('atc-mark-white-1024.png')).convert('RGBA'), w=150), SIG)
SUB = txt('Tech Explorer', READ(32, 500), SLATE)
FOLLOW = txt('+ Follow', MONT(40), WHITE)
FOLLOWING = txt('Following', MONT(38), WHITE)

def cursor():
    s = 3; im = Image.new('RGBA', (40 * s, 52 * s), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    pts = [(2, 2), (2, 42), (12, 32), (19, 48), (26, 45), (19, 30), (33, 30)]
    d.polygon([(x * s, y * s) for x, y in pts], fill=GRAPH, outline=WHITE); d.line([(x * s, y * s) for x, y in pts + [pts[0]]], fill=WHITE, width=2 * s)
    return im.resize((40, 52), Image.LANCZOS)
CURSOR = cursor()


# ================= ambient motion (no empty frames) =================
def _chip(label, col=GRAPH, bg=(255, 255, 255), size=30):
    t_ = txt(label, MONT(size), col) if not any('\u0600' <= ch <= '\u06ff' for ch in label) else txt(label, READ(size, 600), col, rtl=True)
    w_, h_ = t_.width + 56, t_.height + 30
    im = Image.new('RGBA', (w_ * 2, h_ * 2), (0, 0, 0, 0)); ImageDraw.Draw(im).rounded_rectangle((0, 0, w_ * 2 - 1, h_ * 2 - 1), h_, fill=bg + (255,))
    im = im.resize((w_, h_), Image.LANCZOS); im.alpha_composite(t_, (28, 15)); return im
def _strip(labels, styles):
    chips = [_chip(l, *st) for l, st in zip(labels, styles)]
    w_ = sum(c.width + 22 for c in chips); h_ = max(c.height for c in chips) + 30
    im = Image.new('RGBA', (w_, h_), (0, 0, 0, 0)); x = 0
    for c in chips:
        sh = Image.new('RGBA', (c.width + 20, c.height + 20), (0, 0, 0, 0)); m = c.split()[3].point(lambda v: v * 40 // 255)
        k = Image.new('RGBA', c.size, (30, 40, 60, 255)); k.putalpha(m); sh.alpha_composite(k, (10, 16)); sh = sh.filter(ImageFilter.GaussianBlur(6))
        im.alpha_composite(sh, (x - 10, 0)); im.alpha_composite(c, (x, 8)); x += c.width + 22
    return im
_W_, _B_, _M_ = (GRAPH, (255, 255, 255)), (WHITE, SIG), (GRAPH, (214, 247, 236))
STRIP_TOP = _strip(['Claude', 'Motion', '30 fps', 'موشن', 'SFX', '9:16', 'Render', 'كود', 'Music', 'AI'],
                   [_B_, _W_, _W_, _M_, _W_, _W_, _B_, _W_, _M_, _W_])
STRIP_BOT = _strip(['بدون مونتاج', 'Prompt', 'Code', 'Export', 'فكرة', 'Reels', 'TikTok', 'Shorts', 'سهل', 'Claude'],
                   [_M_, _W_, _W_, _B_, _W_, _W_, _W_, _W_, _M_, _B_])
def marquee(f, strip, y, speed, t):
    off = (t * speed) % strip.width
    for k in range(-1, 3):
        x = int(-off + k * strip.width) if speed > 0 else int(off - strip.width + k * strip.width)
        if x < W and x + strip.width > 0: f.alpha_composite(strip, (x, int(y)), (0, 0)) if x >= 0 else f.alpha_composite(strip.crop((-x, 0, min(strip.width, -x + W), strip.height)), (0, int(y)))

# floating mini widgets (drift + bob) living in the top/bottom bands around the explanation
def _widget(kind):
    s = 2; S = 120; im = Image.new('RGBA', (S * s, S * s), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    if kind == 'toggle':
        d.rounded_rectangle((10 * s, 36 * s, 110 * s, 84 * s), 24 * s, fill=MINT + (255,)); d.ellipse((64 * s, 40 * s, 104 * s, 80 * s), fill=(255, 255, 255, 255))
    elif kind == 'play':
        d.ellipse((14 * s, 14 * s, 106 * s, 106 * s), fill=SIG + (255,)); d.polygon([(48 * s, 38 * s), (48 * s, 82 * s), (84 * s, 60 * s)], fill=(255, 255, 255, 255))
    elif kind == 'check':
        d.ellipse((18 * s, 18 * s, 102 * s, 102 * s), fill=(255, 255, 255, 255)); d.line([(40 * s, 62 * s), (54 * s, 76 * s), (82 * s, 46 * s)], fill=SIG + (255,), width=10 * s)
    elif kind == 'bars':
        d.rounded_rectangle((10 * s, 22 * s, 110 * s, 98 * s), 18 * s, fill=(255, 255, 255, 255))
        for i, (hh, c) in enumerate(((30, SIG), (50, MINT), (40, BLUE4))): d.rounded_rectangle(((26 + i * 26) * s, (84 - hh) * s, (42 + i * 26) * s, 84 * s), 6 * s, fill=c + (255,))
    elif kind == 'note':
        d.ellipse((20 * s, 20 * s, 100 * s, 100 * s), fill=GRAPH + (255,)); d.rounded_rectangle((52 * s, 34 * s, 60 * s, 76 * s), 3 * s, fill=(255, 255, 255, 255))
        d.ellipse((38 * s, 68 * s, 60 * s, 86 * s), fill=(255, 255, 255, 255)); d.polygon([(60 * s, 34 * s), (80 * s, 42 * s), (60 * s, 48 * s)], fill=(255, 255, 255, 255))
    elif kind == 'spark':
        pts = [(60 + (46 if k % 2 == 0 else 16) * math.cos(math.radians(-90 + 45 * k)), 60 + (46 if k % 2 == 0 else 16) * math.sin(math.radians(-90 + 45 * k))) for k in range(8)]
        d.polygon([(x * s, y * s) for x, y in pts], fill=(255, 196, 120, 255))
    im = im.resize((S, S), Image.LANCZOS)
    sh = Image.new('RGBA', (S + 40, S + 40), (0, 0, 0, 0)); m = im.split()[3].point(lambda v: v * 50 // 255)
    k = Image.new('RGBA', im.size, (30, 40, 60, 255)); k.putalpha(m); sh.alpha_composite(k, (20, 30)); sh = sh.filter(ImageFilter.GaussianBlur(8)); sh.alpha_composite(im, (20, 20))
    return sh
WIDGETS = [('toggle', 120, 470, 0.0), ('play', 950, 430, 1.3), ('check', 960, 1470, 2.1), ('bars', 130, 1480, 0.7),
           ('note', 300, 395, 2.8), ('spark', 790, 1545, 1.9)]
WSPR = {k: _widget(k) for k, *_ in WIDGETS}
def ambient(f, t):
    # dotted grid drifting slowly
    off = int((t * 12) % 60)
    if not hasattr(ambient, 'grid'):
        g = Image.new('RGBA', (W, H + 60), (0, 0, 0, 0)); gd = ImageDraw.Draw(g)
        for y in range(0, H + 60, 60):
            for x in range(30, W, 60): gd.ellipse((x - 2, y - 2, x + 2, y + 2), fill=(170, 176, 190, 70))
        ambient.grid = g
        b1 = Image.new('RGBA', (900, 900), (0, 0, 0, 0)); ImageDraw.Draw(b1).ellipse((225, 225, 675, 675), fill=(37, 99, 235, 45)); ambient.b1 = b1.filter(ImageFilter.GaussianBlur(90))
        b2 = Image.new('RGBA', (800, 800), (0, 0, 0, 0)); ImageDraw.Draw(b2).ellipse((200, 200, 600, 600), fill=(45, 212, 168, 55)); ambient.b2 = b2.filter(ImageFilter.GaussianBlur(80))
    f.alpha_composite(ambient.grid.crop((0, off, W, off + H)))
    f.alpha_composite(ambient.b1, (int(-200 + 140 * math.sin(t * 0.45)), int(-120 + 100 * math.cos(t * 0.35))))
    f.alpha_composite(ambient.b2, (int(500 + 120 * math.cos(t * 0.4)), int(1250 + 110 * math.sin(t * 0.5))))
    # marquees: top scrolls left, bottom scrolls right
    a_in = ease(prog(t, 0.3, 0.6))
    if a_in > 0:
        marquee(f, STRIP_TOP, 200 - 40 * (1 - a_in), 70, t); marquee(f, STRIP_BOT, 1640 + 40 * (1 - a_in), -70, t)
    # floating widgets: pop in staggered, bob, gently swap positions every few seconds
    for i, (k, x, y, ph) in enumerate(WIDGETS):
        p = spring(prog(t, 0.6 + i * 0.15, 0.5))
        if p <= 0: continue
        dx = 14 * math.sin(t * 0.9 + ph); dy = 18 * math.sin(t * 1.3 + ph * 2)
        fo = 1 - prog(t, 28.4, 0.4) if y > 1300 else 1
        put(f, WSPR[k], x + dx, y + dy, min(1, p * 2) * 0.95 * fo, p * (1 + 0.04 * math.sin(t * 2 + ph)))

# headline entrances from different places
def _words(spr_text, size, col=GRAPH, font=None):
    font = font or CAIRO
    return [txt(w_, font(size), col, rtl=True) for w_ in spr_text.split(' ')]
def enter(f, t, spr, cx, cy, t_in, t_out, mode, words=None):
    p = prog(t, t_in + 0.12, 0.42); e = ease(p); out = prog(t, t_out - 0.18, 0.18)
    if p <= 0 or out >= 1: return
    a = min(1, p * 2.5) * (1 - out)
    if mode == 'right': put(f, spr, cx + 700 * (1 - e), cy, a)
    elif mode == 'left': put(f, spr, cx - 700 * (1 - e), cy, a)
    elif mode == 'down': put(f, spr, cx, cy - 260 * (1 - e), a)
    elif mode == 'up': put(f, spr, cx, cy + 260 * (1 - e), a)
    elif mode == 'zoom': put(f, spr, cx, cy, a, 1.6 - 0.6 * spring(p))
    elif mode == 'words' and words:
        gap = 22; total = sum(w_.width for w_ in words) + gap * (len(words) - 1); x = cx + total / 2
        for i, w_ in enumerate(words):
            q = ease(prog(t, t_in + 0.12 + i * 0.1, 0.32)); dir_ = -1 if i % 2 else 1
            put(f, w_, x - w_.width / 2, cy + dir_ * 120 * (1 - q), min(1, q * 2.5) * (1 - out)); x -= w_.width + gap

STEP_CHIPS = [
    (4.7, 8.4, _chip('خطوة 1', WHITE, SIG, 34), 240, 590, -1),
    (8.6, 11.0, _chip('خطوة 2', WHITE, SIG, 34), 840, 870, 1),
    (11.2, 15.0, _chip('خطوة 3', WHITE, SIG, 34), 840, 1290, 1),
    (15.2, 19.0, _chip('تعديل', GRAPH, (214, 247, 236), 34), 840, 1300, 1),
    (19.4, 24.0, _chip('100% Claude', WHITE, SIG, 34), 830, 610, 1),
]
# ---------- the morphing container ----------
# (time, cx, cy, w, h, r, color)
ST = [
    (0.00, CX, CY, 0, 0, 0, GRAPH),
    (2.50, CX, CY, 44, 44, 22, GRAPH),
    (2.75, CX, CY, 560, 124, 62, WHITE),
    (4.50, CX, 960, 840, 600, 52, GRAPH),
    (8.40, CX, 1010, 860, 150, 75, WHITE),
    (11.0, CX, 1000, 860, 470, 44, GRAPH),
    (15.0, CX, 1010, 860, 520, 44, WHITE),
    (19.0, CX, 1040, 452, 794, 48, GRAPH),
    (24.0, CX, 1000, 860, 380, 44, WHITE),
    (27.0, CX, 960, 720, 500, 52, WHITE),
]
def container(t):
    idx = 0
    for i in range(len(ST)):
        if t >= ST[i][0]: idx = i
    if idx == 0: return None
    a, b = ST[idx - 1], ST[idx]
    p = spring(prog(t, b[0], 0.6)); pc = ease(prog(t, b[0], 0.35))
    vals = [lerp(a[k], b[k], p) for k in range(1, 6)]
    if idx == 1: vals = [b[1], b[2]] + [b[k] * ease(prog(t, b[0], 0.2)) for k in (3, 4, 5)]
    return vals + [lerpc(a[6], b[6], pc)]

def render(t):
    f = Image.new('RGBA', (W, H), BG + (255,))
    ambient(f, t)
    kinetic(f, t, H1, 860, 0.15, 2.3); kinetic(f, t, H2, 990, 0.75, 2.3)
    c = container(t)
    if c:
        cx, cy, w, h, r, col = c
        box(f, cx, cy, w, h, r, col)
        # B2 pill
        a, dy = vis(t, 2.75, 4.5)
        if a > 0: put(f, MARK, cx - 200, cy + dy, a); put(f, PILL_T, cx + 40, cy + dy, a)
        # B3 chat window
        a, dy = vis(t, 4.5, 8.4)
        if a > 0:
            top = cy - 300; ov = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
            d.ellipse((cx - 380, top + 34, cx - 324, top + 90), fill=(60, 64, 72, int(255 * a)))
            put(f, CHAT_TITLE, cx, top + 62 + dy, a)
            d.ellipse((cx + 324, top + 34, cx + 380, top + 90), fill=(214, 168, 60, int(255 * a)))
            # input field
            fy = cy + 210
            box(f, cx - 30, fy + dy, 700, 96, 48, (45, 49, 58), shadow=False, alpha=a)
            sent = t >= 7.35
            n = int(clamp((t - 5.2) / 0.22, 0, len(TYPE_SPR)))
            if not sent:
                x = cx + 300
                for i in range(n):
                    sp = TYPE_SPR[i]; put_r(f, sp, x, fy + dy, a); x -= sp.width + 12
                if n < len(TYPE_SPR) and int(t * 3) % 2 == 0:
                    d.rectangle((x - 4, fy - 22, x - 1, fy + 22), fill=(255, 255, 255, int(220 * a)))
            # send button
            press = 1 - 0.15 * math.sin(math.pi * prog(t, 7.2, 0.2))
            box(f, cx + 365, fy + dy, 84 * press, 84 * press, 42, SIG, shadow=False, alpha=a)
            d.polygon([(cx + 352, fy + 18), (cx + 365, fy - 16), (cx + 378, fy + 18), (cx + 365, fy + 8)], fill=(255, 255, 255, int(255 * a)))
            # cursor flies to send
            cp = prog(t, 6.6, 0.6)
            if sent:  # message becomes a bubble, Claude 'typing…'
                p = spring(prog(t, 7.35, 0.5))
                by = lerp(fy, top + 190, p)
                box(f, cx + 330 - (BUBBLE_T.width + 50) / 2, by + dy, BUBBLE_T.width + 50, 92, 46, SIG, shadow=False, alpha=a)
                put_r(f, BUBBLE_T, cx + 305, by + dy, a)
                if t > 7.75:
                    box(f, cx - 290, top + 300 + dy, 140, 70, 35, (60, 64, 72), shadow=False, alpha=a)
                    for k in range(3):
                        bb = 0.5 + 0.5 * math.sin(t * 9 - k * 0.9)
                        d.ellipse((cx - 330 + k * 30, top + 290 - bb * 6, cx - 314 + k * 30, top + 306 - bb * 6), fill=(255, 255, 255, int(255 * a)))
            f.alpha_composite(ov)
            if 0 < cp and t < 7.6:
                put(f, CURSOR, lerp(cx + 120, cx + 380, ease(cp)), lerp(cy + 420, fy + 18, ease(cp)), a * (1 - prog(t, 7.4, 0.2)))
        # B4 upload
        a, dy = vis(t, 8.4, 11.0)
        if a > 0:
            enter(f, t, HEAD3, CX, 720, 8.4, 11.0, 'right')
            put(f, PLUS, cx + 360, cy - 4 + dy, a); put(f, UPL, cx + 60, cy + dy, a)
            for i, ch in enumerate(CHIPS):
                p = prog(t, 9.0 + i * 0.28, 0.4)
                if p > 0:
                    s = spring(p); x = CX + (i - 1) * 290; y = 1180 + dy
                    box(f, x, y, (ch.width + 50) * s, 76 * s, 38, (225, 235, 255), shadow=False, alpha=a)
                    put(f, ch, x, y, a * min(1, p * 2), s)
        # B5 code + render
        a, dy = vis(t, 11.0, 15.0)
        if a > 0:
            enter(f, t, HEAD4, CX, 680, 11.0, 15.0, 'words', H4W)
            lx = cx - 380
            for i, sp in enumerate(CODE_SPR):
                p = prog(t, 11.4 + i * 0.55, 0.45)
                if p > 0:
                    cw = int(sp.width * p); crop = sp.crop((0, 0, max(1, cw), sp.height))
                    put_l(f, crop, lx, cy - 150 + i * 62 + dy, a)
            p = prog(t, 13.6, 1.2)
            if p > 0:
                ov = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov); by = cy + 150
                d.rounded_rectangle((cx - 380, by - 9, cx + 380, by + 9), 9, fill=(55, 60, 70, int(255 * a)))
                d.rounded_rectangle((cx - 380, by - 9, cx - 380 + 760 * ease(p), by + 9), 9, fill=MINT + (int(255 * a),))
                f.alpha_composite(ov)
                lab = txt(f'Rendering… {int(100 * ease(p))}%', MONO(28), (200, 206, 216))
                put_l(f, lab, cx - 380, by + 50, a)
        # B6 chat edits
        a, dy = vis(t, 15.0, 19.0)
        if a > 0:
            enter(f, t, HEAD5, CX, 650, 15.0, 19.0, 'left')
            for i, (side, sp) in enumerate(BUB_SPR):
                p = prog(t, 15.4 + i * 0.9, 0.45)
                if p > 0:
                    s = spring(p); bw = sp.width + 56; y = cy - 150 + i * 130 + dy
                    x = cx + 400 - bw / 2 if side == 'r' else cx - 400 + bw / 2
                    box(f, x, y, bw * s, 96 * s, 48, SIG if side == 'r' else LIGHTB, shadow=False, alpha=a)
                    put(f, sp, x, y, a * min(1, p * 2), s)
        # B7 result video
        a, dy = vis(t, 19.0, 24.0, delay=0.3)
        if a > 0:
            enter(f, t, HEAD6, CX, 545, 19.0, 24.0, 'zoom')
            k = int(clamp((t - 19.3) * 30, 0, len(RES) - 1))
            fr = RES[k]; s = 2; m = Image.new('L', (fr.width * s, fr.height * s), 0)
            ImageDraw.Draw(m).rounded_rectangle((0, 0, fr.width * s - 1, fr.height * s - 1), 34 * s, fill=int(255 * a))
            fr = fr.copy(); fr.putalpha(m.resize(fr.size, Image.LANCZOS))
            f.alpha_composite(fr, (int(cx - fr.width / 2), int(cy - fr.height / 2 + dy)))
        # B8 timeline
        a, dy = vis(t, 24.0, 27.0)
        if a > 0:
            enter(f, t, HEAD7, CX, 720, 24.0, 27.0, 'up')
            ov = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
            for i, ((n, col_), lab) in enumerate(zip(TRACKS, TRK_L)):
                y = cy - 100 + i * 100 + dy; put_l(f, lab, cx - 380, y, a)
                for j in range(5):
                    p = prog(t, 24.4 + i * 0.15 + j * 0.12, 0.35)
                    if p > 0:
                        x0 = cx - 230 + j * 125 + (i * 37) % 60; ww = (70 + (i * 53 + j * 31) % 60) * ease(p)
                        d.rounded_rectangle((x0, y - 22, x0 + ww, y + 22), 12, fill=col_ + (int(255 * a),))
            p = prog(t, 24.4, 2.4)
            px = cx - 230 + 690 * p; d.line((px, cy - 150 + dy, px, cy + 150 + dy), fill=(239, 68, 68, int(230 * a)), width=4)
            f.alpha_composite(ov)
        # B9 closing: profile card + Follow tap (single Spark Coral element)
        a, dy = vis(t, 27.0, 99, delay=0.25)
        if a > 0:
            enter(f, t, HEAD8, CX, 590, 27.0, 99, 'words', H8W)
            put(f, LOGO_END, cx, cy - 120 + dy, a, 0.6 + 0.4 * spring(prog(t, 27.3, 0.5)))
            put(f, NAME, cx, cy + 10 + dy, a); put(f, SUB, cx, cy + 66 + dy, a)
            tap = prog(t, 28.0, 0.22); done = t >= 28.12
            bs = 1 - 0.1 * math.sin(math.pi * tap)
            box(f, cx, cy + 160 + dy, (300 if not done else 330) * bs, 96 * bs, 48, CORAL if not done else GRAPH, shadow=False, alpha=a)
            put(f, FOLLOW if not done else FOLLOWING, cx, cy + 160 + dy, a)
            pc = prog(t, 28.7, 0.5)
            if pc > 0:
                e = ease(pc); y0 = cy + 375 + 200 * (1 - e)
                put(f, CMT_CARD, cx, y0, min(1, pc * 2.5))
                n = int(clamp((t - 29.1) / 0.12, 0, 5)); kw = 'SKILL'[:n]
                if n > 0: put(f, txt(kw, MONT(54), WHITE), cx + KW_X, y0 - 39, min(1, pc * 2.5))
            cp = prog(t, 27.35, 0.6)
            if 0 < cp and t < 28.6:
                put(f, CURSOR, lerp(cx + 260, cx + 30, ease(cp)) + 14, lerp(cy + 420, cy + 175, ease(cp)) + 20, a * (1 - prog(t, 28.3, 0.3)))
    # step chips that fly in from alternating sides (text moving from different places)
    for (t_in, t_out, spr, x, y, side) in STEP_CHIPS:
        p = prog(t, t_in, 0.45); out = prog(t, t_out - 0.18, 0.18)
        if p > 0 and out < 1:
            put(f, spr, x + side * 600 * (1 - ease(p)), y + 6 * math.sin(t * 2), min(1, p * 2.5) * (1 - out), 1, ) if True else None
    return f.convert('RGB')

if __name__ == '__main__':
    if sys.argv[1] == 'test':
        ts = [float(x) for x in sys.argv[2:]]; ims = []
        for x in ts:
            im = render(x); im.save(config.work(f'ui_{x}.png')); ims.append(im.resize((216, 384)))
        sh = Image.new('RGB', (216 * len(ims), 384)); [sh.paste(im, (i * 216, 0)) for i, im in enumerate(ims)]
        sh.save(config.work('uisheet.png')); sys.exit()
    enc = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS),
                            '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '16', '-pix_fmt', 'yuv420p', config.work('ui_v.mp4')], stdin=subprocess.PIPE)
    t0 = time.time()
    for i in range(int(DUR * FPS)): enc.stdin.write(render(i / FPS).tobytes())
    enc.stdin.close(); enc.wait(); print('done', round(time.time() - t0))
