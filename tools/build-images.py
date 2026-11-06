"""
يجهّز صور الموقع من لقطات التطبيق الأصلية (screenshots/raw) بدون أي تعديل في محتوى الواجهة:
- نسخة WebP بعرضين (540 و1080 بكسل) لكل لقطة مستخدمة.
- تفاصيل مكبّرة: قصّ مستطيل من اللقطة الأصلية نفسها (بإحداثيات بكسلات اللقطة 1080×2400).
- صورة المشاركة (og.png) تُصنع بـ tools/build-og.py من tools/og.html، لأن Pillow هنا ما بيشكّلش الحروف العربية.

التشغيل من جذر المستودع: python tools/build-images.py
"""
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / 'screenshots' / 'raw'
OUT = ROOT / 'docs' / 'assets' / 'img'
OUT.mkdir(parents=True, exist_ok=True)

# اللقطات المستخدمة في الصفحة: الاسم في الموقع ← الملف الأصلي
SHOTS = {
    'home': '02-home.png',
    'setup': '01-home-setup.png',
    'adhan': '03-adhan.png',
    'quran': '04-quran.png',
    'mushaf': '05-mushaf-baqarah.png',
    'athkar': '06-athkar.png',
    'tasbih': '07-tasbih.png',
    'worship': '08-worship.png',
    'stats': '09-stats.png',
    'muhasaba': '10-muhasaba.png',
    'travel': '11-travel-mode.png',
    'morning': '12-athkar-morning.png',
    'hifz-plan': '14-hifz-plan.png',
    'qibla': '15-qibla.png',
    'fasting': '17-fasting.png',
    'imsakiya': '18-imsakiya.png',
    'zakat': '19-zakat.png',
    'qada': '20-qada.png',
    'library': '21-library.png',
    'radio': '22-radio.png',
    'more': '23-more.png',
    'ayah': '24-ayah-sheet.png',
    'ayah-image': '25-ayah-image.png',
    'kids': '26-kids.png',
    'quiz': '27-quiz.png',
    'prophets': '28-prophets.png',
    'sirah': '29-sirah.png',
    'umrah': '30-umrah.png',
    'history': '31-history.png',
    'asma': '32-asma.png',
    'tajweed': '33-tajweed.png',
    'topics': '34-topics.png',
    'prayer-month': '35-prayer-month.png',
    'adhan-prefs': '36-adhan-prefs.png',
    'alarm': '37-alarm-card.png',
    'dark-home': '40-dark-home.png',
    'dark-mushaf': '41-dark-mushaf.png',
    'dark-athkar': '42-dark-athkar.png',
    'dark-worship': '43-dark-worship.png',
}

# تفاصيل مكبّرة: (الملف الأصلي، (يسار، أعلى، يمين، أسفل)) بإحداثيات اللقطة الأصلية
CROPS = {
    'detail-ayah-card': ('25-ayah-image.png', (42, 640, 1038, 1430)),
    'detail-tasbih': ('07-tasbih.png', (150, 1340, 930, 2090)),
    'detail-muhasaba': ('10-muhasaba.png', (0, 980, 1080, 1820)),
    'detail-alarm': ('37-alarm-card.png', (0, 1440, 1080, 2130)),
    'detail-ayah-sheet': ('24-ayah-sheet.png', (0, 300, 1080, 1700)),
    'detail-setup': ('01-home-setup.png', (30, 410, 1050, 1450)),
}


def save_webp(img: Image.Image, name: str, widths=(540, 1080)) -> None:
    for w in widths:
        if img.width < w:
            continue
        h = round(img.height * w / img.width)
        img.resize((w, h), Image.LANCZOS).save(OUT / f'{name}-{w}.webp', 'WEBP', quality=84, method=6)




def main() -> None:
    for name, src in SHOTS.items():
        save_webp(Image.open(RAW / src).convert('RGB'), name)
    for name, (src, box) in CROPS.items():
        save_webp(Image.open(RAW / src).convert('RGB').crop(box), name, widths=(720, 1080))
    total = sum(p.stat().st_size for p in OUT.iterdir())
    print(f'{len(list(OUT.iterdir()))} files, {total / 1e6:.1f} MB')


if __name__ == '__main__':
    main()
