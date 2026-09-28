# Claude Skills by AdelTechTalks 🧰

**Claude Skills** مجانية للـ Creators: Design، و Video Editing، و Writing، و Web Building.
حمّل الـ Skill، ارفعها على Claude، واشتغل على طول.

[English](README.en.md) · [Instagram @AdelTechTalks](https://instagram.com/adeltechtalks)

![Social Cover Studio — Before / After](docs/social-cover-studio/before-after.png)

---

## الـ Skills

### 🎨 Design

| الـ Skill | بتعمل إيه | تحميل |
|---|---|---|
| **[Social Cover Studio](skills/design/social-cover-studio/)** | Covers و Thumbnails بالـ Brand بتاعك من صورة واحدة، بـ 5 Templates وبكل المقاسات: Instagram و TikTok و Facebook و YouTube | [⬇ ZIP](https://github.com/adeltechtalks/claude-skills/raw/main/downloads/social-cover-studio.zip) |

### 🎬 Video Editing
قريباً.

### ✍️ Writing
قريباً.

### 🌐 Web Building
قريباً.

> اعمل **⭐ Star** للريبو عشان يوصلك كل Skill جديدة أول ما تنزل.

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
skills/<الفئة>/<اسم-الـ-skill>/   ← الـ Skill نفسها (SKILL.md و scripts و assets) + README بالشرح
docs/<اسم-الـ-skill>/             ← الصور والدليل PDF
downloads/<اسم-الـ-skill>.zip     ← ملف التحميل الجاهز
.claude-plugin/marketplace.json   ← للتسطيب من Claude Code
```

### إضافة Skill جديدة
1. حط الفولدر في `skills/<الفئة>/<اسم-الـ-skill>/`، وجواه `SKILL.md` و `README.md`.
2. حط الصور والدليل في `docs/<اسم-الـ-skill>/`.
3. شغّل `./scripts/build-zips.sh` عشان يتعمل ملف الـ ZIP في `downloads/`.
4. زوّد سطر في جدول الـ Skills هنا وفي `README.en.md`، وزوّد مسار الـ Skill في `.claude-plugin/marketplace.json`.

---

## License

كل الـ Skills متاحة بـ **[MIT License](LICENSE)**. استخدمها وعدّل عليها وشاركها، بس سيب الـ Credit.
Built by **[@AdelTechTalks](https://instagram.com/adeltechtalks)**.
