"""يصوّر tools/og.html إلى docs/assets/img/og.png (1200×630) بـ Chromium. التشغيل: python tools/build-og.py"""
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
with sync_playwright() as p:
    b = p.chromium.launch()
    page = b.new_page(viewport={'width': 1200, 'height': 630})
    page.goto((ROOT / 'tools' / 'og.html').as_uri(), wait_until='networkidle')
    page.evaluate('document.fonts.ready')
    page.screenshot(path=str(ROOT / 'docs' / 'assets' / 'img' / 'og.png'))
    b.close()
print('og.png done')
