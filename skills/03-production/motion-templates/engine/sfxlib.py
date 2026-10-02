import numpy as np
from scipy.signal import butter, sosfilt
import subprocess, wave

SR = 48000; DUR = 17.0
rng = np.random.default_rng(42)
mix = np.zeros((int(SR * DUR), 2), np.float32)

def bp(x, lo, hi, order=2):
    return sosfilt(butter(order, [lo, hi], 'bandpass', fs=SR, output='sos'), x)
def hp(x, f): return sosfilt(butter(2, f, 'highpass', fs=SR, output='sos'), x)
def lp(x, f): return sosfilt(butter(2, f, 'lowpass', fs=SR, output='sos'), x)
def env(n, a, d):  # attack/decay in seconds, exponential decay
    t = np.arange(n) / SR
    e = np.minimum(1, t / max(a, 1e-4)) * np.exp(-np.maximum(0, t - a) / d)
    return e
def noise(sec): return rng.standard_normal(int(SR * sec))
def norm(x, peak): return x / (np.abs(x).max() + 1e-9) * peak

def add(t, x, gain=1.0, pan=0.0):
    i = int(t * SR); x = x[: max(0, len(mix) - i)]
    l, r = np.sqrt(0.5 * (1 - pan)), np.sqrt(0.5 * (1 + pan))
    mix[i:i + len(x), 0] += x * gain * l * 1.41
    mix[i:i + len(x), 1] += x * gain * r * 1.41

# ---------- sound designs ----------
def crackle(sec, density=180):
    n = int(SR * sec); x = np.zeros(n)
    idx = rng.integers(0, n, int(density * sec)); x[idx] = rng.uniform(-1, 1, len(idx))
    return bp(x, 1800, 9000)

def rustle(sec=0.5, bright=1.0):
    n = int(SR * sec); t = np.linspace(0, 1, n)
    body = bp(noise(sec), 900, 7000) * (0.5 + 0.5 * np.abs(lp(noise(sec), 30)) * 6)
    x = body * 0.6 + crackle(sec) * 1.4 * bright
    shape = np.sin(np.pi * t) ** 0.7
    return norm(x * shape, 0.5)

def whoosh(sec=0.45, f0=400, f1=4000):
    n = int(SR * sec); t = np.linspace(0, 1, n); src = noise(sec); out = np.zeros(n)
    blk = 512
    for s in range(0, n, blk):
        c = f0 * (f1 / f0) ** np.sin(np.pi * t[s] * 0.5)
        seg = src[max(0, s - 2048):s + blk]
        y = bp(seg, max(60, c * 0.5), min(SR / 2 - 100, c * 1.6))
        out[s:s + blk] = y[-len(out[s:s + blk]):]
    shape = np.sin(np.pi * t) ** 1.5
    return norm(out * shape, 0.45)

def thud(f=85, sec=0.18):
    n = int(SR * sec); t = np.arange(n) / SR
    return norm(np.sin(2 * np.pi * f * t * (1 - 0.3 * t / sec)) * env(n, 0.002, 0.05), 0.6)

def slap(big=False):
    sec = 0.22; n = int(SR * sec)
    snap = hp(noise(sec), 1200) * env(n, 0.0008, 0.018)
    body = bp(noise(sec), 300, 2500) * env(n, 0.001, 0.04)
    x = norm(snap, 0.7) + norm(body, 0.35) + thud(110 if big else 140, sec) * (0.9 if big else 0.5)
    return norm(x, 0.85 if big else 0.7)

def land():  # paper card landing on paper
    sec = 0.25; n = int(SR * sec)
    tap = bp(noise(sec), 500, 5000) * env(n, 0.001, 0.03)
    return norm(norm(tap, 0.5) + thud(70, sec) * 0.8 + crackle(sec, 90) * env(n, 0.002, 0.08) * 2, 0.7)

def peel(sec=0.32):
    n = int(SR * sec); t = np.linspace(0, 1, n)
    x = crackle(sec, 900) * (0.3 + t) + bp(noise(sec), 2000, 8000) * 0.25 * t
    return norm(x * np.minimum(1, (1 - t) * 8), 0.55)

def tick(f=2600):  # code character "type" click
    sec = 0.06; n = int(SR * sec); t = np.arange(n) / SR
    c = hp(noise(sec), 3000) * env(n, 0.0003, 0.004)
    tone = np.sin(2 * np.pi * f * t) * env(n, 0.0005, 0.012)
    low = np.sin(2 * np.pi * 180 * t) * env(n, 0.001, 0.015)
    return norm(c * 0.8 + tone * 0.5 + low * 0.5, 0.6)

def pop():
    sec = 0.14; n = int(SR * sec); t = np.arange(n) / SR
    f = 900 * np.exp(-t * 18) + 220
    ph = 2 * np.pi * np.cumsum(f) / SR
    return norm(np.sin(ph) * env(n, 0.001, 0.045) + hp(noise(sec), 2000) * env(n, 0.0005, 0.005) * 0.6, 0.7)

def sparkle(sec=0.6):
    n = int(SR * sec); x = np.zeros(n); t = np.arange(n) / SR
    for j, f in enumerate([2093, 2637, 3136, 4186]):
        s = int(j * 0.045 * SR); tt = t[: n - s]
        x[s:] += np.sin(2 * np.pi * f * tt) * np.exp(-tt / 0.18) * 0.5
    return norm(x, 0.3)

def riser(sec=2.3):
    n = int(SR * sec); t = np.linspace(0, 1, n); src = noise(sec); out = np.zeros(n); blk = 1024
    for s in range(0, n, blk):
        c = 300 * (20 ** t[s]); seg = src[max(0, s - 4096):s + blk]
        y = bp(seg, c * 0.6, min(SR / 2 - 100, c * 1.4)); out[s:s + blk] = y[-len(out[s:s + blk]):]
    return norm(out * t ** 2.2, 0.28)



# ---------- library sounds (engine/sfx_library.py) ----------
# MT_SFX = mix (default: library sound when it has that kind, else synth) · synth · library
# MT_SFX_SEED picks the palette: every video gets a different set unless you repeat the seed.
import json as _json, os as _os, random as _random
from pathlib import Path as _Path

MODE = _os.environ.get("MT_SFX", "mix")
SEED = int(_os.environ.get("MT_SFX_SEED") or _random.randrange(10 ** 6))
_LIB = _Path(_os.environ.get("MT_SFX_LIB", _Path(__file__).resolve().parents[1] / "sfx" / "library"))
_STARTER = _Path(__file__).resolve().parents[1] / "sfx" / "starter"      # CC0 pack that ships with the skill
_PAL, _TURN, _CACHE = None, {}, {}


def _palette(per_kind=3):
    """Up to `per_kind` library sounds per kind, chosen by SEED."""
    global _PAL
    if _PAL is None:
        _PAL = {}
        by = {}
        if MODE != "synth":
            for root in (_LIB, _STARTER):
                ix = root / "index.json"
                if ix.exists():
                    for e in _json.loads(ix.read_text()):
                        by.setdefault(e["kind"], []).append(dict(e, path=str(root / e["file"])))
        if by:
            r = _random.Random(SEED)
            for k, es in by.items():
                r.shuffle(es); _PAL[k] = es[:per_kind]
            if _PAL:
                print(f"[sfx] library palette seed {SEED} (MT_SFX_SEED={SEED} repeats it): "
                      + ", ".join(f"{k} {len(v)}" for k, v in sorted(_PAL.items())))
    return _PAL


def _read(path):
    if path not in _CACHE:
        with wave.open(str(path)) as w:
            x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
            if w.getframerate() != SR:
                x = np.interp(np.arange(0, len(x), w.getframerate() / SR), np.arange(len(x)), x).astype(np.float32)
        _CACHE[path] = x
    return _CACHE[path]


def S(kind, synth=None):
    """A `kind` sound for this video: the next one from the library palette (round-robin, so repeats vary),
    matched to the synthesized sound's level — or the synthesized sound when the library has none."""
    pal = _palette().get(kind)
    ref = synth() if synth else None
    if not pal or MODE == "synth":
        return ref
    i = _TURN.get(kind, 0); _TURN[kind] = i + 1
    x = _read(pal[i % len(pal)]["path"])
    peak = float(np.abs(ref).max()) if ref is not None and len(ref) else 0.6
    return x * (peak / (float(np.abs(x).max()) + 1e-9))


def use_library(ns):
    """Make a SFX script library-aware: rebinds whoosh/thud/tick/pop/riser (and ting if defined) in its globals."""
    kinds = {"whoosh": "whoosh", "thud": "hit", "tick": "click", "pop": "pop", "riser": "riser", "ting": "ding"}
    for name, kind in kinds.items():
        fn = ns.get(name)
        if callable(fn):
            ns[name] = (lambda f, k: (lambda *a, **kw: S(k, lambda: f(*a, **kw))))(fn, kind)
