import math, os, sys, random, subprocess
import numpy as np
from engine import config
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops, ImageEnhance

W, H, FPS, DUR = 1080, 1920, 30, 15.0
UP = str(config.INPUT_DIR) + os.sep  # kept for older scripts; prefer config.input_image()
F = str(config.FONTS_DIR) + os.sep
PHOTO = os.environ.get('PHOTO', '')  # high-res photo path; falls back to story avatar
OUT = config.work('pframes'); os.makedirs(OUT, exist_ok=True)
CX = 540

# Brand tokens (from brand.json — see engine/config.py)
_C = config.color
PAPER = _C("paper"); WHITE = _C("surface"); GRAPH = _C("ink"); SLATE = _C("muted")
SIG = _C("primary"); ICE = _C("primary_soft"); MINT = _C("accent"); HAIR = _C("hairline")
CORAL = _C("cta"); NOONY = _C("highlight")

def font(name, size, w):
    ft = ImageFont.truetype(F + name + '.ttf', size, layout_engine=ImageFont.Layout.RAQM)
    try:  # variable fonts: pick the weight; static fonts keep their own weight
        ax = ft.get_variation_axes(); ft.set_variation_by_axes([w] + [a['default'] for a in ax[1:]])
    except Exception:
        pass
    return ft
_FONTS = config.brand()["fonts"]
CAIRO = lambda s: font(_FONTS["display"], s, 900)
MONT = lambda s: font(_FONTS["latin"], s, 800)
READ = lambda s, w=600: font(_FONTS["body"], s, w)
MONO = lambda s: font(_FONTS["mono"], s, 800)

def txt(t, ft, fill, rtl=False, spacing=0):
    d = ImageDraw.Draw(Image.new('RGBA', (1, 1)))
    if spacing:
        ws = [d.textlength(c, font=ft) for c in t]
        im = Image.new('RGBA', (int(sum(ws) + spacing * len(t)) + 20, int(ft.size * 1.6)), (0, 0, 0, 0))
        dd = ImageDraw.Draw(im); x = 10
        for c, w in zip(t, ws): dd.text((x, 10), c, font=ft, fill=fill); x += w + spacing
        return im.crop(im.getbbox())
    kw = dict(direction='rtl', language='ar') if rtl else {}
    bb = d.textbbox((0, 0), t, font=ft, **kw)
    im = Image.new('RGBA', (bb[2] - bb[0] + 8, bb[3] - bb[1] + 8), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((4 - bb[0], 4 - bb[1]), t, font=ft, fill=fill, **kw)
    return im

def fit(im, w=None, h=None):
    r = (w / im.width) if w else (h / im.height)
    return im.resize((max(1, int(im.width * r)), max(1, int(im.height * r))), Image.LANCZOS)

# ---- paper grain ----
rng = np.random.default_rng(7)
def grain_layer(w, h, amt=10, seed=0):
    r = np.random.default_rng(seed)
    n = r.normal(0, amt, (h, w)).astype(np.float32)
    g = Image.fromarray(np.clip(128 + n, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.7))
    return g
def paperize(im, amt=9, seed=1):
    """multiply paper grain into an RGBA sprite"""
    g = grain_layer(im.width, im.height, amt, seed).convert('RGB')
    rgb = im.convert('RGB')
    rgb = ImageChops.overlay(rgb, g)
    out = rgb.convert('RGBA'); out.putalpha(im.split()[3]); return out

def die_cut(im, border=14, col=WHITE):
    pad = border + 4
    base = Image.new('RGBA', (im.width + pad * 2, im.height + pad * 2), (0, 0, 0, 0))
    base.alpha_composite(im, (pad, pad))
    a = base.split()[3].point(lambda v: 255 if v > 40 else 0)
    a = a.filter(ImageFilter.MaxFilter(3))
    for _ in range(border // 2): a = a.filter(ImageFilter.MaxFilter(5))
    a = a.filter(ImageFilter.GaussianBlur(1.2)).point(lambda v: 255 if v > 110 else int(v * 2.3))
    sticker = Image.new('RGBA', base.size, col + (255,)); sticker.putalpha(a)
    sticker = paperize(sticker, 7, 3)
    sticker.alpha_composite(base)
    return sticker

def shadow(im, blur=16, off=12, op=70):
    a = im.split()[3].point(lambda v: v * op // 255)
    out = Image.new('RGBA', (im.width + blur * 4, im.height + blur * 4 + off), (0, 0, 0, 0))
    blk = Image.new('RGBA', im.size, GRAPH + (255,)); blk.putalpha(a)
    out.alpha_composite(blk, (blur * 2, blur * 2 + off))
    out = out.filter(ImageFilter.GaussianBlur(blur))
    out.alpha_composite(im, (blur * 2, blur * 2)); return out

def rrect(w, h, r, fill):
    s = 2; im = Image.new('RGBA', (w * s, h * s), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle((0, 0, w * s - 1, h * s - 1), r * s, fill=fill)
    return im.resize((w, h), Image.LANCZOS)

def torn(w, h, fill, edges='lr', depth=10, seed=2):
    r = random.Random(seed); pts = []
    step = 14
    # top
    for x in range(0, w + 1, step): pts.append((x, (r.uniform(0, depth) if 't' in edges else 0)))
    for y in range(0, h + 1, step): pts.append((w - (r.uniform(0, depth) if 'r' in edges else 0), y))
    for x in range(w, -1, -step): pts.append((x, h - (r.uniform(0, depth) if 'b' in edges else 0)))
    for y in range(h, -1, -step): pts.append(((r.uniform(0, depth) if 'l' in edges else 0), y))
    s = 2; im = Image.new('RGBA', (w * s, h * s), (0, 0, 0, 0))
    ImageDraw.Draw(im).polygon([(x * s, y * s) for x, y in pts], fill=fill)
    return paperize(im.resize((w, h), Image.LANCZOS), 8, seed)

# ---- easing ----
def bez(p1x, p1y, p2x, p2y):
    def f(t):
        if t <= 0: return 0.0
        if t >= 1: return 1.0
        u = t
        for _ in range(8):
            x = 3*(1-u)**2*u*p1x + 3*(1-u)*u*u*p2x + u**3 - t
            dx = 3*(1-u)**2*p1x + 6*(1-u)*u*(p2x-p1x) + 3*u*u*(1-p2x)
            if abs(dx) < 1e-6: break
            u = min(max(u - x / dx, 0), 1)
        return 3*(1-u)**2*u*p1y + 3*(1-u)*u*u*p2y + u**3
    return f
ENTER = bez(0.16, 0.84, 0.44, 1); EXIT = bez(0.4, 0, 1, 1); MOVE = bez(0.4, 0, 0.2, 1)
def prog(t, s, d): return min(max((t - s) / d, 0), 1)

# ---- fold ----
BACK = (236, 236, 232)
def unfold(spr, p, axis='v', moving='top'):
    im = spr
    if axis == 'h': im = im.transpose(Image.TRANSPOSE)
    if moving in ('bottom', 'right'): im = im.transpose(Image.FLIP_TOP_BOTTOM)
    w, h = im.size; half = h // 2
    out = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    out.alpha_composite(im.crop((0, half, w, h)), (0, half))
    c = math.cos(math.pi * (1 - MOVE(p)))
    if c >= 0.01:
        top = im.crop((0, 0, w, half)); hh = max(1, int(half * c))
        top = top.resize((w, hh), Image.BICUBIC)
        dark = Image.new('RGBA', top.size, (0, 0, 0, int(110 * (1 - c))))
        dark.putalpha(ImageChops.multiply(top.split()[3], dark.split()[3]))
        top.alpha_composite(dark); out.alpha_composite(top, (0, half - hh))
    elif c <= -0.01:
        m = im.crop((0, 0, w, half)).transpose(Image.FLIP_TOP_BOTTOM).split()[3]
        hh = max(1, int(half * -c)); m = m.resize((w, hh), Image.BICUBIC)
        shade = int(BACK[0] * (0.78 + 0.22 * -c))
        back = Image.new('RGBA', (w, hh), (shade, shade, shade - 4, 255)); back.putalpha(m)
        out.alpha_composite(back, (0, half))
    if moving in ('bottom', 'right'): out = out.transpose(Image.FLIP_TOP_BOTTOM)
    if axis == 'h': out = out.transpose(Image.TRANSPOSE)
    return out

# ---- compositing ----
FRAME_IDX = [0]
def boil(key, amp=1.4):
    r = random.Random(hash((key, FRAME_IDX[0] // 3)))
    return r.uniform(-amp, amp), r.uniform(-amp, amp), r.uniform(-0.35, 0.35)

def put(f, spr, cx, cy, scale=1, alpha=1, rot=0, key=None):
    if alpha <= 0.01 or scale <= 0.01: return
    if key is not None:
        dx, dy, dr = boil(key); cx += dx; cy += dy; rot += dr
    im = spr
    if abs(scale - 1) > 0.003:
        im = im.resize((max(1, int(im.width * scale)), max(1, int(im.height * scale))), Image.BICUBIC)
    if abs(rot) > 0.05: im = im.rotate(rot, Image.BICUBIC, expand=True)
    if alpha < 0.999:
        im = im.copy(); im.putalpha(im.split()[3].point(lambda v: int(v * alpha)))
    f.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2)))

def slap(f, t, spr, cx, cy, t0, rot=0, key=None, t_peel=None):
    p = prog(t, t0, 0.32)
    if p <= 0: return
    s = 1.28 - 0.28 * ENTER(p)
    if p < 1: s = 1.28 - 0.31 * ENTER(min(1, p / 0.75)) if p < 0.75 else 0.97 + 0.03 * MOVE((p - 0.75) / 0.25)
    r = rot + 7 * (1 - ENTER(p)); a = min(1, p * 3.5)
    x, y = cx, cy
    if t_peel is not None:
        q = prog(t, t_peel, 0.32)
        if q >= 1: return
        e = EXIT(q); r -= 22 * e; x -= 140 * e; y -= 220 * e; s *= 1 - 0.1 * e; a *= 1 - e
    put(f, spr, x, y, s, a, r, key if p >= 1 else None)

def fold_in(f, t, spr, cx, cy, t0, axis='v', moving='top', rot=0, key=None, dur=0.55):
    pa = prog(t, t0, 0.18)
    if pa <= 0: return
    pu = prog(t, t0 + 0.12, dur)
    im = unfold(spr, pu, axis, moving) if pu < 1 else spr
    im = shadow(im, 16, 12, 70) if pu < 1 else SH[id(spr)]
    put(f, im, cx, cy, 0.94 + 0.06 * ENTER(pa), min(1, pa * 2.5), rot, key if pu >= 1 else None)

SH = {}
def preshadow(spr):
    SH[id(spr)] = shadow(spr, 16, 12, 70); return spr

