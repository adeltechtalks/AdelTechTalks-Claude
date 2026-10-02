"""Editorial Poster demo — a short reel made only from images the skill found itself.

Learned from a reference reel (Swiss-poster scenes, a colour disc behind a black & white
cut-out, giant word sliding behind, words landing one by one, hard cuts, name → logo ending).
Uses the moves ghost_words · marquee_word · push_in · split_reveal from engine/moves.py.

Get the images first (free, licence-safe, credits logged in input/credits.json):
    python engine/assets.py search "astronaut helmet"   → look at the sheet, pick a number
    python engine/assets.py get <n> --as helmet.png --cutout --bw
    python engine/assets.py search "earth from space" --source nasa
    python engine/assets.py get <n> --as earth.jpg --bw

    python templates/lab/poster_demo.py test 1.5 5 8      # stills + contact sheet in work/
    python templates/lab/poster_demo.py render            # work/poster_demo.mp4 (silent)
"""
import random
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # skill root, so the engine package is importable
from engine import config
from PIL import Image, ImageDraw, ImageFilter, ImageOps
from engine.plib import MONO, fit, put, txt
from engine.moves import ghost_words, marquee_word, push_in, split_reveal

_BRAND = config.brand()
W, H, FPS = 1080, 1920, 30
BAR = 4 * 60 / 128                       # 128 BPM, cuts on the bar
S1, S2, END = 0.0, 2 * BAR, 3.5 * BAR    # scene starts
DUR = round(END + 1.6 * BAR, 2)

PAPER = config.color("background"); INK = config.color("ink"); SIG = config.color("primary")
MUTED = config.color("muted"); WHITE = (255, 255, 255); BLACK = (8, 8, 10)
RTL = _BRAND["language"].startswith("ar")

# story — swap per video (English tech words stay English)
LINES_1 = (("مش مهم الـ Tool", 62), ("المهم الفكرة", 150)) if RTL else (("it's not the tool", 62), ("it's the idea", 140))
LINES_2 = (("الفكرة اللي", 62), ("بتغيّر كل حاجة", 120)) if RTL else (("the idea that", 62), ("changes everything", 110))
BIG_WORD = "IDEAS"

# ---------- layers (built once) ----------
helmet = config.input_image("helmet.png", (900, 900), "a black & white cut-out (engine/assets.py get … --cutout --bw)", rgba=True).convert("RGBA")
helmet = fit(helmet, w=780) if helmet.width / helmet.height > 0.9 else fit(helmet, h=860)
earth = config.input_image("earth.jpg", (1400, 1400), "a background photo (engine/assets.py get … --bw)").convert("RGB")


def vignette_bg(col, edge):
    g = Image.new("L", (W, H), 0)
    ImageDraw.Draw(g).ellipse((-300, -200, W + 300, H + 200), fill=255)
    g = g.filter(ImageFilter.GaussianBlur(260))
    return Image.composite(Image.new("RGB", (W, H), col), Image.new("RGB", (W, H), edge), g).convert("RGBA")


BG1 = vignette_bg(PAPER, tuple(int(c * 0.86) for c in PAPER))


def disc(r, col):
    im = Image.new("RGBA", (2 * r, 2 * r), (0, 0, 0, 0))
    ImageDraw.Draw(im).ellipse((0, 0, 2 * r - 1, 2 * r - 1), fill=col + (255,))
    return im


DISC = disc(330, SIG)
DOT = disc(26, SIG)


def decor(col, alpha):
    """Poster furniture: issue line, frame rules, dotted orbit, barcode."""
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = col + (alpha,)
    im.alpha_composite(txt(_BRAND["name"].upper(), MONO(26), c), (70, 90))
    im.alpha_composite(txt("VOL. 01  ·  " + _BRAND["tagline"].upper(), MONO(20), c), (70, 132))
    d.line((70, 180, W - 70, 180), fill=c, width=2)
    d.line((W - 70, 180, W - 70, 1500), fill=c, width=2)
    for a in range(0, 360, 6):                       # dotted orbit around the disc
        import math
        x = 470 + 430 * math.cos(math.radians(a)); y = 1010 + 430 * math.sin(math.radians(a))
        d.ellipse((x - 3, y - 3, x + 3, y + 3), fill=col + (int(alpha * 0.8),))
    rnd = random.Random(7); x = 640
    while x < 900:                                   # barcode
        w = rnd.choice((2, 2, 4, 6)); d.rectangle((x, 1560, x + w, 1620), fill=c); x += w + rnd.choice((3, 4, 6))
    return im


DECOR_LIGHT = decor(INK, 150)
DECOR_DARK = decor(WHITE, 110)


def earth_layer():
    im = ImageOps.fit(earth, (W, int(H * 0.62)), centering=(0.5, 0.5)).convert("RGBA")
    m = Image.linear_gradient("L").resize(im.size)   # fade the top edge into black
    m = m.point(lambda v: min(255, int(v * 2.2)))
    im.putalpha(m)
    return im


EARTH = earth_layer()
LOGO = config.logo()
LOGO = fit(LOGO, h=150)
_lw = Image.new("RGBA", LOGO.size, WHITE + (255,)); _lw.putalpha(LOGO.split()[3]); LOGO = _lw   # white logo on dark


def render(t):
    if t < S2:                                        # scene 1 — light poster, cut-out on the disc
        f = BG1.copy()
        marquee_word(f, t, None, 0, 1330, S1, word=BIG_WORD, col=INK, alpha=0.10, size=360, speed=120)
        push_in(f, t, DISC, 470, 1010, S1, dur=S2 - S1, amount=0.05)
        f.alpha_composite(DECOR_LIGHT)
        push_in(f, t, helmet, 560, 1140, S1, dur=S2 - S1, amount=0.10, drift=-24)
        put(f, DOT, 900, 1440, 1, 1)
        ghost_words(f, t, None, 990 if RTL else 90, 300, S1 + 0.35, lines=LINES_1, col=INK, rtl=RTL)
    elif t < END:                                     # scene 2 — dark, earth rising, white words
        f = Image.new("RGBA", (W, H), BLACK + (255,))
        push_in(f, t, EARTH, W // 2, H - EARTH.height // 2 + 40, S2, dur=END - S2, amount=0.08, drift=-40)
        marquee_word(f, t, None, 0, 1180, S2, word=BIG_WORD, col=WHITE, alpha=0.16, size=360, speed=140)
        f.alpha_composite(DECOR_DARK.crop((0, 0, W, 190)), (0, 0))
        ghost_words(f, t, None, 990 if RTL else 90, 520, S2 + 0.2, lines=LINES_2, col=WHITE, rtl=RTL)
    else:                                             # ending — name parts, logo pops in
        f = Image.new("RGBA", (W, H), BLACK + (255,))
        split_reveal(f, t, LOGO, W // 2, H // 2, END + 0.5, text=_BRAND["name"], size=84, col=WHITE)
    return f.convert("RGB")


if __name__ == "__main__":
    if sys.argv[1] == "test":
        ts = [float(x) for x in sys.argv[2:]]; ims = []
        for x in ts:
            im = render(x); im.save(config.work(f"poster_{x}.png")); ims.append(im.resize((270, 480)))
        sh = Image.new("RGB", (270 * len(ims), 480)); [sh.paste(im, (i * 270, 0)) for i, im in enumerate(ims)]
        sh.save(config.work("poster_sheet.png")); sys.exit()
    out = config.work("poster_demo.mp4")
    enc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                            "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    t0 = time.time()
    for k in range(int(DUR * FPS)): enc.stdin.write(render(k / FPS).tobytes())
    enc.stdin.close(); enc.wait(); print("done", out, round(time.time() - t0), "s")
