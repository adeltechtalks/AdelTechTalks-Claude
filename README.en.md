# Claude Skills by AdelTechTalks 🧰

Free **Claude Skills** for creators: design, video editing, writing and web building.
Download a skill, upload it to Claude, and start using it.

[العربي](README.md) · [Instagram @AdelTechTalks](https://instagram.com/adeltechtalks)

---

## Skills

### 🎨 Design

| Skill | What it does | Download |
|---|---|---|
| **[Social Cover Studio](skills/design/social-cover-studio/)** | Branded covers and thumbnails from one photo — 5 templates, exported for Instagram/TikTok, Facebook and YouTube | [⬇ ZIP](https://github.com/adeltechtalks/claude-skills/raw/main/downloads/social-cover-studio.zip) |

### 🎬 Video Editing · ✍️ Writing · 🌐 Web Building
Coming soon — **⭐ Star** the repo to get notified.

---

## Install

**Claude.ai:** download the skill ZIP → Settings → Capabilities → turn on *Code execution and file creation* → Customize → Skills → **+** → upload the ZIP (don't unzip it).

**Claude Code:**
```
/plugin marketplace add adeltechtalks/claude-skills
/plugin install design-skills@adeltechtalks-skills
```
Or copy a skill folder (e.g. `skills/design/social-cover-studio`) into `~/.claude/skills/`.

---

## Social Cover Studio

One product photo → branded covers and thumbnails in 5 templates (Editorial, Depth, Cinematic, Studio, Creator), with your colours and fonts, exported for Instagram/TikTok (9:16), Facebook (4:5) and YouTube (16:9), with the product in its real colours.

- **First use:** "Use social-cover-studio and set up my brand first." Keep the `brand.json` it gives you.
- **Make a cover:** send a photo + "Make a cover: big word GLACIER, product iPhone 18 Pro Max, keyword 'my favourite colour'. Show me the templates first."
- Full guide (Arabic): [docs/social-cover-studio/guide.pdf](docs/social-cover-studio/guide.pdf)

---

## Repo layout

```
skills/<category>/<skill>/        the skill itself (SKILL.md, scripts, assets) + README
docs/<skill>/                     images and PDF guide
downloads/<skill>.zip             ready-to-upload ZIP (built by scripts/build-zips.sh)
.claude-plugin/marketplace.json   Claude Code plugin marketplace
```

MIT License · by [@AdelTechTalks](https://instagram.com/adeltechtalks)
