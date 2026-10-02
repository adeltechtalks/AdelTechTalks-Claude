# Changelog

## v1.5 — Style H · Studio Stage
- `templates/core/style_h_studio_stage.py`: eight scene looks (orbit, tiles, rise, tv, slab, card, pillar, drop) with whip-pan transitions; `sfx/sfx_style_h.py`; `render.py --style h`.
- New moves learned from a second user reference: `focus_in`, `blur_rise`, `orbit_dots`, `roll_in`, plus the `whip` transition and `motion_blur`; `ghost_words(shadow=True)`.
- `engine/endings.py`: the name → logo → Follow → comment ending, shared by G and H.

## v1.4 — Style G · Editorial Poster
- `templates/core/style_g_editorial_poster.py`: 12 bars (22.5 s), six scene looks (poster, dark, frame, pedestal, giant, type) + name → logo → Follow → comment ending; story in one table at the top.
- `sfx/sfx_style_g.py` reads the template's timeline, so sounds follow any story edit. `render.py --style g`.
- `engine/assets.py get … --one` keeps only the biggest subject in a cut-out.

## v1.3 — Finds its own images
- `engine/assets.py`: search free, licence-safe images (Openverse, Wikimedia Commons, NASA; Pexels / Pixabay / Unsplash with a key), pick from a numbered sheet, save into `input/` with optional cut-out (`rembg`) and black & white, credits logged in `input/credits.json`.
- New moves learned from a user reference (editorial poster reel): `ghost_words`, `marquee_word`, `push_in`, `split_reveal`.
- `templates/lab/poster_demo.py`: a full reel made only from found images.

## v1.2 — Motion library
- Renamed the skill to `motion-templates` (env vars are now `MT_*`).
- `engine/moves.py`: reusable moves with one signature (`pop_in`, `slide_in`, `slide_out`, `spring_drop`, `slap_in`, `fold_open`).
- `templates/lab/moves_demo.py`: preview any move on a brand card (`test` / `render`).
- `engine/study.py`: break a reference clip into frames, a contact sheet and a motion graph.
- `references/motion-library.md` and the "Learn a new motion" workflow in `SKILL.md`.

## v1.1 — Your brand
- Brand comes from `input/brand.json` + `input/logo.png` (Step 0 asks for it); AdelTechTalks ships only as an example.
- Missing inputs draw labelled placeholders.

## v1.0 — Paths and CLI
- Paths in `engine/config.py` (no hardcoded `/home/claude`), smoke tests, `render.py` one-command pipeline, `.gitignore`.
