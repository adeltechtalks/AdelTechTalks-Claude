"""Style E — Orange Ball Story: glossy orange balls carry the story (split, label, merge, morph)"""
import sys, math, subprocess, time, glob
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # skill root, so the engine package is importable
from engine import config
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from engine.plib import UP, txt, CAIRO, MONT, READ, MONO, WHITE, GRAPH

W, H, FPS = 1080, 1920, 30
BAR = 1.875; DUR = 22.5
BG = (248, 247, 245); OR = (255, 106, 28); SLATE = (110, 116, 130); SIG = (37, 99, 235)
CX, CY = 540, 1020
def clamp(v, a, b): return max(a, min(b, v))
def prog(t, s, d): return clamp((t - s) / d, 0, 1)
def ease(p): return 1 - (1 - p) ** 3
def eio(p): return 3 * p * p - 2 * p ** 3
def spring(p): return 1 - math.exp(-8 * p) * math.cos(10 * p) if p < 1 else 1.0
def lerp(a, b, p): return a + (b - a) * p
def put(f, spr, cx, cy, a=1.0, s=1.0):
    if a <= 0.01 or s <= 0.01: return
    im = spr if abs(s - 1) < 0.003 else spr.resize((max(1, int(spr.width * s)), max(1, int(spr.height * s))), Image.BICUBIC)
    if a < 0.999: im = im.copy(); im.putalpha(im.split()[3].point(lambda v: int(v * a)))
    f.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2)))

# glossy sphere (radial shading + specular), built once large
def sphere(D=600):
    yy, xx = np.mgrid[0:D, 0:D].astype(np.float32); r = D / 2
    nx, ny = (xx - r) / r, (yy - r) / r; d2 = nx ** 2 + ny ** 2; inside = d2 <= 1
    nz = np.sqrt(np.clip(1 - d2, 0, 1)); L = np.array([-0.45, -0.6, 0.66]); L /= np.linalg.norm(L)
    diff = np.clip(nx * L[0] + ny * L[1] + nz * L[2], 0, 1)
    spec = np.clip(nx * L[0] + ny * L[1] + nz * L[2], 0, 1) ** 40
    rim = (1 - nz) ** 3
    base = np.array(OR, np.float32)
    col = base[None, None, :] * (0.55 + 0.55 * diff[..., None]) + 255 * spec[..., None] * 0.9 + np.array([255, 170, 120]) * rim[..., None] * 0.25
    img = np.zeros((D, D, 4), np.uint8); img[..., :3] = np.clip(col, 0, 255); img[..., 3] = inside * 255
    im = Image.fromarray(img, 'RGBA'); a = im.split()[3].filter(ImageFilter.GaussianBlur(1.2)); im.putalpha(a); return im
BALL = sphere(600)
def ball_at(d): return BALL.resize((max(2, int(d)), max(2, int(d))), Image.BICUBIC)
def floor_shadow(f, x, y, d, a=1.0):
    w, h = int(d * 0.9), int(d * 0.16) + 2
    m = Image.new('L', (w + 40, h + 40), 0); ImageDraw.Draw(m).ellipse((20, 20, 20 + w, 20 + h), fill=int(70 * a))
    m = m.filter(ImageFilter.GaussianBlur(10)); s = Image.new('RGBA', m.size, (120, 60, 30, 255)); s.putalpha(m)
    f.alpha_composite(s, (int(x - m.width / 2), int(y - m.height / 2)))

def T(s, size, col=GRAPH, w=900): return txt(s, CAIRO(size) if w == 900 else READ(size, w), col, rtl=True)
def label(s, size=52, col=WHITE): return txt(s, CAIRO(size), col, rtl=True)
RES = [fr for fr in config.input_frames('result')]
MARK = Image.open(config.asset('atc-mark-white-1024.png')).convert('RGBA'); MARK = MARK.resize((52, int(52 * MARK.height / MARK.width)), Image.LANCZOS)
CTA_T = txt('تابع AdelTechTalks', CAIRO(54), WHITE, rtl=True); FOLLOWING = txt('Following', MONT(42), WHITE)

HEADS = [  # (bar, text, size, color, small?)
    (0, 'الفيديو ده؟', 96, GRAPH), (1, 'اتعمل في دقايق', 88, GRAPH), (2, 'إزاي؟', 110, OR),
    (3, 'فكرة', 88, GRAPH), (4, '+ ريفرنس', 88, GRAPH), (5, '+ صورك', 88, GRAPH),
    (6, 'Claude', 120, SIG), (7, 'يكتب الكود', 88, GRAPH), (8, 'ويرندر', 88, GRAPH), (9, 'والنتيجة', 88, GRAPH),
    (10, 'عايز تتعلمها؟', 88, GRAPH),
]
HEAD_S = {b: (txt(s, MONT(sz), c) if s == 'Claude' else T(s, sz, c)) for b, s, sz, c in HEADS}
SUBS = {0: T('من غير ولا برنامج مونتاج', 44, SLATE, 400)}
LAB = {'فكرة': label('فكرة'), 'ريفرنس': label('ريفرنس'), 'صور': label('صور'), 'code': txt('</>', MONO(110), WHITE)}

def render(t):
    f = Image.new('RGBA', (W, H), BG + (255,))
    b = int(t / BAR); lt = t - b * BAR
    # headline per bar
    if b in HEAD_S and t < BAR * 11:
        p = ease(prog(lt, 0.0, 0.22)); out = prog(lt, BAR - 0.15, 0.15)
        put(f, HEAD_S[b], CX, 560 + 30 * (1 - p), p * (1 - out))
        if b in SUBS: put(f, SUBS[b], CX, 680, ease(prog(lt, 0.25, 0.3)) * (1 - out))
    # ---- the balls ----
    if t < 2 * BAR:                        # bar 0–1: one ball drops & bounces, then grows
        p = prog(t, 0.05, 0.9); bounce = abs(math.cos(p * math.pi * 2.5)) * (1 - p) ** 1.5
        d = 260 + 160 * ease(prog(t, BAR, 0.6)); y = CY + 120 - 520 * bounce * (p < 1) - (0 if p > 0 else 900)
        floor_shadow(f, CX, CY + 120 + d / 2, d, 1 - 0.5 * bounce); put(f, ball_at(d * (1 + 0.08 * bounce)), CX, y - d / 2 + 130)
        if t >= BAR:
            n = int(30 * ease(prog(t, BAR + 0.1, 1.2)))
            put(f, txt(f'{n}s', MONT(120), WHITE), CX, y - d / 2 + 130, ease(prog(t, BAR + 0.05, 0.2)))
    elif t < 6 * BAR:                      # bar 2: split into 3 · bars 3–5: label each
        p = spring(prog(t, 2 * BAR, 0.55)); d = lerp(420, 230, ease(prog(t, 2 * BAR, 0.4)))
        xs = [CX + 300, CX, CX - 300]
        for k, x in enumerate(xs):
            xx = lerp(CX, x, p); act = 3 + k; pop = spring(prog(t, act * BAR, 0.4)) if t >= act * BAR else 0
            dd = d * (1 + 0.12 * math.sin(math.pi * clamp(prog(t, act * BAR, 0.4), 0, 1)))
            yy = CY + 40 * math.sin(t * 3 + k)
            floor_shadow(f, xx, CY + 170, dd, 0.8); put(f, ball_at(dd), xx, yy)
            if pop > 0: put(f, LAB[['فكرة', 'ريفرنس', 'صور'][k]], xx, yy, min(1, pop * 2))
    elif t < 9 * BAR:                      # bar 6: merge into big 'Claude' ball · 7: code · 8: render ring
        p = eio(prog(t, 6 * BAR, 0.5)); xs = [CX + 300, CX, CX - 300]
        if p < 1:
            for k, x in enumerate(xs): put(f, ball_at(230), lerp(x, CX, p), CY, 1)
        d = 230 + 270 * spring(prog(t, 6 * BAR + 0.35, 0.6)) if t > 6 * BAR + 0.35 else 0
        if d:
            pulse = 1 + 0.03 * math.sin(t * 12) * (t > 7 * BAR)
            floor_shadow(f, CX, CY + 290, d); put(f, ball_at(d * pulse), CX, CY)
            if t >= 7 * BAR: put(f, LAB['code'], CX, CY, ease(prog(t, 7 * BAR, 0.25)) * (1 - prog(t, 8 * BAR - 0.1, 0.1)))
            if t >= 8 * BAR:
                pr = eio(prog(t, 8 * BAR + 0.1, 1.5)); R = 330
                ov = Image.new('RGBA', (W * 2, H * 2), (0, 0, 0, 0)); dd = ImageDraw.Draw(ov)
                dd.ellipse(((CX - R) * 2, (CY - R) * 2, (CX + R) * 2, (CY + R) * 2), outline=(230, 226, 220, 255), width=32)
                if pr > 0: dd.arc(((CX - R) * 2, (CY - R) * 2, (CX + R) * 2, (CY + R) * 2), -90, -90 + 360 * pr, fill=OR + (255,), width=32)
                f.alpha_composite(ov.resize((W, H), Image.LANCZOS))
                put(f, txt(f'{int(100 * pr)}%', MONT(110), WHITE), CX, CY)
    elif t < 10 * BAR:                     # bar 9: ball morphs into a phone playing the real reel
        p = spring(prog(t, 9 * BAR, 0.55)); w = lerp(500, 440, p); h = lerp(500, 782, p); r = lerp(250, 44, p)
        s = 2; ov = Image.new('RGBA', (int(w) * s, int(h) * s), (0, 0, 0, 0))
        ImageDraw.Draw(ov).rounded_rectangle((0, 0, int(w) * s - 1, int(h) * s - 1), int(r * s), fill=OR + (255,))
        ph = ov.resize((int(w), int(h)), Image.LANCZOS)
        if p > 0.6:
            k = int(clamp((t - 9 * BAR - 0.3) * 40, 0, len(RES) - 1)); fr = RES[k].resize((int(w) - 24, int(h) - 24), Image.BICUBIC)
            m = Image.new('L', (fr.width * 2, fr.height * 2), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, fr.width * 2 - 1, fr.height * 2 - 1), 64, fill=255)
            fr.putalpha(m.resize(fr.size, Image.LANCZOS)); a = ease((p - 0.6) / 0.4)
            fr2 = fr.copy(); fr2.putalpha(fr.split()[3].point(lambda v: int(v * a))); ph.alpha_composite(fr2, (12, 12))
        floor_shadow(f, CX, CY + h / 2 + 30, w); put(f, ph, CX, CY + 40)
    elif t < 11 * BAR:                     # bar 10: phone collapses back into a small ball, bounces
        p = prog(t, 10 * BAR, 0.5); d = lerp(440, 200, ease(p)); y = CY + 60 - 140 * abs(math.sin(p * math.pi)) * (1 - p)
        floor_shadow(f, CX, CY + 180, d); put(f, ball_at(d), CX, y)
    else:                                  # CTA: ball stretches into the Follow pill → tap → Following
        t0 = 11 * BAR; p = spring(prog(t, t0, 0.5)); tap = prog(t, t0 + 0.8, 0.2); done = t >= t0 + 0.9
        put(f, HEAD_S[10], CX, 760, 1)
        w_ = int(lerp(200, CTA_T.width + 160, p)) if not done else FOLLOWING.width + 150; h_ = int(lerp(200, 120, p))
        bs = 1 - 0.1 * math.sin(math.pi * tap)
        pill = Image.new('RGBA', (w_ * 2, h_ * 2), (0, 0, 0, 0))
        ImageDraw.Draw(pill).rounded_rectangle((0, 0, w_ * 2 - 1, h_ * 2 - 1), h_, fill=(OR if not done else GRAPH) + (255,))
        pill = pill.resize((w_, h_), Image.LANCZOS)
        if p > 0.7 and not done:
            pill.alpha_composite(MARK, (40, (h_ - MARK.height) // 2)); pill.alpha_composite(CTA_T, (110, (h_ - CTA_T.height) // 2))
        if done: pill.alpha_composite(FOLLOWING, ((w_ - FOLLOWING.width) // 2, (h_ - FOLLOWING.height) // 2))
        floor_shadow(f, CX, CY + 110, w_ * 0.9, 0.7); put(f, pill, CX, CY, 1, bs)
    return f.convert('RGB')

if __name__ == '__main__':
    if sys.argv[1] == 'test':
        ts = [float(x) for x in sys.argv[2:]]; ims = []
        for x in ts:
            im = render(x); im.save(config.work(f'bl_{x}.png')); ims.append(im.resize((180, 320)))
        sh = Image.new('RGB', (180 * len(ims), 320)); [sh.paste(im, (i * 180, 0)) for i, im in enumerate(ims)]
        sh.save(config.work('blsheet.png')); sys.exit()
    enc = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS),
                            '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '16', '-pix_fmt', 'yuv420p', config.work('bl_v.mp4')], stdin=subprocess.PIPE)
    t0 = time.time()
    for i in range(int(DUR * FPS)): enc.stdin.write(render(i / FPS).tobytes())
    enc.stdin.close(); enc.wait(); print('done', round(time.time() - t0))
