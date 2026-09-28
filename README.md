<p align="center"><a href="README.md"><img src="docs/assets/lang-en-on.svg" alt="English" height="40"></a>&nbsp;&nbsp;<a href="README.ar.md"><img src="docs/assets/lang-ar-off.svg" alt="العربية" height="40"></a></p>

<div align="center">

<img src="docs/assets/banner-en.svg" alt="Claude Skills for Content Creators — by AdelTechTalks" width="100%">

<br>

**Free, ready-to-use [Claude Skills](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview) for every step of content creation — from the first idea to the analysis of what worked.**

<br>

<a href="skills/"><img src="docs/assets/btn-browse-en.svg" alt="Browse skills" height="48"></a>&nbsp;&nbsp;<a href="#install"><img src="docs/assets/btn-install-en.svg" alt="Install" height="48"></a>&nbsp;&nbsp;<a href="https://github.com/adeltechtalks/AdelTechTalks-Claude/stargazers"><img src="docs/assets/btn-star-en.svg" alt="Star the repo" height="48"></a>

<br>

[![Stars](https://img.shields.io/github/stars/adeltechtalks/AdelTechTalks-Claude?style=flat-square&color=2563EB&labelColor=171A1F)](https://github.com/adeltechtalks/AdelTechTalks-Claude/stargazers)
[![Skills](https://img.shields.io/badge/skills-1-2563EB?style=flat-square&labelColor=171A1F)](skills/)
[![Works with Claude](https://img.shields.io/badge/works%20with-Claude.ai%20%7C%20Claude%20Code-2DD4A8?style=flat-square&labelColor=171A1F)](#install)
[![License: MIT](https://img.shields.io/badge/license-MIT-667085?style=flat-square&labelColor=171A1F)](LICENSE)

</div>

---

## Available now

<!-- featured:start -->

<table>
<tr>
<td width="50%" valign="top"><a href="skills/04-publish-grow/social-cover-studio/"><img src="docs/assets/skills/social-cover-studio-en.svg" alt="Social Cover Studio" width="100%"></a><p align="center"><a href="https://github.com/adeltechtalks/AdelTechTalks-Claude/raw/main/downloads/social-cover-studio.zip"><img src="docs/assets/btn-download-en.svg" alt="Download ZIP" height="40"></a>&nbsp;<a href="skills/04-publish-grow/social-cover-studio/"><img src="docs/assets/btn-more-en.svg" alt="How it works" height="40"></a></p></td>
<td width="50%" valign="top"><a href="https://github.com/adeltechtalks/AdelTechTalks-Claude/subscription"><img src="docs/assets/skills/coming-en.svg" alt="Coming next" width="100%"></a><p align="center"><a href="https://github.com/adeltechtalks/AdelTechTalks-Claude/subscription"><img src="docs/assets/btn-watch-en.svg" alt="Get notified" height="40"></a></p></td>
</tr>
</table>

<!-- featured:end -->

---

## The system

Every idea walks the same 14 steps — and every step gets a skill. Foundations are set once; Lanes and Monetization run alongside. **[Read the full method →](os/)**

<img src="docs/assets/flow-en.svg" alt="From Idea to Analysis — the 14-step flow" width="100%">

---

## Skills by stage

Tap a stage to see its skills. **Free** skills are open in this repo; **🔒 Pro** skills ship with [Content Creation OS Pro](course/). **[See all skills in one list →](skills/)**

<!-- stages:start -->

<table>
<tr>
<td width="50%"><a href="skills/00-foundations/"><img src="docs/assets/stages/00-foundations-en.svg" alt="Foundations" width="100%"></a></td>
<td width="50%"><a href="skills/01-ideas/"><img src="docs/assets/stages/01-ideas-en.svg" alt="Ideas" width="100%"></a></td>
</tr>
<tr>
<td width="50%"><a href="skills/02-pre-production/"><img src="docs/assets/stages/02-pre-production-en.svg" alt="Pre-Production" width="100%"></a></td>
<td width="50%"><a href="skills/03-production/"><img src="docs/assets/stages/03-production-en.svg" alt="Production" width="100%"></a></td>
</tr>
<tr>
<td width="50%"><a href="skills/04-publish-grow/"><img src="docs/assets/stages/04-publish-grow-en.svg" alt="Publish & Grow" width="100%"></a></td>
<td width="50%"><a href="skills/05-lanes/"><img src="docs/assets/stages/05-lanes-en.svg" alt="Lanes" width="100%"></a></td>
</tr>
<tr>
<td width="50%"><a href="skills/06-monetization/"><img src="docs/assets/stages/06-monetization-en.svg" alt="Monetization" width="100%"></a></td>
<td width="50%"></td>
</tr>
</table>

<!-- stages:end -->

---

<a id="install"></a>

## Install

<img src="docs/assets/install-en.svg" alt="1 Download the skill ZIP · 2 Settings → Capabilities → turn on Code execution and file creation · 3 Customize → Skills → + and upload the ZIP" width="100%">

<sub>Works on every Claude plan. On Team and Enterprise, an admin must enable Skills first.</sub>

**Using Claude Code?**

```bash
/plugin marketplace add adeltechtalks/AdelTechTalks-Claude
/plugin install publish-grow-skills@adeltechtalks-claude
```

---

## Principles

<img src="docs/assets/principles-en.svg" alt="The AI suggests, you decide · Real over generated · One source, many formats · Verified before published" width="100%">

---

<details>
<summary><b>🤖 Agents — the Content Machine</b></summary>

<br>

Skills do one job each. The **Content Machine** agent chains them and walks the whole flow with you — suggesting at every step while you approve. It's in design and will ship with [Content Creation OS Pro](course/). **[See the agent map →](agents/)**

</details>

<details>
<summary><b>📁 Repository structure</b></summary>

<br>

```
os/                               The Content Creation OS — the method behind the skills
skills/<stage>/<skill>/           Free skills, grouped by stage
agents/                           The Content Machine and the agent map
course/                           Learning path and Pro access
docs/                             Images and guides (art built by scripts/build-art.py)
downloads/<skill>.zip             Ready-to-upload ZIPs (scripts/build-zips.sh)
catalog.json                      Single source of truth for the catalog (scripts/build-catalog.py)
templates/skill-template/         Starting point for a new skill
.claude-plugin/marketplace.json   Claude Code plugin marketplace
```

</details>

<details>
<summary><b>🛠 Contributing</b></summary>

<br>

New skills follow [`templates/skill-template`](templates/skill-template/). The full checklist is in [CONTRIBUTING.md](CONTRIBUTING.md).

</details>

---

<div align="center">
<sub>Free skills are released under the <a href="LICENSE">MIT License</a> · Pro content is licensed separately</sub>
<br><br>
<sub><b>AdelTechTalks</b> · Curated by Adel · <i>Experience it. Don't just consume it.</i></sub>
<br>
<sub><a href="https://instagram.com/adeltechtalks">Instagram</a> · <a href="https://adeltechtalks.com">adeltechtalks.com</a></sub>
</div>
