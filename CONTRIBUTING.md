# إضافة Skill جديدة · Adding a new skill

## بالعربي

1. **انسخ القالب:** انسخ `templates/skill-template/` إلى `skills/<الفئة>/<اسم-الـ-skill>/`.
   الاسم بحروف إنجليزي صغيرة وشرطات، مثلاً `reel-hook-writer`، ولازم يكون هو نفسه `name` في `SKILL.md`.
2. **الفئات:** `ideation-research` · `writing` · `design` · `video-editing` · `publishing` · `analytics` · `business` · `web`
3. **اكتب `SKILL.md`:** أهم حاجة فيه الـ `description`، لأن Claude بيقرر منه إمتى يستخدم الـ Skill. حط فيه أمثلة للطلبات بالعربي والإنجليزي.
4. **اكتب `README.md`:** ده صفحة الـ Skill على GitHub، وفيه صورة قبل/بعد، وطريقة التسطيب، و Prompt جاهز للتجربة.
5. **الصور والـ PDF:** تتحط في `docs/<اسم-الـ-skill>/`، مش جوه فولدر الـ Skill، عشان الـ ZIP يفضل صغير.
6. **اعمل الـ ZIP:** شغّل `./scripts/build-zips.sh`.
7. **سجّل الـ Skill:**
   - زوّد سطر في جدول `README.md` و `README.en.md`.
   - زوّد مسارها في `.claude-plugin/marketplace.json`، تحت الـ Plugin بتاع الفئة. ولو الفئة لسه مالهاش Plugin، اعمل واحد اسمه `<الفئة>-skills`.
8. **اعمل Release** باسم الـ Skill ورقم نسخة، عشان اللي عامل Watch يوصله إشعار.

### قبل ما ترفع
- [ ] جرّبت الـ Skill على Claude.ai بالـ ZIP نفسه.
- [ ] مفيش أي API keys أو بيانات شخصية أو ملفات عملاء.
- [ ] العربي في الردود والصور مكتوب صح، والكلمات الإنجليزي بحروف إنجليزي.
- [ ] الـ Credits والـ Licenses للمكتبات والخطوط مكتوبة.

## In English

Copy `templates/skill-template/` to `skills/<category>/<skill-name>/` (kebab-case, same as `name` in `SKILL.md`), write a sharp `description`, put images and PDFs in `docs/<skill-name>/`, run `./scripts/build-zips.sh`, add the skill to both READMEs and to `.claude-plugin/marketplace.json`, then publish a GitHub Release. Never commit API keys, personal data or client files.

By submitting a skill you agree to release it under the repo's [MIT License](LICENSE).
