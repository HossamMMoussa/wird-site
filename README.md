# صفحة عرض وِرد

موقع ثابت (HTML وCSS وJavaScript بلا مكتبات) لعرض تطبيق وِرد بلقطات حقيقية من التطبيق.

- `docs/` الموقع المنشور (فرع `gh-pages` على GitHub Pages).
- `screenshots/raw/` اللقطات الأصلية من محاكي أندرويد ١٥ (1080×2400)، ببيانات تجريبية.
- `tools/features.py` قائمة المميزات ومدى التحقق منها (مصدر قسم «كل المميزات» و`FEATURES.md`).
- `tools/index.template.html` نص الصفحة.

البناء:

```
python tools/build-images.py   # صور WebP وتفاصيل مكبّرة من اللقطات الأصلية
python tools/build-og.py       # صورة المشاركة (يحتاج Playwright)
python tools/build-site.py     # docs/index.html وdocs/privacy.html وFEATURES.md
python tools/shoot.py <url> <dir> [motion]   # لقطات مراجعة على ثلاثة مقاسات
```

النشر: `git subtree split --prefix docs -b gh-pages` ثم دفع فرع `gh-pages` وحده.
