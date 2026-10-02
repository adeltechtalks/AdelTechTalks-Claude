"""Motion library — reusable moves every template can call.

Every move has the same shape:

    move(f, t, spr, cx, cy, t0, **options)

    f      the frame being drawn (RGBA Image)
    t      current time (s)
    spr    the sprite to animate (RGBA Image: text, chip, logo, card…)
    cx, cy where it lands (centre)
    t0     when the move starts (s)

It draws nothing before t0 and holds the final pose after it finishes, so a
template can call it on every frame. Colours and fonts always come from the
brand, never from the move.

To teach the skill a new move, follow "Learn a new motion" in SKILL.md: study the
reference, add a function here, register it in MOVES, render the lab demo
(templates/lab/moves_demo.py), and log it in references/motion-library.md.
"""
import math

from PIL import Image, ImageDraw, ImageFilter

from engine.plib import CAIRO, ENTER, EXIT, MONT, MOVE, SH, fold_in, preshadow, prog, put, slap


def _spring(p, freq=8.0, damp=7.0):
    return 1 - math.exp(-damp * p) * math.cos(freq * p) if p < 1 else 1.0


def pop_in(f, t, spr, cx, cy, t0, dur=0.42):
    """Title pop: 0.96 → 1.03 → 1.0 with a quick fade in."""
    p = prog(t, t0, dur)
    if p <= 0:
        return
    if p < 0.6:
        s = 0.96 + 0.07 * ENTER(p / 0.6)
    else:
        s = 1.03 - 0.03 * MOVE((p - 0.6) / 0.4)
    put(f, spr, cx, cy, s, min(1, p * 3))


def slide_in(f, t, spr, cx, cy, t0, side="left", dist=420, dur=0.3):
    """Enter from a side with the brand ENTER curve (300 ms)."""
    p = prog(t, t0, dur)
    if p <= 0:
        return
    e = ENTER(p)
    dx, dy = {"left": (-dist, 0), "right": (dist, 0), "up": (0, -dist), "down": (0, dist)}[side]
    put(f, spr, cx + dx * (1 - e), cy + dy * (1 - e), 1, min(1, p * 2.5))


def spring_drop(f, t, spr, cx, cy, t0, height=520, dur=0.9):
    """Falls from above and settles with a small bounce (ball / sticker drop)."""
    p = prog(t, t0, dur)
    if p <= 0:
        return
    y = cy - height * (1 - _spring(p, freq=11, damp=6))
    squash = 1 + 0.06 * math.sin(math.pi * min(1, p * 2.2)) * (1 - p)
    put(f, spr, cx, y, squash, min(1, p * 4))


def slide_out(f, t, spr, cx, cy, t0, side="right", dist=420, dur=0.2):
    """Exit with the brand EXIT curve (200 ms). Draws the sprite until t0."""
    p = prog(t, t0, dur)
    if p >= 1:
        return
    e = EXIT(p)
    dx, dy = {"left": (-dist, 0), "right": (dist, 0), "up": (0, -dist), "down": (0, dist)}[side]
    put(f, spr, cx + dx * e, cy + dy * e, 1, 1 - e)


def slap_in(f, t, spr, cx, cy, t0, rot=0):
    """Sticker slap: lands big and rotated, snaps flat (from paper_collage)."""
    slap(f, t, spr, cx, cy, t0, rot=rot)


def fold_open(f, t, spr, cx, cy, t0, axis="v", moving="top"):
    """Paper card unfolds along an axis (from paper_collage)."""
    if id(spr) not in SH:
        preshadow(spr)
    fold_in(f, t, spr, cx, cy, t0, axis=axis, moving=moving)


_CACHE = {}


def _word(w, size, col, rtl, font):
    k = (w, size, col, rtl, font)
    if k not in _CACHE:
        # fixed-height box drawn on the baseline, so words of one line always line up
        ft = (font or (CAIRO if rtl else MONT))(size)
        kw = dict(direction="rtl", language="ar") if rtl else {}
        d = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
        x0, _, x1, _ = d.textbbox((0, 0), w, font=ft, anchor="ls", **kw)
        im = Image.new("RGBA", (int(x1 - x0) + 16, int(size * 1.5)), (0, 0, 0, 0))
        ImageDraw.Draw(im).text((8 - x0, int(size * 1.08)), w, font=ft, fill=col, anchor="ls", **kw)
        _CACHE[k] = im
    return _CACHE[k]


def ghost_words(f, t, spr, cx, cy, t0, lines=(("one idea", 64), ("at a time", 120)), gap=0.26,
                col=(255, 255, 255), rtl=False, align="left", font=None, lead=0.78):
    """Words land one by one: each appears as a big blurred ghost, then sharpens into place.

    lines   [(text, size), …] — a small set-up line over a big punch line works best
    cx, cy  left edge (align='left', or right edge for rtl) / centre (align='center') and top of the block
    spr     unused (pass None) — the words are drawn from the brand fonts
    """
    k = 0
    y = cy
    for text, size in lines:
        words = [_word(w, size, col, rtl, font) for w in text.split()]
        sp = int(size * 0.28)
        total = sum(w.width for w in words) + sp * (len(words) - 1)
        if align == "center":
            x = cx - total / 2
        else:
            x = cx - total if rtl else cx
        order = list(reversed(words)) if rtl else words   # draw left→right, reveal in reading order
        xs = []
        for w in order:
            xs.append(x); x += w.width + sp
        if rtl:
            xs = list(reversed(xs))
        for w, wx in zip(words, xs):
            p = prog(t, t0 + k * gap, 0.34)
            k += 1
            if p <= 0:
                continue
            e = ENTER(p)
            im = w if p >= 1 else w.filter(ImageFilter.GaussianBlur(7 * (1 - e)))
            put(f, im, wx + w.width / 2, y + w.height / 2, 1.12 - 0.12 * e, 0.25 + 0.75 * e)
        y += int(max(w.height for w in words) * lead)


def marquee_word(f, t, spr, cx, cy, t0, word="IDEAS", size=380, speed=160, col=(255, 255, 255), alpha=0.28,
                 rows=2, font=None, rtl=False):
    """Giant word repeated edge to edge, rows sliding in opposite directions behind the subject."""
    p = prog(t, t0, 0.3)
    if p <= 0:
        return
    w = _word(word + "  ", size, col, rtl, font)
    W = f.width
    for r in range(rows):
        dirn = -1 if r % 2 == 0 else 1
        off = (dirn * speed * (t - t0) + r * w.width / 3) % w.width
        y = cy + r * int(w.height * 0.82)
        x = off - w.width
        while x < W:
            put(f, w, x + w.width / 2, y, 1, alpha * p)
            x += w.width


def push_in(f, t, spr, cx, cy, t0, dur=3.0, amount=0.06, drift=-14):
    """Slow camera push: the layer grows a few % and drifts while the scene plays (stack layers with
    different amounts for parallax)."""
    p = prog(t, t0, dur)
    if t < t0:
        return
    e = MOVE(p)
    put(f, spr, cx, cy + drift * e, 1 + amount * e, min(1, (t - t0) / 0.12))


def split_reveal(f, t, spr, cx, cy, t0, text="your name", size=96, col=(255, 255, 255), rtl=False, font=None,
                 gap=None, dur=0.45):
    """Ending: the name parts in the middle, fades back, and the logo (spr) pops into the gap."""
    w = _word(text, size, col, rtl, font)
    half = w.width // 2
    left, right = w.crop((0, 0, half, w.height)), w.crop((half, 0, w.width, w.height))
    gap = gap or int(spr.width * 1.7)
    p = prog(t, t0, dur)
    e = ENTER(p)
    a = 1 - 0.55 * e
    put(f, left, cx - half / 2 - gap / 2 * e, cy, 1, a)
    put(f, right, cx + (w.width - half) / 2 + gap / 2 * e, cy, 1, a)
    q = prog(t, t0 + dur * 0.5, 0.42)
    if q > 0:
        s = 0.6 + 0.48 * ENTER(min(1, q / 0.6)) if q < 0.6 else 1.08 - 0.08 * MOVE((q - 0.6) / 0.4)
        put(f, spr, cx, cy, s, min(1, q * 3))


# name → (function, what it looks like, best for, length in seconds)
MOVES = {
    "pop_in":      (pop_in,      "Scales 0.96 → 1.03 → 1.0 while fading in",     "headlines, CTA",               0.42),
    "slide_in":    (slide_in,    "Enters from a side on the ENTER curve",         "chips, cards, alternating text", 0.30),
    "slide_out":   (slide_out,   "Leaves to a side on the EXIT curve",            "clearing a scene",             0.20),
    "spring_drop": (spring_drop, "Falls in and settles with a small bounce",      "balls, stickers, badges",      0.90),
    "slap_in":     (slap_in,     "Lands big and rotated, snaps flat",             "paper stickers, labels",       0.32),
    "fold_open":   (fold_open,   "Unfolds like a paper card",                     "cards, photos, notes",         0.67),
    "ghost_words": (ghost_words, "Words land one by one, blurred ghost → sharp",  "hooks, quotes, punch lines",   1.20),
    "marquee_word": (marquee_word, "Giant word slides edge to edge behind",      "backgrounds behind a cut-out", 0.30),
    "push_in":     (push_in,     "Slow camera push with a small drift",           "every poster scene, parallax", 3.00),
    "split_reveal": (split_reveal, "Name splits open, logo pops into the gap",    "endings, brand reveal",        0.70),
}
