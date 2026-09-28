<div align="center">

# Claude Skills for Content Creators 🎬✨

**The Claude Skills library for content creators, built Arabic-first — from idea to publish.**

Free skills that make Claude work with you at every stage: ideas, writing, design, editing, publishing, analytics and brand deals.
Built **Arabic-first** (Arabic dialects, correct RTL captions, regional seasons like Ramadan), and fully usable in English.

[العربي](README.md) · [Instagram @AdelTechTalks](https://instagram.com/adeltechtalks) · [Add a skill](CONTRIBUTING.md)

⭐ **Star** and 👁 **Watch → Releases** to get notified when a new skill drops.

</div>

---

## Skills

| Stage | Skill | What it does | Download |
|---|---|---|---|
| 🎨 Design | **[Social Cover Studio](skills/design/social-cover-studio/)** | Branded covers and thumbnails from one photo — 5 templates, exported for Instagram/TikTok, Facebook and YouTube | [⬇ ZIP](https://github.com/adeltechtalks/claude-skills/raw/main/downloads/social-cover-studio.zip) |

## Roadmap

| Stage | Coming soon |
|---|---|
| 💡 [Ideation & Research](skills/ideation-research/) | Episode ideas, trend analysis, competitor research |
| ✍️ [Scripting & Writing](skills/writing/) | Hooks, reel scripts, Arabic & English captions, threads |
| 🎨 [Design](skills/design/) | Carousels, brand kit |
| 🎬 [Video Editing](skills/video-editing/) | Reel editing, Arabic subtitles, shorts from long videos |
| 📤 [Publishing](skills/publishing/) | Content calendar, hashtags, posting times, Ramadan & seasonal plans |
| 📊 [Analytics](skills/analytics/) | Post performance analysis, monthly reports |
| 🤝 [Business](skills/business/) | Media kit, brand-deal replies, pricing |
| 🌐 [Web](skills/web/) | Landing page, link-in-bio |

Need a skill for your workflow? Request it in **[Issues](https://github.com/adeltechtalks/claude-skills/issues)**.

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
skills/<stage>/<skill>/           the skill itself (SKILL.md, scripts, assets) + README
docs/<skill>/                     images and PDF guide
downloads/<skill>.zip             ready-to-upload ZIP (built by scripts/build-zips.sh)
templates/skill-template/         starting point for a new skill
.claude-plugin/marketplace.json   Claude Code plugin marketplace
```

MIT License · by [@AdelTechTalks](https://instagram.com/adeltechtalks)
