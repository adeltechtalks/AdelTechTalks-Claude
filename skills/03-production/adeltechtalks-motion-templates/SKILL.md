---
name: adeltechtalks-motion-templates
description: Render motion-graphics reels (9:16) entirely from code — no editing software — in the user's own brand (colours, fonts, logo, name). Use whenever someone wants a reel/short/explainer/promo built as motion graphics, a video in one of the locked styles (A Morphing UI, E Orange Balls, F Kinetic Type, or the extras Paper Collage, Liquid Glass, Isometric 3D, Shape Morph, Editorial Depth), a style comparison (the same story in A/E/F), or SFX/music for a motion video. Triggers include "make a motion reel", "same as style A", "compare the three styles", "add SFX and music", "اعملي ريل موشن", "نفس ستايل A", "قارنلي التلات ستايلات", "حط SFX ومزيكا".
---

# Motion Templates (v1.1)

Every video is a Python script that draws each frame with Pillow and pipes raw frames to ffmpeg. Sound (SFX + music) is synthesized in code, so everything is original and copyright-free. The look comes from the user's **brand file** — the templates were designed with the AdelTechTalks brand, which ships only as an example in `examples/adeltechtalks/`.

## Step 0 — Brand setup (first time only)

If `input/brand.json` doesn't exist, set it up before rendering anything. Never use the example brand for someone else's video. Ask in one go (offer tappable options where possible):

1. **Name** shown on the ending card, and a 2–3 word **tagline**.
2. **Language** of on-screen text (e.g. Egyptian Arabic, English).
3. **Colours** — background, ink (text), primary, accent, and one CTA colour. Accept hex codes, a logo or screenshot to sample from, or words ("navy and gold") that you turn into hex. Derive `primary_light`, `primary_soft`, `muted`, `hairline`, `paper`, `surface`, `ball` from them.
4. **Fonts** — a display font, a body font, a Latin font and a mono font. Defaults: Cairo, Readex Pro, Montserrat, JetBrains Mono (downloaded by `engine/fetch_fonts.sh`). For another Google Font, download its `.ttf` into `engine/fonts/` and use the file name.
5. **Logo** — a PNG with a transparent background (it's recoloured to fit each scene). Save it as `input/logo.png`.
6. **Ending** — headline, follow button text (`{name}` is replaced by the name), and the comment card: words before/after the keyword, the keyword itself, and the promise line.

Write `input/brand.json` from `brand.template.json`, show it back briefly, and tell the user to keep `brand.json` + `logo.png` so every video stays consistent. Without a brand file the scripts fall back to the example and print a notice — treat that notice as "Step 0 is missing".

## Locked comparison set
| Code | Style | File | Best for |
|---|---|---|---|
| **A** ⭐ main | Morphing UI — one shape morphs chat → files → code → phone; ambient chips/widgets so no frame is ever empty; headlines enter from different directions | `templates/core/style_a_morphing_ui.py` | tool/feature explainers |
| **E** | Orange Balls — glossy ball drops, splits, carries labels, merges, becomes a phone | `templates/core/style_e_orange_balls.py` | stories with numbers, reviews |
| **F** | Kinetic Type — one phrase per half-bar @128 BPM, varied layouts (big, box, strike, outline, counter) | `templates/core/style_f_kinetic_type.py` | daily news / hooks (easiest to automate) |

Extras (proven, not in the default set): `templates/extras/` — paper_collage_4k, liquid_glass, isometric_3d, shape_morph, editorial_depth.

## Non-negotiable rules
1. **Language:** on-screen text in the user's language and dialect; English tech terms stay English (never transliterated). Arabic is shaped with Pillow RAQM (`direction='rtl'`).
2. **Brand comes from `brand.json`:** colours, fonts, logo, name, tagline and the ending text. Don't hardcode brand values in a template — add a key to `brand.json` instead.
3. **Cross-platform safe layout:** every readable element inside the centre 4:5 crop (y 285–1635 on 1080×1920) and above y 1500 (full-screen UI). Never right-weight the layout for TikTok's rail — keep it centred.
4. **No empty frames:** style A always runs `ambient()` (dot grid, colour blobs, top/bottom chip marquees, floating widgets).
5. **Pacing:** fast. Music 128 BPM (`engine/music_fast.py`); scene changes on bars/half-bars; a 1-bar build + drum break right before the result reveal.
6. **The CTA colour appears once** — the follow button. (Style E uses the brand's `ball` colour as its theme; say so when delivering.)
7. **No shadows/overlays across faces or photos.** Photos keep full colour.
8. **Ending (default):** headline → logo card (name · tagline) → Follow tapped → "Following" → comment card «comment_before KEYWORD comment_after / comment_promise». The logo, not the person's photo.
9. **Claims/numbers** on screen must come from the user or a verified source.

## Workflow
Paths live in `engine/config.py`: fonts in `engine/fonts/`, per-video inputs in `./input/`, intermediate files in `./work/`, finished videos in `./output/` (override with `ATC_INPUT_DIR`, `ATC_WORK_DIR`, `ATC_OUT_DIR`). Needs `pip install -r requirements.txt` and ffmpeg.

1. Brand (Step 0) and fonts: `bash engine/fetch_fonts.sh` (once).
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

## Inputs the user supplies per video
Story/script, plus optional files in `input/`: `photo.jpg` (portrait), `result/*.png` (result clip frames), `cutout.png`, `partner_1.png` / `partner_2.png`, `flag_1.jpg` / `flag_2.png`, plus `brand.json` and `logo.png` from Step 0. Anything missing is drawn as a labelled placeholder and listed in the console. `input/` is git-ignored — never commit partner logos or personal photos.
