"""Style F — Kinetic Typography: one phrase per half-bar @128 BPM, varied layouts, soft colour blobs"""
import sys, math, subprocess, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # skill root, so the engine package is importable
from engine import config
from PIL import Image, ImageDraw, ImageFilter
from engine.plib import UP, txt, CAIRO, MONT, READ, MONO, WHITE, GRAPH, CORAL

W, H, FPS = 1080, 1920, 30
HB = 1.875 / 2; DUR = 22.5
BG = (247, 247, 245); SIG = (37, 99, 235); MINT = (45, 212, 168); SLATE = (120, 126, 140); CX, CY = 540, 960
def clamp(v, a, b): return max(a, min(b, v))
def prog(t, s, d): return clamp((t - s) / d, 0, 1)
def ease(p): return 1 - (1 - p) ** 3
def spring(p): return 1 - math.exp(-8 * p) * math.cos(10 * p) if p < 1 else 1.0
def put(f, spr, cx, cy, a=1.0, s=1.0, blur=0, rot=0):
    if a <= 0.01 or s <= 0.01: return
    im = spr if abs(s - 1) < 0.003 else spr.resize((max(1, int(spr.width * s)), max(1, int(spr.height * s))), Image.BICUBIC)
    if rot: im = im.rotate(rot, Image.BICUBIC, expand=True)
    if blur > 0.5:
        pad = int(blur * 3); big = Image.new('RGBA', (im.width + pad * 2, im.height + pad * 2), (0, 0, 0, 0)); big.alpha_composite(im, (pad, pad))
        im = big.filter(ImageFilter.GaussianBlur(blur))
    if a < 0.999: im = im.copy(); im.putalpha(im.split()[3].point(lambda v: int(v * a)))
    f.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2)))

def A(s, size, col=GRAPH, font=CAIRO): return txt(s, font(size), col, rtl=True)
def boxed(s, size, fg=WHITE, bg=SIG):
    t = A(s, size, fg); pad = 40
    im = Image.new('RGBA', ((t.width + pad * 2) * 2, (t.height + pad) * 2), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle((0, 0, im.width - 1, im.height - 1), 36, fill=bg + (255,))
    im = im.resize((t.width + pad * 2, t.height + pad), Image.LANCZOS); im.alpha_composite(t, (pad, pad // 2)); return im
def outlined(s, size, col=GRAPH):
    ft = CAIRO(size); d = ImageDraw.Draw(Image.new('RGBA', (1, 1)))
    bb = d.textbbox((0, 0), s, font=ft, direction='rtl', language='ar', stroke_width=7)
    im = Image.new('RGBA', (bb[2] - bb[0] + 20, bb[3] - bb[1] + 20), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((10 - bb[0], 10 - bb[1]), s, font=ft, fill=(0, 0, 0, 0), stroke_width=7, stroke_fill=col + (255,), direction='rtl', language='ar')
    return im

# phrase list: (style, sprite, extra)
P = [
    ('big', A('الفيديو ده', 150)), ('small', A('مفيهوش', 90, SLATE)), ('strike', A('برنامج مونتاج', 120)),
    ('strike', txt('After Effects', MONT(110), GRAPH)), ('big', A('كله', 190)), ('hero', txt('Claude', MONT(230), SIG)),
    ('small', A('إنت بتكتب', 90, SLATE)), ('box', boxed('فكرة', 150)), ('small', A('بتبعت', 90, SLATE)),
    ('box', boxed('ريفرنس + صور', 110, GRAPH, (220, 235, 255))), ('small', A('وهو', 100, SLATE)), ('big', A('يكتب الكود', 130)),
    ('outline', outlined('يحرّك', 190)), ('box', boxed('يحط الصوت', 120, WHITE, MINT)), ('big', A('ويرندر', 160)),
    ('count', None), ('small', A('في', 100, SLATE)), ('big', A('دقايق', 190, SIG)), ('strike', A('مش ساعات', 120)),
    ('small', A('عايز', 100, SLATE)), ('big', A('تتعلمها؟', 170)), ('cta', None),
]
PREV_SMALL = {}  # phrase shown small above the next one (stacking effect)
CTA_T = txt('تابع AdelTechTalks', CAIRO(54), WHITE, rtl=True); FOLLOWING = txt('Following', MONT(42), WHITE)
MARK = Image.open(config.asset('atc-mark-white-1024.png')).convert('RGBA'); MARK = MARK.resize((52, int(52 * MARK.height / MARK.width)), Image.LANCZOS)

def blob(d, col, a):
    b = Image.new('RGBA', (d, d), (0, 0, 0, 0)); ImageDraw.Draw(b).ellipse((d // 4, d // 4, d * 3 // 4, d * 3 // 4), fill=col + (a,))
    return b.filter(ImageFilter.GaussianBlur(d // 10))
B1, B2 = blob(1200, SIG, 70), blob(1000, MINT, 80)

def render(t):
    f = Image.new('RGBA', (W, H), BG + (255,))
    f.alpha_composite(B1, (int(-300 + 160 * math.sin(t * 0.7)), int(-200 + 120 * math.cos(t * 0.5))))
    f.alpha_composite(B2, (int(400 + 140 * math.cos(t * 0.6)), int(1100 + 160 * math.sin(t * 0.8))))
    i = min(int(t / HB), len(P) - 1); lt = t - i * HB
    style, spr = P[i]
    if style == 'cta': lt = t - (len(P) - 1) * HB
    shake = (8 * math.sin(t * 60) * (1 - prog(lt, 0, 0.25))) if style in ('hero', 'big') and i in (5, 17) else 0
    # previous phrase lingers small above (gives a reading line)
    if i > 0 and P[i - 1][0] == 'small' and style != 'cta':
        put(f, P[i - 1][1], CX, CY - 200, 0.9, 0.85)
    if style in ('big', 'hero'):
        p = prog(lt, 0, 0.28); put(f, spr, CX + shake, CY + shake * 0.5, min(1, p * 4), 1.35 - 0.35 * spring(p), blur=10 * (1 - ease(p)))
    elif style == 'small':
        p = ease(prog(lt, 0, 0.22)); put(f, spr, CX, CY + 40 * (1 - p), p)
    elif style == 'strike':
        p = ease(prog(lt, 0, 0.22)); put(f, spr, CX, CY, p)
        q = ease(prog(lt, 0.35, 0.25))
        if q > 0:
            ov = Image.new('RGBA', (W, H), (0, 0, 0, 0)); x0 = CX + spr.width / 2 + 20
            ImageDraw.Draw(ov).line((x0, CY + 6, x0 - (spr.width + 40) * q, CY - 6), fill=CORAL + (255,), width=14)
            f.alpha_composite(ov)
    elif style == 'box':
        p = prog(lt, 0, 0.32); put(f, spr, CX, CY, min(1, p * 3), spring(p), rot=-3 * (1 - ease(p)))
    elif style == 'outline':
        p = prog(lt, 0, 0.3); x = CX + 500 * (1 - ease(p)); put(f, spr, x, CY, min(1, p * 2.5))
        put(f, spr, x - 30, CY + 26, 0.25 * p)
    elif style == 'count':
        p = ease(prog(lt, 0, HB * 0.85)); put(f, txt(f'{int(100 * p)}%', MONT(240), SIG), CX, CY, 1, 1 + 0.03 * math.sin(t * 25) * (p < 1))
    elif style == 'cta':  # Follow pill (single Spark Coral element) → tap → Following
        p = spring(prog(lt, 0, 0.45)); tap = prog(lt, 0.8, 0.2); done = lt >= 0.9
        put(f, P[-2][1], CX, CY - 220, 1, 0.75)
        w_ = CTA_T.width + 160 if not done else FOLLOWING.width + 150; bs = 1 - 0.1 * math.sin(math.pi * tap)
        pill = Image.new('RGBA', (w_ * 2, 240), (0, 0, 0, 0)); ImageDraw.Draw(pill).rounded_rectangle((0, 0, w_ * 2 - 1, 239), 120, fill=(CORAL if not done else GRAPH) + (255,))
        pill = pill.resize((w_, 120), Image.LANCZOS)
        if not done: pill.alpha_composite(MARK, (40, (120 - MARK.height) // 2)); pill.alpha_composite(CTA_T, (110, (120 - CTA_T.height) // 2))
        else: pill.alpha_composite(FOLLOWING, ((w_ - FOLLOWING.width) // 2, (120 - FOLLOWING.height) // 2))
        put(f, pill, CX, CY + 40, min(1, p * 2), p * bs)
    # beat flash on the 'Claude' drop
    if 0 <= t - 5 * HB < 0.12: f.alpha_composite(Image.new('RGBA', (W, H), (255, 255, 255, int(150 * (1 - (t - 5 * HB) / 0.12)))))
    return f.convert('RGB')

if __name__ == '__main__':
    if sys.argv[1] == 'test':
        ts = [float(x) for x in sys.argv[2:]]; ims = []
        for x in ts:
            im = render(x); im.save(config.work(f'kt_{x}.png')); ims.append(im.resize((150, 266)))
        sh = Image.new('RGB', (150 * len(ims), 266)); [sh.paste(im, (i * 150, 0)) for i, im in enumerate(ims)]
        sh.save(config.work('ktsheet.png')); sys.exit()
    enc = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS),
                            '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '16', '-pix_fmt', 'yuv420p', config.work('kt_v.mp4')], stdin=subprocess.PIPE)
    t0 = time.time()
    for i in range(int(DUR * FPS)): enc.stdin.write(render(i / FPS).tobytes())
    enc.stdin.close(); enc.wait(); print('done', round(time.time() - t0))
