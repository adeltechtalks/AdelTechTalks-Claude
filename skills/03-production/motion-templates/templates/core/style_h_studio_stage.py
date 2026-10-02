"""Style H — Studio Stage: real objects on a light studio set with a brand-coloured floor,
whip-pan transitions with motion smear, orbit rings, extruded 3D cards with long shadows,
big display words with soft shadows. 11 bars + ending @128 BPM = 24.4 s.

No photos needed: find the objects with engine/assets.py (see SKILL.md, "No images? Find them"):
    brain.png  tv.png  gem.png  bulb.png  knight.png      cut-outs (get <n> --as <file> --cutout --one)
Colour cut-outs work best; a black & white one gets a warm duotone (DUOTONE below).

    python templates/core/style_h_studio_stage.py test 1.5 6 9 15 22    # stills + sheet in work/
    python templates/core/style_h_studio_stage.py render                # work/ss_v.mp4 (silent)
    python render.py --style h                                          # whole reel with SFX + music
"""
import math
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # skill root, so the engine package is importable
from engine import config
_BRAND = config.brand()
from PIL import Image, ImageDraw, ImageFilter, ImageOps
from engine.plib import MOVE, _FONTS, fit, font, prog, put, zoom_frame
from engine.moves import _spring, blur_rise, focus_in, ghost_words, orbit_dots, roll_in, whip
from engine.endings import TIMES as END_T, name_logo_follow

W, H = 1080, 1920
FPS = config.FPS          # 60 by default (MT_FPS), for smooth motion
BPM = 128; BAR = 4 * 60 / BPM
RTL = _BRAND["language"].startswith("ar")

# ---------- story: one row per scene (bars, look, words, transition into the next scene) ----------
# words: [(text, size, colour key)] — colour keys: ink · cta · primary · muted · white
if RTL:
    SCENES = [
        (1.5, "orbit",  [("عمرك سألت؟", 130, "cta")],                                   "left"),
        (1.5, "tiles",  [("ليه حاجات", 120, "cta")],                                    "up"),
        (1.5, "rise",   [("بتفضل", 84, "ink"), ("في دماغك؟", 120, "primary")],          "left"),
        (1.5, "tv",     [("Motion", 64, "ink"), ("Design", 104, "cta")],                "up"),
        (1.0, "slab",   [("إحساس", 120, "ink"), ("بيوصل", 64, "muted"), ("رسالتك", 130, "cta")], "right"),
        (1.5, "card",   [("بيشد", 84, "white"), ("الانتباه", 84, "white"), ("في ثانيتين", 84, "ink")], "up"),
        (1.5, "pillar", [("مش", 60, "muted"), ("ديكور", 230, "cta")],                   "down"),
        (1.0, "drop",   [("دي استراتيجية", 72, "ink"), ("بتتحرك", 110, "cta")],         "up"),
    ]
else:
    SCENES = [
        (1.5, "orbit",  [("ever wonder?", 120, "cta")],                                 "left"),
        (1.5, "tiles",  [("why some things", 100, "cta")],                              "up"),
        (1.5, "rise",   [("stick in", 84, "ink"), ("your mind?", 120, "primary")],      "left"),
        (1.5, "tv",     [("Motion", 64, "ink"), ("Design", 104, "cta")],                "up"),
        (1.0, "slab",   [("Emotion", 120, "ink"), ("to your", 64, "muted"), ("message", 130, "cta")], "right"),
        (1.5, "card",   [("grabs", 76, "white"), ("attention", 64, "white"), ("in two seconds", 80, "ink")], "up"),
        (1.5, "pillar", [("it's not", 60, "muted"), ("DECORATION", 170, "cta")],         "down"),
        (1.0, "drop",   [("it's strategy", 72, "ink"), ("that moves", 110, "cta")],     "up"),
    ]
END_BARS = 2.0
OBJECTS = {"orbit": "brain.png", "rise": "brain.png", "tv": "tv.png", "card": "bulb.png", "pillar": "gem.png", "drop": "knight.png"}
TILES = ["tv.png", "gem.png", "bulb.png", "knight.png"]
DUOTONE = ((70, 22, 30), (255, 208, 200))   # warm tint for black & white cut-outs …
DUOTONE_FOR = {"brain.png"}                 # … listed here (others keep their own tones)
TV_SCREEN = (0.33, 0.61)                    # screen centre inside tv.png (fractions) — adjust for another TV
DRIFT = 0.03                                # camera creeps in 3% over each scene
WHIP = 0.13                                 # half-length of a whip transition (s)
WORDS_AT = 0.05
WORD_GAP = 0.13

STARTS = []
_t = 0.0
for sc in SCENES:
    STARTS.append(_t); _t += sc[0] * BAR
END = _t
DUR = round(END + END_BARS * BAR, 3)


def events():
    """Timeline for the SFX script: (time, kind)."""
    ev = [(s, "whip") for s in STARTS[1:]] + [(END, "cut")]
    for (bars, look, words, _d), s in zip(SCENES, STARTS):
        if look in ("rise", "drop", "pillar"): ev.append((s + 0.2, "land"))
        if look == "card": ev.append((s + 0.35, "roll"))
        if look == "orbit": ev.append((s + 0.1, "pop"))
        if look == "tiles": ev += [(s + 0.15 + k * 0.09, "tile") for k in range(4)]
        k = 0
        for text, size, _c in words:
            for _ in text.split():
                ev.append((s + WORDS_AT + k * WORD_GAP, "word_big" if size >= 110 else "word")); k += 1
    ev += [(END + END_T[k], k) for k in ("split", "follow", "tap")]
    return sorted(ev)


# ---------- brand ----------
C = {"ink": config.color("ink"), "cta": config.color("cta"), "primary": config.color("primary"),
     "muted": config.color("muted"), "white": (255, 255, 255)}
PAPER = config.color("background"); SIG = C["primary"]; CTA = C["cta"]; INK = C["ink"]
FLOOR_Y = 1240
_L = {}


def L(key, make):
    if key not in _L:
        _L[key] = make()
    return _L[key]


def obj(name, h=None, w=None):
    """A cut-out (duotoned if it has no colour), fitted to h or w."""
    def make():
        im = config.input_image(name, (700, 700), "an object cut-out (engine/assets.py get … --cutout --one)", rgba=True).convert("RGBA")
        rgb = im.convert("RGB")
        hsv = rgb.resize((48, 48)).convert("HSV").split()[1]
        if name in DUOTONE_FOR and sum(hsv.histogram()[i] * i for i in range(256)) / (48 * 48) < 22:  # B&W → duotone
            tinted = ImageOps.colorize(rgb.convert("L"), DUOTONE[0], DUOTONE[1]).convert("RGBA")
            tinted.putalpha(im.split()[3]); im = tinted
        return fit(im, h=h) if h else fit(im, w=w)
    return L(("obj", name, h, w), make)


def drop_shadow(spr, blur=22, off=(18, 30), op=95):
    def make():
        pad = blur * 3
        sh = Image.new("RGBA", (spr.width + pad * 2, spr.height + pad * 2), (0, 0, 0, 0))
        sh.paste((0, 0, 0, op), (pad + off[0], pad + off[1]), spr.split()[3])
        sh = sh.filter(ImageFilter.GaussianBlur(blur))
        sh.alpha_composite(spr, (pad, pad))
        return sh
    return L(("sh", id(spr), blur, off, op), make)


def contact(w, op=110):
    def make():
        im = Image.new("RGBA", (w * 2, w // 2), (0, 0, 0, 0))
        ImageDraw.Draw(im).ellipse((w // 2, w // 8, w * 3 // 2, w * 3 // 8), fill=(0, 0, 0, op))
        return im.filter(ImageFilter.GaussianBlur(w // 10))
    return L(("contact", w, op), make)


def studio(floor=False):
    def make():
        g = Image.new("L", (W, H), 0)
        ImageDraw.Draw(g).ellipse((-260, -60, W + 260, H * 0.9), fill=255)
        g = g.filter(ImageFilter.GaussianBlur(240))
        edge = tuple(int(c * 0.80) for c in PAPER)
        im = Image.composite(Image.new("RGB", (W, H), PAPER), Image.new("RGB", (W, H), edge), g).convert("RGBA")
        if floor:
            fl = Image.new("RGBA", (W, H - FLOOR_Y), SIG + (255,))
            sh = Image.linear_gradient("L").resize((W, H - FLOOR_Y)).point(lambda v: int(90 * (1 - v / 255) ** 2))
            fl.paste((0, 0, 0, 255), (0, 0), sh)
            im.alpha_composite(fl, (0, FLOOR_Y))
        return im
    return L(("studio", floor), make)


def tile(size, fill, depth=22, r=34):
    """Extruded rounded square with a long soft shadow."""
    def make():
        pad = 140
        im = Image.new("RGBA", (size + pad, size + pad), (0, 0, 0, 0))
        sh = Image.new("L", im.size, 0)
        ImageDraw.Draw(sh).rounded_rectangle((40, 50, size + 70, size + 80), r, fill=120)
        im.paste((0, 0, 0, 255), (0, 0), sh.filter(ImageFilter.GaussianBlur(30)))
        d = ImageDraw.Draw(im)
        dark = tuple(int(c * 0.62) for c in fill)
        for k in range(depth, 0, -1):
            d.rounded_rectangle((k, k, size + k - 1, size + k - 1), r, fill=dark + (255,))
        d.rounded_rectangle((0, 0, size - 1, size - 1), r, fill=fill + (255,))
        return im
    return L(("tile", size, fill, depth), make)


def say(f, t, s, words, top, x=None, align=None, gap=WORD_GAP, shadow=True, lead=0.8):
    """Each (text, size, colour) line lands word by word; lines follow one another."""
    x = x if x is not None else ((W - 90) if RTL else 90)
    t0 = s + WORDS_AT; y = top
    for text, size, ck in words:
        ghost_words(f, t, None, x, y, t0, lines=((text, size),), col=C[ck], rtl=RTL, align=align or "left",
                    gap=gap, shadow=shadow and size >= 100)
        t0 += gap * len(text.split()); y += int(size * 1.5 * lead)


def column():
    def make():
        w, h = 230, 760
        im = Image.new("RGBA", (w + 80, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.rectangle((0, 0, w + 79, 34), fill=(236, 236, 232, 255)); d.rectangle((14, 34, w + 65, 64), fill=(222, 222, 218, 255))
        for i in range(w):
            v = int(205 + 45 * math.sin(math.pi * i / w) - 18 * (i % 26 < 5))
            d.line((40 + i, 64, 40 + i, h), fill=(v, v, v - 4, 255))
        return im
    return L("column", make)


# ---------- scene looks ----------
def orbit(f, t, s, d, words):
    f.alpha_composite(studio())
    c = drop_shadow(obj(OBJECTS["orbit"], h=300))
    put(f, L("disc", lambda: _disc(190, SIG)), W // 2, 1060, 1, min(1, (t - s) * 5))
    orbit_dots(f, t, c, W // 2, 1060, s, rings=((300, 3, 0.9), (420, 4, -0.55)), col=INK)
    say(f, t, s, words, 560, x=W // 2, align="center")


def _disc(r, col):
    im = Image.new("RGBA", (2 * r, 2 * r), (0, 0, 0, 0))
    ImageDraw.Draw(im).ellipse((0, 0, 2 * r - 1, 2 * r - 1), fill=col + (255,))
    return im


def tiles(f, t, s, d, words):
    f.alpha_composite(studio())
    size = 330
    for k, name in enumerate(TILES):
        cx = W // 2 + (-1 if k % 2 == 0 else 1) * 205
        cy = 640 + (k // 2) * 430
        p = prog(t, s + 0.15 + k * 0.09, 0.4)
        if p <= 0:
            continue
        e = MOVE(p)
        tl = tile(size, SIG)
        put(f, tl, cx + 40 + 300 * (1 - e), cy + 40, 1, min(1, p * 3))
        put(f, drop_shadow(obj(name, h=220), 12, (8, 14), 80), cx + 300 * (1 - e), cy, 1, min(1, p * 3))
    say(f, t, s, words, 1460, x=W // 2, align="center")


def rise(f, t, s, d, words):
    f.alpha_composite(studio())
    blur_rise(f, t, drop_shadow(obj(OBJECTS["rise"], h=520)), W // 2, 1180, s + 0.15)
    say(f, t, s, words, 520, x=W // 2, align="center")


def tv(f, t, s, d, words):
    f.alpha_composite(studio(floor=True))
    def screen():
        im = obj(OBJECTS["tv"], w=760).copy()
        ft_s = font(_FONTS["latin"], 56, 800); ft_b = font(_FONTS["latin"], 88, 900)
        dd = ImageDraw.Draw(im)
        sx, sy = int(im.width * TV_SCREEN[0]), int(im.height * TV_SCREEN[1])   # centre of the screen
        dd.text((sx, sy - 38), words[0][0], font=ft_s, fill=C[words[0][2]], anchor="mm")
        dd.text((sx, sy + 34), words[1][0], font=ft_b, fill=C[words[1][2]], anchor="mm")
        return im
    scr = L("tvscreen", screen)
    put(f, contact(380, 120), W // 2 + 20, FLOOR_Y + 30)
    p = prog(t, s, 0.6); e = MOVE(p)
    put(f, drop_shadow(scr, 16, (10, 18), 70), W // 2, FLOOR_Y - scr.height // 2 + 70 - 30 * (1 - e), 1.25 - 0.25 * e)


def slab(f, t, s, d, words):
    f.alpha_composite(studio())
    p = prog(t, s, 0.35); e = MOVE(p)
    ImageDraw.Draw(f).rectangle((W - 290, 0, W - 80, int(820 * e)), fill=CTA + (255,))
    q = prog(t, s + 0.05, 0.4); g = MOVE(q)
    ImageDraw.Draw(f).rectangle((0, 1250, int(520 * g), H), fill=SIG + (255,))
    say(f, t, s, words, 640, x=(W - 330) if RTL else 90, gap=0.18)


def card(f, t, s, d, words):
    f.alpha_composite(studio())
    tl = tile(520, SIG, depth=26)
    focus_in(f, t, tl, W // 2 + 110, 930, s, dur=0.35, scale=1.08, blur=6)
    ghost_words(f, t, None, W // 2 + 170, 790, s + 0.2, lines=((words[0][0], words[0][1]), (words[1][0], words[1][1])),
                col=C[words[0][2]], rtl=RTL, align="center", gap=WORD_GAP, lead=1.1)
    roll_in(f, t, drop_shadow(obj(OBJECTS["card"], h=270), 14, (10, 18), 80), W // 2 - 180, 900, s + 0.3, dist=600, turns=0.6)
    say(f, t, s + 0.35, words[2:], 1300, x=W // 2, align="center")


def pillar(f, t, s, d, words):
    f.alpha_composite(studio(floor=True))
    big = words[-1]
    ghost_words(f, t, None, W // 2, 760, s + 0.22, lines=((big[0], big[1]),), col=C[big[2]], rtl=RTL, align="center",
                shadow=True)
    ghost_words(f, t, None, W // 2, 660, s + 0.06, lines=((words[0][0], words[0][1]),), col=C[words[0][2]], rtl=RTL, align="center")
    col = column()
    p = prog(t, s + 0.1, 0.5)
    lift = 700 * (1 - _spring(p, 9, 7)) if p > 0 else 900
    put(f, col, W // 2 + 20, 1232 + col.height // 2 + lift)   # top of the column meets the gem
    blur_rise(f, t, drop_shadow(obj(OBJECTS["pillar"], h=330), 16, (12, 20), 90), W // 2, 1060, s + 0.18, dist=900)


def drop(f, t, s, d, words):
    f.alpha_composite(studio(floor=True))
    p = prog(t, s + 0.2, 0.55)
    if p > 0:
        put(f, contact(240, 130), W // 2 + 20, FLOOR_Y + 120, 0.4 + 0.6 * min(1, p * 1.6), min(1, p * 2))
    blur_rise(f, t, obj(OBJECTS["drop"], h=480), W // 2, FLOOR_Y + 120 - 240, s + 0.2, side="up", dist=1200)
    say(f, t, s, words, 420, x=W // 2, align="center")


LOOKS = {"orbit": orbit, "tiles": tiles, "rise": rise, "tv": tv, "slab": slab, "card": card, "pillar": pillar, "drop": drop}


def scene(i, t):
    f = Image.new("RGBA", (W, H), PAPER + (255,))
    bars, look, words, _d = SCENES[i]
    LOOKS[look](f, t, STARTS[i], bars * BAR, words)
    k = 1 + DRIFT * MOVE(prog(t, STARTS[i], bars * BAR))     # slow camera drift: no frame stands still
    return zoom_frame(f, k, W / 2, H * 0.45)


def render(t):
    if t >= END:
        f = Image.new("RGBA", (W, H))
        name_logo_follow(f, t, END)
        return f.convert("RGB")
    i = max(k for k, s in enumerate(STARTS) if s <= t)
    nxt = STARTS[i + 1] if i + 1 < len(STARTS) else None
    if nxt is not None and t > nxt - WHIP:                       # whip into the next scene
        p = (t - (nxt - WHIP)) / (2 * WHIP)
        return whip(scene(i, t), scene(i + 1, t), p, SCENES[i][3]).convert("RGB")
    if i > 0 and t < STARTS[i] + WHIP:                            # second half of the whip
        p = 0.5 + (t - STARTS[i]) / (2 * WHIP)
        return whip(scene(i - 1, t), scene(i, t), p, SCENES[i - 1][3]).convert("RGB")
    return scene(i, t).convert("RGB")


if __name__ == "__main__":
    if sys.argv[1] == "test":
        ts = [float(x) for x in sys.argv[2:]]; ims = []
        for x in ts:
            im = render(x); im.save(config.work(f"ss_{x}.png")); ims.append(im.resize((270, 480)))
        sh = Image.new("RGB", (270 * len(ims), 480)); [sh.paste(im, (i * 270, 0)) for i, im in enumerate(ims)]
        sh.save(config.work("sssheet.png")); sys.exit()
    out = config.work("ss_v.mp4")
    enc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                            "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    t0 = time.time()
    for k in range(int(DUR * FPS)): enc.stdin.write(render(k / FPS).tobytes())
    enc.stdin.close(); enc.wait(); print("done", out, round(time.time() - t0), "s")
