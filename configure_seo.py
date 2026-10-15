"""Configure the public URL before deployment using only the standard library."""
from pathlib import Path
from urllib.parse import urlsplit
from xml.sax.saxutils import escape as xml_escape
import html
import json
import re
import sys


def configure(base, root):
    parts = urlsplit(base)
    if parts.scheme != 'https' or not parts.hostname or parts.username or parts.password or parts.query or parts.fragment:
        raise ValueError('Provide a public HTTPS URL without credentials, query parameters or fragments.')
    if parts.hostname in ('localhost', '127.0.0.1', '::1'):
        raise ValueError('Use the public GitHub Pages address.')
    base = base.rstrip('/') + '/'
    products = json.loads((root / 'assets/products.json').read_text(encoding='utf-8'))
    by_slug = {p['slug']: p for p in products}
    urls = []
    for path in sorted(root.rglob('*.html')):
        relative = path.relative_to(root).as_posix()
        url = base + ('' if relative == 'index.html' else relative)
        urls.append(url)
        product = by_slug.get(path.stem)
        image = base + (product['image'] if product else products[0]['image'])
        source = path.read_text(encoding='utf-8')
        source = re.sub(r'<!-- deployment-seo -->.*?<!-- /deployment-seo -->', '', source, flags=re.S)
        block = '<!-- deployment-seo -->' + f'<link rel="canonical" href="{html.escape(url, quote=True)}"><meta property="og:url" content="{html.escape(url, quote=True)}"><meta property="og:image" content="{html.escape(image, quote=True)}"><meta name="twitter:image" content="{html.escape(image, quote=True)}">' + '<!-- /deployment-seo -->'
        source = source.replace('</head>', block + '</head>')
        def update_schema(match):
            data = json.loads(match.group(1))
            if product:
                data['sameAs'] = product['url']
            data['url'] = url
            data['image'] = image
            return '<script type="application/ld+json">' + json.dumps(data, ensure_ascii=False) + '</script>'
        source = re.sub(r'<script type="application/ld\+json">(.*?)</script>', update_schema, source, flags=re.S)
        path.write_text(source, encoding='utf-8')
    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + '\n'.join('<url><loc>' + xml_escape(url) + '</loc></url>' for url in urls) + '\n</urlset>\n'
    (root / 'sitemap.xml').write_text(sitemap, encoding='utf-8')
    (root / 'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: ' + base + 'sitemap.xml\n', encoding='utf-8')
    print(f'SEO configured for {base}: {len(urls)} pages.')


if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit('Usage: python configure_seo.py https://USERNAME.github.io/REPOSITORY/')
    configure(sys.argv[1], Path(__file__).resolve().parent)
