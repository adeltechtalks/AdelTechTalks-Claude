"""AdelTechTalks — Liquid Glass template (noon ambassador demo content)"""
import sys, math, os, subprocess, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # skill root, so the engine package is importable
from engine import config
_BRAND = config.brand(); _END = _BRAND['ending']  # name, tagline and ending text from brand.json
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops, ImageOps, ImageEnhance
from engine.plib import UP, txt, CAIRO, MONT, READ, MONO, GRAPH, WHITE, CORAL, NOONY

W, H, FPS, DUR = 1080, 1920, 30, 17.0
SIG = config.color('primary'); BLUE4 = config.color('primary_light'); MINT = config.color('accent')

# ---------- helpers ----------
def fit(im, w=None, h=None):
    r = (w / im.width) if w else (h / im.height)
    return im.resize((max(1, int(im.width * r)), max(1, int(im.height * r))), Image.LANCZOS)
def recolor(im, col):
    o = Image.new('RGBA', im.size, col + (255,)); o.putalpha(im.split()[3]); return o
def soft_shadow(im, blur=10, op=110, off=3):
    a = im.split()[3].point(lambda v: v * op // 255)
    out = Image.new('RGBA', (im.width + blur * 4, im.height + blur * 4 + off), (0, 0, 0, 0))
    blk = Image.new('RGBA', im.size, (5, 10, 25, 255)); blk.putalpha(a)
    out.alpha_composite(blk, (blur * 2, blur * 2 + off)); out = out.filter(ImageFilter.GaussianBlur(blur))
    out.alpha_composite(im, (blur * 2, blur * 2)); return out
def T(text, ft, col=WHITE, rtl=False, spacing=0):
    return soft_shadow(txt(text, ft, col, rtl=rtl, spacing=spacing))
def clamp(v, a, b): return max(a, min(b, v))
def prog(t, s, d): return clamp((t - s) / d, 0, 1)
def ease(p): return 1 - (1 - p) ** 3
def spring(p):  # ~6% overshoot, settles by p=1
    return 1 - math.exp(-7 * p) * math.cos(8 * p) if p < 1 else 1.0
def circ(im, d):
    im = im.convert('RGBA').resize((d, d), Image.LANCZOS)
    m = Image.new('L', (d * 3, d * 3), 0); ImageDraw.Draw(m).ellipse((0, 0, d * 3 - 1, d * 3 - 1), fill=255)
    im.putalpha(m.resize((d, d), Image.LANCZOS)); return im

# ---------- background: his photo, slow push-in ----------
src = ImageOps.exif_transpose(config.input_image('photo.jpg', (2000, 2100), 'the portrait photo')).convert('RGB')
BGSRC = src.crop((345, 0, 1794, 2576)).resize((1216, 2160), Image.LANCZOS)
BGSRC = ImageEnhance.Contrast(ImageEnhance.Color(BGSRC).enhance(1.12)).enhance(1.04)
grad = Image.new('L', (1, H), 0)
for y in range(H):
    v = 0
    if y > 900: v = int(170 * ((y - 900) / (H - 900)) ** 1.2)
    if y < 200: v = max(v, int(70 * (1 - y / 200)))
    grad.putpixel((0, y), v)
SHADE = Image.new('RGBA', (W, H), (8, 12, 24, 255)); SHADE.putalpha(grad.resize((W, H)))

def background(t):
    z = 1.0 + 0.09 * (t / DUR)
    cw, ch = 1216 / z, 2160 / z
    cx, cy = 608, 1080 - 60 * (t / DUR)
    bg = BGSRC.crop((int(cx - cw / 2), int(cy - ch / 2), int(cx + cw / 2), int(cy + ch / 2))).resize((W, H), Image.BICUBIC)
    f = bg.convert('RGBA'); f.alpha_composite(SHADE)
    dim = prog(t, 13.4, 0.6)
    if dim > 0: f.alpha_composite(Image.new('RGBA', (W, H), (8, 12, 24, int(90 * ease(dim)))))
    small = f.convert('RGB').resize((W // 4, H // 4), Image.BILINEAR).filter(ImageFilter.GaussianBlur(7))
    small = ImageEnhance.Color(ImageEnhance.Brightness(small).enhance(0.92)).enhance(1.4)
    return f, small.resize((W, H), Image.BICUBIC)

# ---------- liquid glass ----------
SHEEN = Image.new('L', (1, 256))
for y in range(256): SHEEN.putpixel((0, y), int(70 * max(0, 1 - y / 110) ** 1.6))
def rr_mask(w, h, r, s=2):
    m = Image.new('L', (w * s, h * s), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, w * s - 1, h * s - 1), int(r * s), fill=255)
    return m.resize((w, h), Image.LANCZOS)

def glass(f, blur, cx, cy, w, h, r, tint=(14, 20, 38), tint_a=0.42, alpha=1.0, shadow=True):
    w, h = int(w), int(h)
    if w < 6 or h < 6 or alpha <= 0.01: return
    r = min(r, w / 2, h / 2)
    x0, y0 = int(cx - w / 2), int(cy - h / 2)
    m = rr_mask(w, h, r)
    if shadow:  # soft drop shadow, built at quarter res
        q = 4; sw, sh = w // q + 16, h // q + 16
        sm = Image.new('L', (sw, sh), 0)
        ImageDraw.Draw(sm).rounded_rectangle((8, 8, 8 + w // q, 8 + h // q), int(r / q), fill=int(120 * alpha))
        sm = sm.filter(ImageFilter.GaussianBlur(5)).resize((sw * q, sh * q), Image.BICUBIC)
        sl = Image.new('RGBA', sm.size, (0, 5, 20, 255)); sl.putalpha(sm)
        f.alpha_composite(sl, (x0 - 32, y0 - 32 + 18))
    # lens: magnify what's behind (refraction)
    ins_w, ins_h = w * 0.05, h * 0.05
    bx0, by0 = clamp(x0 + ins_w, 0, W - 2), clamp(y0 + ins_h, 0, H - 2)
    bx1, by1 = clamp(x0 + w - ins_w, bx0 + 1, W), clamp(y0 + h - ins_h, by0 + 1, H)
    body = blur.crop((int(bx0), int(by0), int(bx1), int(by1))).resize((w, h), Image.BICUBIC).convert('RGBA')
    body = Image.blend(body, Image.new('RGBA', (w, h), tint + (255,)), tint_a)
    # sheen
    sheen = SHEEN.resize((w, h)); body.alpha_composite(Image.merge('RGBA', (*[Image.new('L', (w, h), 255)] * 3, sheen)))
    body.putalpha(m.point(lambda v: int(v * alpha)))
    f.alpha_composite(body, (x0, y0))
    # rim light: bright top-left → faint bottom-right
    s = 2; rim = Image.new('L', (w * s, h * s), 0)
    ImageDraw.Draw(rim).rounded_rectangle((1, 1, w * s - 2, h * s - 2), int(r * s), outline=255, width=3 * s)
    rim = rim.resize((w, h), Image.LANCZOS)
    gx = np.linspace(1.0, 0.25, w)[None, :]; gy = np.linspace(1.0, 0.35, h)[:, None]
    g = Image.fromarray((np.clip(gx * gy * 1.3, 0, 1) * 210 * alpha).astype(np.uint8))
    rl = Image.new('RGBA', (w, h), (255, 255, 255, 255)); rl.putalpha(ImageChops.multiply(rim, g))
    f.alpha_composite(rl, (x0, y0))

def put(f, spr, cx, cy, a=1.0, s=1.0):
    if a <= 0.01: return
    im = spr if abs(s - 1) < 0.003 else spr.resize((max(1, int(spr.width * s)), max(1, int(spr.height * s))), Image.BICUBIC)
    if a < 0.999: im = im.copy(); im.putalpha(im.split()[3].point(lambda v: int(v * a)))
    f.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2)))

# ---------- content sprites ----------
def bw_logo(path, crop):
    g = config.input_image(path, (600, 600), 'a partner logo').convert('L').crop(crop)
    im = Image.new('RGBA', g.size, (255, 255, 255, 255)); im.putalpha(g.point(lambda v: 255 - v)); return im
NOON_W = bw_logo('partner_1.png', (20, 211, 580, 389))
NAMSHI_W = bw_logo('partner_2.png', (20, 165, 580, 435))
GRAPH_NOON = recolor(NOON_W, GRAPH)

S1 = T('الحمد لله', CAIRO(92), rtl=True)
S2a = T('بقيت رسمياً', CAIRO(96), rtl=True)
amb = txt('AMBASSADOR', MONT(30), GRAPH, spacing=4)
S2_LOGO = fit(GRAPH_NOON, w=180)

def code_set(logo, label, code):
    return dict(logo=soft_shadow(fit(logo, w=200) if logo.width / logo.height > 2.5 else fit(logo, h=78)),
                label=T(label, READ(32, 500), (230, 236, 248), rtl=True),
                chars=[T(c, MONO(124)) for c in code], cw=MONO(124).getlength('A'),
                hint=T('اكتبه وقت الدفع', READ(30, 400), (220, 228, 242), rtl=True))
C1 = code_set(NOON_W, 'كود خصم', 'ATT001'); C2 = code_set(NAMSHI_W, 'كود خصم', 'ATT002')

FL_UAE = soft_shadow(circ(config.input_image('flag_1.jpg', (300, 300), 'flag 1'), 112), 8, 120)
FL_KSA = soft_shadow(circ(config.input_image('flag_2.png', (300, 300), 'flag 2'), 112), 8, 120)
S5 = T('متاح في الإمارات والسعودية', CAIRO(56), rtl=True)

R1_LOGO = soft_shadow(fit(NOON_W, w=170)); R2_LOGO = soft_shadow(fit(NAMSHI_W, h=62))
R1_CODE = T('ATT001', MONO(80)); R2_CODE = T('ATT002', MONO(80))
CTA_T = T('استخدم الكود دلوقتي', CAIRO(56), rtl=True)

AV = circ(src.crop((610, 310, 1510, 1210)), 132)
ring = Image.new('RGBA', (148, 148), (0, 0, 0, 0)); ImageDraw.Draw(ring).ellipse((0, 0, 147, 147), fill=(255, 255, 255, 230))
ring.alpha_composite(AV, (8, 8)); AV = soft_shadow(ring, 8, 120)
NAME = T(_BRAND['name'], MONT(46))
SUB = T(_BRAND['tagline'], READ(28, 400), (225, 232, 245))
FOL = T('+ Follow', MONT(36)); FOLD = T(_END['following'], MONT(34))
CHIP = T('noon ATT001  ·  Namshi ATT002', MONO(34))
MARK = soft_shadow(fit(config.logo().convert('RGBA'), w=70), 6, 100)

# ---------- main glass card: states it morphs between ----------
STATES = [  # (start, cx, cy, w, h, r)
    (0.30, 540, 1250, 120, 120, 60),
    (0.62, 540, 1250, 500, 168, 84),
    (2.60, 540, 1230, 740, 320, 60),
    (4.60, 540, 1230, 800, 340, 60),
    (7.00, 540, 1230, 800, 340, 60),
    (9.40, 540, 1230, 840, 300, 60),
    (11.40, 540, 1185, 860, 480, 60),
    (13.60, 540, 1300, 880, 200, 100),
]
def card_state(t):
    if t < STATES[0][0]: return None
    cur = STATES[0]
    for i in range(len(STATES) - 1, -1, -1):
        if t >= STATES[i][0]: idx = i; break
    if idx == 0:
        p = ease(prog(t, STATES[0][0], 0.32)); _, cx, cy, w, h, r = STATES[0]
        return cx, cy, w * p, h * p, r * p
    prev, nxt = STATES[idx - 1], STATES[idx]
    p = spring(prog(t, nxt[0], 0.62))
    return tuple(prev[k] + (nxt[k] - prev[k]) * p for k in range(1, 6))

def vis(t, t_in, t_out, delay=0.18):
    """content alpha + rise for an element living in a scene"""
    a_in = ease(prog(t, t_in + delay, 0.3)); a_out = 1 - prog(t, t_out, 0.14)
    return a_in * a_out, 26 * (1 - a_in)

def render(t):
    f, blur = background(t)
    # floating glass droplets for the liquid feel
    for i, (bx, by, d, ph) in enumerate([(170, 1010, 64, 0.0), (905, 1080, 44, 1.7), (870, 1560, 34, 3.1)]):
        a = ease(prog(t, 0.9 + i * 0.25, 0.5)) * (1 - prog(t, 13.4, 0.3))
        if a > 0:
            glass(f, blur, bx + 10 * math.sin(t * 0.8 + ph), by + 14 * math.sin(t * 1.1 + ph), d, d, d / 2, tint=(255, 255, 255), tint_a=0.10, alpha=a, shadow=False)
    st = card_state(t)
    if st:
        cx, cy, w, h, r = st
        bob = 4 * math.sin(t * 1.6)
        glass(f, blur, cx, cy + bob, w, h, r)
        cy += bob
        # S1
        a, dy = vis(t, 0.62, 2.6); put(f, S1, cx, cy + dy, a)
        # S2
        a, dy = vis(t, 2.6, 4.6)
        if a > 0:
            put(f, S2a, cx, cy - 62 + dy, a)
            glass(f, blur, cx, cy + 78 + dy, 520, 104, 52, tint=NOONY, tint_a=0.82, alpha=a, shadow=False)
            put(f, S2_LOGO, cx - 138, cy + 78 + dy, a); put(f, amb, cx + 118, cy + 78 + dy, a)
        # S3 / S4 codes
        for (cs, t0, t1) in ((C1, 4.6, 7.0), (C2, 7.0, 9.4)):
            a, dy = vis(t, t0, t1)
            if a > 0:
                put(f, cs['logo'], cx + 230, cy - 108 + dy, a)
                put(f, cs['label'], cx - 200, cy - 108 + dy, a)
                n = len(cs['chars']); x0 = cx - cs['cw'] * n / 2 + cs['cw'] / 2
                for i, ch in enumerate(cs['chars']):
                    p = prog(t, t0 + 0.5 + i * 0.07, 0.2)
                    if p > 0: put(f, ch, x0 + i * cs['cw'], cy + 18 + dy, a * min(1, p * 3), 1.35 - 0.35 * ease(p))
                put(f, cs['hint'], cx, cy + 122 + dy, a * ease(prog(t, t0 + 1.0, 0.3)))
        # S5
        a, dy = vis(t, 9.4, 11.4)
        if a > 0:
            for k, (fl, dx) in enumerate(((FL_KSA, 80), (FL_UAE, -80))):
                p = prog(t, 9.7 + k * 0.12, 0.35)
                if p > 0: put(f, fl, cx + dx, cy - 52 + dy, a, 0.5 + 0.5 * spring(p))
            put(f, S5, cx, cy + 82 + dy, a)
        # S6 recap + CTA (single Spark Coral element)
        a, dy = vis(t, 11.4, 13.6)
        if a > 0:
            for row, (lg, cd) in enumerate(((R1_LOGO, R1_CODE), (R2_LOGO, R2_CODE))):
                ry = cy - 160 + row * 108 + dy
                put(f, lg, cx + 250, ry, a); put(f, cd, cx - 130, ry, a)
            ImageDraw.Draw(f).line((cx - 360, cy - 106 + dy, cx + 360, cy - 106 + dy), fill=(255, 255, 255, int(70 * a)), width=2)
            p = prog(t, 11.8, 0.5)
            if p > 0:
                s = spring(p); pulse = 1 + 0.02 * math.sin((t - 12.5) * 6) if t > 12.5 else 1
                glass(f, blur, cx, cy + 135 + dy, 660 * s * pulse, 124 * s * pulse, 62, tint=CORAL, tint_a=0.86, alpha=a, shadow=False)
                put(f, CTA_T, cx, cy + 135 + dy, a * min(1, p * 2), pulse)
        # S7 follow bar
        a, dy = vis(t, 13.6, 99, 0.3)
        if a > 0:
            put(f, AV, cx + 340, cy + dy, a)
            put(f, NAME, cx + 70, cy - 26 + dy, a); put(f, SUB, cx + 70, cy + 32 + dy, a)
            tap = prog(t, 15.3, 0.25)
            col = SIG if tap < 0.5 else (32, 160, 120)
            bs = 1 - 0.08 * math.sin(math.pi * tap)
            glass(f, blur, cx - 290, cy + dy, 230 * bs, 92 * bs, 46, tint=col, tint_a=0.85, alpha=a, shadow=False)
            put(f, FOL if tap < 0.5 else FOLD, cx - 290, cy + dy, a)
            if 0 < tap < 1 or prog(t, 15.3, 0.6) < 1 and t > 15.3:  # tap ripple
                rp = prog(t, 15.3, 0.6); rr = int(20 + 110 * ease(rp))
                ImageDraw.Draw(f).ellipse((cx - 290 - rr, cy - rr, cx - 290 + rr, cy + rr), outline=(255, 255, 255, int(200 * (1 - rp))), width=4)
    # top chip + brand mark during end
    p = prog(t, 14.2, 0.5)
    if p > 0:
        s = spring(p)
        glass(f, blur, 540, 1120, 720 * s, 96 * s, 48)
        put(f, CHIP, 540, 1120, min(1, p * 2))
    return f.convert('RGB')

if __name__ == '__main__':
    if sys.argv[1] == 'test':
        ts = [float(x) for x in sys.argv[2:]]; ims = []
        for x in ts:
            t0 = time.time(); im = render(x); print(x, round(time.time() - t0, 2)); im.save(config.work(f'lg_{x}.png'))
            ims.append(im.resize((270, 480)))
        sh = Image.new('RGB', (270 * len(ims), 480)); [sh.paste(im, (i * 270, 0)) for i, im in enumerate(ims)]
        sh.save(config.work('lgsheet.png')); sys.exit()
    a, b = int(sys.argv[1]), int(sys.argv[2])
    enc = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}',
                            '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '15', '-pix_fmt', 'yuv420p',
                            config.work(f'lgseg_{a:04d}.mp4')], stdin=subprocess.PIPE)
    t0 = time.time()
    for i in range(a, min(b, int(DUR * FPS))): enc.stdin.write(render(i / FPS).tobytes())
    enc.stdin.close(); enc.wait(); print('done', round(time.time() - t0))
