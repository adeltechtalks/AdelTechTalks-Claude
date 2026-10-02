import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # skill root, so the engine package is importable
from engine import config
import importlib.util
import numpy as np, wave
import engine.sfxlib as L

# timeline comes from the template, so SFX follow any story edits
_spec = importlib.util.spec_from_file_location("style_g", Path(__file__).resolve().parents[1] / "templates/core/style_g_editorial_poster.py")
G = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(G)

L.mix = np.zeros((int(L.SR * G.DUR), 2), np.float32)
from engine.sfxlib import *
def add2(t, x, g=1.0, pan=0.0):
    i = int(t * L.SR); x = x[:max(0, len(L.mix) - i)]; l, r = np.sqrt(0.5 * (1 - pan)), np.sqrt(0.5 * (1 + pan))
    L.mix[i:i + len(x), 0] += x * g * l * 1.41; L.mix[i:i + len(x), 1] += x * g * r * 1.41
def ting(f=3200, sec=0.5):
    n = int(SR * sec); t = np.arange(n) / SR; x = np.zeros(n)
    for m, a in ((1, 1), (2.76, 0.4), (5.4, 0.2)): x += a * np.sin(2 * np.pi * f * m * t) * np.exp(-t / (0.12 / m))
    return norm(x, 0.35)
def snap():  # hard cut: short bright noise burst over a low thump
    n = int(SR * 0.16); t = np.arange(n) / SR
    burst = hp(rng.standard_normal(n), 1800) * np.exp(-t / 0.018)
    body = thud(70, 0.16)[:n]
    return norm(burst, 0.5) + norm(np.pad(body, (0, n - len(body))), 0.5)

L.use_library(globals())   # library sounds where we have them (engine/sfx_library.py), synth otherwise
add2(0.0, whoosh(0.35, 500, 5000), 0.5)
for t, kind in G.events():
    if kind == "cut": add2(t - 0.12, whoosh(0.14, 1500, 9000), 0.35); add2(t, snap(), 0.9)
    elif kind == "word": add2(t, tick(2600), 0.32, pan=-0.2)
    elif kind == "word_big": add2(t, tick(1900), 0.45); add2(t + 0.02, thud(95, 0.12), 0.45)
    elif kind == "split": add2(t, whoosh(0.4, 300, 3000), 0.7); add2(t + 0.25, pop(), 0.9)
    elif kind == "follow": add2(t, pop(), 0.8)
    elif kind == "tap": add2(t, tick(1500), 1.2); add2(t + 0.12, ting(2600), 0.7); add2(t + 0.2, ting(3500), 0.5)
m = L.mix / np.abs(L.mix).max() * 0.85
with wave.open(config.work('sfx_ep.wav'), 'wb') as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(L.SR); w.writeframes((m * 32767).astype(np.int16).tobytes())
print('ok')
