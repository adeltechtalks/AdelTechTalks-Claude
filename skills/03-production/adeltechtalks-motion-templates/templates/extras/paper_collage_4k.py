import sys, math, random, subprocess, os, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # skill root, so the engine package is importable
from engine import config
_BRAND = config.brand(); _END = _BRAND['ending']  # name, tagline and ending text from brand.json
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops, ImageOps, ImageEnhance
from engine import plib
from engine.plib import UP, txt, unfold, prog, ENTER, EXIT, MOVE, CAIRO, MONT, READ, MONO, GRAPH, WHITE, CORAL, NOONY

K = 2                       # 2 = 2160x3840 (4K vertical)
W, H, FPS, DUR = 1080 * K, 1920 * K, 30, 17.0
CX = 540                    # layout coordinates stay in 1080-space; put() scales them
PARCH = (255, 255, 252); BGC = (247, 246, 242); INK = GRAPH
SIG = config.color('primary'); ICE = config.color('primary_soft'); MINT = config.color('accent'); SLATE = config.color('muted'); HAIR = (210, 216, 226)
plib.BACK = (226, 230, 238)
TEX = 0.45                  # paper texture strength (lower = cleaner, sharper look)

def k(v): return int(round(v * K))
def fit(im, w=None, h=None):
    r = (w / im.width) if w else (h / im.height)
    return im.resize((max(1, int(im.width * r)), max(1, int(im.height * r))), Image.LANCZOS)

def shadow(im, blur=16, off=12, op=70):
    blur, off = k(blur), k(off)
    a = im.split()[3].point(lambda v: v * op // 255)
    out = Image.new('RGBA', (im.width + blur * 4, im.height + blur * 4 + abs(off)), (0, 0, 0, 0))
    blk = Image.new('RGBA', im.size, (20, 28, 45, 255)); blk.putalpha(a)
    out.alpha_composite(blk, (blur * 2, blur * 2 + max(off, 0)))
    out = out.filter(ImageFilter.GaussianBlur(blur))
    out.alpha_composite(im, (blur * 2, blur * 2)); return out

def rrect(w, h, r, fill):
    s = 2; im = Image.new('RGBA', (w * s, h * s), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle((0, 0, w * s - 1, h * s - 1), r * s, fill=fill)
    return im.resize((w, h), Image.LANCZOS)

# ---------- textures (subtle) ----------
def noise(w, h, scale, seed):
    r = np.random.default_rng(seed)
    n = Image.fromarray((r.random((max(2, h // scale), max(2, w // scale))) * 255).astype(np.uint8))
    return n.resize((w, h), Image.BICUBIC)

def crumple(w, h, seed=0, strength=1.0):
    a = np.asarray(noise(w, h, k(90), seed), np.float32)
    b = np.asarray(noise(w, h, k(35), seed + 1), np.float32)
    c = np.asarray(noise(w, h, k(12), seed + 2), np.float32)
    m = 0.5 * a + 0.32 * b + 0.18 * c
    e = (np.asarray(Image.fromarray(np.clip(m, 0, 255).astype(np.uint8)).filter(ImageFilter.EMBOSS), np.float32) - 128) * 1.6 * strength
    fine = np.random.default_rng(seed + 9).normal(0, 3, (h, w)).astype(np.float32)
    return np.clip(128 + e + (m - 128) * 0.2 * strength + fine, 0, 255).astype(np.uint8)

def tex(img, seed, strength=1.0):
    lum = Image.fromarray(crumple(img.width, img.height, seed, strength * TEX)).convert('RGB')
    return ImageChops.overlay(img.convert('RGB'), lum)

def torn_mask(w, h, depth, seed=1):
    r = random.Random(seed); pts = []; step = k(10); depth = k(depth)
    for x in range(0, w + 1, step): pts.append((x, r.uniform(0, depth)))
    for y in range(0, h + 1, step): pts.append((w - r.uniform(0, depth), y))
    for x in range(w, -1, -step): pts.append((x, h - r.uniform(0, depth)))
    for y in range(h, -1, -step): pts.append((r.uniform(0, depth), y))
    s = 2; m = Image.new('L', (w * s, h * s), 0)
    ImageDraw.Draw(m).polygon([(x * s, y * s) for x, y in pts], fill=255)
    return m.resize((w, h), Image.LANCZOS)

def paper(w, h, seed=1, col=PARCH, burn=0.35, depth=12):
    """w, h already in output pixels"""
    m = torn_mask(w, h, depth, seed)
    base = tex(Image.new('RGB', (w, h), col), seed + 30, 0.8)
    if burn > 0:
        inner = m.filter(ImageFilter.GaussianBlur(k(14)))
        edge = ImageChops.subtract(m, inner).point(lambda v: min(255, int(v * 2.2 * burn)))
        base = Image.composite(Image.new('RGB', (w, h), tuple(int(v * 0.84) for v in col)), base,
                               edge.point(lambda v: int(v * 0.75)))
    out = base.convert('RGBA'); out.putalpha(m); return out

def ink_on(card, im, xy):
    region = card.crop((xy[0], xy[1], xy[0] + im.width, xy[1] + im.height)).convert('RGB')
    rgb = Image.new('RGB', im.size, (255, 255, 255)); rgb.paste(im.convert('RGB'), (0, 0), im.split()[3])
    card.paste(ImageChops.multiply(region, rgb), xy, im.split()[3])

# ---------- assets ----------
logo_w = config.logo().convert('RGBA')
def recolor(im, col):
    o = Image.new('RGBA', im.size, col + (255,)); o.putalpha(im.split()[3]); return o
def bw_logo(path, crop):
    g = config.input_image(path, (600, 600), 'a partner logo').convert('L').crop(crop)
    im = Image.new('RGBA', g.size, INK + (255,)); im.putalpha(g.point(lambda v: 255 - v)); return im
noon_bw = bw_logo('partner_1.png', (20, 211, 580, 389))
namshi_bw = bw_logo('partner_2.png', (20, 165, 580, 435))

# photo — full colour, sharp, cropped from the original
src = ImageOps.exif_transpose(config.input_image('photo.jpg', (2000, 2100), 'the portrait photo')).convert('RGB')
PW, PH = k(500), k(640)
ph = src.crop((330, 80, 330 + 1560, 80 + 1997)).resize((PW, PH), Image.LANCZOS)
ph = ph.filter(ImageFilter.UnsharpMask(2, 60, 2))
ph = ImageEnhance.Contrast(ImageEnhance.Color(ph).enhance(1.15)).enhance(1.08)
CW_, CH_ = k(580), k(716)
pc = paper(CW_, CH_, 3)
pc.paste(ph, ((CW_ - PW) // 2, k(38)))
PHOTO = shadow(pc, 20, 16, 110)

def strip(text, size, seed, color=WHITE, col=SIG, padx=60, pady=26):
    t = txt(text, CAIRO(k(size)), color, rtl=True)
    s = paper(t.width + k(padx) * 2, t.height + k(pady) * 2, seed, col=col, depth=10, burn=0.35)
    s.alpha_composite(t, (k(padx), k(pady))); return shadow(s, 14, 10, 100)
S_H1 = strip('الحمد لله', 108, 11)
S_H2 = strip('بقيت رسمياً', 108, 12)

nc = paper(k(360), k(230), 21, col=NOONY, burn=0.3, depth=10)
nl = fit(noon_bw, w=k(250)); nc.alpha_composite(nl, ((k(360) - nl.width) // 2, k(42)))
am = txt('AMBASSADOR', MONT(k(34)), INK, spacing=k(4)); nc.alpha_composite(am, ((k(360) - am.width) // 2, k(158)))
NOON = shadow(nc, 16, 12, 100)

def stamp(path, seed):
    sw, sh = k(170), k(200); s = 2
    m = Image.new('L', (sw * s, sh * s), 255); d = ImageDraw.Draw(m); r = k(7) * s
    for x in range(0, sw * s + 1, k(20) * s):
        d.ellipse((x - r, -r, x + r, r), fill=0); d.ellipse((x - r, sh * s - r, x + r, sh * s + r), fill=0)
    for y in range(0, sh * s + 1, k(20) * s):
        d.ellipse((-r, y - r, r, y + r), fill=0); d.ellipse((sw * s - r, y - r, sw * s + r, y + r), fill=0)
    m = m.resize((sw, sh), Image.LANCZOS)
    base = tex(Image.new('RGB', (sw, sh), (255, 255, 252)), seed, 0.6)
    base.paste(config.input_image(path, (300, 300), 'a flag').convert('RGB').resize((k(130), k(130)), Image.LANCZOS), (k(20), k(20)))
    cap = txt('POSTAGE', MONT(k(16)), SIG, spacing=k(3)); base.paste(cap, ((sw - cap.width) // 2, k(162)), cap)
    out = base.convert('RGBA'); out.putalpha(m)
    pm = Image.new('RGBA', (sw, sh), (0, 0, 0, 0)); pd = ImageDraw.Draw(pm)
    pd.ellipse((k(70), k(60), k(190), k(180)), outline=(23, 26, 31, 90), width=k(3))
    for j in range(4):
        pd.line([(k(x), k(40 + j * 14 + 5 * math.sin(x / 9))) for x in range(-10, 120, 2)], fill=(23, 26, 31, 80), width=k(3))
    pm.putalpha(ImageChops.multiply(pm.split()[3], m)); out.alpha_composite(pm)
    return shadow(out, 12, 10, 100)
ST_UAE, ST_KSA = stamp('flag_1.jpg', 41), stamp('flag_2.png', 42)

SH = {}
geo_t = txt('متاح في الإمارات والسعودية', READ(k(36), 600), SIG, rtl=True)
GEO = paper(geo_t.width + k(90), k(84), 51, depth=8, burn=0.3)
GEO.alpha_composite(geo_t, (k(45), (k(84) - geo_t.height) // 2)); SH[id(GEO)] = shadow(GEO, 14, 10, 100)

TW, TH, STUB = 680, 150, 220
MONOF = MONO(k(78)); CWD = MONOF.getlength('A') / K
def coupon(lg, label, seed):
    c = paper(k(TW), k(TH), seed, depth=8, burn=0.3)
    d = ImageDraw.Draw(c); px = k(TW - STUB)
    for y in range(k(22), k(TH - 20), k(16)): d.line((px, y, px, y + k(8)), fill=HAIR + (255,), width=k(3))
    l = fit(lg, w=k(165))
    if l.height > k(84): l = fit(lg, h=k(84))
    c.alpha_composite(l, (px + (k(STUB) - l.width) // 2, (k(TH) - l.height) // 2))
    lb = txt(label, READ(k(25), 500), SLATE, rtl=True); c.alpha_composite(lb, ((px - lb.width) // 2, k(10)))
    SH[id(c)] = shadow(c, 14, 10, 100); return c
C1, C2 = coupon(noon_bw, 'كود خصم noon', 61), coupon(namshi_bw, 'كود خصم Namshi', 62)
CH1 = [txt(ch, MONOF, SIG) for ch in 'ATT001']; CH2 = [txt(ch, MONOF, SIG) for ch in 'ATT002']

CTA = strip('استخدم الكود دلوقتي', 76, 71, color=WHITE, col=CORAL, pady=18)   # single Spark Coral element

END = paper(W + k(700), H + k(300), 77, col=(252, 252, 249), burn=0.0, depth=26)
END_SH = shadow(END, 24, -14, 120)
MARK = recolor(fit(logo_w, w=k(300)), SIG)
F1 = txt(_END['follow'].replace(_BRAND['name'], '').strip(), CAIRO(k(120)), INK, rtl=True)
F2 = txt(_BRAND['name'], MONT(k(100)), SIG)
fb_t = txt('+ Follow', MONT(k(62)), WHITE)
FB = rrect(fb_t.width + k(110), fb_t.height + k(56), k(60), SIG); FB.alpha_composite(fb_t, (k(55), k(28))); FB = shadow(FB, 14, 10, 110)
RC = txt('noon ATT001  ·  Namshi ATT002', MONO(k(40)), GRAPH)
TAG = txt("Experience it. Don't just consume it.", MONT(k(30)), SLATE)

# ---------- background + light ----------
BG0 = tex(Image.new('RGB', (W, H), BGC), 5, 1.0).convert('RGBA')
for (pw, ph_, sd, col, rot, xy) in [(760, 980, 8, ICE, 7, (220, 360)), (320, 170, 9, MINT, -14, (740, 150)),
                                    (360, 420, 10, (255, 228, 210), 11, (-120, 1380))]:
    pp = shadow(paper(k(pw), k(ph_), sd, col=col, burn=0.2), 16, 8, 50).rotate(rot, Image.BICUBIC, expand=True)
    BG0.alpha_composite(pp, (k(xy[0]), k(xy[1])))
vig = Image.new('L', (W // 4, H // 4), 0); ImageDraw.Draw(vig).ellipse((-90, -60, W // 4 + 90, H // 4 + 60), fill=255)
vig = ImageChops.invert(vig.filter(ImageFilter.GaussianBlur(50))).resize((W, H), Image.BICUBIC)
vl = Image.new('RGBA', (W, H), (40, 50, 70, 255)); vl.putalpha(vig.point(lambda v: v * 22 // 255))
BG0.alpha_composite(vl)

# gobo light map (built at quarter res then upscaled — it's soft anyway)
q = 4; GW, GH = k(1700) // q, k(2600) // q
gobo = Image.new('L', (GW, GH), 255); gd = ImageDraw.Draw(gobo)
for y in range(0, GH, k(150) // q): gd.rectangle((0, y, GW, y + k(46) // q), fill=120)
gd.rectangle((k(780) // q, 0, k(840) // q, GH), fill=110)
r = random.Random(3)
for _ in range(26):
    cx, cy = r.uniform(0, k(600) / q), r.uniform(0, GH); L = r.uniform(k(80) / q, k(200) / q); ang = r.uniform(0, math.pi)
    pts = []
    for sgn in (1, -1):
        for j in range(20):
            tt = j / 19 * math.pi; px = sgn * L * math.cos(tt) - L; py = sgn * 0.35 * L * math.sin(tt)
            pts.append((cx + px * math.cos(ang) - py * math.sin(ang), cy + px * math.sin(ang) + py * math.cos(ang)))
    gd.polygon(pts, fill=105)
gobo = gobo.rotate(-24, Image.BICUBIC, fillcolor=255).filter(ImageFilter.GaussianBlur(k(16) / q))
gobo = gobo.point(lambda v: int(182 + v * 73 / 255))   # lighter shadows than before
GOBO = np.asarray(gobo.resize((k(1700), k(2600)), Image.BICUBIC), np.uint16)
TINT = np.array([0.97, 0.985, 1.0], np.float32)

def light(f, t):
    return f.convert('RGB')   # gobo shadows removed — clean, full colour
    ox = k(420 - 20 * t); oy = k(300 - 8 * math.sin(t * 0.6) - 10 * t)
    g = GOBO[oy:oy + H, ox:ox + W]
    a = np.asarray(f.convert('RGB'), np.uint16)
    out = (a * g[:, :, None]) >> 8
    out = (out * TINT).astype(np.uint8)
    return Image.fromarray(out)

# ---------- compositing (no jitter, cached rotations = crisp) ----------
RC_CACHE = {}
GS, SRC_C, DST_C = 0.95, 870, 915   # cross-platform safe layout: shrink & centre the content block
def put(f, spr, cx, cy, scale=1, alpha=1, rot=0, cache=False):
    if alpha <= 0.01 or scale <= 0.01: return
    cx = 540 + (cx - 540) * GS; cy = DST_C + (cy - SRC_C) * GS
    key = (id(spr), round(rot, 2))
    if cache and abs(scale - 1) < 0.003 and key in RC_CACHE:
        im = RC_CACHE[key]
    else:
        im = spr; scale = scale * GS
        if abs(scale - 1) > 0.003:
            im = im.resize((max(1, int(im.width * scale)), max(1, int(im.height * scale))), Image.BICUBIC)
        if abs(rot) > 0.05: im = im.rotate(rot, Image.BICUBIC, expand=True)
        if cache and abs(scale / GS - 1) < 0.003: RC_CACHE[key] = im
    if alpha < 0.999:
        im = im.copy(); im.putalpha(im.split()[3].point(lambda v: int(v * alpha)))
    f.alpha_composite(im, (int(cx * K - im.width / 2), int(cy * K - im.height / 2)))

def drop(f, t, spr, cx, cy, t0, rot=0, dur=0.5, dx=0, dy=170, rr=9):
    p = prog(t, t0, dur)
    if p <= 0: return
    e = ENTER(p)
    put(f, spr, cx + dx * (1 - e), cy + dy * (1 - e), 1.06 - 0.06 * e, min(1, p * 3), rot + rr * (1 - e), cache=p >= 1)

def pop(p):
    return 1.3 - 0.33 * ENTER(min(1, p / 0.75)) if p < 0.75 else 0.97 + 0.03 * MOVE((p - 0.75) / 0.25)

def slap(f, t, spr, cx, cy, t0, rot=0, t_peel=None):
    p = prog(t, t0, 0.32)
    if p <= 0: return
    s = pop(p); r_ = rot + 7 * (1 - ENTER(p)); a = min(1, p * 3.5); x, y = cx, cy
    peeling = False
    if t_peel is not None:
        qq = prog(t, t_peel, 0.32)
        if qq >= 1: return
        if qq > 0:
            peeling = True; e = EXIT(qq); r_ -= 22 * e; x -= 140 * e; y -= 220 * e; s *= 1 - 0.1 * e; a *= 1 - e
    put(f, spr, x, y, s, a, r_, cache=(p >= 1 and not peeling))

def fold(f, t, spr, cx, cy, t0, axis='v', moving='bottom', rot=0, dur=0.55):
    pa = prog(t, t0, 0.18)
    if pa <= 0: return
    pu = prog(t, t0 + 0.12, dur)
    im = shadow(unfold(spr, pu, axis, moving), 14, 10, 100) if pu < 1 else SH[id(spr)]
    put(f, im, cx, cy, 0.94 + 0.06 * ENTER(pa), min(1, pa * 2.5), rot, cache=(pu >= 1 and pa >= 1))

def codes(f, t, chars, cy, t0):
    x0 = CX + ((TW - STUB) / 2 - TW / 2) - CWD * len(chars) / 2 + CWD / 2
    for i, ch in enumerate(chars):
        p = prog(t, t0 + i * 0.07, 0.22)
        if p > 0: put(f, ch, x0 + i * CWD, cy + 14, 1.4 - 0.4 * ENTER(p), min(1, p * 3), cache=p >= 1)

Y_HEAD, Y_PH, Y_GEO, Y_C1, Y_C2 = 330, 705, 1105, 1235, 1400
T_END = 13.6

def collage(t):
    f = BG0.copy()
    drop(f, t, PHOTO, CX + 10, Y_PH, 0.1, rot=-3, dur=0.6)
    slap(f, t, S_H1, CX, Y_HEAD, 0.85, rot=2, t_peel=2.6)
    slap(f, t, S_H2, CX, Y_HEAD, 2.8, rot=2)
    drop(f, t, NOON, CX + 255, Y_PH + 70, 3.25, rot=6, dx=220, dy=60, rr=14)
    slap(f, t, ST_UAE, CX - 275, Y_PH - 150, 8.8, rot=-9)
    slap(f, t, ST_KSA, CX - 255, Y_PH + 40, 9.0, rot=6)
    fold(f, t, GEO, CX, Y_GEO, 9.3, 'h', 'left', rot=-1.5)
    fold(f, t, C1, CX, Y_C1, 4.6)
    if t >= 5.25: codes(f, t, CH1, Y_C1, 5.25)
    fold(f, t, C2, CX, Y_C2, 6.6)
    if t >= 7.25: codes(f, t, CH2, Y_C2, 7.25)
    slap(f, t, CTA, CX, Y_PH + 268, 10.8, rot=-4)
    return f

def render(t):
    if t < T_END + 0.55:
        f = collage(t)
        push = 1 + 0.03 * MOVE(prog(t, 11.2, 2.4))
        if push > 1.0005:
            cw, ch = int(W / push), int(H / push)
            f = f.crop(((W - cw) // 2, (H - ch) // 2, (W - cw) // 2 + cw, (H - ch) // 2 + ch)).resize((W, H), Image.LANCZOS)
    else:
        f = BG0.copy()
    p = prog(t, T_END, 0.55)
    if p > 0:
        e = MOVE(p); y = int(H * (1 - e)) - k(100)
        if p < 1: f.alpha_composite(END_SH, (-k(350) - k(48), y - k(48)))
        else: f.alpha_composite(END, (-k(350), y))
        if p >= 1:
            slap(f, t, MARK, CX, 600, T_END + 0.45)
            drop(f, t, F1, CX, 860, T_END + 0.7, dy=60, rr=0)
            drop(f, t, F2, CX, 1000, T_END + 0.8, dy=60, rr=0)
            pp = prog(t, T_END + 1.0, 0.32)
            if pp > 0:
                pulse = 1 + 0.03 * math.sin((t - T_END - 1.4) * 5) if t > T_END + 1.4 else 1
                put(f, FB, CX, 1170, pop(pp) * pulse, min(1, pp * 3.5))
            drop(f, t, RC, CX, 1330, T_END + 1.3, dy=40, rr=0)
            drop(f, t, TAG, CX, 1420, T_END + 1.45, dy=40, rr=0)
    return light(f, t)

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        for x in [12.8, 16.5]:
            t0 = time.time(); im = render(x); print(x, round(time.time() - t0, 2), 's'); im.save(config.work(f'hd_{x}.png'))
        sys.exit()
    a, b = int(sys.argv[1]), int(sys.argv[2])
    out = config.work(f'sseg_{a:04d}.mp4')
    enc = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}',
                            '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '14',
                            '-profile:v', 'high', '-level', '5.2', '-pix_fmt', 'yuv420p', '-tune', 'stillimage',
                            '-movflags', '+faststart', out], stdin=subprocess.PIPE)
    t0 = time.time()
    for i in range(a, min(b, int(DUR * FPS))):
        enc.stdin.write(render(i / FPS).tobytes())
        if i % 30 == 0: print(i, round(time.time() - t0), flush=True)
    enc.stdin.close(); enc.wait(); print('done', round(time.time() - t0))
