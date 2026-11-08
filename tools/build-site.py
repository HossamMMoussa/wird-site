"""
يبني docs/index.html من tools/index.template.html، وdocs/privacy.html من سياسة خصوصية التطبيق، وFEATURES.md.

- <x-shot name="..." alt="..." [kind="detail"] [eager] [class] [data-step]> ← <img> بمقاسين وأبعاد ثابتة.
- قسم «كل المميزات» بين <!-- FEATURES:START --> و<!-- FEATURES:END --> من tools/features.py.

التشغيل من جذر المستودع: python tools/build-site.py
"""
import html
import re
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / 'docs'
IMG = DOCS / 'assets' / 'img'
GIF = DOCS / 'assets' / 'gif'
APP = ROOT.parent / 'wird'
BASE = 'https://hossammoussa1.github.io/wird-site/'

sys.path.insert(0, str(ROOT / 'tools'))
from features import F, GROUPS, STATUS  # noqa: E402

esc = html.escape


def ar(n: int) -> str:
    return str(n).translate(str.maketrans('0123456789', '٠١٢٣٤٥٦٧٨٩'))


def shot_tag(m: re.Match) -> str:
    attrs = dict(re.findall(r'([\w-]+)="([^"]*)"', m.group(1)))
    flags = re.sub(r'([\w-]+)="[^"]*"', '', m.group(1)).split()
    name, alt = attrs['name'], attrs.get('alt', '')
    detail = attrs.get('kind') == 'detail'
    gif = GIF / f'{name}.gif'
    if not detail and 'static' not in flags and gif.exists():
        # لقطة متحرّكة مسجّلة من التطبيق نفسه (تمرير ولمس حقيقي) بدل الصورة الثابتة
        gw, gh = Image.open(gif).size
        extra = ''
        if 'class' in attrs:
            extra += f' class="{attrs["class"]}"'
        if 'data-step' in attrs:
            extra += f' data-step="{attrs["data-step"]}"'
        loading = 'eager" fetchpriority="high' if 'eager' in flags else 'lazy'
        return (f'<img src="assets/gif/{name}.gif" width="{gw}" height="{gh}" alt="{esc(alt)}" '
                f'loading="{loading}" decoding="async"{extra}>')
    widths = (720, 1080) if detail else (540, 1080)
    small = IMG / f'{name}-{widths[0]}.webp'
    if not small.exists():
        raise SystemExit(f'missing image: {small.name}')
    w, h = Image.open(small).size
    srcset = ', '.join(f'assets/img/{name}-{x}.webp {x}w' for x in widths if (IMG / f'{name}-{x}.webp').exists())
    sizes = '(max-width: 900px) 92vw, 560px' if detail else '(max-width: 560px) 70vw, (max-width: 900px) 300px, 360px'
    extra = ''
    if 'class' in attrs:
        extra += f' class="{attrs["class"]}"'
    if 'data-step' in attrs:
        extra += f' data-step="{attrs["data-step"]}"'
    loading = 'eager" fetchpriority="high' if 'eager' in flags else 'lazy'
    return (f'<img src="assets/img/{name}-{widths[0]}.webp" srcset="{srcset}" sizes="{sizes}" '
            f'width="{w}" height="{h}" alt="{esc(alt)}" loading="{loading}" decoding="async"{extra}>')


def features_html() -> str:
    out = ['<div class="index"><nav aria-label="أقسام المميزات"><ol>']
    for gid, gtitle in GROUPS:
        n = sum(1 for f in F if f['g'] == gid)
        out.append(f'<li><a href="#g-{gid}">{esc(gtitle)} <span aria-hidden="true">({ar(n)})</span></a></li>')
    out.append('</ol></nav><div>')
    for gid, gtitle in GROUPS:
        out.append(f'<section class="group" id="g-{gid}" aria-labelledby="g-{gid}-t"><h3 id="g-{gid}-t">{esc(gtitle)}</h3>')
        for f in (x for x in F if x['g'] == gid):
            rows = [('مكانها', f['where']), ('طريقة الاستعمال', f['how']),
                    ('الخيارات', f['options']), ('ما تحتاجه', f['needs']), ('حدودها', f['limits'])]
            dl = ''.join(f'<dt>{esc(k)}</dt><dd>{esc(v)}</dd>' for k, v in rows if v and v != '—')
            thumb = ''
            if f.get('shot') and (IMG / f'{f["shot"]}-540.webp').exists():
                thumb = (f'<div class="thumb"><img src="assets/img/{f["shot"]}-540.webp" '
                         f'srcset="assets/img/{f["shot"]}-540.webp 540w, assets/img/{f["shot"]}-1080.webp 1080w" sizes="140px" width="540" height="1200" '
                         f'loading="lazy" decoding="async" alt="لقطة من التطبيق: {esc(f["t"])}"></div>')
            out.append(
                f'<details class="feature" id="f-{f["id"]}"><summary><span>{esc(f["t"])}</span>'
                f'<span class="sum">{esc(f["benefit"])}</span></summary>'
                f'<div class="body"><dl>{dl}</dl>{thumb}</div></details>')
        out.append('</section>')
    out.append('</div></div>')
    return '\n'.join(out)


def status_html() -> str:
    """قسم «حالة النسخة التجريبية»: مدى التحقق مجمّعًا، بعيدًا عن عرض المميزات."""
    out = ['<div class="status-grid">']
    for k, label in STATUS.items():
        items = [f for f in F if f['status'] == k]
        out.append(f'<div class="status-col {k}"><h3><span class="badge {k}">{ar(len(items))}</span> {esc(label)}</h3><ul>')
        for f in items:
            note = f' <span class="why">— {esc(f["needs"])}</span>' if k == 'device' and f['needs'] != '—' else ''
            out.append(f'<li><a href="#f-{f["id"]}">{esc(f["t"])}</a>{note}</li>')
        out.append('</ul></div>')
    out.append('</div>')
    return '\n'.join(out)


def features_md() -> str:
    lines = ['# مميزات وِرد الموثّقة', '',
             'مصدر هذا الملف `tools/features.py`، وهو نفسه مصدر قسم «كل المميزات» في الصفحة.', '',
             '| الحالة | المعنى |', '|---|---|']
    lines += [f'| `{k}` | {v} |' for k, v in STATUS.items()]
    for gid, gtitle in GROUPS:
        lines += ['', f'## {gtitle}', '', '| الميزة | الحالة | اللقطة | الفائدة | ما تحتاجه | حدودها |', '|---|---|---|---|---|---|']
        for f in (x for x in F if x['g'] == gid):
            shot = f'`{f["shot"]}`' if f.get('shot') else '—'
            lines.append(f'| {f["t"]} | `{f["status"]}` | {shot} | {f["benefit"]} | {f["needs"]} | {f["limits"]} |')
    return '\n'.join(lines) + '\n'


def privacy_html() -> str:
    md = (APP / 'docs' / 'privacy-policy.md').read_text(encoding='utf-8')
    body = []
    for block in re.split(r'\n\s*\n', md.strip()):
        b = block.strip()
        if b.startswith('# '):
            continue
        if b.startswith('## '):
            body.append(f'<h2>{esc(b[3:])}</h2>')
        else:
            text = esc(' '.join(b.split('\n')))
            text = re.sub(r'([\w.+-]+@[\w-]+\.[\w.]+)', r'<a href="mailto:\1">\1</a>', text)
            body.append(f'<p>{text}</p>')
    return f'''<!doctype html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>سياسة الخصوصية — وِرد</title>
<meta name="description" content="سياسة خصوصية تطبيق وِرد: ما يُحفظ على جهازك، وما يُرسل إلى خدمات خارجية عند استعمال بعض الميزات.">
<link rel="icon" href="assets/img/mark.svg" type="image/svg+xml">
<link rel="icon" href="assets/img/icon.png" sizes="192x192">
<link rel="stylesheet" href="assets/css/site.css">
<style>.doc {{ max-width: 760px; padding: 48px 0 80px; }} .doc h1 {{ font-size: clamp(34px, 5vw, 52px); color: var(--teal-deep); margin: 0 0 6px; }}
.doc h2 {{ color: var(--teal-deep); font-size: 22px; margin: 34px 0 8px; }} .doc p {{ color: var(--ink-dim); }}</style>
</head>
<body>
<header class="top"><div class="wrap"><a class="brand" href="./"><img src="assets/img/mark.svg" width="32" height="32" alt="">وِرد</a><nav class="chapters"><a href="./">الصفحة الرئيسية</a></nav></div></header>
<main class="wrap doc">
<h1>سياسة الخصوصية</h1>
<p>هذه السياسة منقولةٌ كما هي من التطبيق.</p>
{chr(10).join(body)}
</main>
</body>
</html>
'''


def main() -> None:
    tpl = (ROOT / 'tools' / 'index.template.html').read_text(encoding='utf-8')
    page = re.sub(r'<x-shot\s+([^>]*)></x-shot>', shot_tag, tpl)
    page = re.sub(r'<!-- FEATURES:START -->.*?<!-- FEATURES:END -->',
                  lambda _: '<!-- FEATURES:START -->\n' + features_html() + '\n<!-- FEATURES:END -->', page, flags=re.S)
    page = re.sub(r'<!-- STATUS:START -->.*?<!-- STATUS:END -->',
                  lambda _: '<!-- STATUS:START -->\n' + status_html() + '\n<!-- STATUS:END -->', page, flags=re.S)
    page = page.replace('{{BASE}}', BASE)
    if '<x-shot' in page or '{{' in page:
        raise SystemExit('unrendered placeholders left')
    (DOCS / 'index.html').write_text(page, encoding='utf-8')
    (DOCS / 'privacy.html').write_text(privacy_html(), encoding='utf-8')
    (ROOT / 'FEATURES.md').write_text(features_md(), encoding='utf-8')
    # أيقونات الموقع من علامة الهوية (mark.svg)، لا من أيقونة التطبيق الحالية (أيقونة Expo الافتراضية)
    (DOCS / '.nojekyll').write_text('', encoding='utf-8')
    print('built index.html, privacy.html, FEATURES.md;', len(F), 'features')


if __name__ == '__main__':
    main()
