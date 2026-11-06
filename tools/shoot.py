"""
لقطات مراجعة للصفحة على ثلاثة مقاسات، لكل فصل لقطة بحجم الشاشة.
التشغيل: python tools/shoot.py <url> <مجلد الحفظ> [motion]
بدون motion: الحركة مقلّلة (كل المحتوى ظاهر). مع motion: نمرّر الصفحة تدريجيًا علشان نختبر الظهور.
"""
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

URL, OUT = sys.argv[1], Path(sys.argv[2])
MOTION = len(sys.argv) > 3 and sys.argv[3] == 'motion'
OUT.mkdir(parents=True, exist_ok=True)

VIEWS = {
    'phone': dict(viewport={'width': 390, 'height': 844}, device_scale_factor=3, is_mobile=True, has_touch=True),
    'tablet': dict(viewport={'width': 820, 'height': 1180}, device_scale_factor=2, is_mobile=True, has_touch=True),
    'desktop': dict(viewport={'width': 1440, 'height': 900}, device_scale_factor=1),
}
SECTIONS = ['top', 'prayer', 'quran', 'hifz', 'athkar', 'track', 'know', 'place', 'night', 'data', 'all']

with sync_playwright() as p:
    b = p.chromium.launch()
    for name, opts in VIEWS.items():
        ctx = b.new_context(**opts, reduced_motion='no-preference' if MOTION else 'reduce', locale='ar')
        page = ctx.new_page()
        errors = []
        page.on('console', lambda m: m.type == 'error' and errors.append(m.text))
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.goto(URL, wait_until='networkidle')
        page.evaluate('document.fonts.ready')
        if MOTION:
            # تمرير تدريجي حقيقي لحدّ آخر الصفحة (عجلة الماوس بتقف قبل الآخر في الوضع بلا واجهة)
            y = 0
            while y <= page.evaluate('document.documentElement.scrollHeight'):
                page.evaluate(f'window.scrollTo(0, {y})')
                page.wait_for_timeout(16)
                y += 600
            page.evaluate('window.scrollTo(0, 0)')
            page.wait_for_timeout(300)
        for s in SECTIONS:
            page.evaluate(f'document.getElementById("{s}").scrollIntoView({{block: "start"}})')
            page.wait_for_timeout(700 if MOTION else 250)
            page.screenshot(path=str(OUT / f'{name}-{s}.png'))
        if MOTION:
            hidden = page.evaluate('[...document.querySelectorAll(".reveal")].filter(e => !e.classList.contains("in")).length')
            print(name, 'reveal elements still hidden after full scroll:', hidden)
        print(name, 'console errors:', errors or 'none')
        ctx.close()
    b.close()
