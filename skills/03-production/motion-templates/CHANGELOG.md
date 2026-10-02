# Changelog

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
