"""Configure the public URL and structured SEO metadata using only the standard library."""
from pathlib import Path
from urllib.parse import urlsplit
from xml.sax.saxutils import escape as xml_escape
import html
import json
import re
import sys


FAQS = [
    (
        "What does the blue rose (Chando) mean in Ado fan art?",
        "In Japanese flower language, the blue rose (aoi bara) means miracles and dreams come true. It is the signature emblem of Ado and her persona Chando, featured across our Blue Rose Garden tee, Blue Rose Eye sticker and Blue Rose Collage case.",
    ),
    (
        "Is this official Ado merchandise?",
        "No. This is an independent, fan-made art collection illustrated by Oddloop42 and inspired by Ado's Utaite aesthetic. This studio is not affiliated with Ado, Cloud Nine, or Universal Music.",
    ),
    (
        "Are these Ado T-shirts and hoodies good for concert outfits (Hibana / Wish tour)?",
        "Yes. Both the Blue Rose Garden T-shirt and the Neon World Domination pullover hoodie are designed for dark fabrics (black and deep navy) so the cobalt blue roses and neon highlights stand out under venue lighting.",
    ),
    (
        "What products, sizes and phone models are available?",
        "The 8-design collection includes unisex classic and heavyweight T-shirts (S–5XL), pullover hoodies, kiss-cut vinyl stickers in 4 sizes, gallery-grade wall art prints, and fitted cases for iPhone and Samsung Galaxy.",
    ),
    (
        "How do ordering, pricing and international shipping work?",
        "Every design page links to its official Oddloop42 listing on Redbubble, which prints on demand and ships worldwide (US, Canada, Europe, Latin America, Asia and Oceania) with local currency pricing and buyer protection.",
    ),
]


def render_design_page(product, products):
    title = html.escape(product['seo_title'], quote=True)
    desc = html.escape(product['description'], quote=True)
    alt = html.escape(product['alt'], quote=True)
    eyebrow = html.escape(f"{product['category'].upper()} / ADO UTAITE FAN ART")
    name = html.escape(product['name'])
    singular = html.escape(product['singular'])
    intro = html.escape(product['intro'])
    inspiration = html.escape(product['inspiration'])
    advice = html.escape(product['advice'])
    buy_url = html.escape(product['url'], quote=True)
    related = ''.join(
        f'<a href="{p["slug"]}.html">{html.escape(p["name"])} {html.escape(p["singular"])} ↗</a>'
        for p in products
        if p['slug'] != product['slug']
    )
    schema = {
        "@context": "https://schema.org",
        "@type": "ItemPage",
        "name": product['seo_title'],
        "description": product['description'],
        "inLanguage": "en",
        "mainEntity": {
            "@type": "VisualArtwork",
            "name": f"Ado {product['name']} – {product['singular']}",
            "artform": f"Digital Fan Art ({product['category']})",
            "creator": {"@type": "Organization", "name": "Oddloop42"},
            "about": {"@type": "Thing", "name": "Ado (Japanese Utaite Singer)"},
            "sameAs": product['url'],
        },
    }
    return (
        f'<!doctype html><html lang="en"><head><meta charset="utf-8">'
        f'<meta name="viewport" content="width=device-width,initial-scale=1">'
        f'<title>{title}</title>'
        f'<meta name="description" content="{desc}">'
        f'<meta name="robots" content="index,follow,max-image-preview:large">'
        f'<meta name="theme-color" content="#080b13">'
        f'<meta property="og:type" content="article">'
        f'<meta property="og:locale" content="en_US">'
        f'<meta property="og:title" content="{title}">'
        f'<meta property="og:description" content="{desc}">'
        f'<meta name="twitter:card" content="summary_large_image">'
        f'<link rel="icon" href="../assets/favicon.svg" type="image/svg+xml">'
        f'<link rel="stylesheet" href="../assets/style.css">'
        f'<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False)}</script>'
        f'</head><body><a class="skip" href="#content">Skip to content</a>'
        f'<header><a class="brand" href="../index.html" aria-label="Oddloop42, home"><span class="mark">◎</span> ODDLOOP<span class="blue">42</span><small>INDEPENDENT ART STUDIO</small></a>'
        f'<nav aria-label="Main navigation"><a href="../index.html#collection">Collection</a><a href="../index.html#universe">The universe</a><a href="../index.html#faq">FAQ</a></nav>'
        f'<a class="shop-nav" href="https://www.redbubble.com/people/oddloop42/shop?asc=u&collections=4354562" target="_blank" rel="noopener">Redbubble <span>↗</span></a></header>'
        f'<main id="content" class="detail section"><a class="back" href="../index.html#collection">← Back to the Ado fan art collection</a>'
        f'<div class="detail-grid"><img class="detail-image" src="../{html.escape(product["image"], quote=True)}" width="600" height="600" fetchpriority="high" alt="{alt}">'
        f'<div><p class="eyebrow">{eyebrow}</p>'
        f'<h1>Ado<br><em>{name}</em> {singular}</h1>'
        f'<p class="intro">{intro}</p>'
        f'<a class="button" href="{buy_url}" target="_blank" rel="noopener">View {singular} on Redbubble ↗</a>'
        f'<p class="detail-note">Check live pricing, fabric colors, sizes and worldwide shipping options on Redbubble.</p>'
        f'<h2>Artwork &amp; Chando Utaite Inspiration</h2><p>{inspiration}</p>'
        f'<h2>Sizing, Material &amp; Fit Guide</h2><p>{advice}</p>'
        f'<h2>Independent Ado Fan Art by Oddloop42</h2><p>Illustrated in Buenos Aires by Oddloop42 for J-pop, anime and Utaite fans worldwide. This is independent fan-made art inspired by Ado and is not official merchandise.</p>'
        f'</div></div>'
        f'<div class="related"><h2>More Ado Fan Art Designs &amp; Merch</h2><div class="related-links">{related}</div></div></main>'
        f'<footer><a class="brand" href="../index.html">ODDLOOP<span class="blue">42</span></a><p>Independent Utaite &amp; anime digital art studio from Buenos Aires.</p>'
        f'<a href="https://www.redbubble.com/people/oddloop42/shop?asc=u&collections=4354562" target="_blank" rel="noopener">Explore on Redbubble ↗</a>'
        f'<div class="legal">Independent fan art inspired by Ado. This website is not affiliated with Ado and is not an official store. Purchases are fulfilled on Redbubble. © 2026 Oddloop42.</div></footer></body></html>\n'
    )


def configure(base, root):
    parts = urlsplit(base)
    if parts.scheme != 'https' or not parts.hostname or parts.username or parts.password or parts.query or parts.fragment:
        raise ValueError('Provide a public HTTPS URL without credentials, query parameters or fragments.')
    if parts.hostname in ('localhost', '127.0.0.1', '::1'):
        raise ValueError('Use the public GitHub Pages address.')
    base = base.rstrip('/') + '/'
    products = json.loads((root / 'assets/products.json').read_text(encoding='utf-8'))
    by_slug = {p['slug']: p for p in products}

    for p in products:
        design_path = root / 'designs' / f"{p['slug']}.html"
        design_path.write_text(render_design_page(p, products), encoding='utf-8')

    urls = []
    for path in sorted(root.rglob('*.html')):
        relative = path.relative_to(root).as_posix()
        url = base + ('' if relative == 'index.html' else relative)
        urls.append(url)
        product = by_slug.get(path.stem)
        image = base + (product['image'] if product else products[0]['image'])
        source = path.read_text(encoding='utf-8')
        source = re.sub(r'<!-- deployment-seo -->.*?<!-- /deployment-seo -->', '', source, flags=re.S)
        block = (
            '<!-- deployment-seo -->'
            f'<link rel="canonical" href="{html.escape(url, quote=True)}">'
            f'<meta property="og:url" content="{html.escape(url, quote=True)}">'
            f'<meta property="og:image" content="{html.escape(image, quote=True)}">'
            f'<meta name="twitter:image" content="{html.escape(image, quote=True)}">'
            '<!-- /deployment-seo -->'
        )
        source = source.replace('</head>', block + '</head>')

        def update_schema(match):
            data = json.loads(match.group(1))
            if product:
                data['url'] = url
                data['image'] = image
                data['sameAs'] = product['url']
                if 'mainEntity' in data:
                    data['mainEntity']['image'] = image
                    data['mainEntity']['url'] = url
                data['breadcrumb'] = {
                    "@type": "BreadcrumbList",
                    "itemListElement": [
                        {"@type": "ListItem", "position": 1, "name": "Ado Fan Art Merch", "item": base},
                        {"@type": "ListItem", "position": 2, "name": f"Ado {product['name']} {product['singular']}", "item": url},
                    ],
                }
            else:
                data['url'] = url
                data['image'] = image
                data['mainEntity'] = {
                    "@type": "ItemList",
                    "itemListElement": [
                        {
                            "@type": "ListItem",
                            "position": idx,
                            "name": f"Ado {p['name']} {p['singular']}",
                            "url": f"{base}designs/{p['slug']}.html",
                            "image": base + p['image'],
                        }
                        for idx, p in enumerate(products, start=1)
                    ],
                }
                data['subjectOf'] = {
                    "@type": "FAQPage",
                    "mainEntity": [
                        {
                            "@type": "Question",
                            "name": q,
                            "acceptedAnswer": {"@type": "Answer", "text": a},
                        }
                        for q, a in FAQS
                    ],
                }
            return '<script type="application/ld+json">' + json.dumps(data, ensure_ascii=False) + '</script>'

        source = re.sub(r'<script type="application/ld\+json">(.*?)</script>', update_schema, source, flags=re.S)
        path.write_text(source, encoding='utf-8')

    sitemap = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + '\n'.join('<url><loc>' + xml_escape(url) + '</loc></url>' for url in urls)
        + '\n</urlset>\n'
    )
    (root / 'sitemap.xml').write_text(sitemap, encoding='utf-8')
    (root / 'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: ' + base + 'sitemap.xml\n', encoding='utf-8')
    print(f'SEO configured for {base}: {len(urls)} pages.')


if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit('Usage: python configure_seo.py https://USERNAME.github.io/REPOSITORY/')
    configure(sys.argv[1], Path(__file__).resolve().parent)
