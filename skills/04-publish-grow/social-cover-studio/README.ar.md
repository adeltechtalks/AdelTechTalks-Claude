# Social Cover Studio 🎨

[← كل الـ Skills](../../../README.ar.md) · [Publish & Grow](../README.ar.md) · [English](README.md) · **العربية**

`Stage: Publish & Grow` `Step 11 · Package & Publish` `Free`

**Claude Skill** مجانية بتعملك Covers و Thumbnails بالـ Brand بتاعك، من صورة واحدة، وبكل المقاسات: Instagram و TikTok و Facebook و YouTube.

![Before / After](../../../docs/social-cover-studio/before-after.png)

---

## إيه اللي بتعمله؟

تبعت لـ Claude صورة الـ Product، أو صورتك وإنت ماسكه، وهو:

1. يوريك **5 Templates** جنب بعض، وتختار منهم
2. يحط ألوانك والـ Fonts بتاعتك
3. يطلعلك الـ Cover بكل المقاسات، والـ Product بألوانه الحقيقية

| # | الـ Template | شكله |
|---|---|---|
| 0 | **Editorial** | الصورة بألوانها الطبيعية، والكلام فوقها على خلفية فاتحة |
| 1 | **Depth** | كلمة كبيرة **ورا** الـ Product |
| 2 | **Cinematic** | الصورة كاملة، وعنوان من سطرين تحت |
| 3 | **Studio** | الـ Product مقصوص على خلفية بلون الـ Brand |
| 4 | **Creator** | لصورتك إنت: الكلمة ورا راسك، و Stickers للـ Product |

![Templates](../../../docs/social-cover-studio/templates-beats-360.jpg)

---

## التسطيب (5 دقايق، مرة واحدة)

### 1. نزّل الـ Skill
**[⬇ social-cover-studio.zip](https://github.com/adeltechtalks/AdelTechTalks-Claude/raw/main/downloads/social-cover-studio.zip)** ← التحميل هيبدأ على طول.

ولو عايز الدليل كامل بالصور: **[📄 الدليل PDF](../../../docs/social-cover-studio/guide.pdf)**

### 2. فعّل Code execution
في Claude روح لـ **Settings → Capabilities**، وشغّل **Code execution and file creation**.

### 3. ارفع الـ Skill
روح لـ **Customize → Skills**، ودوس **+**، وارفع ملف الـ ZIP زي ما هو، **من غير ما تفكه**.

> الـ Skills شغالة على كل خطط Claude: Free و Pro و Max و Team و Enterprise. ولو إنت على Team أو Enterprise، الأدمن لازم يكون مفعّل Skills للمؤسسة.

---

## أول مرة: الـ Brand بتاعك

افتح Chat جديد واكتب:

```
عايز أستخدم social-cover-studio. ظبطلي الـ Brand بتاعي الأول.
```

Claude هيسألك 3 أسئلة: اسم الـ Account، وألوانك (Hex أو لوجو أو بالكلام)، والـ Fonts من قايمة جاهزة. وفي الآخر هيديك ملف **`brand.json`**. **احفظه** وابعته في أول أي Chat، أو حطه في Project، عشان الشكل يفضل ثابت.

---

## اعمل أول Cover

ابعت الصورة ومعاها `brand.json`، واكتب:

```
اعملي Cover للصورة دي:
- الكلمة الكبيرة: GLACIER
- اسم الـ Product: iPhone 18 Pro Max
- الكلمة القصيرة: لوني المفضل
وريني الـ Templates الأول
```

اختار Template، وقوله: **"عجبني رقم 1، طلعلي كل المقاسات"**.

| الملف | المقاس | لفين |
|---|---|---|
| `instagram-tiktok` | 1080×1920 (9:16) | Reels و TikTok و Facebook Reels |
| `facebook` | 1080×1350 (4:5) | Post في الـ Feed |
| `youtube` | 1920×1080 (16:9) | Thumbnail لفيديو عادي |

---

## نصايح

- سيب مساحة فاضية فوق الـ Product، أو فوق راسك في Creator.
- الكلمة الكبيرة من 4 لـ 9 حروف: اسم اللون، أو الموديل، أو كلمة واحدة بتلخص الفيديو.
- لو الخلفية فيها حاجات كتير، Editorial و Depth بيطلعوا أنضف من Studio و Creator.
- الإيموجي الغامق (🖤) مش بيبان على الخلفيات الغامقة.

## لو حصلت مشكلة

| المشكلة | الحل |
|---|---|
| Claude مش بيستخدم الـ Skill | اكتب صراحة: "استخدم social-cover-studio" |
| أول مرة في كل Chat بطيئة | طبيعي، بيحمّل أدوات قص الصورة، وبياخد دقيقة أو اتنين |
| الملف مش راضي يترفع | اتأكد إنه `.zip` ومش مفكوك |
| الكلام اتقص في الـ Grid | وإنت بترفع على Instagram استخدم **Edit profile grid** |

---

## Credits

Built by **[@AdelTechTalks](https://instagram.com/adeltechtalks)** · rembg و pymatting (MIT) · Google Fonts (SIL OFL) · Emoji: Twemoji (CC-BY 4.0)

الكود متاح بـ **MIT License**. استخدمه وعدّل عليه وشاركه، بس سيب الـ Credit.
