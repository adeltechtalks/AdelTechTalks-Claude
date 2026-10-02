"""Style B — Minimal Shape-Morph (one white shape morphing into icons), same 30s story"""
import sys, math, subprocess, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # skill root, so the engine package is importable
from engine import config
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from engine.plib import UP, txt, CAIRO, MONT, READ, MONO, WHITE, CORAL

W, H, FPS, DUR = 1080, 1920, 30, 30.0
BG = (14, 16, 20); INK = (23, 26, 31); CX, CY = 540, 1030; N = 360
TH = np.linspace(0, 2 * np.pi, N, endpoint=False)

def clamp(v, a, b): return max(a, min(b, v))
def prog(t, s, d): return clamp((t - s) / d, 0, 1)
def ease(p): return 1 - (1 - p) ** 3
def eio(p): return 3 * p * p - 2 * p ** 3
def spring(p): return 1 - math.exp(-7 * p) * math.cos(8 * p) if p < 1 else 1.0

# ---- shapes as polar radius arrays r(θ) around the centre ----
def polar_of_poly(pts):
    pts = np.asarray(pts, float); r = np.zeros(N)
    a = pts; b = np.roll(pts, -1, 0)
    for i, th in enumerate(TH):
        d = np.array([math.cos(th), -math.sin(th)]); best = 0
        for p, q in zip(a, b):
            e = q - p; den = d[0] * e[1] - d[1] * e[0]
            if abs(den) < 1e-9: continue
            s = (p[0] * e[1] - p[1] * e[0]) / den; u = (p[0] * d[1] - p[1] * d[0]) / den
            if s > 0 and 0 <= u <= 1: best = max(best, s)
        r[i] = best
    return r
def rrect_pts(w, h, r, k=12):
    pts = []
    for cx, cy, a0 in ((w / 2 - r, -h / 2 + r, -90), (w / 2 - r, h / 2 - r, 0), (-w / 2 + r, h / 2 - r, 90), (-w / 2 + r, -h / 2 + r, 180)):
        for j in range(k + 1):
            a = math.radians(a0 + 90 * j / k); pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts
def circle(R): return np.full(N, float(R))
def rrect(w, h, r): return polar_of_poly(rrect_pts(w, h, r))
def bubble(w, h, r):
    pts = rrect_pts(w, h, r)
    # tail at bottom-left
    i = min(range(len(pts)), key=lambda k: (pts[k][0] + w * 0.25) ** 2 + (pts[k][1] - h / 2) ** 2)
    pts = pts[:i] + [(-w * 0.18, h / 2), (-w * 0.36, h / 2 + 70), (-w * 0.30, h / 2)] + pts[i:]
    return polar_of_poly(pts)
def triangle_play(R):
    return polar_of_poly([(R * math.cos(math.radians(a)), R * math.sin(math.radians(a))) for a in (0, 120, 240)])
def gear(R, teeth=8, depth=34):
    sq = (np.sin(TH * teeth) > 0).astype(float)
    sq = np.convolve(np.concatenate([sq[-6:], sq, sq[:6]]), np.ones(7) / 7, 'same')[6:-6]
    return R + depth * sq
def star(R, r):
    pts = []
    for k in range(10):
        a = math.radians(-90 + 36 * k); rr = R if k % 2 == 0 else r; pts.append((rr * math.cos(a), rr * math.sin(a)))
    return polar_of_poly(pts)

SH = {
    'dot': circle(26), 'big': circle(120), 'bubble': bubble(560, 340, 70), 'frame': rrect(380, 660, 34),
    'gear': gear(170), 'small': circle(18), 'play': triangle_play(190), 'pill': rrect(660, 130, 65), 'none': circle(0),
}
# (start, shape, cx, cy)
STATES = [(0.0, 'none'), (0.25, 'dot'), (1.6, 'big'), (3.0, 'bubble'), (10.0, 'dot'), (10.5, 'frame'),
          (14.0, 'gear'), (18.0, 'none'), (22.0, 'play'), (26.0, 'dot'), (26.5, 'pill')]
def shape_at(t):
    idx = 0
    for i, s in enumerate(STATES):
        if t >= s[0]: idx = i
    a = SH[STATES[max(0, idx - 1)][1]]; b = SH[STATES[idx][1]]
    p = spring(prog(t, STATES[idx][0], 0.55)) if idx else 1
    return a + (b - a) * p

def poly_xy(r, cx, cy, rot=0.0, S=2):
    th = TH + rot
    return [((cx + rr * math.cos(a)) * S, (cy - rr * math.sin(a)) * S) for rr, a in zip(r, th)]

# ---- text ----
def T(s, size=72, col=WHITE, font=CAIRO): return txt(s, font(size), col, rtl=True)
LINES = [  # (in, out, text)
    (0.3, 2.9, T('ينفع تعمل موشن جرافيك؟')),
    (3.2, 6.0, T('كل اللي محتاجه… Claude')),
    (6.1, 9.9, T('اكتبله فكرتك')),
    (10.4, 13.9, T('ابعتله ريفرنس وصورك')),
    (14.2, 17.9, T('Claude بيكتب الكود')),
    (18.2, 21.9, T('ويرندر الفيديو في دقايق')),
    (22.2, 25.9, T('والنتيجة؟ تحفة')),
    (26.4, 99, T('عايز تتعلمها؟')),
]
SUB = txt('بدون أي برنامج مونتاج', READ(40, 400), (150, 156, 168), rtl=True)
CTA = T('تابع AdelTechTalks', 52)
MARK = Image.open(config.asset('atc-mark-white-1024.png')).convert('RGBA'); MARK = MARK.resize((90, int(90 * MARK.height / MARK.width)), Image.LANCZOS)
SMALL_MARK = MARK.resize((50, int(50 * MARK.height / MARK.width)), Image.LANCZOS)
CODE = txt('</>', MONO(110), INK)

def put(f, spr, cx, cy, a=1.0, s=1.0):
    if a <= 0.01: return
    im = spr if abs(s - 1) < 0.003 else spr.resize((max(1, int(spr.width * s)), max(1, int(spr.height * s))), Image.BICUBIC)
    if a < 0.999: im = im.copy(); im.putalpha(im.split()[3].point(lambda v: int(v * a)))
    f.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2)))

def render(t):
    f = Image.new('RGBA', (W, H), BG + (255,))
    # soft spotlight behind the shape (like the reference glow)
    S = 2; L = Image.new('RGBA', (W * S, H * S), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    r = shape_at(t)
    rot = (t - 14.0) * 1.2 if 14.0 <= t < 18.3 else 0.0
    breathe = 1 + (0.06 * math.sin(t * 4) if t < 1.6 else 0)
    col = WHITE
    pc = prog(t, 26.5, 0.4)
    if pc > 0: col = tuple(int(WHITE[k] + (CORAL[k] - WHITE[k]) * ease(pc)) for k in range(3))   # single Spark Coral element
    if r.max() > 0.5:
        d.polygon(poly_xy(r * breathe, CX, CY, rot), fill=col + (255,))
    # beat overlays drawn on the same supersampled layer
    if 6.1 <= t < 10.0:      # message lines inside the bubble + send arrow
        for i in range(3):
            p = ease(prog(t, 6.4 + i * 0.35, 0.4)); wl = [400, 330, 220][i] * p
            y = CY - 80 + i * 80
            if wl > 4: d.rounded_rectangle(((CX - 200) * S, (y - 14) * S, (CX - 200 + wl) * S, (y + 14) * S), 14 * S, fill=INK + (255,))
    if 10.9 <= t < 14.0:     # image icon inside the frame: sun + mountains
        p = ease(prog(t, 11.1, 0.5))
        d.ellipse(((CX + 60) * S, (CY - 180) * S, (CX + 130) * S, (CY - 110) * S), fill=INK + (int(255 * p),))
        hh = 220 * p
        d.polygon([((CX - 170) * S, (CY + 160) * S), ((CX - 40) * S, (CY + 160 - hh) * S), ((CX + 90) * S, (CY + 160) * S)], fill=INK + (255,))
        d.polygon([((CX - 10) * S, (CY + 160) * S), ((CX + 80) * S, (CY + 160 - hh * 0.6) * S), ((CX + 170) * S, (CY + 160) * S)], fill=INK + (255,))
    if 14.3 <= t < 18.0:     # gear hub
        d.ellipse(((CX - 92) * S, (CY - 92) * S, (CX + 92) * S, (CY + 92) * S), fill=BG + (255,))
    if 18.2 <= t < 22.0:     # progress ring
        p = eio(prog(t, 18.5, 2.6)); R = 230
        d.ellipse(((CX - R) * S, (CY - R) * S, (CX + R) * S, (CY + R) * S), outline=(60, 64, 72, 255), width=16 * S)
        if p > 0: d.arc(((CX - R) * S, (CY - R) * S, (CX + R) * S, (CY + R) * S), -90, -90 + 360 * p, fill=WHITE + (255,), width=16 * S)
    if 22.6 <= t < 26.0:     # stars burst around the play triangle
        p = ease(prog(t, 22.6, 0.7)); fade = 1 - prog(t, 25.6, 0.3)
        for k in range(5):
            a = math.radians(-90 + 72 * k); dist = 230 + 90 * p; sx, sy = CX + dist * math.cos(a), CY + dist * math.sin(a)
            st = SH_STAR * (0.4 + 0.6 * p)
            d.polygon(poly_xy(st, sx, sy, 0, S), fill=WHITE + (int(255 * fade * min(1, p * 2)),))
    L = L.resize((W, H), Image.LANCZOS)
    glow = L.resize((W // 8, H // 8), Image.BILINEAR).filter(ImageFilter.GaussianBlur(10)).resize((W, H), Image.BICUBIC)
    ga = glow.split()[3].point(lambda v: int(v * 0.35)); glow.putalpha(ga); f.alpha_composite(glow)
    f.alpha_composite(L)
    # sprites on top
    if 14.3 <= t < 18.0: put(f, CODE, CX, CY - 4, 1 - prog(t, 17.8, 0.2), 0.7 + 0.3 * ease(prog(t, 14.4, 0.4)))
    if 18.2 <= t < 22.0:
        p = eio(prog(t, 18.5, 2.6)); put(f, txt(f'{int(100 * p)}%', MONO(72), WHITE), CX, CY, 1 - prog(t, 21.8, 0.2))
    if t >= 26.9:
        a = ease(prog(t, 26.9, 0.35)); put(f, SMALL_MARK, CX - CTA.width / 2 - 12, CY, a); put(f, CTA, CX + 22, CY, a)
    if t >= 1.0 and t < 2.9: put(f, SUB, CX, 760, ease(prog(t, 1.0, 0.4)) * (1 - prog(t, 2.7, 0.2)))
    for t_in, t_out, spr in LINES:
        a = ease(prog(t, t_in, 0.35)) * (1 - prog(t, t_out - 0.2, 0.2))
        if a > 0: put(f, spr, CX, 640 + 22 * (1 - ease(prog(t, t_in, 0.35))), a)
    if t >= 27.6:  # brand sign-off under the pill
        put(f, MARK, CX, 1300, ease(prog(t, 27.6, 0.4)) * 0.9)
    return f.convert('RGB')
SH_STAR = star(34, 14)

if __name__ == '__main__':
    if sys.argv[1] == 'test':
        ts = [float(x) for x in sys.argv[2:]]; ims = []
        for x in ts:
            im = render(x); im.save(config.work(f'sh_{x}.png')); ims.append(im.resize((216, 384)))
        sh = Image.new('RGB', (216 * len(ims), 384)); [sh.paste(im, (i * 216, 0)) for i, im in enumerate(ims)]
        sh.save(config.work('shsheet.png')); sys.exit()
    enc = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS),
                            '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '16', '-pix_fmt', 'yuv420p', config.work('sh_v.mp4')], stdin=subprocess.PIPE)
    t0 = time.time()
    for i in range(int(DUR * FPS)): enc.stdin.write(render(i / FPS).tobytes())
    enc.stdin.close(); enc.wait(); print('done', round(time.time() - t0))
