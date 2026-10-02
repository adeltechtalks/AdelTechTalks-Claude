"""Style J — Edit Compare: the same talking-head clip side by side — a small raw card ("$5 Edit")
and a big polished card ("$100 Edit") with punch-in jump cuts, word-by-word captions with one big
highlighted word, and b-roll with glowing titles. Ends by darkening into the shared name → logo ending.

Inputs:
    talk.mp4      your talking-head clip (9:16). Its voice becomes the main audio in render.py.
                  Without it, photo.jpg is used as a still stand-in (or a placeholder).
    b-roll images listed in BROLL — find them with engine/assets.py if you have none.
Write CAPTIONS to match what you say (start, end, small words, big word).

    python templates/core/style_j_edit_compare.py test 1.5 4 8 17         # stills + sheet in work/
    python templates/core/style_j_edit_compare.py render                   # work/ec_v.mp4 (silent)
    python render.py --style j                                             # whole reel (voice + music + SFX)
"""
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # skill root, so the engine package is importable
from engine import config
_BRAND = config.brand()
from PIL import Image, ImageDraw, ImageFilter, ImageOps
from engine.plib import CAIRO, MONT, READ, ENTER, MOVE, prog, put, txt
from engine.moves import ghost_words, _word
from engine.endings import TIMES as END_T, name_logo_follow

W, H, FPS = 1080, 1920, 30
BPM = 128; BAR = 4 * 60 / BPM
RTL = _BRAND["language"].startswith("ar")

# ---------- story ----------
LABEL_CHEAP, LABEL_PRO = "$5 Edit", "$100 Edit"
if RTL:   # (start, end, small words, big word) — match them to your clip
    CAPTIONS = [(0.2, 3.0, "الفرق بين", "المونتاجين"), (3.0, 6.0, "مش في", "البرنامج"), (6.0, 9.0, "الفرق في", "الفكرة"),
                (9.0, 12.0, "واللي بتحكيه", "للناس"), (12.0, 15.0, "وده اللي", "بيفرق")]
else:
    CAPTIONS = [(0.2, 3.0, "the difference between", "edits"), (3.0, 6.0, "isn't the", "software"), (6.0, 9.0, "it's the", "idea"),
                (9.0, 12.0, "and the story", "you tell"), (12.0, 15.0, "that's what", "matters")]
BROLL = [(3.0, 6.0, "city.jpg", "Reels"), (9.0, 12.0, "hills.jpg", "Story")]   # (start, end, image, title)
END_BARS = 2.0

TALK = config.INPUT_DIR / "talk.mp4"
BIG = dict(cx=650, cy=980, w=640, h=1000, r=44)
SMALL = dict(cx=205, cy=900, w=250, h=390, r=26)


def _talk_len():
    if TALK.exists():
        try:
            out = subprocess.run(["ffmpeg", "-i", str(TALK)], capture_output=True, text=True).stderr
            hh, mm, ss = out.split("Duration: ")[1].split(",")[0].split(":")
            return int(hh) * 3600 + int(mm) * 60 + float(ss)
        except Exception:
            pass
    return max(c[1] for c in CAPTIONS)


END = round(_talk_len(), 3)
DUR = round(END + END_BARS * BAR, 3)


def events():
    ev = [(b[0], "broll") for b in BROLL] + [(b[1], "broll_out") for b in BROLL]
    for s, e, small, big in CAPTIONS:
        n = len(small.split())
        ev += [(s + k * 0.16, "word") for k in range(n)] + [(s + n * 0.16 + 0.05, "word_big")]
    ev += [(END, "cut")] + [(END + END_T[k], k) for k in ("split", "follow", "tap")]
    return sorted(ev)


# ---------- brand ----------
PAPER = config.color("background"); INK = config.color("ink"); ACC = config.color("accent"); SIG = config.color("primary")
GLOW = config.color("primary_light"); WHITE = (255, 255, 255)
_L = {}


def L(key, make):
    if key not in _L:
        _L[key] = make()
    return _L[key]


# ---------- talk frames ----------
def talk_frames():
    """Decode talk.mp4 once into work/talk_frames (JPEG, 30 fps, 720 wide)."""
    d = Path(config.work("talk_frames"))
    stamp = d / ".src"
    key = f"{TALK.stat().st_mtime}" if TALK.exists() else ""
    if not (stamp.exists() and stamp.read_text() == key):
        d.mkdir(parents=True, exist_ok=True)
        for p in d.glob("*.jpg"): p.unlink()
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(TALK), "-vf", f"fps={FPS},scale=720:-2", "-q:v", "3",
                        str(d / "%05d.jpg")], check=True)
        stamp.write_text(key)
    return sorted(d.glob("*.jpg"))


def talk(t):
    if TALK.exists():
        fr = L("frames", talk_frames)
        return Image.open(fr[min(len(fr) - 1, int(t * FPS))]).convert("RGB")
    still = L("still", lambda: config.input_image("photo.jpg", (720, 1280), "your talking-head clip (talk.mp4) or a photo").convert("RGB"))
    k = 1 + 0.03 * (t / max(1, END))                       # still stand-in: slow push
    w, h = still.size
    return still.crop((int(w * (1 - 1 / k) / 2), int(h * (1 - 1 / k) / 2), int(w * (1 + 1 / k) / 2), int(h * (1 + 1 / k) / 2)))


def mask(w, h, r):
    def make():
        m = Image.new("L", (w * 2, h * 2), 0)
        ImageDraw.Draw(m).rounded_rectangle((0, 0, w * 2 - 1, h * 2 - 1), r * 2, fill=255)
        return m.resize((w, h), Image.LANCZOS)
    return L(("mask", w, h, r), make)


def card_shadow(w, h, r):
    def make():
        pad = 90
        im = Image.new("RGBA", (w + 2 * pad, h + 2 * pad), (0, 0, 0, 0))
        m = Image.new("L", im.size, 0)
        ImageDraw.Draw(m).rounded_rectangle((pad + 10, pad + 26, pad + w + 10, pad + h + 26), r, fill=95)
        im.putalpha(m.filter(ImageFilter.GaussianBlur(34)))
        return im
    return L(("cs", w, h, r), make)


def place(f, content, g):
    w, h = g["w"], g["h"]
    c = ImageOps.fit(content, (w, h)).convert("RGBA")
    c.putalpha(mask(w, h, g["r"]))
    sh = card_shadow(w, h, g["r"])
    f.alpha_composite(sh, (g["cx"] - sh.width // 2, g["cy"] - sh.height // 2))
    f.alpha_composite(c, (g["cx"] - w // 2, g["cy"] - h // 2))


def title_glow(word):
    def make():
        ft = (CAIRO if any("؀" <= ch <= "ۿ" for ch in word) else MONT)(130)
        t_ = txt(word, ft, WHITE, rtl=RTL)
        pad = 60
        im = Image.new("RGBA", (t_.width + 2 * pad, t_.height + 2 * pad), (0, 0, 0, 0))
        g = Image.new("RGBA", im.size, (0, 0, 0, 0)); g.paste(GLOW + (255,), (pad, pad), t_.split()[3])
        g = g.filter(ImageFilter.GaussianBlur(18))
        im.alpha_composite(g); im.alpha_composite(g); im.alpha_composite(t_, (pad, pad))
        return im
    return L(("tg", word), make)


def pro_content(t):
    """The $100 side: punch-ins, b-roll with titles, captions."""
    w, h = BIG["w"], BIG["h"]
    br = next((b for b in BROLL if b[0] <= t < b[1]), None)
    if br:
        src = L(("br", br[2]), lambda: config.input_image(br[2], (900, 1400), "a b-roll image (engine/assets.py get …)").convert("RGB"))
        k = 1.08 + 0.10 * (t - br[0]) / (br[1] - br[0])
        c = ImageOps.fit(src, (int(w * k), int(h * k))).crop(((int(w * k) - w) // 2, (int(h * k) - h) // 2,
                                                              (int(w * k) - w) // 2 + w, (int(h * k) - h) // 2 + h)).convert("RGBA")
        c.alpha_composite(Image.new("RGBA", (w, h), (0, 0, 0, 70)))
        p = prog(t, br[0] + 0.1, 0.4)
        if p > 0:
            put(c, title_glow(br[3]), w // 2, 190 + 40 * (1 - ENTER(p)), 1.1 - 0.1 * ENTER(p), min(1, p * 2))
    else:
        i = next((k for k, cp in enumerate(CAPTIONS) if cp[0] <= t < cp[1]), 0)
        z = 1.0 if i % 2 == 0 else 1.14                      # jump-cut punch-in on every other caption
        src = talk(t)
        sw, shh = src.size
        c = src.crop((int(sw * (1 - 1 / z) / 2), int(shh * (1 - 1 / z) / 3), int(sw * (1 - 1 / z) / 2 + sw / z),
                      int(shh * (1 - 1 / z) / 3 + shh / z)))
        c = ImageOps.fit(c, (w, h)).convert("RGBA")
    cap = next((cp for cp in CAPTIONS if cp[0] <= t < cp[1]), None)
    if cap:
        s, e, small, big = cap
        n = len(small.split())
        ghost_words(c, t, None, w // 2, h - 330, s, lines=((small, 50),), col=WHITE, rtl=RTL, align="center", gap=0.16,
                    shadow=True)
        ghost_words(c, t, None, w // 2, h - 260, s + n * 0.16 + 0.05, lines=((big, 104),), col=ACC, rtl=RTL,
                    align="center", gap=0.16, shadow=True)
    return c


def bg():
    def make():
        g = Image.new("L", (W, H), 0)
        ImageDraw.Draw(g).ellipse((-300, -200, W + 300, H + 200), fill=255)
        g = g.filter(ImageFilter.GaussianBlur(260))
        return Image.composite(Image.new("RGB", (W, H), PAPER), Image.new("RGB", (W, H), tuple(int(c * 0.9) for c in PAPER)), g).convert("RGBA")
    return L("bg", make)


def scene(t):
    f = bg().copy()
    lab = L("lab_p", lambda: txt(LABEL_PRO, READ(46, 800), INK))
    lab2 = L("lab_c", lambda: txt(LABEL_CHEAP, READ(30, 800), INK))
    p = prog(t, 0, 0.5); e = ENTER(p)
    place(f, talk(t), dict(SMALL, cx=int(SMALL["cx"] - 300 * (1 - e))))
    put(f, lab2, SMALL["cx"] - 300 * (1 - e), SMALL["cy"] - SMALL["h"] // 2 - 40, 1, e)
    place(f, pro_content(t), dict(BIG, cy=int(BIG["cy"] + 200 * (1 - e))))
    put(f, lab, BIG["cx"], BIG["cy"] - BIG["h"] // 2 - 52 + 200 * (1 - e), 1, e)
    put(f, L("handle", lambda: txt(_BRAND["name"], READ(24, 600), tuple(int(c * 0.6 + 255 * 0.4) for c in INK))), W // 2, 1640)
    return f


def render(t):
    f = scene(min(t, END - 1 / FPS))
    if t >= END:
        name_logo_follow(f, t, END, bg=None)
    return f.convert("RGB")


if __name__ == "__main__":
    if sys.argv[1] == "test":
        ts = [float(x) for x in sys.argv[2:]]; ims = []
        for x in ts:
            im = render(x); im.save(config.work(f"ec_{x}.png")); ims.append(im.resize((270, 480)))
        sh = Image.new("RGB", (270 * len(ims), 480)); [sh.paste(im, (i * 270, 0)) for i, im in enumerate(ims)]
        sh.save(config.work("ecsheet.png")); sys.exit()
    out = config.work("ec_v.mp4")
    enc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                            "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    t0 = time.time()
    for k in range(int(DUR * FPS)): enc.stdin.write(render(k / FPS).tobytes())
    enc.stdin.close(); enc.wait(); print("done", out, round(time.time() - t0), "s")
