#!/usr/bin/env python3
"""One command from template to finished reel.

    python render.py --style a --out output/

Runs: test frames → silent render → SFX → music → mix (music ducked under SFX) → final 1080p mp4.
Needs ffmpeg on PATH (or FFMPEG=/path/to/ffmpeg).
"""
import argparse
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# Per style: template, its silent render, its SFX script/output, and music timing.
# drop = the result reveal (music builds for one bar before it); end = start of the ending section.
STYLES = {
    "a": dict(name="A · Morphing UI", template="templates/core/style_a_morphing_ui.py", video="ui_v.mp4", test="uisheet.png",
              sfx="sfx/sfx_style_a.py", sfx_wav="sfx_ui.wav", dur=32.0, drop=19.3, end=27.0, test_t=(1.0, 10.0, 20.5, 29.5)),
    "e": dict(name="E · Orange Balls", template="templates/core/style_e_orange_balls.py", video="bl_v.mp4", test="blsheet.png",
              sfx="sfx/sfx_style_e.py", sfx_wav="sfx_bl.wav", dur=22.5, drop=16.875, end=20.625, test_t=(1.0, 10.0, 18.0, 21.0)),
    "f": dict(name="F · Kinetic Type", template="templates/core/style_f_kinetic_type.py", video="kt_v.mp4", test="ktsheet.png",
              sfx="sfx/sfx_style_f.py", sfx_wav="sfx_kt.wav", dur=22.5, drop=4.6875, end=20.625, test_t=(1.0, 10.0, 20.0)),
    "g": dict(name="G · Editorial Poster", template="templates/core/style_g_editorial_poster.py", video="ep_v.mp4", test="epsheet.png",
              sfx="sfx/sfx_style_g.py", sfx_wav="sfx_ep.wav", dur=22.5, drop=3.75, end=16.875, test_t=(2.5, 8.5, 14.5, 20.5)),
    "h": dict(name="H · Studio Stage", template="templates/core/style_h_studio_stage.py", video="ss_v.mp4", test="sssheet.png",
              sfx="sfx/sfx_style_h.py", sfx_wav="sfx_ss.wav", dur=24.375, drop=5.625, end=20.625, test_t=(2.2, 7.6, 14.6, 17.6, 22.5)),
}

MIX_FILTER = ("[0:a]volume=0.5[m];[1:a]asplit=2[s1][s2];"
              "[m][s1]sidechaincompress=threshold=0.05:ratio=4:attack=5:release=200[md];"
              "[md][s2]amix=inputs=2:normalize=0,volume=4dB,alimiter=limit=0.7:level=false")


def run(step, cmd, env):
    print(f"\n▶ {step}\n  {' '.join(str(c) for c in cmd)}", flush=True)
    t0 = time.time()
    subprocess.run([str(c) for c in cmd], check=True, env=env)
    print(f"  ✓ {step} ({time.time() - t0:.0f}s)", flush=True)


def main():
    ap = argparse.ArgumentParser(description="Render a motion reel end to end.")
    ap.add_argument("--style", required=True, choices=sorted(STYLES), help="a (Morphing UI), e (Orange Balls), f (Kinetic Type), g (Editorial Poster) or h (Studio Stage)")
    ap.add_argument("--out", default="output", help="folder for the final mp4 (default: output/)")
    ap.add_argument("--work", default=None, help="folder for intermediate files (default: ./work)")
    ap.add_argument("--input", default=None, help="folder with per-video inputs (default: ./input)")
    ap.add_argument("--brand", default=None, help="brand file (default: <input>/brand.json, else the example brand)")
    ap.add_argument("--drop", type=float, default=None, help="override the music drop time (seconds)")
    ap.add_argument("--end", type=float, default=None, help="override the music ending time (seconds)")
    ap.add_argument("--skip-test", action="store_true", help="skip the test frames")
    args = ap.parse_args()

    ffmpeg = os.environ.get("FFMPEG") or shutil.which("ffmpeg")
    if not ffmpeg:
        sys.exit("ffmpeg not found — install it or set FFMPEG=/path/to/ffmpeg")

    env = dict(os.environ)
    env["MT_OUT_DIR"] = str(Path(args.out).resolve())
    if args.work:
        env["MT_WORK_DIR"] = str(Path(args.work).resolve())
    if args.input:
        env["MT_INPUT_DIR"] = str(Path(args.input).resolve())
    if args.brand:
        env["MT_BRAND"] = str(Path(args.brand).resolve())
    env["PATH"] = str(Path(ffmpeg).parent) + os.pathsep + env.get("PATH", "")
    os.environ.update(env)

    from engine import config  # after the env is set, so it picks up --out/--work/--input

    s = STYLES[args.style]
    work, out = config.WORK_DIR, config.OUT_DIR
    py = sys.executable
    drop = s["drop"] if args.drop is None else args.drop
    end = s["end"] if args.end is None else args.end
    print(f"Brand: {config.brand()['name']}")
    print(f"Style {s['name']} · {s['dur']}s · music drop {drop}s, ending {end}s\nwork → {work}\nout  → {out}")

    if not args.skip_test:
        run("Test frames", [py, ROOT / s["template"], "test", *s["test_t"]], env)
        print(f"  contact sheet: {work / s['test']}")
    run("Render video (silent)", [py, ROOT / s["template"], "render"], env)
    run("SFX", [py, ROOT / s["sfx"]], env)
    run("Music", [py, ROOT / "engine/music_fast.py", s["dur"], drop, end], env)

    mix = work / f"mix_{args.style}.wav"
    run("Mix (music ducked under SFX)", [ffmpeg, "-y", "-loglevel", "error", "-i", work / "music_fast.wav", "-i", work / s["sfx_wav"],
                                         "-filter_complex", MIX_FILTER, mix], env)
    final = out / f"style_{args.style}_final.mp4"
    run("Mux → final 1080p mp4", [ffmpeg, "-y", "-loglevel", "error", "-i", work / s["video"], "-i", mix, "-map", "0:v", "-map", "1:a",
                                  "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", final], env)
    print(f"\n✅ Done: {final}")


if __name__ == "__main__":
    main()
