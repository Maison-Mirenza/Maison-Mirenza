#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Maison Mirenza — static site generator (shared library).
Governance is applied at BUILD TIME: confidential records are filtered out
before any HTML is written, so private R&D never appears in the DOM.
"""
import json, os, html, shutil, datetime

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "src")
DATA = os.path.join(SRC, "data")
OUT = os.path.join(ROOT, "docs")

# ---------------------------------------------------------------- data
def load(name):
    with open(os.path.join(DATA, name), encoding="utf-8") as f:
        return json.load(f)

SITE = load("site.json")
CATALOG = load("catalog.json")
RESEARCH = load("research.json")
CLAIMS = load("claims.json")
SELECTOR = load("selector.json")
JOURNAL = load("journal.json")
CONTENT = load("content.json")

CLAIM_INDEX = {c["id"]: c for c in CLAIMS.get("claims", [])}
BASE_URL = SITE["seo"]["base_url"].rstrip("/")

# ---------------------------------------------------------------- governance
def claim_is_public(claim):
    return bool(claim) and claim.get("public") is True and claim.get("status") in ("verified", "published")

def public_axes():
    return [a for a in RESEARCH.get("axes", []) if a.get("public") is True]

def public_programs():
    return [p for p in RESEARCH.get("programs", []) if p.get("public") is True]

def published_universes():
    return [u for u in CATALOG.get("universes", []) if u.get("status") == "published"]

def published_families():
    fams = []
    for u in published_universes():
        for fam in u.get("families", []):
            if fam.get("status") == "published":
                fam = dict(fam); fam["_universe"] = u["name"]
                fams.append(fam)
    return fams

def published_products(fam):
    prods = []
    for line in fam.get("lines", []):
        for p in line.get("products", []):
            if p.get("status") == "published":
                p = dict(p); p["_line"] = line["name"]
                prods.append(p)
    return prods

def render_capacity(variant):
    """Return (html_snippet, tag_html). Only shows the ml number when the claim is public+verified/published."""
    claim = CLAIM_INDEX.get(variant.get("publication_claim_id"))
    if claim_is_public(claim):
        num = html.escape(claim["exact_wording"])
        cap = f'<span class="flow-capacity" data-state="validated">{num}</span>'
        tag = '<span class="tag tag--verified">Capacité validée</span>'
    else:
        cap = '<span class="flow-capacity" data-state="pending">Capacité en cours de validation</span>'
        tag = '<span class="tag tag--pending">En validation</span>'
    return cap, tag

# ---------------------------------------------------------------- helpers
def e(s):
    return html.escape(str(s), quote=True)

def rel_for(route):
    segs = [s for s in route.strip("/").split("/") if s]
    return "../" * len(segs)

def linker(rel):
    def L(href):
        if href is None:
            return "#"
        if href.startswith(("http://", "https://", "mailto:", "tel:", "#")):
            return href
        if href.startswith("/"):
            t = rel + href.lstrip("/")
            return t if t else "./"
        return href
    return L

# ---------------------------------------------------------------- SVG posters
def svg_poster(theme="paper", ratio="16x9"):
    w, h = {"16x9": (1280, 720), "4x5": (1000, 1250), "9x16": (720, 1280),
            "4x3": (1200, 900), "1x1": (1000, 1000)}.get(ratio, (1280, 720))
    # (a,b,c gradient stops) , glow color+opacity , motif stroke color+opacity , frame color
    themes = {
        "paper":  ("#EFE9DE", "#DFD3C4", "#C4B2A0", "#7C1F2B", 0.16, "#7C1F2B", 0.10, "#211E1B"),
        "dark":   ("#302B26", "#221E1B", "#171512", "#7C1F2B", 0.30, "#CBB9A8", 0.10, "#FAF8F3"),
        "lab":    ("#252220", "#1A1817", "#111010", "#3C4657", 0.34, "#9FA994", 0.12, "#FAF8F3"),
        "endo":   ("#E9E0D4", "#CDB9A6", "#A98D7C", "#7C1F2B", 0.12, "#7C1F2B", 0.10, "#211E1B"),
        "product":("#8A2531", "#7C1F2B", "#4E1420", "#CDA9A5", 0.22, "#F3EFE7", 0.12, "#F3EFE7"),
        "blush":  ("#E7D6CF", "#D4B7B0", "#B98F89", "#7C1F2B", 0.16, "#7C1F2B", 0.12, "#211E1B"),
    }
    a, b, c, glow, go, motif, mo, frame = themes.get(theme, themes["paper"])
    cx, cy = w * 0.5, h * 0.46
    s = min(w, h) * 0.16
    # A minimal droplet motif (brand signature), thin-stroked, low opacity.
    drop = (f'<path d="M {cx} {cy - s*1.15} '
            f'C {cx + s*0.95} {cy - s*0.15}, {cx + s*0.72} {cy + s}, {cx} {cy + s} '
            f'C {cx - s*0.72} {cy + s}, {cx - s*0.95} {cy - s*0.15}, {cx} {cy - s*1.15} Z" '
            f'fill="none" stroke="{motif}" stroke-opacity="{mo}" stroke-width="1.5"/>')
    ring = f'<circle cx="{cx}" cy="{cy}" r="{s*1.9:.0f}" fill="none" stroke="{motif}" stroke-opacity="{mo*0.6:.3f}" stroke-width="1"/>'
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="Poster de film Maison Mirenza">
<defs>
<linearGradient id="g" x1="0.1" y1="0" x2="0.9" y2="1">
<stop offset="0" stop-color="{a}"/><stop offset="0.55" stop-color="{b}"/><stop offset="1" stop-color="{c}"/>
</linearGradient>
<radialGradient id="r" cx="32%" cy="24%" r="55%">
<stop offset="0" stop-color="{glow}" stop-opacity="{go}"/><stop offset="1" stop-color="{glow}" stop-opacity="0"/>
</radialGradient>
<radialGradient id="v" cx="50%" cy="50%" r="72%">
<stop offset="0.62" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity="0.16"/>
</radialGradient>
<filter id="n"><feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves="2" stitchTiles="stitch"/>
<feColorMatrix type="saturate" values="0"/><feComponentTransfer><feFuncA type="linear" slope="0.05"/></feComponentTransfer>
<feComposite operator="over" in2="SourceGraphic"/></filter>
</defs>
<rect width="{w}" height="{h}" fill="url(#g)"/>
<rect width="{w}" height="{h}" fill="url(#r)"/>
{ring}{drop}
<rect width="{w}" height="{h}" fill="url(#v)"/>
<rect width="{w}" height="{h}" filter="url(#n)" opacity="0.55"/>
<rect x="16" y="16" width="{w-32}" height="{h-32}" fill="none" stroke="{frame}" stroke-opacity="0.14"/>
</svg>'''

def write_poster(name, theme, ratio):
    path = os.path.join(OUT, "assets", "media", name + ".svg")
    with open(path, "w", encoding="utf-8") as f:
        f.write(svg_poster(theme, ratio))

# ---------------------------------------------------------------- film component
def film_frame(cfg, rel, theme="paper", classes=""):
    """Render a film placeholder frame (poster + label). Wires to real video when a src exists."""
    ratio = cfg.get("ratio", "16x9")
    poster = cfg.get("id", "mm_placeholder")
    label = cfg.get("label", "")
    note = cfg.get("note", "")
    src = cfg.get("src")  # real video file, if provided
    poster_url = f'{rel}{cfg["poster_file"]}' if cfg.get("poster_file") else f'{rel}assets/media/{poster}.svg'
    inner = f'<img src="{poster_url}" alt="" loading="lazy" decoding="async">'
    play = ""
    if src:
        inner = (f'<video data-lazy-video muted loop playsinline preload="none" '
                 f'poster="{poster_url}"><source data-src="{rel}assets/media/{e(src)}" type="video/mp4"></video>')
        play = '<button class="film-play" aria-label="Lire le film"><span></span></button>'
    lbl = ""
    if label:
        lbl = (f'<div class="film-label"><span>{e(label)}</span>'
               + (f'<span class="note">{e(note)}</span>' if note else "") + '</div>')
    return (f'<div class="film {classes}" data-ratio="{ratio}" data-theme="{theme}">'
            f'{inner}{play}{lbl}</div>')

# ---------------------------------------------------------------- layout chrome
def head(title, description, rel, canonical, og_type="website", jsonld=None, extra=""):
    seo = SITE["seo"]
    og_image = f'{BASE_URL}/{seo["og_image"]}'
    ld = ""
    if jsonld:
        ld = '<script type="application/ld+json">' + json.dumps(jsonld, ensure_ascii=False) + '</script>'
    return f'''<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<script>document.documentElement.classList.add('js')</script>
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(description)}">
<link rel="canonical" href="{e(canonical)}">
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="Maison Mirenza">
<meta property="og:locale" content="{seo['locale']}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(description)}">
<meta property="og:url" content="{e(canonical)}">
<meta property="og:image" content="{e(og_image)}">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#F3EFE7">
<link rel="icon" href="{rel}assets/media/favicon-32.png" sizes="32x32">
<link rel="icon" href="{rel}assets/media/favicon-512.png" sizes="512x512">
<link rel="apple-touch-icon" href="{rel}assets/media/favicon-180.png">
<link rel="preconnect" href="{BASE_URL}">
<link rel="stylesheet" href="{rel}assets/css/styles.css">
{ld}{extra}
</head>'''

def header(rel, active=""):
    L = linker(rel)
    feats = SITE.get("features", {})
    nav_items = []
    for item in SITE["navigation"]:
        cur = ' aria-current="page"' if item["href"] == active else ""
        nav_items.append(f'<li><a href="{L(item["href"])}"{cur}>{e(item["label"])}</a></li>')
    nav = "".join(nav_items)
    tools = []
    for item in SITE.get("utility_navigation", []):
        feat = item.get("feature")
        if feat and not feats.get(feat, False):
            continue
        cls = ' class="tool--contextual"' if item.get("contextual") else ""
        tools.append(f'<li><a{cls} href="{L(item["href"])}">{e(item["label"])}</a></li>')
    tools_html = "".join(tools)

    # mobile menu items
    mnav = "".join(f'<li><a href="{L(item["href"])}">{e(item["label"])}</a></li>' for item in SITE["navigation"])
    mtools = "".join(
        f'<a href="{L(item["href"])}">{e(item["label"])}</a>'
        for item in SITE.get("utility_navigation", [])
        if not (item.get("feature") and not feats.get(item.get("feature"), False))
    )
    mono = f'<img class="mono" src="{rel}assets/media/monogram.png" alt="" aria-hidden="true">'
    return f'''<a class="skip-link" href="#main">Aller au contenu</a>
<header class="site-header">
  <div class="container nav">
    <a class="brand" href="{L('/')}">{mono}<span>MAISON MIRENZA</span></a>
    <nav class="nav-main" aria-label="Navigation principale"><ul>{nav}</ul></nav>
    <div class="nav-tools">
      <ul>{tools_html}</ul>
      <button class="menu-toggle" data-menu-toggle aria-expanded="false" aria-controls="mobile-menu">Menu</button>
    </div>
  </div>
</header>
<div class="mobile-menu" id="mobile-menu" data-mobile-menu>
  <div class="mobile-menu-top">
    <a class="brand" href="{L('/')}">{mono}<span>MAISON MIRENZA</span></a>
    <button class="menu-close" data-menu-close>Fermer</button>
  </div>
  <nav aria-label="Navigation mobile"><ul>{mnav}</ul>
    <div class="mm-utility">{mtools}</div>
  </nav>
</div>'''

def footer(rel):
    L = linker(rel)
    f = SITE["footer"]
    cols = ""
    for col in f["columns"]:
        links = "".join(f'<a href="{L(x["href"])}">{e(x["label"])}</a>' for x in col["links"])
        cols += f'<div class="footer-col"><strong>{e(col["title"])}</strong>{links}</div>'
    legal_links = "".join(f'<li><a href="{L(x["href"])}">{e(x["label"])}</a></li>' for x in f["legal_links"])
    return f'''<footer class="footer">
  <div class="container">
    <div class="footer-grid">
      <div class="footer-brand">
        <a class="brand" href="{L('/')}"><img class="mono" src="{rel}assets/media/monogram.png" alt="" aria-hidden="true"><span>MAISON MIRENZA</span></a>
        <p class="muted">{e(SITE["brand"]["tagline"])} Une Maison de santé intime et d’innovation, à Paris.</p>
      </div>
      {cols}
    </div>
    <div class="footer-legal">
      <p>{e(f["legal_line"])}</p>
      <ul>{legal_links}</ul>
    </div>
  </div>
</footer>'''

def page(route, title, description, body, *, active="", body_class="", og_type="website", jsonld=None, extra_head="", extra_scripts=""):
    rel = rel_for(route)
    canonical = BASE_URL + "/" + route if route else BASE_URL + "/"
    doc = head(title, description, rel, canonical, og_type, jsonld, extra_head)
    body_attr = f' class="{body_class}"' if body_class else ""
    doc += f'<body{body_attr}>'
    doc += header(rel, active)
    doc += f'<main id="main">{body}</main>'
    doc += footer(rel)
    doc += f'{extra_scripts}<script src="{rel}assets/js/main.js"></script>'
    doc += "</body></html>"
    write_page(route, doc)

def write_page(route, doc):
    if route == "404.html":
        path = os.path.join(OUT, "404.html")
    else:
        d = os.path.join(OUT, route)
        os.makedirs(d, exist_ok=True)
        path = os.path.join(d, "index.html")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(doc)

def section_head(eyebrow, title, body="", single=False, on_lab=False):
    cls = "section-head--single" if single else ""
    right = "" if single else f'<p>{body}</p>'
    left = f'<div><span class="eyebrow">{e(eyebrow)}</span><h2>{title}</h2>{("<p>"+body+"</p>") if single and body else ""}</div>'
    if single:
        return f'<div class="section-head {cls}">{left}</div>'
    return f'<div class="section-head">{left}{right}</div>'
