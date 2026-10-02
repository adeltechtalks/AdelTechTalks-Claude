import numpy as np, wave
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # skill root, so the engine package is importable
from engine import config
from scipy.signal import butter, sosfilt, fftconvolve

SR = 48000; DUR = 30.0; BPM = 120; BEAT = 60 / BPM; N = int(SR * DUR)
rng = np.random.default_rng(7)
def lp(x, f, o=2): return sosfilt(butter(o, f, 'lowpass', fs=SR, output='sos'), x)
def hp(x, f, o=2): return sosfilt(butter(o, f, 'highpass', fs=SR, output='sos'), x)
def bp(x, a, b): return sosfilt(butter(2, [a, b], 'bandpass', fs=SR, output='sos'), x)
def midi(n): return 440 * 2 ** ((n - 69) / 12)
def place(buf, t, x, g=1.0):
    i = int(t * SR); x = x[:max(0, len(buf) - i)]; buf[i:i + len(x)] += x * g

# chords: Fmaj7 – Em7 – Dm7 – Cmaj7 (one per bar, 2s)
CH = [[53, 57, 60, 64], [52, 55, 59, 62], [50, 53, 57, 60], [48, 52, 55, 59]]
BASS = [41, 40, 38, 36]

pad = np.zeros(N); pluck = np.zeros(N); bass = np.zeros(N); kick = np.zeros(N); clap = np.zeros(N); hat = np.zeros(N)

def pad_note(f, sec):
    t = np.arange(int(SR * sec)) / SR; x = np.zeros_like(t)
    for d in (-0.12, 0.0, 0.11):
        ph = 2 * np.pi * f * (1 + d / 100) * t
        x += np.sin(ph) + 0.35 * np.sin(2 * ph) + 0.15 * np.sin(3 * ph)
    a = np.minimum(1, t / 0.35) * np.minimum(1, (sec - t) / 0.5)
    return x * np.clip(a, 0, 1)

def pluck_note(f):
    sec = 0.6; t = np.arange(int(SR * sec)) / SR
    x = (np.sin(2 * np.pi * f * t) + 0.3 * np.sin(4 * np.pi * f * t)) * np.exp(-t / 0.18)
    return x * np.minimum(1, t / 0.004)

def kick_s():
    sec = 0.35; t = np.arange(int(SR * sec)) / SR
    f = 45 + 80 * np.exp(-t * 30); return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.12)
def clap_s():
    sec = 0.25; n = int(SR * sec); t = np.arange(n) / SR
    return bp(rng.standard_normal(n), 900, 4000) * np.exp(-t / 0.07)
def hat_s(open_=False):
    sec = 0.12 if not open_ else 0.25; n = int(SR * sec); t = np.arange(n) / SR
    return hp(rng.standard_normal(n), 7000) * np.exp(-t / (0.02 if not open_ else 0.08))
def bass_note(f, sec):
    t = np.arange(int(SR * sec)) / SR
    x = np.sin(2 * np.pi * f * t) + 0.25 * np.sin(4 * np.pi * f * t)
    return lp(x, 400) * np.minimum(1, t / 0.01) * np.exp(-t / 0.6)

bars = int(DUR / (4 * BEAT))
for b in range(bars):
    t0 = b * 4 * BEAT; ch = CH[b % 4]
    final = t0 >= 26.0
    sec = 4 * BEAT + (2.0 if final else 0.3)
    for n in ch: place(pad, t0, pad_note(midi(n), sec), 0.12)
    # arpeggio 8ths (sparse in intro, doubled octave in the 'result' section)
    if not final:
        pattern = [0, 2, 1, 3, 2, 1, 3, 2]
        for k, idx in enumerate(pattern):
            if t0 < 4 and k % 2: continue
            place(pluck, t0 + k * BEAT / 2, pluck_note(midi(ch[idx] + 12)), 0.22)
            if 19 <= t0 < 27 and k % 2 == 0: place(pluck, t0 + k * BEAT / 2, pluck_note(midi(ch[idx] + 24)), 0.08)
    drums = 4.0 <= t0 < 26.0
    for k in range(8):
        tt = t0 + k * BEAT / 2 + (0.03 if k % 2 else 0)        # light swing
        if 18.5 <= tt < 19.0 or final: continue                 # break before the result reveal
        place(hat, tt, hat_s(open_=(k == 7)), 0.10 if drums else 0.05)
    if drums:
        for k in range(4):
            tt = t0 + k * BEAT
            if 18.5 <= tt < 19.0: continue
            if k in (0, 2) or (k == 3 and b % 2): place(kick, tt + (BEAT / 2 if k == 3 else 0), kick_s(), 0.75)
            if k in (1, 3): place(clap, tt, clap_s(), 0.22)
        place(bass, t0, bass_note(midi(BASS[b % 4]), 1.6), 0.5)
        place(bass, t0 + 2.5 * BEAT, bass_note(midi(BASS[b % 4]), 0.9), 0.35)

# sidechain-ish pump on pad from kick envelope
env = np.abs(kick); env = lp(env, 12, 1); env = env / (env.max() + 1e-9)
pad = pad * (1 - 0.45 * env)
# intro filter sweep on pad + pluck
sweep = np.clip(np.arange(N) / (SR * 4.0), 0, 1)
pad = lp(pad, 1400); pluck = lp(pluck, 3500)
pad = pad * (0.5 + 0.5 * sweep); pluck = pluck * (0.6 + 0.4 * sweep)
# small room reverb on pluck + clap
ir = rng.standard_normal(int(SR * 0.9)) * np.exp(-np.arange(int(SR * 0.9)) / (SR * 0.22)); ir /= np.abs(ir).sum() / 6
wet = fftconvolve(pluck + clap * 0.5, ir)[:N] * 0.25
music = pad + pluck + bass + kick + clap + hat + wet
# outro fade
music *= np.clip((DUR - np.arange(N) / SR) / 2.5, 0, 1) ** 0.7
music = music / np.abs(music).max()

# stereo widen pluck/hat slightly
L = music + 0.04 * np.roll(pluck + hat, 240); R = music - 0.04 * np.roll(pluck + hat, 240)
mus = np.stack([L, R], 1); mus /= np.abs(mus).max()

def read(p):
    w = wave.open(p); x = np.frombuffer(w.readframes(w.getnframes()), np.int16).reshape(-1, 2).astype(np.float32) / 32768; return x
sfx = read(config.work('sfx_ui2.wav'))[:N]
if len(sfx) < N: sfx = np.vstack([sfx, np.zeros((N - len(sfx), 2), np.float32)])
# duck music under SFX hits
se = lp(np.abs(sfx).mean(1), 8, 1); se = se / (se.max() + 1e-9)
duck = 1 - 0.35 * np.clip(se * 3, 0, 1)
MUS_GAIN = 0.30                                   # music sits well under SFX (and under a future voiceover)
out = sfx + mus * MUS_GAIN * duck[:, None]
out = out / np.abs(out).max() * 0.85
for name, arr in ((config.work('ui_mix.wav'), out), (config.work('ui_music_only.wav'), mus * 0.85)):
    with wave.open(name, 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((arr * 32767).astype(np.int16).tobytes())
print('ok')
