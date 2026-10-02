"""Style G — Editorial Poster: Swiss-poster scenes, black & white cut-outs on a brand disc,
giant words sliding behind, words landing one by one, hard cuts on the bar @128 BPM,
name → logo ending. 12 bars = 22.5 s.

No photos needed: find the images with engine/assets.py (see SKILL.md, "No images? Find them"):
    helmet.png  brain.png  bulb.png  knight.png   cut-outs  (get <n> --as <file> --cutout --one --bw)
    earth.jpg                                       background photo (get <n> --as earth.jpg --bw)

    python templates/core/style_g_editorial_poster.py test 1.5 5 12 20   # stills + sheet in work/
    python templates/core/style_g_editorial_poster.py render              # work/ep_v.mp4 (silent)
    python render.py --style g                                            # whole reel with SFX + music
"""
import math
import random
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # skill root, so the engine package is importable
from engine import config
_BRAND = config.brand(); _END = _BRAND['ending']  # name, tagline and ending text from brand.json
from PIL import Image, ImageDraw, ImageFilter, ImageOps
from engine.plib import MONO, fit, put, txt
from engine.moves import ghost_words, marquee_word, push_in
from engine.endings import TIMES as END_T, name_logo_follow

W, H, FPS = 1080, 1920, 30
BPM = 128; BAR = 4 * 60 / BPM
RTL = _BRAND["language"].startswith("ar")

# ---------- story: one row per scene (bars, look, image, big word, lines) ----------
# looks: poster · dark · frame · pedestal · giant · type      English tech words stay English.
if RTL:
    SCENES = [
        (2.0, "poster",   "helmet.png", "IDEAS",  (("مش مهم الـ Tool", 62), ("المهم الفكرة", 150))),
        (1.5, "dark",     "earth.jpg",  "IDEAS",  (("الفكرة اللي", 62), ("بتغيّر كل حاجة", 120))),
        (1.5, "frame",    "brain.png",  "SKILL",  (("مش الـ Skill", 62), ("اللي في دماغك", 112))),
        (1.5, "pedestal", "knight.png", "",       (("اللي بتشوفه", 58), ("كل يوم", 120))),
        (1.5, "giant",    "bulb.png",   "PROMPT", (("وإنت بتجرّب", 62), ("بنفسك", 150))),
        (1.0, "type",     "",           "",       (("ابدأ", 220),)),
    ]
else:
    SCENES = [
        (2.0, "poster",   "helmet.png", "IDEAS",  (("it's not the tool", 62), ("it's the idea", 140))),
        (1.5, "dark",     "earth.jpg",  "IDEAS",  (("the idea that", 62), ("changes everything", 108))),
        (1.5, "frame",    "brain.png",  "SKILL",  (("not the skill", 62), ("what you absorb", 118))),
        (1.5, "pedestal", "knight.png", "",       (("the thing you", 58), ("see daily", 130))),
        (1.5, "giant",    "bulb.png",   "PROMPT", (("by trying it", 62), ("yourself", 150))),
        (1.0, "type",     "",           "",       (("start", 220),)),
    ]
END_BARS = 3.0

STARTS = []
_t = 0.0
for sc in SCENES:
    STARTS.append(_t); _t += sc[0] * BAR
END = _t
DUR = round(END + END_BARS * BAR, 3)
WORD_GAP = 0.26        # ghost_words: one word every 0.26 s
WORDS_AT = 0.3         # words start this long after each cut


def events():
    """Timeline for the SFX script: (time, kind)."""
    ev = [(s, "cut") for s in STARTS[1:]] + [(END, "cut")]
    for (bars, look, *_r), s in zip(SCENES, STARTS):
        k = 0
        for text, size in _r[2]:
            for _ in text.split():
                ev.append((s + WORDS_AT + k * WORD_GAP, "word_big" if size >= 140 else "word")); k += 1
    ev += [(END + END_T[k], k) for k in ("split", "follow", "tap")]
    return sorted(ev)


# ---------- brand ----------
PAPER = config.color("background"); INK = config.color("ink"); SIG = config.color("primary")
MUTED = config.color("muted"); CTA = config.color("cta"); WHITE = (255, 255, 255); BLACK = (8, 8, 10)

_L = {}


def L(key, make):
    if key not in _L:
        _L[key] = make()
    return _L[key]


def cutout(name, w=None, h=None):
    def make():
        im = config.input_image(name, (800, 800), "a black & white cut-out (engine/assets.py get … --cutout --one --bw)", rgba=True).convert("RGBA")
        return fit(im, w=w) if w else fit(im, h=h)
    return L(("cut", name, w, h), make)


def vignette(col, k=0.86):
    def make():
        g = Image.new("L", (W, H), 0)
        ImageDraw.Draw(g).ellipse((-300, -200, W + 300, H + 200), fill=255)
        g = g.filter(ImageFilter.GaussianBlur(260))
        return Image.composite(Image.new("RGB", (W, H), col), Image.new("RGB", (W, H), tuple(int(c * k) for c in col)), g).convert("RGBA")
    return L(("vig", col, k), make)


def disc(r, col):
    def make():
        im = Image.new("RGBA", (2 * r, 2 * r), (0, 0, 0, 0))
        ImageDraw.Draw(im).ellipse((0, 0, 2 * r - 1, 2 * r - 1), fill=col + (255,))
        return im
    return L(("disc", r, col), make)


def furniture(col, alpha, orbit=None, frame=True, barcode=True, n=1):
    """Poster details: issue line, rules, dotted orbit, barcode."""
    def make():
        im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im); c = col + (alpha,)
        im.alpha_composite(txt(_BRAND["name"].upper(), MONO(26), c), (70, 90))
        im.alpha_composite(txt(f"VOL. 0{n}  ·  " + _BRAND["tagline"].upper(), MONO(20), c), (70, 132))
        d.line((70, 180, W - 70, 180), fill=c, width=2)
        if frame:
            d.line((W - 70, 180, W - 70, 1500), fill=c, width=2)
        if orbit:
            ox, oy, r = orbit
            for a in range(0, 360, 6):
                x = ox + r * math.cos(math.radians(a)); y = oy + r * math.sin(math.radians(a))
                d.ellipse((x - 3, y - 3, x + 3, y + 3), fill=col + (int(alpha * 0.8),))
        if barcode:
            rnd = random.Random(n); x = 640
            while x < 900:
                w = rnd.choice((2, 2, 4, 6)); d.rectangle((x, 1560, x + w, 1620), fill=c); x += w + rnd.choice((3, 4, 6))
        return im
    return L(("furn", col, alpha, orbit, frame, barcode, n), make)


def photo_bottom(name):
    def make():
        src = config.input_image(name, (1400, 1400), "a background photo (engine/assets.py get … --bw)").convert("RGB")
        im = ImageOps.fit(src, (W, int(H * 0.62))).convert("RGBA")
        im.putalpha(Image.linear_gradient("L").resize(im.size).point(lambda v: min(255, int(v * 2.2))))
        return im
    return L(("photo", name), make)


def words(f, t, s, lines, col, top, align=None):
    x = (W - 90) if RTL else 90
    if align == "center":
        x = W // 2
    ghost_words(f, t, None, x, top, s + WORDS_AT, lines=lines, col=col, rtl=RTL, gap=WORD_GAP, align=align or "left")


# ---------- scene looks ----------
def poster(f, t, s, d, img, big, lines, n):
    f.alpha_composite(vignette(PAPER))
    marquee_word(f, t, None, 0, 1330, s, word=big, col=INK, alpha=0.10, size=360, speed=120)
    push_in(f, t, disc(330, SIG), 470, 1010, s, dur=d, amount=0.05)
    f.alpha_composite(furniture(INK, 150, orbit=(470, 1010, 430), n=n))
    c = cutout(img, w=780)
    push_in(f, t, c, 560, 1250 - c.height // 2, s, dur=d, amount=0.10, drift=-24)
    put(f, disc(26, SIG), 900, 1440)
    words(f, t, s, lines, INK, 300)


def dark(f, t, s, d, img, big, lines, n):
    f.paste(BLACK + (255,), (0, 0, W, H))
    ph = photo_bottom(img)
    push_in(f, t, ph, W // 2, H - ph.height // 2 + 40, s, dur=d, amount=0.08, drift=-40)
    marquee_word(f, t, None, 0, 1180, s, word=big, col=WHITE, alpha=0.16, size=360, speed=140)
    f.alpha_composite(furniture(WHITE, 110, frame=False, barcode=False, n=n))
    words(f, t, s, lines, WHITE, 520)


def frame(f, t, s, d, img, big, lines, n):
    f.alpha_composite(vignette(PAPER, 0.9))
    def box():
        im = Image.new("RGBA", (560, 700), (0, 0, 0, 0)); dd = ImageDraw.Draw(im)
        dd.rectangle((40, 40, 520, 660), fill=SIG + (255,)); dd.rectangle((0, 0, 559, 699), outline=SIG + (255,), width=4)
        return im
    push_in(f, t, L("box", box), 540, 960, s, dur=d, amount=0.04)
    f.alpha_composite(furniture(INK, 150, frame=False, n=n))
    c = cutout(img, h=900)
    push_in(f, t, c, 540, 1010, s, dur=d, amount=0.09, drift=-20)
    th = L(("thumb", img), lambda: fit(cutout(img, h=900), h=130))
    put(f, th, 140, 1500)
    marquee_word(f, t, None, 0, 1700, s, word=big, col=INK, alpha=0.92, size=420, speed=200, rows=1)
    words(f, t, s, lines, INK, 240 if RTL else 230)


def pedestal(f, t, s, d, img, big, lines, n):
    f.alpha_composite(vignette((236, 236, 234), 0.82))
    f.alpha_composite(furniture(INK, 120, frame=True, barcode=False, n=n))
    def block():
        im = Image.new("RGBA", (360, 760), (0, 0, 0, 0)); dd = ImageDraw.Draw(im)
        dd.polygon([(0, 40), (40, 0), (360, 0), (320, 40)], fill=(200, 200, 198, 255))
        dd.rectangle((0, 40, 320, 760), fill=(14, 14, 16, 255))
        return im
    p = math.sin(min(1, (t - s) / d) * math.pi / 2)
    blk = L("block", block)
    put(f, blk, 560, 1340 + 380 - 30 * p, 1 + 0.03 * p)
    c = cutout(img, h=460)
    put(f, c, 545, 1330 - 30 * p - c.height // 2 + 6, 1 + 0.03 * p)
    words(f, t, s, lines, INK, 600, align="center")


def giant(f, t, s, d, img, big, lines, n):
    f.paste(BLACK + (255,), (0, 0, W, H))
    marquee_word(f, t, None, 0, 1150, s, word=big, col=(120, 120, 124), alpha=0.85, size=420, speed=260, rows=2)
    c = cutout(img, w=900)
    push_in(f, t, c, 330, 980, s, dur=d, amount=0.08, drift=-30)
    f.alpha_composite(furniture(WHITE, 110, frame=False, barcode=False, n=n))
    words(f, t, s, lines, WHITE, 330)


def type_only(f, t, s, d, img, big, lines, n):
    f.paste(PAPER + (255,), (0, 0, W, H))
    f.alpha_composite(furniture(INK, 150, frame=False, barcode=True, n=n))
    put(f, disc(40, SIG), W // 2, 1280, 1, min(1, (t - s - 0.5) * 4) if t > s + 0.5 else 0)
    words(f, t, s, lines, INK, 760, align="center")


LOOKS = {"poster": poster, "dark": dark, "frame": frame, "pedestal": pedestal, "giant": giant, "type": type_only}


def render(t):
    f = Image.new("RGBA", (W, H), PAPER + (255,))
    if t >= END:
        name_logo_follow(f, t, END, bg=BLACK, ink=WHITE)
    else:
        i = max(k for k, s in enumerate(STARTS) if s <= t)
        bars, look, img, big, lines = SCENES[i]
        LOOKS[look](f, t, STARTS[i], bars * BAR, img, big, lines, i + 1)
    return f.convert("RGB")


if __name__ == "__main__":
    if sys.argv[1] == "test":
        ts = [float(x) for x in sys.argv[2:]]; ims = []
        for x in ts:
            im = render(x); im.save(config.work(f"ep_{x}.png")); ims.append(im.resize((270, 480)))
        sh = Image.new("RGB", (270 * len(ims), 480)); [sh.paste(im, (i * 270, 0)) for i, im in enumerate(ims)]
        sh.save(config.work("epsheet.png")); sys.exit()
    out = config.work("ep_v.mp4")
    enc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                            "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    t0 = time.time()
    for k in range(int(DUR * FPS)): enc.stdin.write(render(k / FPS).tobytes())
    enc.stdin.close(); enc.wait(); print("done", out, round(time.time() - t0), "s")
