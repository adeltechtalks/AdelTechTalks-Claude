# AdelTechTalks-Claude

Free Claude Skills for content creators, organised by the 14-step Content Creation OS.

## Structure (keep it exactly like this)

- `skills/<stage>/<slug>/` — stages are `00-foundations` · `01-ideas` · `02-pre-production` · `03-production` · `04-publish-grow` · `05-lanes` · `06-monetization`. Folder name = `name` in `SKILL.md`.
- Each skill folder: `SKILL.md`, `README.md`, `README.ar.md`, plus `assets/` and `scripts/` if needed. Nothing else; media lives in `docs/<slug>/`.
- Skill pages copy `templates/skill-template/README*.md`: hero → breadcrumb → download → 🧪 note (testing only) → "You give" table → How it works → showcase → Get started (1 · Install with the install card, 2 · setup, 3 · first result) → `<details>` tips/troubleshooting → credits line.
- Art comes from `scripts/build-art.py` (brand tokens, embedded fonts). Never hand-draw hero/how/install SVGs.
- `catalog.json` is the source for stage pages and the main README blocks: edit it, then run `python3 scripts/build-catalog.py`. Don't edit generated blocks by hand.
- Pro skills, personal strategy, money plans and client files never go in this repo.

## Adding or changing a skill

Follow `CONTRIBUTING.md`, then run:

```bash
python3 scripts/build-catalog.py
python3 scripts/build-art.py
./scripts/build-zips.sh
python3 scripts/check-skills.py   # must pass
claude plugin validate .
```

`build-art.py` and `build-zips.sh` rebuild every skill; revert unrelated outputs that changed only by rebuild noise (e.g. other skills' ZIPs).

## Writing

Arabic pages are Egyptian Arabic; keep platform and product terms (`Reel`, `Skill`, `Install`) in Latin letters. Keep the English and Arabic pages in sync.
