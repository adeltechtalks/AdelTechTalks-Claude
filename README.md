<div align="center">

<img src="docs/assets/banner.png" alt="Claude Skills for Content Creators" width="100%">

<br>

**English** · [العربية](README.ar.md)

[![Stars](https://img.shields.io/github/stars/adeltechtalks/Claude-Skills?style=flat-square&color=D97757)](https://github.com/adeltechtalks/Claude-Skills/stargazers)
[![Skills](https://img.shields.io/badge/skills-1-D97757?style=flat-square)](#skills)
[![Works with Claude](https://img.shields.io/badge/works%20with-Claude.ai%20%7C%20Claude%20Code-1f1f1f?style=flat-square)](#installation)
[![License: MIT](https://img.shields.io/badge/license-MIT-1f1f1f?style=flat-square)](LICENSE)

</div>

**Claude Skills for Content Creators** is a library of free, ready-to-use [Claude Skills](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview) for every stage of a creator's workflow — research, writing, design, editing, publishing, analytics and brand work. Download a skill, upload it to Claude, and it knows how to do the job.

> [!TIP]
> **Star** ⭐ and **Watch → Custom → Releases** to get notified whenever a new skill is released.

---

## Skills

| Stage | Skill | Description | Download |
|:--|:--|:--|:--:|
| 🎨 Design | **[Social Cover Studio](skills/design/social-cover-studio/)** | Branded covers and thumbnails from a single photo. 5 templates, exported for Instagram, TikTok, Facebook and YouTube. | [**ZIP**](https://github.com/adeltechtalks/Claude-Skills/raw/main/downloads/social-cover-studio.zip) |

<br>

<img src="docs/social-cover-studio/before-after.png" alt="Social Cover Studio — before and after" width="100%">

---

## Roadmap

| Stage | In the works |
|:--|:--|
| 💡 [Ideation & Research](skills/ideation-research/) | Episode ideas · Trend analysis · Competitor research |
| ✍️ [Scripting & Writing](skills/writing/) | Hooks · Reel scripts · Captions · Threads |
| 🎨 [Design](skills/design/) | Carousels · Brand kit |
| 🎬 [Video Editing](skills/video-editing/) | Reel editing · Subtitles · Shorts from long-form |
| 📤 [Publishing](skills/publishing/) | Content calendar · Hashtags · Posting schedule · Seasonal campaigns |
| 📊 [Analytics](skills/analytics/) | Post performance review · Monthly reports |
| 🤝 [Business](skills/business/) | Media kit · Brand-deal replies · Pricing |
| 🌐 [Web](skills/web/) | Landing page · Link-in-bio |

Have a skill you need in your workflow? [Request it](https://github.com/adeltechtalks/Claude-Skills/issues/new).

---

## Installation

### Claude.ai — web, desktop and mobile

1. Download the skill's **ZIP** from the table above.
2. In Claude, open **Settings → Capabilities** and turn on **Code execution and file creation**.
3. Go to **Customize → Skills**, click **+**, and upload the ZIP as it is — **don't unzip it**.

Skills are available on all Claude plans. On Team and Enterprise, an admin must enable Skills for the organization.

### Claude Code

```bash
/plugin marketplace add adeltechtalks/Claude-Skills
/plugin install design-skills@adeltechtalks-skills
```

Or copy a skill folder (for example `skills/design/social-cover-studio`) into `~/.claude/skills/`.

---

## Repository structure

```
skills/<stage>/<skill>/           The skill (SKILL.md, scripts, assets) and its README
docs/<skill>/                     Screenshots and guides
downloads/<skill>.zip             Ready-to-upload ZIP, built by scripts/build-zips.sh
templates/skill-template/         Starting point for a new skill
.claude-plugin/marketplace.json   Claude Code plugin marketplace
```

## Contributing

New skills follow the template in [`templates/skill-template`](templates/skill-template/). See [CONTRIBUTING.md](CONTRIBUTING.md) for the full checklist.

## License

[MIT](LICENSE) — free to use, modify and share with attribution.

<div align="center">
<sub>Built by <a href="https://instagram.com/adeltechtalks"><b>@AdelTechTalks</b></a></sub>
</div>
