<div align="center">

# Claude Skills للـ Content Creators 🎬✨

**أول مكتبة Claude Skills للـ Content Creators العرب: من الفكرة لحد النشر.**

Skills مجانية بتخلّي Claude يشتغل معاك في كل مرحلة: الأفكار، والكتابة، والتصميم، والمونتاج، والنشر، والأرقام، وشغل الـ Brands.
معمولة **Arabic-first**: بتفهم العربي والمصري، وبتكتب Captions عربي صح، وبتعرف مواسم المنطقة.

[English](README.en.md) · [Instagram @AdelTechTalks](https://instagram.com/adeltechtalks) · [إضافة Skill](CONTRIBUTING.md)

⭐ اعمل **Star**، و 👁 **Watch → Releases**، عشان يوصلك إشعار مع كل Skill جديدة.

</div>

![Social Cover Studio — Before / After](docs/social-cover-studio/before-after.png)

---

## الـ Skills

| المرحلة | الـ Skill | بتعمل إيه | تحميل |
|---|---|---|---|
| 🎨 Design | **[Social Cover Studio](skills/design/social-cover-studio/)** | Covers و Thumbnails بالـ Brand بتاعك من صورة واحدة، بـ 5 Templates وبكل المقاسات: Instagram و TikTok و Facebook و YouTube | [⬇ ZIP](https://github.com/adeltechtalks/claude-skills/raw/main/downloads/social-cover-studio.zip) |

## الـ Roadmap: جاي قريب

| المرحلة | Skills جاية |
|---|---|
| 💡 [Ideation & Research](skills/ideation-research/) | أفكار حلقات، تحليل الـ Trends، دراسة المنافسين |
| ✍️ [Scripting & Writing](skills/writing/) | Hooks، سكريبت Reel، Captions عربي وإنجليزي، Threads |
| 🎨 [Design](skills/design/) | Carousels، Brand kit |
| 🎬 [Video Editing](skills/video-editing/) | مونتاج Reels، Subtitles عربي، قص Shorts من فيديو طويل |
| 📤 [Publishing](skills/publishing/) | Content calendar، Hashtags، مواعيد النشر، خطة رمضان والمواسم |
| 📊 [Analytics](skills/analytics/) | تحليل أداء البوستات، تقارير شهرية |
| 🤝 [Business](skills/business/) | Media kit، الرد على الـ Brand deals، التسعير |
| 🌐 [Web](skills/web/) | Landing page، Link-in-bio |

> عندك فكرة Skill محتاجها في شغلك؟ اطلبها من **[Issues](https://github.com/adeltechtalks/claude-skills/issues)**.

---

## التسطيب

### على Claude.ai (Desktop أو Web أو Mobile)
1. حمّل ملف الـ ZIP بتاع الـ Skill من الجدول فوق.
2. في Claude روح لـ **Settings → Capabilities**، وشغّل **Code execution and file creation**.
3. روح لـ **Customize → Skills**، ودوس **+**، وارفع ملف الـ ZIP زي ما هو، **من غير ما تفكه**.

> الـ Skills شغالة على كل خطط Claude. ولو إنت على Team أو Enterprise، الأدمن لازم يكون مفعّل Skills للمؤسسة.

### على Claude Code
```
/plugin marketplace add adeltechtalks/claude-skills
/plugin install design-skills@adeltechtalks-skills
```
أو انسخ فولدر الـ Skill نفسه (مثلاً `skills/design/social-cover-studio`) جوه `~/.claude/skills/`.

---

## شكل الريبو

```
skills/<المرحلة>/<اسم-الـ-skill>/   ← الـ Skill نفسها (SKILL.md و scripts و assets) + README بالشرح
docs/<اسم-الـ-skill>/               ← الصور والدليل PDF
downloads/<اسم-الـ-skill>.zip       ← ملف التحميل الجاهز
templates/skill-template/           ← قالب أي Skill جديدة
.claude-plugin/marketplace.json     ← للتسطيب من Claude Code
```

عايز تضيف Skill؟ الخطوات كلها في **[CONTRIBUTING.md](CONTRIBUTING.md)**.

---

## License

كل الـ Skills متاحة بـ **[MIT License](LICENSE)**. استخدمها وعدّل عليها وشاركها، بس سيب الـ Credit.
Built by **[@AdelTechTalks](https://instagram.com/adeltechtalks)**.
