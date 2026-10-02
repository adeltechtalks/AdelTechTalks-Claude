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


def _word(w, size, col, rtl, font, shadow=False):
    k = (w, size, col, rtl, font, shadow)
    if k not in _CACHE:
        # fixed-height box drawn on the baseline, so words of one line always line up
        ft = (font or (CAIRO if rtl else MONT))(size)
        kw = dict(direction="rtl", language="ar") if rtl else {}
        d = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
        x0, _, x1, _ = d.textbbox((0, 0), w, font=ft, anchor="ls", **kw)
        im = Image.new("RGBA", (int(x1 - x0) + 16, int(size * 1.5)), (0, 0, 0, 0))
        ImageDraw.Draw(im).text((8 - x0, int(size * 1.08)), w, font=ft, fill=col, anchor="ls", **kw)
        if shadow:  # soft drop shadow under big display words
            pad = int(size * 0.16)  # shadow falls right/down, so only those sides grow
            sh = Image.new("RGBA", (im.width + pad, im.height + pad), (0, 0, 0, 0))
            a = im.split()[3].point(lambda v: int(v * 0.35))
            sh.paste((0, 0, 0, 255), (int(size * 0.04), int(size * 0.07)), a)
            sh = sh.filter(ImageFilter.GaussianBlur(size * 0.05))
            sh.alpha_composite(im, (0, 0))
            im = sh
        _CACHE[k] = im
    return _CACHE[k]


def ghost_words(f, t, spr, cx, cy, t0, lines=(("one idea", 64), ("at a time", 120)), gap=0.26,
                col=(255, 255, 255), rtl=False, align="left", font=None, lead=0.78, shadow=False):
    """Words land one by one: each appears as a big blurred ghost, then sharpens into place.

    lines   [(text, size), …] — a small set-up line over a big punch line works best
    cx, cy  left edge (align='left', or right edge for rtl) / centre (align='center') and top of the block
    spr     unused (pass None) — the words are drawn from the brand fonts
    """
    k = 0
    y = cy
    for text, size in lines:
        words = [_word(w, size, col, rtl, font, shadow) for w in text.split()]
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


def motion_blur(im, amount, axis="y"):
    """Directional blur by squashing then stretching along one axis (fast, looks like a camera smear)."""
    k = max(1, int(amount))
    if k <= 1:
        return im
    w, h = im.size
    small = im.resize((w, max(1, h // k)) if axis == "y" else (max(1, w // k), h), Image.BILINEAR)
    return small.resize((w, h), Image.BILINEAR)


def whip(f_out, f_in, p, direction="up", blur=26):
    """Whip-pan transition between two full frames (p 0→1). Both frames slide with a strong
    motion smear peaking mid-way. Returns the mixed frame."""
    W, H = f_out.size
    e = MOVE(p)
    axis = "y" if direction in ("up", "down") else "x"
    span = H if axis == "y" else W
    sgn = -1 if direction in ("up", "left") else 1
    amt = 1 + blur * math.sin(math.pi * p)
    out = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    a = motion_blur(f_out, amt, axis); b = motion_blur(f_in, amt, axis)
    d_out = int(sgn * span * e); d_in = int(sgn * span * (e - 1))
    if axis == "y":
        out.paste(a, (0, d_out)); out.paste(b, (0, d_in))
    else:
        out.paste(a, (d_out, 0)); out.paste(b, (d_in, 0))
    return out


def focus_in(f, t, spr, cx, cy, t0, dur=0.5, scale=1.18, blur=14):
    """Focus pull: starts big, soft and faint, settles sharp (titles, objects)."""
    p = prog(t, t0, dur)
    if p <= 0:
        return
    e = ENTER(p)
    im = spr if p >= 1 else spr.filter(ImageFilter.GaussianBlur(blur * (1 - e)))
    put(f, im, cx, cy, scale - (scale - 1) * e, min(1, 0.15 + p * 1.6))


def blur_rise(f, t, spr, cx, cy, t0, dur=0.55, dist=900, side="down"):
    """Flies in from off-screen with a motion smear and a small overshoot (from below, or 'up' = from above)."""
    p = prog(t, t0, dur)
    if p <= 0:
        return
    e = _spring(p, freq=9, damp=7)
    sgn = 1 if side == "down" else -1
    y = cy + sgn * dist * (1 - e)
    sm = 1 + 22 * max(0, 1 - p * 1.8)
    im = spr if sm < 1.5 else motion_blur(spr, sm, "y")
    put(f, im, cx, y, 1, min(1, p * 4))


def orbit_dots(f, t, spr, cx, cy, t0, rings=((300, 4, 0.9), (420, 3, -0.6)), tilt=0.96, col=(23, 26, 31),
               dot=13, line=2):
    """Thin orbit rings around a centre with dots travelling on them; rings grow in, dots get bigger
    on the near side. rings = (radius, dots, speed rad/s). spr is drawn in the centre if given."""
    p = prog(t, t0, 0.5)
    if p <= 0:
        return
    e = ENTER(p)
    d = ImageDraw.Draw(f, "RGBA")
    for r, n, sp in rings:
        rr = r * (0.6 + 0.4 * e)
        a = int(110 * e)
        d.ellipse((cx - rr, cy - rr * tilt, cx + rr, cy + rr * tilt), outline=col + (a,), width=line)
    if spr is not None:
        put(f, spr, cx, cy, 0.85 + 0.15 * e, min(1, p * 3))
    for r, n, sp in rings:
        rr = r * (0.6 + 0.4 * e)
        for k in range(n):
            ang = sp * (t - t0) + k * 2 * math.pi / n + r
            x, y = cx + rr * math.cos(ang), cy + rr * tilt * math.sin(ang)
            s = dot * (0.75 + 0.35 * (math.sin(ang) + 1) / 2) * e
            d.ellipse((x - s, y - s, x + s, y + s), fill=col + (255,))


def roll_in(f, t, spr, cx, cy, t0, dur=0.7, dist=520, side="left", turns=1.0):
    """A round object rolls in and stops (rotation matches the distance travelled)."""
    p = prog(t, t0, dur)
    if p <= 0:
        return
    e = ENTER(p)
    sgn = -1 if side == "left" else 1
    x = cx + sgn * dist * (1 - e)
    put(f, spr, x, cy, 1, min(1, p * 4), rot=sgn * 360 * turns * (1 - e))


def word_turn(f, t, spr, cx, cy, t0, words=("ONE", "TWO"), size=150, col=(160, 220, 40), gap=0.45, rtl=False, font=None):
    """Each new word slams in big at the centre; the previous one turns 90° and parks against its side."""
    k = int((t - t0) // gap) if t >= t0 else -1
    if k < 0:
        return
    k = min(k, len(words) - 1)
    cur = _word(words[k], size, col, rtl, font)
    p = prog(t, t0 + k * gap, 0.22)
    e = ENTER(p)
    im = cur if p >= 1 else motion_blur(cur, 1 + 10 * (1 - e), "x")
    put(f, im, cx, cy, 1.35 - 0.35 * e, min(1, p * 4))
    if k > 0:
        prev = _word(words[k - 1], int(size * 0.55), col, rtl, font).rotate(90, expand=True)
        side = 1 if rtl else -1
        x = cx + side * (cur.width / 2 + prev.width / 2 + 6)
        put(f, prev, x, cy - (prev.height - cur.height) / 2 * 0.0, 1, 1)


def torn_mask(w, h, depth=26, seed=3):
    """Alpha mask with ragged, torn-paper edges (white paper rim included by torn_photo)."""
    import random
    rnd = random.Random(seed)
    pts = []
    for side in range(4):
        n = 26
        for i in range(n):
            a = i / n
            jitter = rnd.uniform(0, depth)
            if side == 0: pts.append((a * w, jitter))
            elif side == 1: pts.append((w - jitter, a * h))
            elif side == 2: pts.append((w - a * w, h - jitter))
            else: pts.append((jitter, h - a * h))
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).polygon(pts, fill=255)
    return m


def torn_photo(photo, w, h, rim=10, seed=3):
    """A photo inside a torn paper hole: ragged edge + thin white paper rim + inner shadow."""
    from PIL import ImageOps
    ph = ImageOps.fit(photo.convert("RGB"), (w, h)).convert("RGBA")
    outer = torn_mask(w, h, 30, seed)
    inner = torn_mask(w, h, 30, seed).filter(ImageFilter.MinFilter(rim * 2 + 1))
    paper = Image.new("RGBA", (w, h), (238, 236, 230, 255)); paper.putalpha(outer)
    ph.putalpha(inner)
    shade = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    shade.paste((0, 0, 0, 120), (0, 0), inner.filter(ImageFilter.GaussianBlur(14)).point(lambda v: 255 - v))
    shade.putalpha(Image.composite(shade.split()[3], Image.new("L", (w, h), 0), inner))
    paper.alpha_composite(ph); paper.alpha_composite(shade)
    return paper


def scribble_strike(f, t, spr, cx, cy, t0, width=700, col=(220, 30, 40), dur=0.45, dash=26, amp=14, thick=8, seed=5):
    """A hand-drawn dashed line strikes through a word from left to right."""
    import random
    p = prog(t, t0, dur)
    if p <= 0:
        return
    rnd = random.Random(seed)
    d = ImageDraw.Draw(f, "RGBA")
    x0 = cx - width / 2; n = int(width // dash)
    ys = [cy + rnd.uniform(-amp, amp) - (i / n - 0.5) * amp * 2 for i in range(n + 1)]
    for i in range(int(n * ENTER(p))):
        if i % 2 == 0:
            d.line((x0 + i * dash, ys[i], x0 + (i + 1) * dash, ys[i + 1]), fill=col + (255,), width=thick)


def echo_rows(f, t, spr, cx, cy, t0, word="NOBODY", size=150, col=(255, 255, 255), rows=3, alpha=0.22, speed=90,
              rtl=False, font=None):
    """Rows of a repeated word, each fainter and offset, drifting sideways (a visual echo)."""
    p = prog(t, t0, 0.3)
    if p <= 0:
        return
    w = _word(word + " ", size, col, rtl, font)
    W = f.width
    for r in range(rows):
        a = alpha * (1 - r * 0.25) * p
        off = ((t - t0) * speed * (1 if r % 2 else -1) + r * w.width / 3) % w.width
        x = off - w.width
        im = w.filter(ImageFilter.GaussianBlur(r * 1.5)) if r else w
        while x < W:
            put(f, im, x + w.width / 2, cy + r * int(size * 0.95), 1, a)
            x += w.width


def glow_underline(f, t, spr, cx, cy, t0, width=420, col=(160, 230, 40), dur=0.4, thick=7):
    """A hand-drawn underline that draws on with a soft glow."""
    p = prog(t, t0, dur)
    if p <= 0:
        return
    e = ENTER(p)
    lay = Image.new("RGBA", f.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    pts = [(cx - width / 2 + width * i / 40, cy + 6 * math.sin(i / 40 * math.pi) - 4 * i / 40) for i in range(int(40 * e) + 1)]
    if len(pts) > 1:
        d.line(pts, fill=col + (255,), width=thick, joint="curve")
        glow = lay.filter(ImageFilter.GaussianBlur(10))
        f.alpha_composite(glow); f.alpha_composite(glow); f.alpha_composite(lay)


def sunburst(f, t, spr, cx, cy, t0, rays=7, col=(240, 205, 20), r0=260, spin=0.35, width=0.32, grow=0.45):
    """Thick rays rotating behind a disc (spr drawn in the centre if given)."""
    p = prog(t, t0, grow)
    if p <= 0:
        return
    e = ENTER(p)
    R = 2600 * e
    d = ImageDraw.Draw(f)
    a0 = spin * (t - t0)
    for k in range(rays):
        a = a0 + k * 2 * math.pi / rays
        d.polygon([(cx, cy), (cx + R * math.cos(a - width / 2), cy + R * math.sin(a - width / 2)),
                   (cx + R * math.cos(a + width / 2), cy + R * math.sin(a + width / 2))], fill=col + (255,))
    rr = r0 * e
    d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), fill=col + (255,))
    if spr is not None:
        put(f, spr, cx, cy, e, min(1, p * 2))


def clock_face(f, t, spr, cx, cy, t0, r=250, col=(240, 205, 20), ink=(60, 50, 10), speed=6.0, dur=0.4):
    """A clock grows in and its hands race (time passing)."""
    p = prog(t, t0, dur)
    if p <= 0:
        return
    rr = r * ENTER(p)
    d = ImageDraw.Draw(f)
    d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), fill=col + (255,), outline=ink + (255,), width=6)
    for k in range(12):
        a = k * math.pi / 6
        d.line((cx + rr * 0.82 * math.cos(a), cy + rr * 0.82 * math.sin(a), cx + rr * 0.92 * math.cos(a), cy + rr * 0.92 * math.sin(a)),
               fill=ink + (255,), width=5)
    am = (t - t0) * speed - math.pi / 2; ah = am / 12 - math.pi / 3
    d.line((cx, cy, cx + rr * 0.75 * math.cos(am), cy + rr * 0.75 * math.sin(am)), fill=ink + (255,), width=8)
    d.line((cx, cy, cx + rr * 0.5 * math.cos(ah), cy + rr * 0.5 * math.sin(ah)), fill=ink + (255,), width=12)
    d.ellipse((cx - 12, cy - 12, cx + 12, cy + 12), fill=ink + (255,))


def count_up(f, t, spr, cx, cy, t0, start=0, end=100, dur=0.8, size=220, col=(255, 255, 255), fmt="{}", font=None):
    """A number rolls up to its value and lands with a tiny pop."""
    p = prog(t, t0, dur)
    if p <= 0:
        return
    v = int(start + (end - start) * ENTER(p))
    im = _word(fmt.format(v), size, col, False, font)
    s = 1.0 + 0.06 * math.sin(math.pi * min(1, max(0, (t - t0 - dur) / 0.2))) if t > t0 + dur else 1.0
    put(f, im, cx, cy, s, min(1, p * 4))


def fan_out(f, t, spr, cx, cy, t0, n=7, spread=70, dur=0.5, pivot=0.9):
    """Copies of a sprite fan open around a pivot near their bottom (cards, notes, tickets)."""
    p = prog(t, t0, dur)
    if p <= 0:
        return
    e = ENTER(p)
    for k in range(n):
        a = (k - (n - 1) / 2) / max(1, (n - 1) / 2) * spread / 2 * e
        im = spr.rotate(-a, Image.BICUBIC, expand=True)
        # rotate around a point near the bottom of the sprite
        dy = spr.height * (pivot - 0.5)
        ox = dy * math.sin(math.radians(a)); oy = dy * (1 - math.cos(math.radians(a)))
        put(f, im, cx + ox, cy + oy, 1, min(1, p * 3))


def desaturate(im, amount):
    """Fade an RGBA frame toward black & white (0 = colour, 1 = grey)."""
    if amount <= 0:
        return im
    g = im.convert("L").convert("RGBA")
    return Image.blend(im, g, min(1, amount))


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
    "focus_in":    (focus_in,    "Focus pull: big, soft and faint → sharp",       "titles, objects",              0.50),
    "blur_rise":   (blur_rise,   "Flies in from off-screen with a motion smear",  "objects entering a stage",     0.55),
    "orbit_dots":  (orbit_dots,  "Orbit rings grow in, dots travel around",       "a central object or icon",     0.50),
    "roll_in":     (roll_in,     "Rolls in and stops, spin matches the distance", "balls, eyes, coins, wheels",   0.70),
}
MOVES.update({
    "word_turn":   (word_turn,   "New word slams in; the previous one turns 90° and parks beside it", "numbers, two-word hooks", 0.45),
    "scribble_strike": (scribble_strike, "Hand-drawn dashed line strikes through a word", "corrections, 'not this'", 0.45),
    "echo_rows":   (echo_rows,   "Rows of a repeated word fading and drifting, like an echo", "dark backgrounds, emphasis", 0.30),
    "glow_underline": (glow_underline, "Hand-drawn underline draws on with a glow", "the key phrase of a line", 0.40),
    "sunburst":    (sunburst,    "Thick rays spin behind a disc", "a big idea, a reveal", 0.45),
    "clock_face":  (clock_face,  "A clock grows in, hands race", "time passing, deadlines", 0.40),
    "count_up":    (count_up,    "A number rolls up and lands with a pop", "years, prices, stats", 0.80),
    "fan_out":     (fan_out,     "Copies fan open around a pivot", "cards, notes, tickets, cash", 0.50),
})
# helpers: torn_photo(photo, w, h) for a torn-paper hole · desaturate(frame, amount) · motion_blur(img, amount, axis)
# transitions work on two whole frames: whip(f_out, f_in, p, direction) — see templates/core/style_h_studio_stage.py
