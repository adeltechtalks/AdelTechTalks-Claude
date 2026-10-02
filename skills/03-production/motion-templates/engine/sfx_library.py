"""SFX library — collect sounds so every video doesn't use the same clicks.

    python engine/sfx_library.py harvest reference.mp4 [--max 40]   # pull SFX out of a reel you like
    python engine/sfx_library.py download "whoosh" [--n 6] [--kind whoosh]   # free CC0 / CC BY sounds (Openverse)
    python engine/sfx_library.py import ~/my-sfx-pack/              # your own pack (wav/mp3/ogg/aif)
    python engine/sfx_library.py list                               # what's in the library, by kind
    python engine/sfx_library.py sheet                              # waveform sheet + audition.wav to listen
    python engine/sfx_library.py remove <id> [<id> …]               # drop sounds you don't like
    python engine/sfx_library.py reclassify                         # re-sort after the classifier improves
    python engine/sfx_library.py starter                            # (maintainers) CC0 downloads → sfx/starter/

Every sound is trimmed, faded, normalised and sorted into a kind:
    click · pop · hit · whoosh · riser · ding · other
The style SFX scripts draw a different palette for each video from your library plus the CC0 starter
pack that ships in sfx/starter/ (see sfxlib.S),
falling back to the synthesized sounds for any kind the library doesn't have.

Harvest separates the percussive part of the mix from the music (harmonic/percussive split), finds
each hit, and cuts it out — sounds sitting on top of loud music come out less clean; listen to the
audition and remove the bad ones. Harvested sounds come from someone else's video: they stay in your
local library (sfx/library/, git-ignored, never shipped) for your own use. Downloads keep their
licence and author in the index — credit CC BY sounds in your caption.
"""
import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # skill root, so the engine package is importable
import numpy as np
from scipy.ndimage import median_filter
from scipy.signal import find_peaks, istft, stft

ROOT = Path(__file__).resolve().parents[1]
LIB = Path(__import__("os").environ.get("MT_SFX_LIB", ROOT / "sfx" / "library"))
INDEX = LIB / "index.json"
SR = 48000
KINDS = ("click", "pop", "hit", "whoosh", "riser", "ding", "other")


# ---------- io ----------
def ffmpeg():
    return shutil.which("ffmpeg") or sys.exit("ffmpeg not found")


def load(path, start=None, dur=None):
    cmd = [ffmpeg(), "-loglevel", "error"] + (["-ss", str(start)] if start else []) + ["-i", str(path)]
    cmd += (["-t", str(dur)] if dur else []) + ["-vn", "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"]
    return np.frombuffer(subprocess.run(cmd, capture_output=True, check=True).stdout, np.float32).copy()


def save(path, x):
    import wave
    x = np.clip(x, -1, 1)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((x * 32767).astype(np.int16).tobytes())


def index():
    return json.loads(INDEX.read_text()) if INDEX.exists() else []


def write_index(ix):
    LIB.mkdir(parents=True, exist_ok=True)
    INDEX.write_text(json.dumps(ix, indent=1, ensure_ascii=False))


# ---------- shaping + classifying ----------
def tidy(x, max_len=2.0):
    """Trim silence, cap the length, fade the edges, normalise to -1 dBFS."""
    if len(x) == 0:
        return x
    env = np.abs(x)
    pk = env.max() or 1
    on = np.where(env > pk * 0.02)[0]
    if len(on) == 0:
        return x[:0]
    a, b = max(0, on[0] - int(0.004 * SR)), on[-1] + int(0.01 * SR)
    x = x[a:min(b, a + int(max_len * SR))].astype(np.float32)
    n_in, n_out = min(len(x), int(0.004 * SR)), min(len(x), int(0.03 * SR))
    x[:n_in] *= np.linspace(0, 1, n_in); x[-n_out:] *= np.linspace(1, 0, n_out)
    return x / (np.abs(x).max() + 1e-9) * 0.89


def features(x):
    n = min(2048, max(256, len(x) // 2))
    f, _t, Z = stft(x, SR, nperseg=n, noverlap=n * 3 // 4)
    M0 = np.abs(Z)
    energy = (M0 ** 2).sum(0) + 1e-12           # weights come from the real energy only
    cent = (f[:, None] * M0).sum(0) / (M0.sum(0) + 1e-12)
    band = (f > 150) & (f < 12000)
    Mb = M0[band] + M0.max() * 1e-5 + 1e-12     # tiny floor so near-silent bins don't dominate flatness
    flat = np.exp(np.log(Mb).mean(0)) / Mb.mean(0)
    M = M0 + 1e-12
    w = energy / (energy.sum() + 1e-9)
    low = M[f < 200].sum() / M.sum()
    peak_i = int(np.argmax(np.abs(x)))
    k = max(1, len(cent) // 3)
    return dict(dur=len(x) / SR, centroid=float((cent * w).sum()), flatness=float((flat * w).sum()), low=float(low),
                attack=peak_i / SR, slope=float(cent[-k:].mean() - cent[:k].mean()) if len(cent) > 2 else 0.0)


def classify(x):
    """Sort by shape: whooshes build up, hits/clicks/pops start instantly, dings ring on one pitch."""
    ft = features(x)
    d, c, fl, low, att = ft["dur"], ft["centroid"], ft["flatness"], ft["low"], ft["attack"]
    sharp = att < 0.03
    if d < 0.14 or (d < 0.2 and sharp and c > 2500):
        kind = "click"
    elif fl < 0.03 and d >= 0.2:
        kind = "ding"
    elif low > 0.3 and sharp:
        kind = "hit"
    elif d > 0.9 and ft["slope"] > 300 and att > 0.4 * d:
        kind = "riser"
    elif d >= 0.2 and fl > 0.25 and att > 0.12 * d:
        kind = "whoosh"
    elif sharp and d < 0.4 and fl < 0.25:
        kind = "pop"
    elif sharp:
        kind = "hit"
    else:
        kind = "other"
    return kind, ft


HINTS = [("riser", ("riser", "rise", "build up", "uplifter")), ("whoosh", ("whoosh", "woosh", "swoosh", "swosh", "swipe", "swish")),
         ("hit", ("impact", "hit", "punch", "thud", "boom", "slam")), ("click", ("click", "tick", "tap", "type")),
         ("pop", ("pop", "bubble", "blip")), ("ding", ("ding", "bell", "chime", "notification"))]


def hint(title):
    t = (title or "").lower()
    return next((k for k, words in HINTS if any(w in t for w in words)), None)


def add(x, origin, source, kind=None, **meta):
    x = tidy(x)
    if len(x) < int(0.03 * SR):
        return None
    k, ft = classify(x)
    forced = kind is not None
    kind = kind or hint(meta.get("title")) or k
    if kind in ("click", "pop", "hit") and len(x) > 0.45 * SR:   # a run of clicks → keep the first one
        x = tidy(x[: int(0.35 * SR)]); ft = features(x)
    sid = hashlib.sha1(x[:: max(1, len(x) // 4000)].tobytes()).hexdigest()[:8]
    ix = index()
    if any(e["id"] == sid for e in ix):
        return None
    (LIB / kind).mkdir(parents=True, exist_ok=True)
    path = LIB / kind / f"{sid}.wav"
    save(path, x)
    ix.append(dict(id=sid, kind=kind, forced=bool(forced), file=str(path.relative_to(LIB)), dur=round(ft["dur"], 3), origin=origin, source=source,
                   **{k_: v for k_, v in meta.items() if v}))
    write_index(ix)
    return ix[-1]


# ---------- harvest ----------
def percussive(x, n=2048):
    """Harmonic/percussive split by median filtering the spectrogram; returns the percussive signal."""
    _f, _t, Z = stft(x, SR, nperseg=n, noverlap=n * 3 // 4)
    M = np.abs(Z)
    H = median_filter(M, size=(1, 31))
    P = median_filter(M, size=(31, 1))
    mask = P ** 3 / (H ** 3 + P ** 3 + 1e-12)
    _t2, y = istft(Z * mask, SR, nperseg=n, noverlap=n * 3 // 4)
    return y[: len(x)].astype(np.float32)


def onsets(y, hop=512):
    n = 1024
    frames = np.lib.stride_tricks.sliding_window_view(np.pad(y, (0, n)), n)[::hop]
    spec = np.abs(np.fft.rfft(frames * np.hanning(n), axis=1))
    flux = np.maximum(0, np.diff(np.log1p(spec * 20), axis=0)).sum(1)
    flux = (flux - flux.mean()) / (flux.std() + 1e-9)
    peaks, _ = find_peaks(flux, height=1.6, distance=int(0.09 * SR / hop))
    return (peaks + 1) * hop / SR, flux[peaks]


def visual_events(video, fps=30):
    """Times of cuts and big moves (frame-difference peaks). SFX in edits sit on these; music beats don't."""
    raw = subprocess.run([ffmpeg(), "-loglevel", "error", "-i", str(video), "-vf", f"fps={fps},scale=64:114,format=gray",
                          "-f", "rawvideo", "-"], capture_output=True).stdout
    fr = np.frombuffer(raw, np.uint8).reshape(-1, 114, 64).astype(np.float32)
    if len(fr) < 3:
        return np.array([])
    d = np.abs(np.diff(fr, axis=0)).mean((1, 2))
    base = median_filter(d, size=15)
    peaks, _ = find_peaks(d - base, height=max(1.5, float(np.std(d - base)) * 1.2), distance=int(0.12 * fps))
    return (peaks + 1) / fps


def harvest(a):
    x = load(a.video)
    if len(x) == 0:
        sys.exit("no audio in that file")
    y = percussive(x)
    times, strength = onsets(y)
    all_times = times.copy()            # every audio hit: a cut ends at the very next one
    vis = visual_events(a.video)
    added, sigs = [], []
    if len(vis) and not a.all:   # keep hits that land on a cut or a big move (±0.1 s); drop the music's own beats
        keep = [i for i, t in enumerate(times) if np.min(np.abs(vis - t)) < 0.1]
        times, strength = times[keep], strength[keep]
        # whooshes lead into cuts: the 0.35 s before each cut, if it is noisy
        for v in vis:
            a0, a1 = int(max(0, v - 0.38) * SR), int((v + 0.08) * SR)
            seg, full = y[a0:a1], x[a0:a1]
            if len(seg) < 0.2 * SR:
                continue
            ft = features(tidy(seg.copy()))
            loud = np.sqrt((seg ** 2).mean()) > 0.3 * np.sqrt((full ** 2).mean() + 1e-12)
            if ft["flatness"] > 0.3 and ft["centroid"] > 2200 and loud:
                e = add(seg, "harvest", Path(a.video).name, kind="whoosh", note=f"t={v - 0.38:.2f}s (into a cut)")
                if e:
                    added.append(e)
    order = np.argsort(-strength)[: a.max * 2]
    picked = sorted(times[order])
    for t0 in picked:
        nxt = all_times[all_times > t0 + 0.03]
        t1 = min(nxt[0] - 0.01, t0 + 0.6) if len(nxt) else t0 + 0.6
        seg = y[int(max(0, t0 - 0.015) * SR): int(t1 * SR)]
        if len(seg) < 0.04 * SR:
            continue
        inner, _ = onsets(seg) if len(seg) > 0.15 * SR else (np.array([]), None)
        if len(inner) > 1:               # several hits glued together (music or speech) — not one SFX
            continue
        sp = np.abs(np.fft.rfft(seg[: int(0.25 * SR)], 4096))[:1024]
        sp /= np.linalg.norm(sp) + 1e-9
        if any(float(sp @ s) > 0.97 for s in sigs):     # near-duplicate of one we already kept
            continue
        e = add(seg, "harvest", Path(a.video).name, note=f"t={t0:.2f}s")
        if e:
            sigs.append(sp); added.append(e)
        if len(added) >= a.max:
            break
    report(added, f"harvested from {Path(a.video).name}")


# ---------- download (Openverse audio: CC0 / CC BY, commercial use allowed) ----------
def download(a):
    import requests
    r = requests.get("https://api.openverse.org/v1/audio/", params={"q": a.query, "page_size": a.n * 2,
                     "license_type": "commercial,modification", "mature": "false"},
                     headers={"User-Agent": "motion-templates (https://github.com/adeltechtalks/AdelTechTalks-Claude)"}, timeout=30)
    r.raise_for_status()
    added = []
    for it in r.json().get("results", []):
        if (it.get("duration") or 0) > 8000:
            continue
        try:
            tmp = LIB / "_dl.tmp"; LIB.mkdir(parents=True, exist_ok=True)
            tmp.write_bytes(requests.get(it["url"], timeout=30).content)
            x = load(tmp); tmp.unlink()
        except Exception:
            continue
        lic = f"CC {it['license'].upper()} {it.get('license_version') or ''}".replace("CC CC0", "CC0").strip()
        e = add(x, "download", it.get("source") or "openverse", kind=a.kind, title=it.get("title"), author=it.get("creator"),
                license=lic, page=it.get("foreign_landing_url"))
        if e:
            added.append(e)
        if len(added) >= a.n:
            break
    report(added, f"downloaded for “{a.query}”")


def do_import(a):
    added = []
    for p in sorted(Path(a.folder).expanduser().rglob("*")):
        if p.suffix.lower() in (".wav", ".mp3", ".ogg", ".aif", ".aiff", ".flac", ".m4a"):
            e = add(load(p, dur=6), "import", p.name, kind=a.kind)
            if e:
                added.append(e)
    report(added, f"imported from {a.folder}")


def report(added, what):
    by = {}
    for e in added:
        by.setdefault(e["kind"], 0); by[e["kind"]] += 1
    print(f"{len(added)} sounds {what}: " + ", ".join(f"{k} {n}" for k, n in sorted(by.items())))
    print("listen: python engine/sfx_library.py sheet")


def ls(_a):
    ix = index()
    for k in KINDS:
        es = [e for e in ix if e["kind"] == k]
        if es:
            print(f"{k:<7} {len(es):>3}  " + "  ".join(f"{e['id']}({e['dur']:.2f}s,{e['origin'][0]})" for e in es[:12]))
    print(f"{len(ix)} sounds in {LIB}")


def sheet(_a):
    from PIL import Image, ImageDraw
    ix = index()
    if not ix:
        sys.exit("library is empty")
    cols, cw, ch = 6, 300, 90
    rows = (len(ix) + cols - 1) // cols
    im = Image.new("RGB", (cols * cw, rows * ch), "white"); d = ImageDraw.Draw(im)
    audition, gap = [], np.zeros(int(0.45 * SR), np.float32)
    for i, e in enumerate(sorted(ix, key=lambda e: e["kind"])):
        x = load(LIB / e["file"])
        audition += [x, gap]
        X, Y = (i % cols) * cw, (i // cols) * ch
        env = np.abs(x)[: len(x) // 280 * 280].reshape(280, -1).max(1) if len(x) >= 280 else np.abs(x)
        for k, v in enumerate(env):
            d.line((X + 10 + k, Y + 55 - v * 30, X + 10 + k, Y + 55 + v * 30), fill=(37, 99, 235))
        d.text((X + 10, Y + 6), f"#{i + 1} {e['kind']} · {e['id']} · {e['dur']:.2f}s · {e['origin']}", fill=(0, 0, 0))
    out = LIB / "sheet.png"; im.save(out)
    save(LIB / "audition.wav", np.concatenate(audition))
    print(f"sheet: {out}\naudition (same order, 0.45 s apart): {LIB / 'audition.wav'}")


def reclassify(_a):
    """Re-sort every sound that wasn't given a kind by hand (after the classifier improves)."""
    ix, moved = index(), 0
    for e in ix:
        if e.get("forced"):
            continue
        k = hint(e.get("title")) or classify(load(LIB / e["file"]))[0]
        if k != e["kind"]:
            new = LIB / k / Path(e["file"]).name
            new.parent.mkdir(parents=True, exist_ok=True)
            (LIB / e["file"]).rename(new)
            e["kind"], e["file"] = k, str(new.relative_to(LIB)); moved += 1
    write_index(ix); print(f"re-sorted {moved} of {len(ix)}")


def starter(_a):
    """Copy the CC0 downloads into sfx/starter/ — the pack that ships with the skill (CC0 only: no credit needed)."""
    dst = ROOT / "sfx" / "starter"
    keep = [e for e in index() if e["origin"] == "download" and str(e.get("license", "")).upper().startswith("CC0")]
    out = []
    for e in keep:
        (dst / e["kind"]).mkdir(parents=True, exist_ok=True)
        shutil.copy2(LIB / e["file"], dst / e["file"])
        out.append(e)
    (dst / "index.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))
    print(f"{len(out)} CC0 sounds in {dst}")


def remove(a):
    ix = index(); keep = []
    for e in ix:
        if e["id"] in a.ids:
            (LIB / e["file"]).unlink(missing_ok=True)
        else:
            keep.append(e)
    write_index(keep); print(f"removed {len(ix) - len(keep)}")


def main():
    ap = argparse.ArgumentParser(description="Collect SFX into the local library.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    h = sub.add_parser("harvest"); h.add_argument("video"); h.add_argument("--max", type=int, default=30)
    h.add_argument("--all", action="store_true", help="keep every hit, even ones not on a visual event")
    d = sub.add_parser("download"); d.add_argument("query"); d.add_argument("--n", type=int, default=6); d.add_argument("--kind", choices=KINDS)
    i = sub.add_parser("import"); i.add_argument("folder"); i.add_argument("--kind", choices=KINDS)
    sub.add_parser("list"); sub.add_parser("sheet")
    r = sub.add_parser("remove"); r.add_argument("ids", nargs="+")
    sub.add_parser("reclassify"); sub.add_parser("starter")
    a = ap.parse_args()
    {"harvest": harvest, "download": download, "import": do_import, "list": ls, "sheet": sheet, "remove": remove,
     "reclassify": reclassify, "starter": starter}[a.cmd](a)


if __name__ == "__main__":
    main()
