"""Motion lab — plays every move in engine/moves.py on a brand-coloured card.

    python templates/lab/moves_demo.py test 0.3 0.8          # PNGs + contact sheet in work/
    python templates/lab/moves_demo.py render                # all moves → work/moves_demo.mp4
    python templates/lab/moves_demo.py render pop_in         # one move only
"""
import sys, subprocess, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # skill root, so the engine package is importable
from engine import config
from PIL import Image
from engine.plib import txt, rrect, CAIRO, MONT, MONO, WHITE, GRAPH, SIG
from engine.moves import MOVES

W, H, FPS, SLOT = 1080, 1920, 30, 1.8
BG = config.color("background")
ONLY = sys.argv[2:] if len(sys.argv) > 2 and sys.argv[1] == "render" else []
NAMES = [n for n in MOVES if not ONLY or n in ONLY]
DUR = SLOT * len(NAMES)


def card(label):
    t = txt(label, MONT(64), WHITE)
    c = rrect(t.width + 120, t.height + 70, 36, SIG + (255,))
    c.alpha_composite(t, (60, 35))
    return c


CARDS = {n: card(n) for n in NAMES}
LABELS = {n: txt(MOVES[n][1], MONO(30), GRAPH) for n in NAMES}


def render(t):
    f = Image.new("RGBA", (W, H), BG + (255,))
    i = min(int(t // SLOT), len(NAMES) - 1)
    name = NAMES[i]
    fn = MOVES[name][0]
    t0 = i * SLOT + 0.25
    lab = LABELS[name]
    f.alpha_composite(lab, ((W - lab.width) // 2, 420))
    fn(f, t, CARDS[name], W // 2, H // 2, t0)
    return f.convert("RGB")


if __name__ == "__main__":
    if sys.argv[1] == "test":
        ts = [float(x) for x in sys.argv[2:]]; ims = []
        for x in ts:
            im = render(x); im.save(config.work(f"lab_{x}.png")); ims.append(im.resize((216, 384)))
        sh = Image.new("RGB", (216 * len(ims), 384)); [sh.paste(im, (i * 216, 0)) for i, im in enumerate(ims)]
        sh.save(config.work("labsheet.png")); sys.exit()
    out = config.work("moves_demo.mp4")
    enc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                            "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    t0 = time.time()
    for k in range(int(DUR * FPS)): enc.stdin.write(render(k / FPS).tobytes())
    enc.stdin.close(); enc.wait(); print("done", out, round(time.time() - t0), "s")
