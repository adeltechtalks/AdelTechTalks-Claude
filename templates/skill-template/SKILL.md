---
name: skill-name
description: >-
  [What it does, in one sentence.] Use this skill whenever the user [concrete
  situations], or asks for [phrases a creator would actually type, e.g.
  "write me a hook", "turn this video into shorts"], including requests in
  other languages (e.g. Arabic: "اكتبلي Hook") — even if they don't name the
  skill. Do not use it for [nearby tasks that belong to another skill].
---

# Skill Name

> **Input:** [what the user provides] → **Output:** [what they get back]

## When to use

- [Situation 1]
- [Situation 2]

Not for: [what this skill deliberately doesn't do].

## Workflow

### Step 0 — Profile setup (first run only · optional)

If results depend on the creator's own settings (brand, tone of voice, audience, platforms):

1. Ask for everything in **one** message; offer sensible defaults.
2. Save the answers from `assets/profile.template.json` into `profile.json`.
3. Tell the user to keep the file (or add it to a Claude Project) so results stay consistent.

Never reuse another creator's values as defaults.

### Step 1 — Collect inputs

| Input | Required | Default |
|:--|:-:|:--|
| [input] | ✅ | — |
| [input] | — | [default] |

Ask only for what's missing. When the user is unsure, propose 3–4 concrete options.

### Step 2 — Produce

1. [Concrete step.]
2. [Concrete step.] Deterministic work lives in `scripts/`:

   ```bash
   pip install -r scripts/requirements.txt --break-system-packages
   python scripts/main.py --input <file> --out out
   ```

3. When there are several good directions, show a short preview first and let the user choose before producing final files.

### Step 3 — Review and deliver

Run the quality checklist on **every** output before sending it, then offer one relevant next step (e.g. captions, other sizes, a variation).

## Quality checklist

- [ ] [Specific, checkable rule]
- [ ] [Specific, checkable rule]
- [ ] Output matches the user's language, and platform terms (`Reel`, `Hook`, `Caption`) stay in their original form.
- [ ] Text in images or video is correctly shaped and directed (including right-to-left scripts).

## Output

| File / section | Format | Notes |
|:--|:--|:--|
| `<name>_<variant>.<ext>` | [e.g. 1080×1920 JPG] | [where it's used] |

## Language

Reply in the user's language and dialect. Keep English platform and product terms in Latin letters rather than transliterating them.

## Credits

[Libraries, fonts, models and assets used, with their licenses.]
