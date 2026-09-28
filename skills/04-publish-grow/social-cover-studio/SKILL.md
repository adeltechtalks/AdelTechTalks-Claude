---
name: social-cover-studio
description: Build branded video covers and thumbnails (Instagram/TikTok reels 9:16, Facebook 4:5, YouTube 16:9) from a single photo of a product or of a person holding a product, using 5 ready templates (Editorial — natural photo under a clean light text panel; Depth — big word behind the product; Cinematic — film-grade photo with bottom headline; Studio — product cut out on a brand-colour glow; Creator — word behind the person with sticker labels). Includes a first-time brand setup (colours, fonts, handle) so every creator gets their own look. Use this whenever someone shares a product/unboxing/review photo and wants a cover, thumbnail, reel cover, "text behind the object", "Cover", "Thumbnail", or writes it in Arabic ("اعملي كفر", "ثامبنيل"), or wants the same design on more photos or sizes — even if they don't name a template.
---

# Social Cover Studio

One photo in → a branded cover in 4 template styles → exported for every platform.

| # | Template | Best for | Look |
|---|---|---|---|
| 0 | `editorial` | any product photo, bright & clean | natural photo (no filter) under a light text panel: product name + keyword + optional series badge (`--badge`). Brand-safe default |
| 1 | `depth` | product in hand / on desk | big word **behind** the product, product name + keyword under it. Minimal |
| 2 | `cinematic` | any photo, strong story | full photo, dark film grade, pill label + 2-line headline at the bottom |
| 3 | `studio` | clean product shots | product (and hand) cut out onto a glowing brand-colour backdrop, huge title |
| 4 | `creator` | **photos of a person** with the product | word behind the person's head, product-name chip + tilted keyword sticker |

Text slots (same for all templates): **word** (the hero word — colour, model or theme), **product** (always shown), **keyword** (1–3 words, any language, Arabic shaped RTL automatically), **emoji**.

## Step 0 — Brand setup (first time only)

If the user has no brand file yet, set it up before making anything. Ask in one go (use tappable options if available):

1. Handle/brand name to show top-left (or none).
2. Colours: a dark background tone, a main brand colour, a highlight colour. Accept hex codes, a logo/screenshot to sample from, or words ("navy and gold") that you translate to hex.
3. Fonts — pick one Latin + one Arabic (if they post in Arabic) from the built-in list:
   Latin: Montserrat, Inter, Poppins, Bebas Neue, Anton · Arabic: Cairo, Tajawal, Readex Pro, IBM Plex Sans Arabic, Alexandria.

Write `brand.json` from `assets/brand.template.json`, show it back briefly, and tell the user to keep it (paste it into a Project's knowledge or send it again next time) so the look stays identical across posts. Never reuse another creator's brand values as defaults.

## Step 1 — Make the covers

1. **Copy the photo out of the uploads folder first** — uploads can be overwritten mid-conversation; always render from your own copy of the original.
2. Get the 4 text slots from the message; ask only for what's missing. If the user is unsure, propose 3–4 options (see "Words").
3. Install once, then render a **preview sheet of all 4 templates** so the user can choose:
   ```bash
   pip install -r scripts/requirements.txt --break-system-packages
   python scripts/cover_studio.py --image photo.jpg --word GLACIER --product "iPhone 18 Pro Max" \
     --keyword "لوني المفضل" --emoji 💙 --brand brand.json --template all --preview --out out --name glacier
   ```
   (Skip the preview if the user already named a template.) First run downloads models (~350 MB) and fonts.
4. After they pick, export the sizes:
   ```bash
   python scripts/cover_studio.py ... --template depth --sizes 9x16,4x5,16x9 --out out --name glacier
   ```
5. **View every file before sending** and run the checklist. Then offer platform captions.

## Quality checklist

- **Edges**: no halo or smear around product/hand. Always render from the original photo — never write on the image and try to remove text later.
- **Grid safe zone**: IG/TikTok profile grids show only the centre 3:4 of a 9:16 cover (y ≈ 240–1680). All text must sit inside it with margin; the 4:5 Facebook file is that same zone.
- **Depth reads**: the product/person overlaps only the lower part of the word. If it hides too much, shorten the word.
- **Stray cut-out pieces** (desk edges, coloured lights) in `studio`/`creator`: if you see any, prefer `depth`/`cinematic` for that photo or ask for a cleaner shot.
- **Emoji**: dark emoji (🖤) vanish on dark backgrounds — use light ones (✨ 🤍).
- **Photo of a person**: `creator` puts the word behind the head, so it needs some free space above the head. Faces must never be covered by text chips — check it.

## Writing Arabic text for the user

When you write Arabic (replies, captions, keywords suggestions), keep every English term in Latin letters — `Cover`, `Product`, `Template`, `Brand`, `Emoji` — even next to Arabic words. Never transliterate English into Arabic script (no كفر، برودكت، تمبلت).

## Words

- **Hero word**: 4–9 letters, uppercase for Latin. Colour names for colour videos; otherwise model name or a one-word theme.
- **Keyword**: a mood or hook, not a sentence. Avoid words that read as a person's name (Arabic صفاء، نسمة). In a series, keep the same shape (فخامة / جرأة / هدوء).
- **Mixed audiences**: keep the local-language keyword small; let the hero word + product name carry the cover.

## Outputs

`<name>_<template>_instagram-tiktok_1080x1920.jpg` · `<name>_<template>_facebook_1080x1350.jpg` (feed; for FB Reels use the 9:16) · `<name>_<template>_youtube_1920x1080.jpg` (long-form thumbnail; Shorts covers are picked in the app).

## Credits
rembg & pymatting (MIT) · Google Fonts (SIL OFL) · Twemoji (CC-BY 4.0 — credit "Twemoji" when publishing or add emoji natively in your editor).
