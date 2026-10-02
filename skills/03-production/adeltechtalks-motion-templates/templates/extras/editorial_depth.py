"""Style C — Editorial Depth: Adel cut out in front of giant words, step cards, counters"""
import sys, math, subprocess, time, glob
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # skill root, so the engine package is importable
from engine import config
_BRAND = config.brand(); _END = _BRAND['ending']  # name, tagline and ending text from brand.json
from PIL import Image, ImageDraw, ImageFilter
from engine.plib import UP, txt, CAIRO, MONT, READ, MONO, WHITE, CORAL, GRAPH

W, H, FPS, DUR = 1080, 1920, 30, 30.0
BG = (243, 238, 228); SIG = config.color('primary'); SLATE = config.color('muted'); CX = 540
def clamp(v, a, b): return max(a, min(b, v))
def prog(t, s, d): return clamp((t - s) / d, 0, 1)
def ease(p): return 1 - (1 - p) ** 3
def spring(p): return 1 - math.exp(-7 * p) * math.cos(8 * p) if p < 1 else 1.0
def put(f, spr, cx, cy, a=1.0, s=1.0, rot=0):
    if a <= 0.01: return
    im = spr if abs(s - 1) < 0.003 else spr.resize((max(1, int(spr.width * s)), max(1, int(spr.height * s))), Image.BICUBIC)
    if rot: im = im.rotate(rot, Image.BICUBIC, expand=True)
    if a < 0.999: im = im.copy(); im.putalpha(im.split()[3].point(lambda v: int(v * a)))
    f.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2)))
def shadowed(im, blur=14, op=70, off=10):
    a = im.split()[3].point(lambda v: v * op // 255)
    out = Image.new('RGBA', (im.width + blur * 4, im.height + blur * 4 + off), (0, 0, 0, 0))
    k = Image.new('RGBA', im.size, (40, 30, 20, 255)); k.putalpha(a); out.alpha_composite(k, (blur * 2, blur * 2 + off))
    out = out.filter(ImageFilter.GaussianBlur(blur)); out.alpha_composite(im, (blur * 2, blur * 2)); return out
def card(w, h, r, col):
    s = 2; im = Image.new('RGBA', (w * s, h * s), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle((0, 0, w * s - 1, h * s - 1), r * s, fill=col); return im.resize((w, h), Image.LANCZOS)

# cut-out of Adel, soft fade at the bottom edge
CUT = config.input_image('cutout.png', (1000, 1100), 'the subject cut-out', rgba=True).convert('RGBA').crop((45, 88, 966, 1063))
CUT = CUT.resize((900, int(900 * CUT.height / CUT.width)), Image.LANCZOS)
fade = Image.new('L', CUT.size, 255); fd = ImageDraw.Draw(fade)
for y in range(CUT.height - 120, CUT.height): fd.line((0, y, CUT.width, y), fill=int(255 * (CUT.height - y) / 120))
CUT.putalpha(Image.composite(CUT.split()[3], Image.new('L', CUT.size, 0), fade))
CUT_SH = shadowed(CUT, 24, 60, 14)
CUT_Y = 1560 - CUT.height / 2

def giant(word, col): return txt(word, MONT(300), col)
GIANTS = [(0.2, 3.4, giant('MOTION', GRAPH)), (3.4, 7.0, giant('CLAUDE', SIG)), (7.0, 19.0, giant('3 STEPS', GRAPH)),
          (19.0, 26.8, giant('RESULT', SIG)), (26.8, 99, giant('FOLLOW', GRAPH))]
TOP = [(0.3, 3.3, 'ينفع تعمل موشن جرافيك؟'), (3.5, 6.9, 'من غير برنامج… بس Claude'), (7.1, 18.9, 'في 3 خطوات بس'),
       (19.1, 23.9, 'ده اتعمل كله بـ Claude'), (24.1, 26.7, '30 ثانية · 0 برامج مونتاج'), (26.9, 99, 'عايز تتعلمها؟')]
TOP_S = [(a, b, txt(s, CAIRO(64), GRAPH, rtl=True)) for a, b, s in TOP]
def step(num, label):
    n = txt(num, MONO(64), SIG); l = txt(label, CAIRO(52), GRAPH, rtl=True)
    c = card(n.width + l.width + 110, 128, 30, (255, 255, 255, 255))
    c.alpha_composite(l, (40, (128 - l.height) // 2)); c.alpha_composite(n, (c.width - n.width - 36, (128 - n.height) // 2))
    return shadowed(c)
STEPS = [(7.4, step('01', 'اكتبله فكرتك')), (11.3, step('02', 'ابعتله ريفرنس وصورك')), (15.2, step('03', 'بيكتب الكود ويرندر'))]
RES = [fr.resize((300, 533), Image.LANCZOS) for fr in config.input_frames('result')]
def round_mask(im, r):
    s = 2; m = Image.new('L', (im.width * s, im.height * s), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, im.width * s - 1, im.height * s - 1), r * s, fill=255)
    im = im.copy(); im.putalpha(m.resize(im.size, Image.LANCZOS)); return im
RES = [round_mask(r, 26) for r in RES]
CTA_T = txt(_END['follow'], CAIRO(54), WHITE, rtl=True)
MARK = config.logo().convert('RGBA'); MARK = MARK.resize((52, int(52 * MARK.height / MARK.width)), Image.LANCZOS)
CTA = card(CTA_T.width + 150, 116, 58, CORAL + (255,)); CTA.alpha_composite(CTA_T, (100, (116 - CTA_T.height) // 2)); CTA.alpha_composite(MARK, (36, (116 - MARK.height) // 2))
CTA = shadowed(CTA)

def arrow(f, x0, y0, x1, y1, p, col=SIG):
    if p <= 0: return
    ov = Image.new('RGBA', (W * 2, H * 2), (0, 0, 0, 0)); d = ImageDraw.Draw(ov); pts = []
    for k in range(int(40 * p) + 1):
        u = k / 40; x = x0 + (x1 - x0) * u; y = y0 + (y1 - y0) * u - 120 * math.sin(math.pi * u)
        pts.append((x * 2, y * 2))
    if len(pts) > 1: d.line(pts, fill=col + (255,), width=12, joint='curve')
    if p >= 1:
        d.line([(x1 * 2, y1 * 2), (x1 * 2 + 40, y1 * 2 - 36)], fill=col + (255,), width=12)
        d.line([(x1 * 2, y1 * 2), (x1 * 2 + 50, y1 * 2 + 14)], fill=col + (255,), width=12)
    f.alpha_composite(ov.resize((W, H), Image.LANCZOS))

def render(t):
    f = Image.new('RGBA', (W, H), BG + (255,))
    # giant word behind (slides + swaps)
    for a_, b_, g in GIANTS:
        pin = ease(prog(t, a_, 0.45)); pout = prog(t, b_ - 0.25, 0.25)
        if pin > 0 and pout < 1:
            s = 1 if g.width < W - 40 else (W - 40) / g.width
            put(f, g, CX + 120 * (1 - pin) - 140 * pout, 700, pin * (1 - pout), s)
    # Adel in front (depth) — slow push
    pin = ease(prog(t, 0.0, 0.6)); z = 1 + 0.04 * (t / DUR)
    put(f, CUT_SH, CX, CUT_Y + 24 + 160 * (1 - pin), pin, z)
    # top line
    for a_, b_, s_ in TOP_S:
        a = ease(prog(t, a_, 0.35)) * (1 - prog(t, b_ - 0.2, 0.2))
        if a > 0: put(f, s_, CX, 360 + 20 * (1 - ease(prog(t, a_, 0.35))), a)
    # steps stack up over the torso
    for i, (t0, sp) in enumerate(STEPS):
        p = prog(t, t0, 0.5); out = prog(t, 18.8, 0.25)
        if p > 0 and out < 1:
            put(f, sp, CX + 600 * (1 - ease(p)) * (1 if i % 2 else -1), 1150 + i * 150, (1 - out) * min(1, p * 2), 1, -2 if i % 2 else 2)
    # render counter during step 3
    if 15.6 <= t < 18.9:
        p = ease(prog(t, 15.7, 2.4)); put(f, txt(f'{int(100 * p)}%', MONO(96), SIG), 880, 1000, 1 - prog(t, 18.7, 0.2))
    # result: the real reel plays in a tilted card + hand-drawn arrow
    if 19.0 <= t < 26.8:
        p = spring(prog(t, 19.1, 0.6)); out = prog(t, 26.5, 0.3)
        k = int(clamp((t - 19.3) * 22, 0, len(RES) - 1))
        put(f, shadowed(RES[k], 18, 90, 14), 770, 1180, (1 - out), 0.6 + 0.4 * p, -5)
        arrow(f, 250, 1050, 590, 1140, prog(t, 20.0, 0.6) * (1 - out) if out < 1 else 0)
    # CTA (single Spark Coral element)
    p = prog(t, 27.3, 0.45)
    if p > 0:
        pulse = 1 + 0.025 * math.sin((t - 28.2) * 6) if t > 28.2 else 1
        put(f, CTA, CX, 1300, min(1, p * 2.5), (0.6 + 0.4 * spring(p)) * pulse)
    return f.convert('RGB')

if __name__ == '__main__':
    if sys.argv[1] == 'test':
        ts = [float(x) for x in sys.argv[2:]]; ims = []
        for x in ts:
            im = render(x); im.save(config.work(f'ed_{x}.png')); ims.append(im.resize((216, 384)))
        sh = Image.new('RGB', (216 * len(ims), 384)); [sh.paste(im, (i * 216, 0)) for i, im in enumerate(ims)]
        sh.save(config.work('edsheet.png')); sys.exit()
    enc = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS),
                            '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '16', '-pix_fmt', 'yuv420p', config.work('ed_v.mp4')], stdin=subprocess.PIPE)
    t0 = time.time()
    for i in range(int(DUR * FPS)): enc.stdin.write(render(i / FPS).tobytes())
    enc.stdin.close(); enc.wait(); print('done', round(time.time() - t0))
