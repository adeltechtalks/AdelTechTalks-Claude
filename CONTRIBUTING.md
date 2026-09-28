# Contributing

**English** · [العربية](#العربية)

## Adding a skill

1. **Copy the template** — `templates/skill-template/` → `skills/<stage>/<skill-name>/`.
   Use kebab-case (e.g. `reel-hook-writer`); it must match `name` in `SKILL.md`.
2. **Pick a stage** — `00-foundations` · `01-ideas` · `02-pre-production` · `03-production` · `04-publish-grow` · `05-lanes` · `06-monetization`. Pro skills never go in this repo.
3. **Write `SKILL.md`** — the `description` decides when Claude loads the skill. Make it specific: what it does, the phrases users type, and what it is *not* for.
4. **Write the skill pages** — `README.md` (English) and `README.ar.md` (Arabic): a hero image, install steps, and a copy-paste prompt.
5. **Add media** to `docs/<skill-name>/` — never inside the skill folder, so the ZIP stays small.
6. **Build the ZIP** — `./scripts/build-zips.sh`
7. **Register the skill**
   - Add or update its entry in `catalog.json` (set `"status": "available"`), then run `python3 scripts/build-catalog.py` — it rebuilds the stage pages, both README catalogs and the skills badge.
   - Add its path to `.claude-plugin/marketplace.json` under that stage's plugin (create `<stage>-skills` if it doesn't exist), then run `claude plugin validate .`.
8. **Publish a GitHub Release** (e.g. `social-cover-studio v1.0.0`) with the ZIP attached, so watchers get notified.

### Before you publish

- [ ] Tested on Claude.ai using the exact ZIP from `downloads/`.
- [ ] No API keys, tokens, personal data or client files anywhere in the skill.
- [ ] Output reads naturally in every language the skill supports.
- [ ] Third-party libraries, fonts and assets are credited with their licenses.

By contributing, you agree to release your work under the repository's [MIT License](LICENSE).

---

## العربية

<div dir="rtl">

1. **انسخ القالب:** من `templates/skill-template/` إلى `skills/<المرحلة>/<اسم-الـ-skill>/`. الاسم بحروف إنجليزي صغيرة وشرطات، ولازم يكون هو نفسه `name` في `SKILL.md`.
2. **اكتب `SKILL.md`:** أهم حاجة فيه الـ `description`، لأن Claude بيقرر منه إمتى يستخدم الـ Skill.
3. **صفحات الـ Skill:** `README.md` بالإنجليزي، و `README.ar.md` بالعربي.
4. **الصور:** تتحط في `docs/<اسم-الـ-skill>/`.
5. **اعمل الـ ZIP:** بأمر `./scripts/build-zips.sh`.
6. **سجّل الـ Skill:** في `catalog.json` وشغّل `python3 scripts/build-catalog.py`، وضيفها في `.claude-plugin/marketplace.json`.
7. **اعمل Release:** عشان اللي عامل Watch يوصله إشعار.

قبل الرفع: جرّب الـ ZIP على Claude.ai، واتأكد إن مفيش أي API keys أو بيانات شخصية.

</div>
