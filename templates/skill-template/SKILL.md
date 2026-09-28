---
name: skill-name
description: One paragraph that tells Claude WHAT this skill does and WHEN to use it. List the concrete triggers a creator would type, in English and Arabic (e.g. "write a hook", "اكتبلي Hook", "سكريبت ريل"), and say to use it even when the user doesn't name the skill. This field is how Claude decides to load the skill, so be specific.
---

# Skill Name

One line: what goes in → what comes out.

## Step 0 — Setup (first time only, optional)

If the skill needs the creator's own settings (brand, tone of voice, audience, platforms), ask for them once in a single message, save them to a small file (e.g. `brand.json` / `voice.md`), and tell the user to keep it so results stay consistent.

## Step 1 — Get the inputs

- List exactly what the skill needs from the user.
- Ask only for what's missing. If the user is unsure, propose 3–4 options.

## Step 2 — Do the work

Numbered, concrete steps. Put any code in `scripts/` and show the exact command:

```bash
python scripts/your_script.py --input file --out out
```

## Quality checklist

Check every output before sending it:

- [ ] ...
- [ ] ...

## Writing Arabic for the user

- Write in the user's dialect when they write in it (Egyptian, Gulf, Levantine…); default to clear Modern Standard Arabic otherwise.
- Keep English platform and tech terms in Latin letters (`Reel`, `Hook`, `Caption`, `Thumbnail`) — never transliterate them into Arabic script.
- Arabic text in images or video must be shaped and right-to-left.

## Outputs

Describe the files or text the user gets, with file names and sizes where relevant.

## Credits

Libraries, fonts and assets used, with their licenses.
