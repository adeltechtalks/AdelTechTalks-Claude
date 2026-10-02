"""Style D — Minimal isometric 3D story (S14), faster pacing: one scene per bar @128 BPM"""
import sys, math, subprocess, time, glob
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # skill root, so the engine package is importable
from engine import config
_BRAND = config.brand(); _END = _BRAND['ending']  # name, tagline and ending text from brand.json
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from engine.plib import UP, txt, CAIRO, MONT, READ, MONO, WHITE, CORAL, GRAPH

W, H, FPS = 1080, 1920, 30
BPM = 128; BAR = 4 * 60 / BPM; NSC = 12; DUR = round(BAR * NSC + 1.6, 2)   # 12 scenes + CTA hold
ORANGE = config.color('ball'); OR_D = tuple(int(v * 0.86) for v in ORANGE); SIG = config.color('primary'); SLATE = config.color('muted')
CX = 540
def clamp(v, a, b): return max(a, min(b, v))
def prog(t, s, d): return clamp((t - s) / d, 0, 1)
def ease(p): return 1 - (1 - p) ** 3
def spring(p): return 1 - math.exp(-8 * p) * math.cos(10 * p) if p < 1 else 1.0
def shade(c, k): return tuple(int(clamp(v * k, 0, 255)) for v in c)
def put(f, spr, cx, cy, a=1.0, s=1.0, rot=0):
    if a <= 0.01 or s <= 0.01: return
    im = spr if abs(s - 1) < 0.003 else spr.resize((max(1, int(spr.width * s)), max(1, int(spr.height * s))), Image.BICUBIC)
    if rot: im = im.rotate(rot, Image.BICUBIC, expand=True)
    if a < 0.999: im = im.copy(); im.putalpha(im.split()[3].point(lambda v: int(v * a)))
    f.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2)))

# ---------- isometric toolkit (drawn at 2x, downsampled) ----------
SS = 3; OS = 1.5   # draw at 3x, deliver at 1.5x (bigger hero objects)
class Iso:
    def __init__(self, size=700, s=90):
        self.w = self.h = size * SS; self.s = s * SS
        self.im = Image.new('RGBA', (self.w, self.h), (0, 0, 0, 0)); self.d = ImageDraw.Draw(self.im)
        self.ox, self.oy = self.w / 2, self.h * 0.62
    def P(self, x, y, z): return (self.ox + (x - y) * 0.866 * self.s, self.oy + (x + y) * 0.5 * self.s - z * self.s)
    def poly(self, pts, col): self.d.polygon([self.P(*p) for p in pts], fill=col + (255,) if len(col) == 3 else col)
    def box(self, x0, y0, z0, dx, dy, dz, col):
        x1, y1, z1 = x0 + dx, y0 + dy, z0 + dz
        self.poly([(x0, y1, z0), (x1, y1, z0), (x1, y1, z1), (x0, y1, z1)], shade(col, 0.78))   # left-front face
        self.poly([(x1, y0, z0), (x1, y1, z0), (x1, y1, z1), (x1, y0, z1)], shade(col, 0.9))    # right-front face
        self.poly([(x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)], shade(col, 1.06))   # top
    def done(self):
        im = self.im.resize((int(self.w * OS / SS), int(self.h * OS / SS)), Image.LANCZOS)
        return im.crop(im.getbbox())

def floor_shadow(w, h=60):
    m = Image.new('L', (w, h * 2), 0); ImageDraw.Draw(m).ellipse((0, 0, w - 1, h * 2 - 1), fill=90)
    m = m.filter(ImageFilter.GaussianBlur(14)); s = Image.new('RGBA', m.size, (120, 60, 20, 255)); s.putalpha(m); return s

def extrude(front, depth=26, dx=0.55, dy=1.0, side=None):
    """fake 3D extrusion of a flat RGBA sprite"""
    a = front.split()[3]; side = side or (60, 66, 76)
    out = Image.new('RGBA', (front.width + int(depth * dx) + 2, front.height + int(depth * dy) + 2), (0, 0, 0, 0))
    for k in range(depth, 0, -1):
        sl = Image.new('RGBA', front.size, shade(side, 0.85 + 0.15 * (1 - k / depth)) + (255,)); sl.putalpha(a)
        out.alpha_composite(sl, (int(k * dx), int(k * dy)))
    out.alpha_composite(front, (0, 0)); return out

# phone (standing). returns sprite + its screen parallelogram (for video mapping)
def make_phone(screen=True):
    I = Iso(800, 95); I.box(0, 0, 0, 0.28, 1.9, 3.6, (40, 44, 52))
    x1 = 0.28; m = 0.12
    scr = [(x1 + 0.001, 0 + m, 0 + m), (x1 + 0.001, 1.9 - m, 0 + m), (x1 + 0.001, 1.9 - m, 3.6 - m), (x1 + 0.001, 0 + m, 3.6 - m)]
    if screen: I.poly(scr, (18, 20, 26))
    bb = I.im.getbbox(); quad = [I.P(*p) for p in scr]
    im = I.done(); quad = [((x - bb[0]) * OS / SS, (y - bb[1]) * OS / SS) for x, y in quad]
    return im, quad
PHONE, PHONE_Q = make_phone()
def play_on(phone, quad):
    im = phone.copy(); d = ImageDraw.Draw(im)
    c = [sum(p[0] for p in quad) / 4, sum(p[1] for p in quad) / 4]
    d.polygon([(c[0] - 50, c[1] - 90), (c[0] - 50, c[1] + 60), (c[0] + 75, c[1] - 15)], fill=ORANGE + (255,)); return im
PHONE_PLAY = play_on(PHONE, PHONE_Q)

def make_laptop():
    I = Iso(900, 80)
    I.box(0, 0, 0, 3.4, 2.4, 0.18, (205, 210, 220))                    # base
    I.poly([(0.3, 0.3, 0.181), (3.1, 0.3, 0.181), (3.1, 1.7, 0.181), (0.3, 1.7, 0.181)], (175, 180, 192))  # keyboard
    I.box(0, 0, 0.18, 3.4, 0.14, 2.3, (190, 196, 208))                 # screen slab (back)
    I.poly([(0.15, 0.141, 0.33), (3.25, 0.141, 0.33), (3.25, 0.141, 2.33), (0.15, 0.141, 2.33)], (24, 26, 32))
    # big X on the screen (no software)
    for a, b in (((0.9, 0.142, 0.75), (2.5, 0.142, 1.95)), ((2.5, 0.142, 0.75), (0.9, 0.142, 1.95))):
        I.d.line([I.P(*a), I.P(*b)], fill=(239, 68, 68, 255), width=13 * SS)
    return I.done()
LAPTOP = make_laptop()

def bubble_sprite(w=620, h=400, col=WHITE):
    s = 2; im = Image.new('RGBA', (w * s, (h + 70) * s), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w * s, h * s), 60 * s, fill=col + (255,))
    d.polygon([(100 * s, (h - 5) * s), (85 * s, (h + 65) * s), (230 * s, (h - 5) * s)], fill=col + (255,))
    return im.resize((w, h + 70), Image.LANCZOS)
BUB = extrude(bubble_sprite(), 40, side=(210, 190, 175))

def make_notepad():
    I = Iso(800, 90); I.box(0, 0, 0, 2.6, 3.2, 0.25, (255, 255, 255))
    for i in range(4):
        y = 0.6 + i * 0.6; L = [1.9, 1.6, 2.0, 1.1][i]
        I.poly([(0.35, y, 0.251), (0.35 + L, y, 0.251), (0.35 + L, y + 0.16, 0.251), (0.35, y + 0.16, 0.251)], SIG if i == 0 else (200, 205, 215))
    return I.done()
NOTE = make_notepad()

def make_tiles():
    out = []
    for k, col in enumerate(((255, 214, 170), (205, 225, 255), (200, 240, 225))):
        I = Iso(600, 80); I.box(0, 0, 0, 2.4, 2.4, 0.16, (255, 255, 255))
        I.poly([(0.2, 0.2, 0.161), (2.2, 0.2, 0.161), (2.2, 2.2, 0.161), (0.2, 2.2, 0.161)], col)
        I.poly([(0.5, 1.9, 0.162), (1.3, 0.9, 0.162), (2.0, 1.9, 0.162)], shade(col, 0.6))
        out.append(I.done())
    return out
TILES = make_tiles()

def make_monitor():
    I = Iso(900, 80)
    I.box(1.3, 0.9, 0, 1.0, 1.0, 0.12, (60, 64, 72)); I.box(1.65, 1.25, 0.12, 0.3, 0.3, 1.1, (70, 74, 82))
    I.box(0, 1.2, 1.2, 3.6, 0.18, 2.3, (40, 44, 52))
    I.poly([(0.12, 1.381, 1.32), (3.48, 1.381, 1.32), (3.48, 1.381, 3.38), (0.12, 1.381, 3.38)], (16, 18, 24))
    bb = I.im.getbbox()
    quad = [I.P(0.12, 1.381, 3.38), I.P(3.48, 1.381, 3.38), I.P(0.12, 1.381, 1.32)]
    return I.done(), [((x - bb[0]) * OS / SS, (y - bb[1]) * OS / SS) for x, y in quad]
MONITOR, MON_Q = make_monitor()

def affine_paste(dst, src, quad3):
    """map src (w,h) onto dst parallelogram given TL, TR, BL points"""
    (x0, y0), (x1, y1), (x2, y2) = quad3; w, h = src.size
    A = np.array([[x1 - x0, x2 - x0], [y1 - y0, y2 - y0]]) / np.array([w, h])
    inv = np.linalg.inv(A)
    a, b = inv[0]; d, e = inv[1]
    c = -(a * x0 + b * y0); ff = -(d * x0 + e * y0)
    warped = src.transform(dst.size, Image.AFFINE, (a, b, c, d, e, ff), Image.BICUBIC)
    dst.alpha_composite(warped)
code_img = Image.new('RGBA', (600, 360), (0, 0, 0, 0)); cd = ImageDraw.Draw(code_img)
cd.text((300, 180), '</>', font=MONO(190), fill=(90, 220, 170, 255), anchor='mm')
MONITOR_CODE = MONITOR.copy(); affine_paste(MONITOR_CODE, code_img, MON_Q)
# phone screen quad as TL, TR, BL for the video
q = PHONE_Q  # order: (y0,z0),(y1,z0),(y1,z1),(y0,z1) -> image left = y1 side
PH_TL, PH_TR, PH_BL = q[2], q[3], q[1]
RES = [fr for fr in config.input_frames('result')]

def gear_sprite(rot):
    R, teeth, dep = 210, 9, 46; s = 2; im = Image.new('RGBA', (600 * s, 600 * s), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    pts = []
    for k in range(360):
        th = math.radians(k) + rot; rr = R + dep * (1 if math.sin(teeth * (math.radians(k))) > 0 else 0)
        pts.append(((300 + rr * math.cos(th)) * s, (300 + rr * math.sin(th)) * s))
    d.polygon(pts, fill=SIG + (255,)); d.ellipse(((300 - 86) * s, (300 - 86) * s, (300 + 86) * s, (300 + 86) * s), fill=(0, 0, 0, 0))
    return extrude(im.resize((600, 600), Image.LANCZOS), 40, side=(20, 60, 160))

MARK = config.logo().convert('RGBA'); MARK = MARK.resize((520, int(520 * MARK.height / MARK.width)), Image.LANCZOS)
MARK_F = Image.new('RGBA', MARK.size, SIG + (255,)); MARK_F.putalpha(MARK.split()[3]); MARK3D = extrude(MARK_F, 44, side=(20, 60, 160))
SMALL_MARK = MARK.resize((52, int(52 * MARK.height / MARK.width)), Image.LANCZOS)

# ---------- text ----------
def line(s, size=84, col=GRAPH): return txt(s, CAIRO(size), col, rtl=True)
SCENES = [  # (headline, accent-sub or None, object key)
    ('موشن جرافيك زي ده؟', None, 'phone'),
    ('من غير ولا برنامج مونتاج', None, 'laptop'),
    ('كل اللي محتاجه…', None, 'bubble'),
    ('Claude', None, 'claude'),
    ('اكتبله فكرتك', '01', 'note'),
    ('ابعتله ريفرنس وصورك', '02', 'tiles'),
    ('بيكتب الكود', '03', 'monitor'),
    ('ويرندر في دقايق', None, 'gear'),
    ('والنتيجة؟', None, 'result'),
    ('ثانية', None, 'count'),
    ('من غير ولا برنامج', None, 'zero'),
    ('عايز تتعلمها؟', None, 'mark'),
]
HEADS = [line(h_) if h_ != 'Claude' else txt('Claude', MONT(150), SIG) for h_, _, _ in SCENES]
NUMS = {i: txt(n, MONO(64), ORANGE) for i, (_, n, _) in enumerate(SCENES) if n}
CTA_T = txt(_END['follow'], CAIRO(54), WHITE, rtl=True)
FOLLOWING = txt(_END['following'], MONT(42), WHITE)

# ---------- background ----------
grad = Image.new('RGB', (1, H))
for y in range(H):
    u = y / H; grad.putpixel((0, y), (int(255 - 8 * u), int(240 - 26 * u), int(228 - 40 * u)))
BG = grad.resize((W, H)).convert('RGBA')
# soft window light on the background only
win = Image.new('L', (W, H), 0); wd = ImageDraw.Draw(win)
for i in range(2):
    for j in range(3): wd.rectangle((120 + i * 330, 160 + j * 300, 400 + i * 330, 420 + j * 300), fill=60)
win = win.rotate(-12, Image.BICUBIC).filter(ImageFilter.GaussianBlur(40))
wl = Image.new('RGBA', (W, H), (255, 252, 245, 255)); wl.putalpha(win); BG.alpha_composite(wl)
# out-of-focus orange bokeh for depth
for (x, y, r) in ((-60, 1650, 230), (980, 180, 170), (1000, 1500, 120)):
    b = Image.new('RGBA', (r * 4, r * 4), (0, 0, 0, 0)); ImageDraw.Draw(b).ellipse((r, r, r * 3, r * 3), fill=ORANGE + (120,))
    BG.alpha_composite(b.filter(ImageFilter.GaussianBlur(r // 3)), (x - r * 2, y - r * 2))

def ribbon(f, t, t0, k):
    """thick orange ribbon sweeping across behind the object on every scene change"""
    p = ease(prog(t, t0 - 0.05, 0.45)); fade = 1 - prog(t, t0 + BAR - 0.2, 0.2)
    if p <= 0 or fade <= 0: return
    ov = Image.new('RGBA', (W // 2, H // 2), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    sgn = 1 if k % 2 else -1; pts = []
    for i in range(int(60 * p) + 1):
        u = i / 60; x = (-200 + 1480 * u) if sgn > 0 else (1280 - 1480 * u)
        y = 1250 - 500 * u + 160 * math.sin(u * math.pi * 1.6 + k)
        pts.append((x / 2, y / 2))
    if len(pts) > 1:
        col = ORANGE + (int(255 * fade),); d.line(pts, fill=col, width=70)
        for (x, y) in pts: d.ellipse((x - 35, y - 35, x + 35, y + 35), fill=col)
    f.alpha_composite(ov.resize((W, H), Image.BICUBIC))

def obj_for(key, t, t0):
    lt = t - t0
    if key == 'phone': return PHONE_PLAY
    if key == 'laptop': return LAPTOP
    if key == 'bubble': return BUB
    if key == 'claude':
        b = BUB.copy(); d = ImageDraw.Draw(b)
        for k in range(3):
            bb = 0.5 + 0.5 * math.sin(lt * 10 - k * 0.9); x = 180 + k * 130; y = 200 - bb * 20
            d.ellipse((x - 32, y - 32, x + 32, y + 32), fill=(120, 126, 138, 255))
        return b
    if key == 'note': return NOTE
    if key == 'monitor': return MONITOR_CODE
    if key == 'gear': return gear_sprite(lt * 2.2)
    if key == 'mark': return MARK3D
    if key == 'result':
        ph = PHONE.copy(); k = int(clamp(lt * 40, 0, len(RES) - 1))
        affine_paste(ph, RES[k], (PH_TL, PH_TR, PH_BL)); return ph
    return None

def render(t):
    f = BG.copy()
    sc = min(int(t / BAR), NSC - 1) if t < BAR * NSC else NSC
    if sc < NSC:
        t0 = sc * BAR; key = SCENES[sc][2]
        ribbon(f, t, t0, sc)
        out = prog(t, t0 + BAR - 0.16, 0.16)
        # headline (types in fast), number badge
        p = ease(prog(t, t0 + 0.05, 0.25))
        hy = 440 if key != 'claude' else 640
        put(f, HEADS[sc], CX, hy + 30 * (1 - p), p * (1 - out))
        if sc in NUMS: put(f, NUMS[sc], CX, hy - 95, p * (1 - out))
        # object drops in with squash & stretch
        o = obj_for(key, t, t0)
        if o is not None:
            pin = prog(t, t0 + 0.08, 0.5); s = spring(pin); y = 1080 - 260 * (1 - ease(pin))
            squash = 1 + 0.08 * math.sin(math.pi * clamp((pin - 0.35) / 0.4, 0, 1))
            put(f, floor_shadow(int(o.width * 0.8)), CX, 1080 + o.height * 0.42, min(1, pin * 2) * (1 - out))
            im = o.resize((max(1, int(o.width * s * (2 - squash) * 0.98)), max(1, int(o.height * s * squash * 0.98))), Image.BICUBIC) if s > 0.05 else None
            if im is not None: put(f, im, CX, y, min(1, pin * 3) * (1 - out), 1 - 0.3 * out)
        if key == 'tiles':
            for k_, tile in enumerate(TILES):
                pin = prog(t, t0 + 0.08 + k_ * 0.12, 0.45)
                put(f, tile, CX - 60 + k_ * 60, 1120 - k_ * 70 - 300 * (1 - ease(pin)), min(1, pin * 3) * (1 - out), spring(pin))
        if key == 'count':
            p = prog(t, t0 + 0.05, BAR * 0.7); n = int(30 * ease(p))
            put(f, txt(str(n), MONT(360), GRAPH), CX, 1000, 1 - out, 1 + 0.04 * math.sin(t * 20) * (p < 1))
        if key == 'zero':
            put(f, txt('0', MONT(360), SIG), CX, 1000, (1 - out) * min(1, prog(t, t0, 0.15) * 3), spring(prog(t, t0, 0.4)))
            put(f, line('برامج مونتاج', 58, SLATE), CX, 1230, 1 - out)
    else:
        # CTA: Follow pill (single Spark Coral element) + tap -> Following
        t0 = BAR * NSC; p = spring(prog(t, t0, 0.45)); tap = prog(t, t0 + 0.75, 0.2); done = t >= t0 + 0.85
        put(f, MARK3D, CX, 800, min(1, prog(t, t0, 0.2) * 3), 0.6 + 0.2 * p)
        w_ = CTA_T.width + 160 if not done else FOLLOWING.width + 150; bs = 1 - 0.1 * math.sin(math.pi * tap)
        pill = Image.new('RGBA', (w_ * 2, 240), (0, 0, 0, 0)); ImageDraw.Draw(pill).rounded_rectangle((0, 0, w_ * 2 - 1, 239), 120, fill=(CORAL if not done else GRAPH) + (255,))
        pill = pill.resize((w_, 120), Image.LANCZOS)
        if not done: pill.alpha_composite(SMALL_MARK, (40, (120 - SMALL_MARK.height) // 2)); pill.alpha_composite(CTA_T, (110, (120 - CTA_T.height) // 2))
        else: pill.alpha_composite(FOLLOWING, ((w_ - FOLLOWING.width) // 2, (120 - FOLLOWING.height) // 2))
        put(f, floor_shadow(int(w_ * 0.9), 40), CX, 1180 + 70, min(1, p))
        put(f, pill, CX, 1180, min(1, p * 2), p * bs)
    return f.convert('RGB')

if __name__ == '__main__':
    if sys.argv[1] == 'test':
        ts = [float(x) for x in sys.argv[2:]]; ims = []
        for x in ts:
            t0 = time.time(); im = render(x); print(x, round(time.time() - t0, 2)); im.save(config.work(f'iso_{x}.png')); ims.append(im.resize((180, 320)))
        sh = Image.new('RGB', (180 * len(ims), 320)); [sh.paste(im, (i * 180, 0)) for i, im in enumerate(ims)]
        sh.save(config.work('isosheet.png')); sys.exit()
    print('DUR', DUR)
    enc = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS),
                            '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '16', '-pix_fmt', 'yuv420p', config.work('iso_v.mp4')], stdin=subprocess.PIPE)
    t0 = time.time()
    for i in range(int(DUR * FPS)): enc.stdin.write(render(i / FPS).tobytes())
    enc.stdin.close(); enc.wait(); print('done', round(time.time() - t0))
