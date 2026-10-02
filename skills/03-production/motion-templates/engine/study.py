"""Study a reference clip before teaching the skill a new motion.

    python engine/study.py reference.mp4 [--fps 10] [--start 0] [--end 6]

Writes to work/study/<clip name>/:
    frames/f_0000.png …      frames at --fps, with their timestamps in timing.csv
    sheet.png                contact sheet with timestamps (read the motion at a glance)
    timing.csv               time, motion energy (frame-to-frame change), cut flag
    motion.png               motion-energy graph — peaks are hits/cuts, slopes are eases

Read the sheet + graph to write the Motion DNA (what moves, from where, how long,
which curve, on which beat) — see "Learn a new motion" in SKILL.md.
"""
import argparse
import csv
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # skill root, so the engine package is importable
from engine import config

import numpy as np
from PIL import Image, ImageDraw


def main():
    ap = argparse.ArgumentParser(description="Break a reference clip into frames, a contact sheet and a motion graph.")
    ap.add_argument("clip")
    ap.add_argument("--fps", type=float, default=10)
    ap.add_argument("--start", type=float, default=0)
    ap.add_argument("--end", type=float, default=None)
    a = ap.parse_args()

    ffmpeg = shutil.which("ffmpeg") or sys.exit("ffmpeg not found")
    out = Path(config.work("study")) / Path(a.clip).stem
    frames = out / "frames"
    if frames.exists():
        shutil.rmtree(frames)
    frames.mkdir(parents=True)
    cmd = [ffmpeg, "-loglevel", "error", "-ss", str(a.start)]
    if a.end:
        cmd += ["-to", str(a.end)]
    cmd += ["-i", a.clip, "-vf", f"fps={a.fps},scale=360:-2", str(frames / "f_%04d.png")]
    subprocess.run(cmd, check=True)

    files = sorted(frames.glob("f_*.png"))
    if not files:
        sys.exit("no frames extracted — check the clip path and --start/--end")
    ims = [Image.open(p).convert("L") for p in files]
    arr = [np.asarray(im, dtype=np.float32) / 255 for im in ims]
    energy = [0.0] + [float(np.abs(arr[i] - arr[i - 1]).mean()) for i in range(1, len(arr))]
    thr = (np.median(energy) + 4 * np.std(energy)) if len(energy) > 2 else 1
    times = [a.start + i / a.fps for i in range(len(files))]

    with open(out / "timing.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["time_s", "motion_energy", "cut"])
        for tt, e in zip(times, energy):
            w.writerow([f"{tt:.2f}", f"{e:.4f}", int(e > thr)])

    # contact sheet
    cols = 8
    tw = 180
    th = int(tw * ims[0].height / ims[0].width)
    rows = (len(files) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * tw, rows * (th + 22)), "white")
    d = ImageDraw.Draw(sheet)
    for i, p in enumerate(files):
        x, y = (i % cols) * tw, (i // cols) * (th + 22)
        sheet.paste(Image.open(p).convert("RGB").resize((tw, th)), (x, y + 22))
        d.text((x + 4, y + 4), f"{times[i]:.2f}s" + ("  CUT" if energy[i] > thr else ""), fill=(0, 0, 0))
    sheet.save(out / "sheet.png")

    # motion graph
    gw, gh = 1200, 300
    g = Image.new("RGB", (gw, gh), "white")
    gd = ImageDraw.Draw(g)
    mx = max(energy) or 1
    pts = [(int(i / max(1, len(energy) - 1) * (gw - 40)) + 20, gh - 30 - int(e / mx * (gh - 60))) for i, e in enumerate(energy)]
    gd.line(pts, fill=(37, 99, 235), width=3)
    for i, e in enumerate(energy):
        if e > thr:
            gd.line([(pts[i][0], 20), (pts[i][0], gh - 30)], fill=(255, 107, 87), width=1)
    for s in range(int(times[-1] - a.start) + 1):
        x = int(s * a.fps / max(1, len(energy) - 1) * (gw - 40)) + 20
        gd.text((x, gh - 22), f"{a.start + s:.0f}s", fill=(102, 112, 133))
    g.save(out / "motion.png")

    cuts = [f"{tt:.2f}" for tt, e in zip(times, energy) if e > thr]
    print(f"{len(files)} frames · {times[-1] - a.start:.1f}s · cuts/hits at: {', '.join(cuts) or 'none'}")
    print(f"sheet:  {out / 'sheet.png'}\ngraph:  {out / 'motion.png'}\ntiming: {out / 'timing.csv'}")


if __name__ == "__main__":
    main()
