---
name: adeltechtalks-motion-templates
description: Render AdelTechTalks motion-graphics reels (9:16) entirely from code — no editing software. Use whenever Adel wants a reel/short/explainer/promo built as motion graphics, a new video in one of the locked styles (A Morphing UI, E Orange Balls, F Kinetic Type, or the extras Paper Collage, Liquid Glass, Isometric 3D, Shape Morph, Editorial Depth), a style comparison (render the same story in A/E/F), or SFX/music for a motion video. Triggers include "اعملي ريل موشن", "نفس ستايل A", "قارنلي التلات ستايلات", "حط SFX ومزيكا", "تيمبلت".
---

# AdelTechTalks Motion Templates (v1.0)

Every video is a Python script that draws each frame with Pillow and pipes raw frames to ffmpeg. Sound (SFX + music) is synthesized in code, so everything is original and copyright-free.

## Locked comparison set
| Code | Style | File | Best for |
|---|---|---|---|
| **A** ⭐ main | Morphing UI — one shape morphs chat → files → code → phone; ambient chips/widgets so no frame is ever empty; headlines enter from different directions | `templates/core/style_a_morphing_ui.py` | tool/feature explainers |
| **E** | Orange Balls — glossy ball drops, splits, carries labels, merges, becomes a phone | `templates/core/style_e_orange_balls.py` | stories with numbers, reviews |
| **F** | Kinetic Type — one phrase per half-bar @128 BPM, varied layouts (big, box, strike, outline, counter) | `templates/core/style_f_kinetic_type.py` | daily news / hooks (easiest to automate) |

Extras (proven, not in the default set): `templates/extras/` — paper_collage_4k, liquid_glass, isometric_3d, shape_morph, editorial_depth.

## Non-negotiable rules
1. **Language:** on-screen text in Egyptian Arabic; English tech terms stay English. Fonts: Cairo 900 (Arabic headlines), Readex Pro (Arabic UI/captions), Montserrat (Latin), JetBrains Mono (codes/numbers). Arabic via Pillow RAQM with `direction='rtl'`.
2. **Cross-platform safe layout:** every readable element inside the centre 4:5 crop (y 285–1635 on 1080×1920) and above y 1500 (full-screen UI). Never right-weight the layout for TikTok's rail — keep it centred.
3. **No empty frames:** style A always runs `ambient()` (dot grid, colour blobs, top/bottom chip marquees, floating widgets).
4. **Pacing:** fast. Music 128 BPM (`engine/music_fast.py`); scene changes on bars/half-bars; a 1-bar build + drum break right before the result reveal.
5. **Spark Coral (#FF6B57) appears once** — the CTA button. (Style E uses orange as its theme; say so when delivering.)
6. **No shadows/overlays across faces or photos** (gobo light was rejected). Photos keep full colour.
7. **Ending (default):** headline "عايز نفس السكيل؟" → logo card (AdelTechTalks · Tech Explorer) → Follow tapped → "Following" → comment card «اكتب SKILL في الكومنتات / وهبعتلك السكيل كاملة بالشرح». Logo, not Adel's photo.
8. **Claims/numbers** on screen must come from Adel or a verified source.

## Workflow
Paths live in `engine/config.py`: fonts in `engine/fonts/`, per-video inputs in `./input/`, intermediate files in `./work/`, finished videos in `./output/` (override with `ATC_INPUT_DIR`, `ATC_WORK_DIR`, `ATC_OUT_DIR`). Needs `pip install -r requirements.txt` and ffmpeg.

1. Fonts: `bash engine/fetch_fonts.sh` (once).
2. Edit the story/text constants at the top of the chosen template (headlines, chips, codes, timings).
3. Test frames: `python templates/core/style_a_morphing_ui.py test 3.6 12.6 29.5` → PNGs + contact sheet in `work/`. Check them before rendering.
4. Whole reel in one command (test → render → SFX → music → mix → final 1080p mp4 in `output/`):
   ```
   python render.py --style a --out output/      # a · e · f
   ```
   Music timing defaults per style (drop = result reveal, end = ending section) can be overridden with `--drop` / `--end`.
5. Step by step, if needed: `python <template> render` (silent mp4 in `work/`) · `python sfx/sfx_style_<x>.py` · `python engine/music_fast.py <dur> <drop_t> <end_t>`, then mix and mux:
   ```
   ffmpeg -i work/music_fast.wav -i work/sfx.wav -filter_complex "[0:a]volume=0.5[m];[1:a]asplit=2[s1][s2];[m][s1]sidechaincompress=threshold=0.05:ratio=4:attack=5:release=200[md];[md][s2]amix=inputs=2:normalize=0,volume=4dB,alimiter=limit=0.7:level=false" work/mix.wav
   ffmpeg -i work/video.mp4 -i work/mix.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart output/final.mp4
   ```
   Target ≈ -16 LUFS, true peak ≤ -1 dBTP.
6. Deliver a light 1080p file for phones (4K masters only when asked: render at K=2, downscale with lanczos, CRF 17).

## Inputs Adel supplies per video
Story/script, plus optional files in `input/`: `photo.jpg` (portrait), `result/*.png` (result clip frames), `cutout.png`, `partner_1.png` / `partner_2.png`, `flag_1.jpg` / `flag_2.png`. Anything missing is drawn as a labelled placeholder and listed in the console. `input/` is git-ignored — never commit partner logos or Adel's personal photos.
