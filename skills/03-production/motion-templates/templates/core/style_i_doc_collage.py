"""Style I — Doc Collage: documentary-style story edit. Hard cuts with a camera punch, words that
slam and turn, an object dropped onto a stool while the world turns black & white, an offer wall
with a rolling year, a torn-paper photo on wood with a scribbled strike, echo words, a spinning
sunburst that becomes a clock, a fan of tickets. Film grain on top. 12 bars + ending = 26.25 s.

No photos needed: find them with engine/assets.py (see SKILL.md, "No images? Find them"):
    gem.png  stool.png            cut-outs (get <n> --as <file> --cutout --one)
    hills.jpg  city.jpg  wood.jpg  photos   (get <n> --as <file>)

    python templates/core/style_i_doc_collage.py test 1.6 4.5 8 11 15 18 21.5 24   # stills + sheet
    python templates/core/style_i_doc_collage.py render                            # work/dc_v.mp4
    python render.py --style i                                                     # whole reel
"""
import math
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # skill root, so the engine package is importable
from engine import config
_BRAND = config.brand()
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageOps
from engine.plib import CAIRO, ENTER, MONO, fit, grain_layer, prog, put, rrect, txt
from engine.moves import (blur_rise, clock_face, count_up, desaturate, echo_rows, fan_out, focus_in, ghost_words,
                          glow_underline, marquee_word, push_in, scribble_strike, sunburst, torn_photo, word_turn)
from engine.endings import TIMES as END_T, name_logo_follow

W, H, FPS = 1080, 1920, 30
BPM = 128; BAR = 4 * 60 / BPM
RTL = _BRAND["language"].startswith("ar")

# ---------- story ----------
if RTL:
    S = dict(turn=("عشرين", "مليار"),
             said=(("قاله", 120), ("لأ", 300)),
             offer_word="عرض", year=2008,
             torn=(("بعد 15 سنة", 64), ("أغلى شركة", 150), ("في العالم", 64)),
             echo_word="محدش", echo_line="‹ اللي محدش بيقوله ›",
             sun=(("القناعة شكلها", 74), ("زي العِند", 96)),
             ask=(("إيه العرض اللي", 72), ("محتاج تقول له لأ؟", 96)),
             ticket="لأ")
else:
    S = dict(turn=("TWENTY", "BILLION"),
             said=(("he said", 110), ("NO", 300)),
             offer_word="OFFER", year=2008,
             torn=(("15 years later", 64), ("most valuable", 120), ("on earth", 64)),
             echo_word="NOBODY", echo_line="< here's what nobody says >",
             sun=(("conviction looks", 74), ("like stubbornness", 80)),
             ask=(("what's the offer", 72), ("you need to say no to?", 76)),
             ticket="NO")
SCENES = [(1.5, "turn"), (2.0, "stool"), (1.5, "offer"), (2.0, "torn"), (1.5, "echo"), (2.0, "sun"), (1.5, "fan")]
END_BARS = 2.0
PUNCH = 0.16          # camera punch on every cut (s)

STARTS = []
_t = 0.0
for b, _l in SCENES:
    STARTS.append(_t); _t += b * BAR
END = _t
DUR = round(END + END_BARS * BAR, 3)
TURN_GAP = 0.6


def events():
    ev = [(s, "cut") for s in STARTS[1:]] + [(END, "cut")]
    st = dict(zip([l for _b, l in SCENES], STARTS))
    ev += [(st["turn"] + k * TURN_GAP, "slam") for k in range(3)]
    ev += [(st["stool"] + 0.2, "drop"), (st["stool"] + BAR, "word_big"), (st["stool"] + BAR + 0.3, "slam")]
    ev += [(st["offer"] + 0.2, "whoosh"), (st["offer"] + 1.4, "pop")]
    ev += [(st["torn"] + 0.1, "rip"), (st["torn"] + 1.2, "slam"), (st["torn"] + 1.7, "scribble")]
    ev += [(st["echo"] + 0.3, "word"), (st["echo"] + 1.0, "glow")]
    ev += [(st["sun"] + 0.05, "whoosh"), (st["sun"] + 0.6, "word"), (st["sun"] + 2.5, "tick")]
    ev += [(st["fan"] + 0.7, "fan")]
    ev += [(END + END_T[k], k) for k in ("split", "follow", "tap")]
    return sorted(ev)


# ---------- brand ----------
INK = config.color("ink"); PAPER = config.color("background"); ACC = config.color("accent"); CTA = config.color("cta")
SIG = config.color("primary"); HL = config.color("highlight"); WHITE = (255, 255, 255); BLACK = (10, 10, 12)
DARK_CTA = tuple(int(c * 0.55) for c in CTA)
_L = {}


def L(key, make):
    if key not in _L:
        _L[key] = make()
    return _L[key]


def img(name, what="a photo"):
    return L(("img", name), lambda: config.input_image(name, (1400, 1400), f"{what} (engine/assets.py get …)").convert("RGB"))


def cut(name, h=None, w=None):
    def make():
        im = config.input_image(name, (700, 700), "an object cut-out (engine/assets.py get … --cutout --one)", rgba=True).convert("RGBA")
        return fit(im, h=h) if h else fit(im, w=w)
    return L(("cut", name, h, w), make)


def shadowed(spr, blur=20, off=(14, 26), op=110):
    def make():
        pad = blur * 3
        sh = Image.new("RGBA", (spr.width + 2 * pad, spr.height + 2 * pad), (0, 0, 0, 0))
        sh.paste((0, 0, 0, op), (pad + off[0], pad + off[1]), spr.split()[3])
        sh = sh.filter(ImageFilter.GaussianBlur(blur)); sh.alpha_composite(spr, (pad, pad))
        return sh
    return L(("sh", id(spr)), make)


def full(name, dark=0.0):
    def make():
        im = ImageOps.fit(img(name), (W, H)).convert("RGBA")
        if dark:
            im = Image.blend(im, Image.new("RGBA", (W, H), (0, 0, 0, 255)), dark)
        return im
    return L(("full", name, dark), make)


def vignette(col):
    def make():
        g = Image.new("L", (W, H), 0)
        ImageDraw.Draw(g).ellipse((-300, -200, W + 300, H + 200), fill=255)
        g = g.filter(ImageFilter.GaussianBlur(260))
        return Image.composite(Image.new("RGB", (W, H), col), Image.new("RGB", (W, H), tuple(int(c * 0.82) for c in col)), g).convert("RGBA")
    return L(("vig", col), make)


def say(f, t, t0, lines, col, top, x=None, align="center", gap=0.2, shadow=False):
    ghost_words(f, t, None, W // 2 if x is None else x, top, t0, lines=lines, col=col, rtl=RTL, align=align, gap=gap,
                shadow=shadow)


# ---------- scenes ----------
def turn(f, t, s, d):
    k = min(2, int((t - s) // TURN_GAP))
    bg = [PAPER, BLACK, ACC][k]
    f.alpha_composite(vignette(bg))
    if k < 2:
        word_turn(f, t, None, W // 2, 900, s, words=S["turn"], size=170, col=ACC, gap=TURN_GAP, rtl=RTL)
    else:
        word_turn(f, t, None, W // 2, 420, s + TURN_GAP, words=S["turn"][1:], size=130, col=INK, gap=99, rtl=RTL)
        focus_in(f, t, shadowed(cut("gem.png", h=620)), W // 2, 1060, s + 2 * TURN_GAP, dur=0.35)


def stool(f, t, s, d):
    hills = L("hills", lambda: ImageOps.fit(img("hills.jpg", "a landscape photo"), (W, H), centering=(0.5, 0.35)).convert("RGBA"))
    push_in(f, t, hills, W // 2, H // 2, s, dur=d, amount=0.05, drift=0)
    st = cut("stool.png", w=560)
    put(f, shadowed(st, 18, (10, 20), 90), W // 2, 1460)
    blur_rise(f, t, shadowed(cut("gem.png", h=420)), W // 2, 1460 - st.height // 2 - 170, s + 0.15, side="up", dist=1400)
    gray = prog(t, s + BAR - 0.2, 0.35)
    if gray > 0:
        f.paste(desaturate(f, gray), (0, 0))
    say(f, t, s + BAR, S["said"], CTA, 300, shadow=True, gap=0.3)


def offer(f, t, s, d):
    f.alpha_composite(vignette(CTA))
    marquee_word(f, t, None, 0, 1420, s, word=S["offer_word"], col=DARK_CTA, alpha=0.9, size=420, speed=220, rows=2, rtl=RTL)
    p = prog(t, s + 0.15, 0.7)
    gem = shadowed(cut("gem.png", h=380))
    if p > 0:
        e = ENTER(p)
        put(f, gem.rotate(-25 + 25 * e, Image.BICUBIC, expand=True), -200 + (W // 2 + 200) * e, 1000 - 200 * math.sin(math.pi * e) * 0.4, 1, min(1, p * 3))
    count_up(f, t, None, W // 2, 520, s + 0.4, start=S["year"] - 40, end=S["year"], dur=0.9, size=230, col=WHITE)


def torn(f, t, s, d):
    f.alpha_composite(full("wood.jpg", 0.35))
    hole = L("hole", lambda: torn_photo(img("city.jpg", "a city or subject photo"), 720, 900))
    p = prog(t, s, 0.35)
    push_in(f, t, hole, W // 2 + 60, 1180, s, dur=d, amount=0.12, drift=-20)
    say(f, t, s + 0.6, S["torn"][:1], WHITE, 560, x=(W - 90) if RTL else 90, align="left")
    say(f, t, s + 1.2, S["torn"][1:2], WHITE, 640, shadow=True)
    scribble_strike(f, t, None, W // 2, 770, s + 1.7, width=760, col=CTA, thick=13)
    say(f, t, s + 2.1, S["torn"][2:], HL, 860, x=(W - 90) if RTL else 90, align="left")


def echo(f, t, s, d):
    f.paste(BLACK + (255,), (0, 0, W, H))
    echo_rows(f, t, None, 0, 260, s, word=S["echo_word"], size=170, col=WHITE, rows=3, alpha=0.2, rtl=RTL)
    echo_rows(f, t, None, 0, 1180, s + 0.1, word=S["echo_word"], size=170, col=WHITE, rows=3, alpha=0.2, rtl=RTL, speed=-90)
    say(f, t, s + 0.3, ((S["echo_line"], 80),), WHITE, 870, gap=0.12)
    glow_underline(f, t, None, W // 2, 1000, s + 1.0, width=520, col=ACC)


def sun(f, t, s, d):
    f.paste(BLACK + (255,), (0, 0, W, H))
    sunburst(f, t, None, W // 2, 960, s, col=HL, r0=290)
    if t < s + 2.4:
        say(f, t, s + 0.6, S["sun"], SIG, 860, gap=0.22)
    else:
        clock_face(f, t, None, W // 2, 960, s + 2.4, r=300, col=HL, ink=INK)


def fan(f, t, s, d):
    f.paste(BLACK + (255,), (0, 0, W, H))
    def ticket():
        tk = rrect(330, 520, 26, ACC + (255,)); dd = ImageDraw.Draw(tk)
        dd.rectangle((24, 24, 305, 495), outline=INK + (255,), width=3)
        w_ = txt(S["ticket"], (CAIRO if RTL else MONO)(150), INK, rtl=RTL); tk.alpha_composite(w_, ((330 - w_.width) // 2, 200 - w_.height // 2 + 40))
        tk.alpha_composite(txt(_BRAND["name"].upper()[:14], MONO(22), INK), (40, 450))
        return tk
    say(f, t, s + 0.2, S["ask"], WHITE, 380, gap=0.2)
    fan_out(f, t, shadowed(L("ticket", ticket), 16, (8, 16), 120), W // 2, 1300, s + 0.7, n=7, spread=90)


LOOKS = {"turn": turn, "stool": stool, "offer": offer, "torn": torn, "echo": echo, "sun": sun, "fan": fan}
GRAIN = [Image.merge("RGBA", [grain_layer(W // 2, H // 2, 14, k).resize((W, H))] * 3 + [Image.new("L", (W, H), 26)]) for k in range(3)]


def render(t):
    f = Image.new("RGBA", (W, H), PAPER + (255,))
    if t >= END:
        name_logo_follow(f, t, END, bg=BLACK, ink=WHITE)
    else:
        i = max(k for k, s in enumerate(STARTS) if s <= t)
        LOOKS[SCENES[i][1]](f, t, STARTS[i], SCENES[i][0] * BAR)
        if i > 0 and t - STARTS[i] < PUNCH:                      # camera punch on the cut
            k = 1 + 0.07 * (1 - (t - STARTS[i]) / PUNCH)
            big = f.resize((int(W * k), int(H * k)), Image.BILINEAR)
            f = big.crop(((big.width - W) // 2, (big.height - H) // 2, (big.width - W) // 2 + W, (big.height - H) // 2 + H))
    f.alpha_composite(GRAIN[int(t * 12) % 3])
    return f.convert("RGB")


if __name__ == "__main__":
    if sys.argv[1] == "test":
        ts = [float(x) for x in sys.argv[2:]]; ims = []
        for x in ts:
            im = render(x); im.save(config.work(f"dc_{x}.png")); ims.append(im.resize((270, 480)))
        sh = Image.new("RGB", (270 * len(ims), 480)); [sh.paste(im, (i * 270, 0)) for i, im in enumerate(ims)]
        sh.save(config.work("dcsheet.png")); sys.exit()
    out = config.work("dc_v.mp4")
    enc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                            "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    t0 = time.time()
    for k in range(int(DUR * FPS)): enc.stdin.write(render(k / FPS).tobytes())
    enc.stdin.close(); enc.wait(); print("done", out, round(time.time() - t0), "s")
