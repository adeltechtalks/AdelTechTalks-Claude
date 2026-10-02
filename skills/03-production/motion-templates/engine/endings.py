"""Shared endings. name_logo_follow: the name parts, the logo pops into the gap, a Follow button
in the brand CTA colour is tapped → "Following", then the comment line lands word by word.

    name_logo_follow(f, t, start, bg=(8, 8, 10), ink=(255, 255, 255))   # bg=None darkens the frame already in f
    TIMES = offsets (from start) of the split, follow and tap — use them for SFX.
"""
from PIL import Image

from engine import config
from engine.moves import ghost_words, pop_in, split_reveal
from engine.plib import READ, fit, put, rrect, txt

TIMES = {"split": 0.5, "follow": 1.7, "tap": 2.5}
_C = {}


def _logo(ink):
    if ("logo", ink) not in _C:
        lg = fit(config.logo(), h=150)
        im = Image.new("RGBA", lg.size, ink + (255,)); im.putalpha(lg.split()[3])
        _C[("logo", ink)] = im
    return _C[("logo", ink)]


def _pill(label, fill, col, rtl):
    k = ("pill", label, fill, col)
    if k not in _C:
        t_ = txt(label, READ(44, 700), col, rtl=rtl)
        p = rrect(t_.width + 110, t_.height + 54, (t_.height + 54) // 2, fill + (255,))
        p.alpha_composite(t_, (55, 27))
        _C[k] = p
    return _C[k]


def name_logo_follow(f, t, start, bg=(8, 8, 10), ink=(255, 255, 255), muted=(200, 200, 204), cy=820):
    b = config.brand(); e = b["ending"]; rtl = b["language"].startswith("ar")
    W, H = f.size
    if bg is None:   # keep what's on screen, darkened (draw the last scene into f first)
        f.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, int(200 * min(1, (t - start) / 0.4)))))
        bg = (30, 30, 32)
    else:
        f.paste(bg + (255,), (0, 0, W, H))
    split_reveal(f, t, _logo(ink), W // 2, cy, start + TIMES["split"], text=b["name"], size=84, col=ink)
    fa, ta = start + TIMES["follow"], start + TIMES["tap"]
    if t >= fa:
        pill = _pill(e["following"], tuple(int(c * 0.25 + v * 0.75) for c, v in zip(ink, bg)), ink, rtl) if t >= ta \
            else _pill(e["follow"], config.color("cta"), (255, 255, 255), rtl)
        if t < fa + 0.42:
            pop_in(f, t, pill, W // 2, cy + 220, fa)
        else:
            put(f, pill, W // 2, cy + 220, 0.94 if ta <= t < ta + 0.12 else 1)
    if t >= fa + 1.2:
        lines = ((f"{e['comment_before']} {e['comment_keyword']} {e['comment_after']}", 50), (e["comment_promise"], 38))
        ghost_words(f, t, None, W // 2, cy + 380, fa + 1.2, lines=lines, col=muted, rtl=rtl, align="center", gap=0.12, lead=1.0)
