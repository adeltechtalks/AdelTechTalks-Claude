<div align="center">

<img src="docs/assets/banner.png" alt="Claude Skills for Content Creators" width="100%">

<br>

[English](README.md) · **العربية**

[![Stars](https://img.shields.io/github/stars/adeltechtalks/Claude-Skills?style=flat-square&color=D97757)](https://github.com/adeltechtalks/Claude-Skills/stargazers)
[![Skills](https://img.shields.io/badge/skills-1-D97757?style=flat-square)](#الـ-skills)
[![Works with Claude](https://img.shields.io/badge/works%20with-Claude.ai%20%7C%20Claude%20Code-1f1f1f?style=flat-square)](#التسطيب)
[![License: MIT](https://img.shields.io/badge/license-MIT-1f1f1f?style=flat-square)](LICENSE)

</div>

<div dir="rtl">

**Claude Skills for Content Creators** مكتبة [Claude Skills](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview) مجانية وجاهزة للاستخدام، بتغطي كل مراحل شغل الـ Content Creator: الأفكار، والكتابة، والتصميم، والمونتاج، والنشر، والأرقام، وشغل الـ Brands. حمّل الـ Skill، ارفعها على Claude، وهو يعرف يعمل الشغل.

> [!TIP]
> اعمل **Star** ⭐، و **Watch → Custom → Releases**، عشان يوصلك إشعار مع كل Skill جديدة.

---

## الـ Skills

| المرحلة | الـ Skill | بتعمل إيه | تحميل |
|:--|:--|:--|:--:|
| 🎨 Design | **[Social Cover Studio](skills/design/social-cover-studio/README.ar.md)** | Covers و Thumbnails بالـ Brand بتاعك من صورة واحدة، بـ 5 Templates وبكل المقاسات: Instagram و TikTok و Facebook و YouTube | [**ZIP**](https://github.com/adeltechtalks/Claude-Skills/raw/main/downloads/social-cover-studio.zip) |

<br>

<img src="docs/social-cover-studio/before-after.png" alt="Social Cover Studio — Before / After" width="100%">

---

## الـ Roadmap

| المرحلة | جاي قريب |
|:--|:--|
| 💡 [Ideation & Research](skills/ideation-research/) | أفكار حلقات · تحليل الـ Trends · دراسة المنافسين |
| ✍️ [Scripting & Writing](skills/writing/) | Hooks · سكريبت Reel · Captions · Threads |
| 🎨 [Design](skills/design/) | Carousels · Brand kit |
| 🎬 [Video Editing](skills/video-editing/) | مونتاج Reels · Subtitles · قص Shorts من فيديو طويل |
| 📤 [Publishing](skills/publishing/) | Content calendar · Hashtags · مواعيد النشر · حملات المواسم |
| 📊 [Analytics](skills/analytics/) | تحليل أداء البوستات · تقارير شهرية |
| 🤝 [Business](skills/business/) | Media kit · الرد على الـ Brand deals · التسعير |
| 🌐 [Web](skills/web/) | Landing page · Link-in-bio |

محتاج Skill معينة في شغلك؟ [اطلبها من هنا](https://github.com/adeltechtalks/Claude-Skills/issues/new).

---

## التسطيب

### على Claude.ai (Web أو Desktop أو Mobile)

1. حمّل ملف الـ **ZIP** بتاع الـ Skill من الجدول فوق.
2. في Claude روح لـ **Settings → Capabilities**، وشغّل **Code execution and file creation**.
3. روح لـ **Customize → Skills**، ودوس **+**، وارفع ملف الـ ZIP زي ما هو، **من غير ما تفكه**.

الـ Skills شغالة على كل خطط Claude. ولو إنت على Team أو Enterprise، الأدمن لازم يكون مفعّل Skills للمؤسسة.

### على Claude Code

</div>

```bash
/plugin marketplace add adeltechtalks/Claude-Skills
/plugin install design-skills@adeltechtalks-skills
```

<div dir="rtl">

أو انسخ فولدر الـ Skill نفسه (مثلاً `skills/design/social-cover-studio`) جوه `~/.claude/skills/`.

---

## المساهمة

كل Skill جديدة بتمشي على القالب اللي في [`templates/skill-template`](templates/skill-template/). والخطوات كلها في [CONTRIBUTING.md](CONTRIBUTING.md).

## License

[MIT](LICENSE): استخدمها وعدّل عليها وشاركها، بس سيب الـ Credit.

</div>

<div align="center">
<sub>Built by <a href="https://instagram.com/adeltechtalks"><b>@AdelTechTalks</b></a></sub>
</div>
