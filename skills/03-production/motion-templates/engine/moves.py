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

from engine.plib import ENTER, EXIT, MOVE, SH, fold_in, preshadow, prog, put, slap


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


# name → (function, what it looks like, best for, length in seconds)
MOVES = {
    "pop_in":      (pop_in,      "Scales 0.96 → 1.03 → 1.0 while fading in",     "headlines, CTA",               0.42),
    "slide_in":    (slide_in,    "Enters from a side on the ENTER curve",         "chips, cards, alternating text", 0.30),
    "slide_out":   (slide_out,   "Leaves to a side on the EXIT curve",            "clearing a scene",             0.20),
    "spring_drop": (spring_drop, "Falls in and settles with a small bounce",      "balls, stickers, badges",      0.90),
    "slap_in":     (slap_in,     "Lands big and rotated, snaps flat",             "paper stickers, labels",       0.32),
    "fold_open":   (fold_open,   "Unfolds like a paper card",                     "cards, photos, notes",         0.67),
}
