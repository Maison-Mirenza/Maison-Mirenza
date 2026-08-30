#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Maison Mirenza — site build. Run: python3 build.py"""
import os, json, shutil, datetime
from build_lib import (
    SITE, CATALOG, RESEARCH, CLAIMS, SELECTOR, JOURNAL, CONTENT, BASE_URL, OUT, SRC,
    e, rel_for, linker, page, section_head, film_frame, write_poster, svg_poster,
    published_families, published_products, public_axes, public_programs,
    render_capacity, claim_is_public, CLAIM_INDEX,
)

ROUTES_FOR_SITEMAP = []

def reg(route):
    ROUTES_FOR_SITEMAP.append(route)

# ============================================================ HOME
def build_home():
    route = ""; rel = rel_for(route); L = linker(rel)
    c = CONTENT["home"]; h = c["hero"]

    # 01 Hero
    hero = f'''<section class="hero" data-component="brand-film">
  <div class="hero-copy">
    <span class="eyebrow">{e(h["eyebrow"])}</span>
    <h1>{h["title"].replace(chr(10),"<br>")}</h1>
    <p>{e(h["body"])}</p>
    <div class="cta-row">{"".join(f'<a class="cta" href="{L(x["href"])}">{e(x["label"])}</a>' for x in h["ctas"])}</div>
  </div>
  {film_frame(h["film"], rel, theme="paper", classes="hero-media")}
</section>'''

    # 02 Territories
    t = c["territories"]
    terr = "".join(
        f'''<article class="territory" data-reveal><span class="territory-index">{e(i["index"])}</span>
        <div><h3>{e(i["title"])}</h3><p>{e(i["text"])}</p><a class="cta" href="{L(i["href"])}">{e(i["cta"])}</a></div></article>'''
        for i in t["items"])
    s02 = f'''<section class="section"><div class="container">
      {section_head(t["eyebrow"], e(t["title"]), e(t["body"]))}
      <div class="territories" data-component="territories">{terr}</div></div></section>'''

    # 03 Creations (data-driven family grid)
    cr = c["creations"]
    fams = published_families()
    cards = ""
    for i, fam in enumerate(fams):
        poster = fam.get("hero_media", {}).get("film", "mm_period_family_master_16x9_v01")
        cards += f'''<article class="editorial-card editorial-card--wide" data-component="creation-family" data-family="{e(fam['id'])}" data-reveal>
          <a href="{L('/creations/'+fam['slug']+'/')}"><div class="visual visual--landscape"><img src="{rel}assets/media/{e(poster)}.svg" alt="" loading="lazy"><span class="visual-label">{e(fam['_universe'])} / {e(fam['name'])}</span></div></a>
          <span class="eyebrow">{e(fam['_universe'])}</span><h3>{e(fam['name'])}</h3><p>{e(fam.get('tagline',''))}</p>
          <a class="cta" href="{L('/creations/'+fam['slug']+'/')}">Découvrir</a></article>'''
    q = c["questions_objects"]
    cards += f'''<article class="editorial-card editorial-card--narrow" data-reveal>
      {film_frame(q["film"], rel, theme="dark")}
      <span class="eyebrow">{e(q["eyebrow"])}</span><h3>{e(q["title"])}</h3>
      <p>{" · ".join(e(s) for s in q["steps"])}.</p></article>'''
    s03 = f'''<section class="section" id="creations"><div class="container">
      {section_head(cr["eyebrow"], e(cr["title"]), e(cr["body"]))}
      <div class="editorial-grid" data-component="creation-family-grid">{cards}</div></div></section>'''

    # 04 Chapter 01 — period selector engine (governance-aware flow cards)
    p = c["period"]
    # Use the first published family's first product variants as the three levels
    fam = fams[0]
    prod = published_products(fam)[0]
    flow_cards = ""
    for v in prod["variants"]:
        cap, tag = render_capacity(v)
        flow_cards += f'''<article class="flow-card" data-reveal>
          <div><span class="eyebrow">{e(v["label"])}</span><div class="flow-level">{e(v["flow_descriptor"])}</div>{cap}</div>
          <div>{tag}<div class="cut-row"><a class="cta" href="{L('/trouver-ma-protection/')}">Choisir {e(v["label"])}</a></div></div></article>'''
    s04 = f'''<section class="section section--paper2" id="period"><div class="container">
      {section_head(p["eyebrow"], e(p["title"]), e(p["body"]))}
      <div class="flow-grid" data-component="product-selector">{flow_cards}</div>
      <div class="cut-row"><span class="chip">Classic Brief — couvrante</span><span class="chip">Hipster — échancrée</span>
      <a class="btn btn--primary" href="{L('/trouver-ma-protection/')}" style="margin-left:auto">Trouver ma protection</a></div>
    </div></section>'''

    # 06 Lab (charcoal)
    lab = c["lab"]; axes = public_axes()[:6]
    lab_cards = "".join(
        f'<article class="lab-card" data-reveal><span class="eyebrow">{e(a["name"])}</span><p>{e(a["summary"])}</p></article>'
        for a in axes)
    s06 = f'''<section class="section section--lab" data-component="research-axis-grid"><div class="container">
      {section_head(lab["eyebrow"], e(lab["title"]), e(lab["body"]))}
      <div class="lab-grid">{lab_cards}</div>
      <div class="cta-row"><a class="cta" href="{L('/lab/')}">Découvrir Mirenza Lab</a></div></div></section>'''

    # 07 Endometriosis feature
    en = c["endometriosis"]
    s07 = f'''<section class="section" id="endometriosis" data-component="endometriosis-feature"><div class="container">
      <div class="endo-feature">
        <div class="endo-copy"><span class="eyebrow">{e(en["eyebrow"])}</span><h2>{e(en["title"])}</h2>
          <p>{e(en["body"])}</p><a class="cta" href="{L('/endometriose/')}">{e(en["cta"])}</a></div>
        {film_frame(en["film"], rel, theme="endo", classes="endo-media")}
      </div></div></section>'''

    # 08 Proof / method
    pr = c["proof"]
    proof_cards = "".join(
        f'<article class="proof" data-component="evidence-card" data-reveal><span class="proof-state">{e(x["state"])}</span><h3>{e(x["title"])}</h3></article>'
        for x in pr["cards"])
    s08 = f'''<section class="section"><div class="container">
      {section_head(pr["eyebrow"], e(pr["title"]), e(pr["body"]))}
      <div class="proof-grid">{proof_cards}</div>
      <div class="cta-row"><a class="cta" href="{L('/lab/methodes/')}">Voir nos méthodes</a></div></div></section>'''

    # 09 Pharmacy (late, scoped)
    ph = c["pharmacy"]
    s09 = f'''<section class="section section--paper2" id="pharmacy" data-component="pharmacy-access"><div class="container">
      {section_head(ph["eyebrow"], e(ph["title"]), e(ph["body"]))}
      <a class="cta" href="{L('/pharmacie/')}">{e(ph["cta"])}</a></div></section>'''

    # 10 Journal
    jc = c["journal"]
    arts = [a for a in JOURNAL["articles"] if a.get("published")][:3]
    jcards = ""
    for a in arts:
        jcards += journal_card_html(a, rel, L)
    s10 = f'''<section class="section" id="journal"><div class="container">
      {section_head(jc["eyebrow"], e(jc["title"]), e(jc["body"]))}
      <div class="journal-grid">{jcards}</div>
      <div class="cta-row"><a class="cta" href="{L('/journal/')}">Tous les cahiers</a></div></div></section>'''

    # 11 Manifesto
    mf = c["manifesto"]
    s11 = f'''<section class="manifesto"><div class="container">
      <img class="mono-lg" src="{rel}assets/media/monogram.png" alt="Maison Mirenza">
      <h2>{e(mf["title"])}</h2><p class="eyebrow">{e(mf["line"])}</p></div></section>'''

    # 05b Univers en mouvement (films par territoire — vision, non catalogue)
    uf = c.get("univers_films")
    s_films = ""
    if uf:
        film_cards = "".join(film_frame(f, rel, theme="dark") for f in uf["films"])
        s_films = f'''<section class="section section--paper2" id="univers"><div class="container">
      {section_head(uf["eyebrow"], e(uf["title"]), e(uf["body"]))}
      <div class="film-grid" data-component="univers-films">{film_cards}</div></div></section>'''

    jsonld = {
        "@context": "https://schema.org", "@type": "Organization",
        "name": "Maison Mirenza", "url": BASE_URL + "/",
        "logo": BASE_URL + "/assets/media/favicon-512.png",
        "description": SITE["seo"]["default_description"],
        "slogan": SITE["brand"]["tagline"],
        "address": {"@type": "PostalAddress", "addressLocality": "Paris", "addressCountry": "FR"},
    }
    body = hero + s02 + s03 + s04 + s_films + s06 + s07 + s08 + s09 + s10 + s11
    page(route, SITE["seo"]["default_title"], SITE["seo"]["default_description"],
         body, active="/", jsonld=jsonld)
    reg(route)

def journal_card_html(a, rel, L):
    date = datetime.date.fromisoformat(a["date"]).strftime("%d.%m.%Y")
    return f'''<article class="journal-card" data-journal-card data-category="{e(a["category"])}" data-reveal>
      <a href="{L('/journal/'+a["slug"]+'/')}"><div class="visual"><img src="{rel}assets/media/mm_journal_template_4x3.svg" alt="" loading="lazy"></div></a>
      <div class="journal-meta"><span>{e(a["category"])}</span><span class="sep">·</span><span>{a["read_minutes"]} min</span></div>
      <h3><a href="{L('/journal/'+a["slug"]+'/')}">{e(a["title"])}</a></h3>
      <p>{e(a["excerpt"])}</p><span class="eyebrow">{date}</span></article>'''

# ============================================================ CREATIONS INDEX
def build_creations_index():
    route = "creations/"; rel = rel_for(route); L = linker(rel)
    fams = published_families()
    cards = ""
    for fam in fams:
        poster = fam.get("hero_media", {}).get("film", "mm_period_family_master_16x9_v01")
        cards += f'''<article class="editorial-card editorial-card--wide" data-reveal>
          <a href="{L('/creations/'+fam['slug']+'/')}"><div class="visual visual--landscape"><img src="{rel}assets/media/{e(poster)}.svg" alt="" loading="lazy"><span class="visual-label">{e(fam['name'])}</span></div></a>
          <span class="eyebrow">{e(fam['_universe'])}</span><h2>{e(fam['name'])}</h2><p>{e(fam.get('summary',''))}</p>
          <a class="cta" href="{L('/creations/'+fam['slug']+'/')}">Découvrir la famille</a></article>'''
    # honest architecture note (no fake "coming soon")
    cards += f'''<article class="editorial-card editorial-card--narrow" data-reveal>
      <div class="visual visual--dark"><span class="visual-label">Architecture extensible</span></div>
      <span class="eyebrow">Modèle de données</span><h3>Des familles à venir</h3>
      <p>Univers → Famille → Ligne → Produit → Variante → SKU. Les futures familles sont prévues dans les données et ne s’affichent qu’une fois publiées — pas de fausses pages « bientôt ».</p></article>'''
    body = f'''<section class="section"><div class="container">
      <div class="breadcrumb"><a href="{L('/')}">Maison</a><span class="sep">/</span><span>Les Créations</span></div>
      <span class="eyebrow">Les Créations</span><h1>Des objets nés de la recherche.</h1>
      <p class="kicker lead">Un index de familles, piloté par les données. Le site ne rend que les familles publiées.</p>
    </div></section>
    <section class="section section--paper2"><div class="container editorial-grid" data-component="creation-family-grid">{cards}</div></section>'''
    page(route, "Les Créations — Maison Mirenza",
         "Les créations de Maison Mirenza, organisées en familles extensibles. Lingerie menstruelle et futures familles pilotées par les données.",
         body, active="/creations/")
    reg(route)

# ============================================================ FAMILY PAGE
def build_family(fam):
    route = f"creations/{fam['slug']}/"; rel = rel_for(route); L = linker(rel)
    prods = published_products(fam)
    # product cards
    pcards = ""
    art_map = {"classic-brief": "mm_couture_4x5", "hipster": "mm_contour_1x1"}
    for p in prods:
        art = art_map.get(p["slug"], "mm_couture_4x5")
        pcards += f'''<article class="editorial-card" data-reveal>
          <a href="{L('/creations/'+fam['slug']+'/'+p['slug']+'/')}"><div class="visual"><img src="{rel}assets/media/{art}.svg" alt="{e(p['name'])}" loading="lazy"><span class="visual-scrim"></span><span class="visual-label">{e(p['cut'])}</span></div></a>
          <span class="eyebrow">{e(p['_line'])}</span><h3>{e(p['name'])}</h3><p>{e(p['summary'])}</p>
          <a class="cta" href="{L('/creations/'+fam['slug']+'/'+p['slug']+'/')}">Voir {e(p['name'])}</a></article>'''
    # governance-aware level strip
    levels = prods[0]["variants"]
    lvl = ""
    for v in levels:
        cap, tag = render_capacity(v)
        lvl += f'''<article class="flow-card" data-reveal><div><span class="eyebrow">{e(v["label"])}</span>
          <div class="flow-level">{e(v["flow_descriptor"])}</div>{cap}</div><div>{tag}</div></article>'''
    colors = "".join(
        f'<span class="swatch" data-name="{e(c["name"])}" style="background:{e(c["hex"])}"></span>'
        for c in CATALOG["sku_dimensions"]["colors"])
    sizes = " · ".join(e(s) for s in CATALOG["sku_dimensions"]["sizes"])
    hm = dict(fam.get("hero_media", {}))
    # Detail-led hero: the signed elastic, in motion (film) with static poster fallback.
    signature_film = {
        "id": "mm_film_signature_16x9", "ratio": "16x9",
        "src": "mm_film_signature_16x9.mp4",
        "poster_file": "assets/media/mm_film_signature_16x9_poster.jpg",
        "label": "La signature — l’élastique « Maison Mirenza »",
    }
    hero_art = film_frame(signature_film, rel, theme="product")

    body = f'''<section class="section"><div class="container">
      <div class="breadcrumb"><a href="{L('/')}">Maison</a><span class="sep">/</span><a href="{L('/creations/')}">Créations</a><span class="sep">/</span><span>{e(fam['name'])}</span></div>
      <span class="eyebrow">{e(fam.get('eyebrow','Créations'))} — {e(fam['_universe'])}</span>
      <h1>{e(fam['name'])}</h1>
      <p class="lead">{e(fam.get('editorial',''))}</p>
      <div class="cta-row"><a class="btn btn--primary" href="{L('/trouver-ma-protection/')}">Trouver ma protection</a>
        <a class="cta" href="{L('/technologie-menstruelle/')}">La technologie en 4 couches</a></div>
    </div></section>

    <section class="section section--tight"><div class="container">{hero_art}</div></section>

    <section class="section section--paper2"><div class="container">
      {section_head("Trois niveaux", "Choisir par le flux, pas par le chiffre.", "Les capacités chiffrées ne s’affichent qu’après validation. En attendant, chaque niveau est décrit par son usage.")}
      <div class="flow-grid">{lvl}</div></div></section>

    <section class="section"><div class="container">
      {section_head("Deux coupes", "Une même architecture, deux portés.", "Même barrière prolongée, même contour intérieur technique. La coupe est une question de confort.")}
      <div class="editorial-grid" style="grid-template-columns:repeat(2,1fr)">{pcards}</div></div></section>

    <section class="section section--paper2"><div class="container">
      {section_head("Coloris & tailles", "Cinq coloris intemporels. Huit tailles.", "Dont une taille Teen 12–14, pour accompagner tôt.")}
      <div class="swatch-row" style="margin-bottom:2.4rem">{colors}</div>
      <p class="muted">Tailles : {sizes}</p></div></section>'''

    jsonld = {
        "@context": "https://schema.org", "@type": "ProductGroup",
        "name": fam["name"], "brand": {"@type": "Brand", "name": "Maison Mirenza"},
        "description": fam.get("summary", ""),
        "url": BASE_URL + "/" + route,
    }
    page(route, f"{fam['name']} — Maison Mirenza", fam.get("summary",""),
         body, active="/creations/", jsonld=jsonld)
    reg(route)
    for p in prods:
        build_product(fam, p)

# ============================================================ PRODUCT PAGE
def build_product(fam, p):
    route = f"creations/{fam['slug']}/{p['slug']}/"; rel = rel_for(route); L = linker(rel)
    variants = ""
    for v in p["variants"]:
        cap, tag = render_capacity(v)
        variants += f'''<tr><th>{e(v["label"])}</th><td>{e(v["flow_descriptor"])}<br><span class="muted" style="font-size:.82rem">{cap}</span></td></tr>'''
    colors = "".join(
        f'<span class="swatch" data-name="{e(c["name"])}" style="background:{e(c["hex"])}"></span>'
        for c in CATALOG["sku_dimensions"]["colors"])
    sizes = "".join(f'<span class="chip">{e(s)}</span>' for s in CATALOG["sku_dimensions"]["sizes"])
    art_map = {"classic-brief": "mm_couture_4x5", "hipster": "mm_contour_1x1"}
    art = art_map.get(p["slug"], "mm_couture_4x5")
    couture_film = {
        "id": "mm_film_couture_4x5", "ratio": "4x5",
        "src": "mm_film_couture_4x5.mp4",
        "poster_file": "assets/media/mm_film_couture_4x5_poster.jpg",
        "label": "La couture — détail (visuel à photographier)",
    }
    product_media = film_frame(couture_film, rel, theme="product") if p["slug"] == "classic-brief" else (
        f'<div class="visual"><img src="{rel}assets/media/{art}.svg" alt="{e(p["name"])} — détail"><span class="visual-scrim"></span><span class="visual-label">Détail — visuel produit à photographier (tech pack)</span></div>')
    body = f'''<section class="section"><div class="container">
      <div class="breadcrumb"><a href="{L('/')}">Maison</a><span class="sep">/</span><a href="{L('/creations/')}">Créations</a><span class="sep">/</span><a href="{L('/creations/'+fam['slug']+'/')}">{e(fam['name'])}</a><span class="sep">/</span><span>{e(p['name'])}</span></div>
      <div class="product">
        <div class="product-media">{product_media}</div>
        <div class="product-info">
          <span class="eyebrow">{e(fam['name'])} · {e(p['_line'])}</span>
          <h1>{e(p['name'])}</h1>
          <p class="lead">{e(p['summary'])}</p>
          <p class="prose">{e(p['editorial'])}</p>

          <h4>Niveaux d’absorption</h4>
          <table class="spec-table">{variants}</table>

          <h4 style="margin-top:2rem">Coloris</h4>
          <div class="swatch-row">{colors}</div>

          <h4 style="margin-top:2.4rem">Tailles</h4>
          <div class="size-row">{sizes}</div>

          <div class="cta-row"><a class="btn btn--primary" href="{L('/trouver-ma-protection/')}">Trouver ma protection</a>
            <a class="cta" href="{L('/pharmacie/')}">Trouver en pharmacie</a></div>
          <p class="callout" style="margin-top:2rem">Les valeurs d’absorption chiffrées sont des cibles de développement. Elles seront publiées comme allégations une fois validées.</p>
        </div>
      </div>
    </div></section>

    <section class="section section--paper2"><div class="container">
      {section_head("Technologie", "Une architecture en quatre couches.", "Présentée à titre informatif à partir de nos références produit approuvées.")}
      <a class="btn" href="{L('/technologie-menstruelle/')}">Voir la technologie</a></div></section>'''
    jsonld = {
        "@context": "https://schema.org", "@type": "Product",
        "name": f"{p['name']} — {fam['name']}", "brand": {"@type": "Brand", "name": "Maison Mirenza"},
        "category": fam["_universe"], "description": p.get("summary", ""),
        "url": BASE_URL + "/" + route,
    }
    page(route, f"{p['name']} — {fam['name']} — Maison Mirenza", p.get("summary",""),
         body, active="/creations/", og_type="product", jsonld=jsonld)
    reg(route)

# ============================================================ SELECTOR
def build_selector():
    route = "trouver-ma-protection/"; rel = rel_for(route); L = linker(rel)
    fam = published_families()[0]
    product_base = L(f'/creations/{fam["slug"]}/')
    cfg = {
        "steps": SELECTOR["steps"], "logic": SELECTOR["logic"],
        "size_map": SELECTOR["size_map"], "reasons": SELECTOR["reasons"],
    }
    body = f'''<section class="section"><div class="container selector">
      <div class="breadcrumb"><a href="{L('/')}">Maison</a><span class="sep">/</span><a href="{L('/creations/'+fam['slug']+'/')}">{e(fam['name'])}</a><span class="sep">/</span><span>Trouver ma protection</span></div>
      <span class="eyebrow">Trouver ma protection</span>
      <h1 style="font-size:clamp(2.2rem,5vw,4rem)">Le bon choix, en quatre questions.</h1>
      <p class="lead" style="margin-bottom:2.4rem">{e(SELECTOR["intro"])}</p>
      <div data-selector-root data-product-base="{product_base}" data-pharmacy-href="{L('/pharmacie/')}">
        <div class="selector-progress" data-selector-progress aria-hidden="true"></div>
        <div data-selector-steps></div>
        <div class="selector-result" data-selector-result hidden></div>
      </div>
    </div></section>'''
    inline = '<script>window.__MM_SELECTOR__ = ' + json.dumps(cfg, ensure_ascii=False) + ';</script>'
    page(route, "Trouver ma protection — Maison Mirenza",
         "Quatre questions pour identifier le niveau, la coupe et la taille de lingerie menstruelle Maison Mirenza qui vous conviennent.",
         body, active="/creations/", extra_scripts=inline)
    reg(route)

# ============================================================ TECHNOLOGIE
def build_technologie():
    route = "technologie-menstruelle/"; rel = rel_for(route); L = linker(rel)
    t = CONTENT["technologie"]; h = t["hero"]
    layers = "".join(
        f'<div class="layer"><span class="n">{e(l["n"])}</span><div><h3>{e(l["title"])}</h3><p>{e(l["text"])}</p></div></div>'
        for l in t["layers"])
    epaisseurs_film = {
        "id": "mm_film_epaisseurs_4x5", "ratio": "4x5",
        "src": "mm_film_epaisseurs_4x5.mp4",
        "poster_file": "assets/media/mm_film_epaisseurs_4x5_poster.jpg",
        "label": "Les épaisseurs — représentation qualitative",
    }
    body = f'''<section class="section"><div class="container">
      <div class="breadcrumb"><a href="{L('/')}">Maison</a><span class="sep">/</span><a href="{L('/creations/')}">Créations</a><span class="sep">/</span><span>Technologie menstruelle</span></div>
      <span class="eyebrow">{e(h["eyebrow"])}</span><h1>{e(h["title"])}</h1>
      <p class="lead">{e(h["body"])}</p></div></section>

    <section class="section section--tight"><div class="container">
      <div class="film-solo">{film_frame(epaisseurs_film, rel, theme="dark")}</div>
      <p class="figure-note">Les épaisseurs — représentation qualitative. Aucune valeur chiffrée n’est publiée avant validation.</p></div></section>

    <section class="section section--paper2"><div class="container">
      {section_head("Quatre couches", "Chaque couche, une fonction.", "Un système pensé pour la sécurité, la discrétion et le confort — sans revendication non validée.")}
      <div class="layer-list">{layers}</div>
      <p class="figure-note">{e(t["note"])}</p>
      <div class="cta-row"><a class="btn btn--primary" href="{L('/trouver-ma-protection/')}">Trouver ma protection</a></div></div></section>'''
    page(route, "Technologie menstruelle — Maison Mirenza",
         "La technologie de protection en quatre couches des lingeries menstruelles Maison Mirenza, présentée à titre informatif.",
         body, active="/creations/")
    reg(route)

# ============================================================ LAB INDEX
def build_lab():
    route = "lab/"; rel = rel_for(route); L = linker(rel)
    lp = CONTENT["lab_page"]; h = lp["hero"]
    axes = public_axes()
    axcards = "".join(
        f'<article class="lab-card" data-reveal><span class="eyebrow">{str(i+1).zfill(2)}</span><h3>{e(a["name"])}</h3><p>{e(a["summary"])}</p></article>'
        for i, a in enumerate(axes))
    methods = RESEARCH["methods"]
    msteps = "".join(
        f'<div class="method-step"><span class="n">{str(i+1).zfill(2)}</span><h3>{e(m["label"])}</h3><p>{e(m["text"])}</p></div>'
        for i, m in enumerate(methods))
    body = f'''<section class="hero hero--lab" data-component="brand-film">
      <div class="hero-copy"><span class="eyebrow">{e(h["eyebrow"])}</span><h1>{e(h["title"])}</h1><p>{e(h["body"])}</p>
        <div class="cta-row"><a class="cta" href="{L('/lab/programmes/')}">Voir les programmes</a><a class="cta" href="{L('/lab/methodes/')}">Nos méthodes</a></div></div>
      {film_frame(h["film"], rel, theme="lab", classes="hero-media")}</section>

    <section class="section section--lab" data-component="research-axis-grid"><div class="container">
      {section_head("Axes de recherche", "Observer. Formuler. Tester. Documenter.", e(RESEARCH["manifesto"]))}
      <div class="lab-grid">{axcards}</div></div></section>

    <section class="section section--lab section--tight"><div class="container">
      {section_head("Méthode", "De la question au prototype.")}
      <div class="method-list">{msteps}</div></div></section>

    <section class="section"><div class="container">
      {section_head("De la question au prototype", e(lp["method"]["title"]), e(lp["method"]["body"]))}
      <div class="cta-row"><a class="cta" href="{L('/lab/programmes/')}">Explorer les programmes publics</a>'''
    if SITE["features"].get("enable_lab_publications"):
        body += f'<a class="cta" href="{L("/lab/publications/")}">Publications</a>'
    body += '</div></div></section>'
    page(route, "Mirenza Lab — Maison Mirenza",
         "Mirenza Lab : recherche appliquée à la matière, à l’usage, au confort, à la performance, à la durabilité et à la santé intime.",
         body, active="/lab/")
    reg(route)

# ============================================================ LAB PROGRAMS (public only)
def build_lab_programs():
    route = "lab/programmes/"; rel = rel_for(route); L = linker(rel)
    progs = public_programs()
    cards = ""
    for p in progs:
        partners = ", ".join(p.get("partners", [])) or "—"
        cards += f'''<article class="program-card" data-component="research-program-card" data-reveal>
          <span class="status">{e(p.get("status",""))}</span>
          <h3>{e(p["name"])}</h3>
          <p class="objective">{e(p.get("objective", p.get("public_wording","")))}</p>
          <div class="program-meta"><span class="eyebrow">Calendrier : {e(p.get("timeline","—"))}</span><span class="eyebrow">Partenaires : {e(partners)}</span></div></article>'''
    note = f'''<p class="callout">Seuls les programmes marqués <code>public=true</code> apparaissent ici. {len([x for x in RESEARCH["programs"] if not x.get("public")])} programme(s) confidentiel(s) existent dans les données internes et ne sont jamais rendus dans cette page.</p>'''
    body = f'''<section class="section"><div class="container">
      <div class="breadcrumb"><a href="{L('/')}">Maison</a><span class="sep">/</span><a href="{L('/lab/')}">Mirenza Lab</a><span class="sep">/</span><span>Programmes</span></div>
      <span class="eyebrow">Programmes de recherche</span><h1>Ce que nous étudions, publiquement.</h1>
      <p class="lead">Chaque programme est présenté avec son statut, son objectif et ses partenaires autorisés.</p></div></section>
    <section class="section section--paper2"><div class="container">
      <div class="program-grid">{cards}</div>{note}</div></section>'''
    page(route, "Programmes de recherche — Mirenza Lab",
         "Les programmes de recherche publics de Mirenza Lab, présentés avec leur statut et leurs partenaires autorisés.",
         body, active="/lab/")
    reg(route)

# ============================================================ LAB METHODS
def build_lab_methods():
    route = "lab/methodes/"; rel = rel_for(route); L = linker(rel)
    methods = RESEARCH["methods"]
    steps = "".join(
        f'<div class="method-step"><span class="n">{str(i+1).zfill(2)}</span><h3>{e(m["label"])}</h3><p>{e(m["text"])}</p></div>'
        for i, m in enumerate(methods))
    body = f'''<section class="hero hero--lab"><div class="hero-copy">
      <div class="breadcrumb" style="opacity:.6"><a href="{L('/')}">Maison</a><span class="sep">/</span><a href="{L('/lab/')}">Lab</a><span class="sep">/</span><span>Méthodes</span></div>
      <span class="eyebrow">Méthodes</span><h1>Comment nous travaillons.</h1>
      <p>Un cycle reproductible. Nous ne publions une valeur qu’après l’avoir validée.</p></div>
      {film_frame(CONTENT["lab_page"]["hero"]["film"], rel, theme="lab", classes="hero-media")}</section>
    <section class="section section--lab"><div class="container">
      <div class="method-list">{steps}</div></div></section>
    <section class="section section--lab section--tight"><div class="container">
      <p class="callout" style="border-color:var(--sage);color:var(--warm-white)">Une activité de recherche n’est pas une allégation produit. Un prototype n’est pas un produit validé. Un partenariat n’est pas une preuve d’efficacité.</p></div></section>'''
    page(route, "Méthodes — Mirenza Lab",
         "Observer, formuler, tester, comparer, documenter, recommencer : la méthode de recherche de Mirenza Lab.",
         body, active="/lab/")
    reg(route)

# ============================================================ LAB PUBLICATIONS
def build_lab_publications():
    if not SITE["features"].get("enable_lab_publications"):
        return
    route = "lab/publications/"; rel = rel_for(route); L = linker(rel)
    body = f'''<section class="section"><div class="container">
      <div class="breadcrumb"><a href="{L('/')}">Maison</a><span class="sep">/</span><a href="{L('/lab/')}">Lab</a><span class="sep">/</span><span>Publications</span></div>
      <span class="eyebrow">Publications & résultats</span><h1>Ce qui peut être publié.</h1>
      <p class="lead">Les résultats sont publiés lorsque leur niveau de preuve et leur statut le permettent.</p>
      <div class="callout" style="margin-top:2.4rem">Aucune publication n’est encore rendue publique. Les prochains résultats validés paraîtront ici, avec leur méthode et leurs limites.</div>
      <div class="cta-row"><a class="cta" href="{L('/journal/')}">Lire le Journal de recherche</a></div></div></section>'''
    page(route, "Publications — Mirenza Lab",
         "Les publications et résultats validés de Mirenza Lab.", body, active="/lab/")
    reg(route)

# ============================================================ ENDOMETRIOSE HUB
def build_endometriose():
    if not SITE["features"].get("enable_endometriosis"):
        return
    route = "endometriose/"; rel = rel_for(route); L = linker(rel)
    en = CONTENT["endometriose"]; h = en["hero"]; ap = en["approach"]; un = en["understand"]; st = en["study"]; pa = en["participate"]
    steps = "".join(
        f'<article class="territory" data-reveal><span class="territory-index">{e(s["index"])}</span><div><h3>{e(s["title"])}</h3><p>{e(s["text"])}</p></div></article>'
        for s in ap["steps"])
    study_items = "".join(f'<li>{e(x)}</li>' for x in st["items"])
    # public endo program
    endo_prog = next((p for p in public_programs() if p["id"] == "endo-program"), None)
    prog_html = ""
    if endo_prog:
        prog_html = f'''<article class="program-card" data-reveal><span class="status">{e(endo_prog.get("status",""))}</span>
          <h3>{e(endo_prog["name"])}</h3><p class="objective">{e(endo_prog.get("public_wording",""))}</p>
          <div class="program-meta"><span class="eyebrow">Calendrier : {e(endo_prog.get("timeline","En cours"))}</span></div></article>'''
    part = ""
    if SITE["features"].get("enable_research_participation"):
        part = f'<div class="cta-row"><a class="btn btn--primary" href="mailto:{e(SITE["brand"]["research_email"])}">{e(pa["cta"])}</a></div>'
    else:
        part = f'<div class="cta-row"><a class="cta" href="{L("/journal/")}">Suivre nos travaux dans le Journal</a></div>'

    body = f'''<section class="hero" data-component="endometriosis-feature">
      <div class="hero-copy"><span class="eyebrow">{e(h["eyebrow"])}</span><h1>{e(h["title"])}</h1><p>{e(h["body"])}</p></div>
      {film_frame(h["film"], rel, theme="endo", classes="hero-media")}</section>

    <section class="section"><div class="container">
      {section_head(ap["eyebrow"], e(ap["title"]), e(ap["body"]))}
      <div class="territories">{steps}</div></div></section>

    <section class="section section--paper2"><div class="container">
      {section_head(un["eyebrow"], e(un["title"]))}
      <div class="prose">{"".join(f"<p>{e(p)}</p>" for p in un["paragraphs"])}</div>
      <p class="callout">{e(un["note"])}</p></div></section>

    <section class="section"><div class="container">
      {section_head(st["eyebrow"], e(st["title"]), "À utiliser comme structure de recherche, jamais comme promesse clinique.")}
      <ul class="list-clean" style="max-width:52ch">{study_items}</ul></div></section>

    <section class="section section--paper2" data-component="research-program-card"><div class="container">
      {section_head("Programmes de recherche", "Recherche en cours.", "Les partenaires, calendriers et résultats apparaissent seulement lorsque leur publication est autorisée.")}
      <div class="program-grid">{prog_html}</div>
      <div class="cta-row" style="margin-top:2rem"><a class="cta" href="{L('/endometriose/recherche/')}">Détail de notre axe de recherche</a></div></div></section>

    <section class="section"><div class="container">
      {section_head(pa["eyebrow"], e(pa["title"]), e(pa["body"]))}
      {part}</div></section>'''
    jsonld = {"@context": "https://schema.org", "@type": "MedicalWebPage",
              "name": "Endométriose — Maison Mirenza", "about": {"@type": "MedicalCondition", "name": "Endométriose"},
              "url": BASE_URL + "/" + route}
    page(route, "Endométriose — Maison Mirenza",
         "L’axe de recherche et de développement de Maison Mirenza consacré aux besoins liés à l’endométriose.",
         body, active="/endometriose/", jsonld=jsonld)
    reg(route)
    build_endometriose_recherche()

def build_endometriose_recherche():
    route = "endometriose/recherche/"; rel = rel_for(route); L = linker(rel)
    endo_prog = next((p for p in public_programs() if p["id"] == "endo-program"), None)
    prog_html = ""
    if endo_prog:
        prog_html = f'''<article class="program-card" data-reveal><span class="status">{e(endo_prog.get("status",""))}</span>
          <h3>{e(endo_prog["name"])}</h3><p class="objective">{e(endo_prog.get("objective",""))}</p>
          <div class="program-meta"><span class="eyebrow">Niveau de divulgation : {e(endo_prog.get("disclosure_level","—"))}</span><span class="eyebrow">Calendrier : {e(endo_prog.get("timeline","En cours"))}</span></div></article>'''
    body = f'''<section class="section"><div class="container">
      <div class="breadcrumb"><a href="{L('/')}">Maison</a><span class="sep">/</span><a href="{L('/endometriose/')}">Endométriose</a><span class="sep">/</span><span>Recherche</span></div>
      <span class="eyebrow">Recherche Endométriose</span><h1>Chercher, tester, documenter.</h1>
      <p class="lead">Notre rôle n’est pas de promettre avant de savoir. Nous présentons ici l’axe de recherche tel qu’il peut être rendu public aujourd’hui.</p></div></section>
    <section class="section section--paper2"><div class="container">
      {section_head("Programme", "Ce qui peut être rendu public.")}
      <div class="program-grid">{prog_html}</div>
      <p class="callout" style="margin-top:2rem">Aucun effet thérapeutique n’est revendiqué. Les mentions « traite », « soulage » ou « dispositif médical » sont exclues par défaut, tant qu’un statut réglementaire et scientifique adapté n’est pas établi.</p></div></section>'''
    page(route, "Recherche Endométriose — Maison Mirenza",
         "Le détail de l’axe de recherche endométriose de Maison Mirenza, présenté selon son niveau de divulgation autorisé.",
         body, active="/endometriose/")
    reg(route)

# ============================================================ MISSION / MAISON / CONTACT / PHARMACY / JOURNAL / LEGAL
def build_mission():
    route = "mission/"; rel = rel_for(route); L = linker(rel)
    m = CONTENT["mission"]; h = m["hero"]
    pillars = "".join(
        f'<article class="territory" data-reveal><span class="territory-index">{str(i+1).zfill(2)}</span><div><h3>{e(p["title"])}</h3><p>{e(p["text"])}</p></div></article>'
        for i, p in enumerate(m["pillars"]))
    body = f'''<section class="section"><div class="container">
      <div class="breadcrumb"><a href="{L('/')}">Maison</a><span class="sep">/</span><span>Notre mission</span></div>
      <span class="eyebrow">{e(h["eyebrow"])}</span><h1>{h["title"].replace(chr(10),"<br>")}</h1>
      <p class="lead">{e(h["body"])}</p></div></section>
    <section class="section section--paper2"><div class="container"><div class="territories">{pillars}</div></div></section>
    <section class="manifesto"><div class="container"><img class="mono-lg" src="{rel}assets/media/monogram.png" alt=""><h2>Construire une Maison avant une boutique.</h2><p class="eyebrow">Construire un système de recherche avant des arguments.</p></div></section>'''
    page(route, "Notre mission — Maison Mirenza",
         "La mission de Maison Mirenza : faire progresser la santé intime féminine par la recherche appliquée.",
         body, active="/mission/")
    reg(route)

def build_maison():
    route = "maison/"; rel = rel_for(route); L = linker(rel)
    m = CONTENT["maison"]; h = m["hero"]
    secs = ""
    for i, s in enumerate(m["sections"]):
        cls = "section--paper2" if i % 2 else ""
        secs += f'''<section class="section {cls}"><div class="container">
          {section_head(s["eyebrow"], e(s["title"]), e(s["body"]))}</div></section>'''
    body = f'''<section class="hero">
      <div class="hero-copy"><span class="eyebrow">{e(h["eyebrow"])}</span><h1>{h["title"].replace(chr(10),"<br>")}</h1><p>{e(h["body"])}</p>
        <div class="cta-row"><a class="cta" href="{L('/creations/')}">Nos créations</a><a class="cta" href="{L('/lab/')}">Notre recherche</a></div></div>
      {film_frame({"id":"mm_house_still_material_4x5_v01","ratio":"4x5","label":"Maison — matière & recherche"}, rel, theme="paper", classes="hero-media")}</section>
    {secs}'''
    page(route, "La Maison — Maison Mirenza",
         "Maison Mirenza : une culture de recherche et du détail, au service de la santé intime féminine.",
         body, active="/maison/")
    reg(route)

def build_contact():
    route = "contact/"; rel = rel_for(route); L = linker(rel)
    c = CONTENT["contact"]; h = c["hero"]
    channels = "".join(
        f'<div class="channel"><h3>{e(ch["title"])}</h3><a href="mailto:{e(ch["detail"])}">{e(ch["detail"])}</a></div>'
        for ch in c["channels"])
    body = f'''<section class="section"><div class="container">
      <div class="breadcrumb"><a href="{L('/')}">Maison</a><span class="sep">/</span><span>Contact</span></div>
      <span class="eyebrow">{e(h["eyebrow"])}</span><h1>{e(h["title"])}</h1>
      <p class="lead" style="margin-bottom:2.6rem">{e(h["body"])}</p>
      <div class="contact-grid">
        <form onsubmit="return false" aria-label="Formulaire de contact (démonstration)">
          <div class="field"><label for="n">Nom</label><input id="n" name="name" autocomplete="name"></div>
          <div class="field"><label for="em">Email</label><input id="em" type="email" name="email" autocomplete="email"></div>
          <div class="field"><label for="msg">Message</label><textarea id="msg" name="message" rows="5"></textarea></div>
          <button class="btn btn--primary" type="submit">Envoyer</button>
          <p class="figure-note">Démonstration statique : connectez un service de formulaire (ex. Formspree) ou un back-end pour l’activer.</p>
        </form>
        <div><div class="channel-list">{channels}</div></div>
      </div></div></section>'''
    page(route, "Contact — Maison Mirenza", "Écrire à Maison Mirenza : informations, recherche et presse.",
         body, active="/maison/")
    reg(route)

def build_pharmacie():
    if not SITE["features"].get("enable_pharmacy"):
        return
    route = "pharmacie/"; rel = rel_for(route); L = linker(rel)
    ph = CONTENT["pharmacie"]; h = ph["hero"]; r = ph["reimbursement"]
    steps = "".join(
        f'<div class="pharmacy-step"><span class="n">{e(s["n"])}</span><h3>{e(s["title"])}</h3><p>{e(s["text"])}</p></div>'
        for s in ph["steps"])
    conds = "".join(f'<li>{e(x)}</li>' for x in r["conditions"])
    body = f'''<section class="section"><div class="container">
      <div class="breadcrumb"><a href="{L('/')}">Maison</a><span class="sep">/</span><span>En pharmacie</span></div>
      <span class="eyebrow">{e(h["eyebrow"])}</span><h1>{e(h["title"])}</h1>
      <p class="lead">{e(h["body"])}</p></div></section>

    <section class="section section--tight"><div class="container">
      <div class="visual visual--landscape"><img src="{rel}assets/reference/packaging_bordeaux.png" alt="Emballage Maison Mirenza — culotte menstruelle, disponible en pharmacie" loading="lazy"></div></div></section>

    <section class="section section--paper2"><div class="container">
      {section_head("Le parcours", "Simple, discret, sans ordonnance.")}
      <div class="pharmacy-steps">{steps}</div></div></section>

    <section class="section"><div class="container">
      {section_head("Prise en charge", e(r["title"]))}
      <div class="reimbursement">
        <p>{e(r["text"])}</p>
        <ul class="list-clean">{conds}</ul>
        <p class="disclaimer">{e(r["disclaimer"])}</p>
      </div></div></section>'''
    page(route, "En pharmacie — Maison Mirenza",
         "Accès en pharmacie des lingeries menstruelles Maison Mirenza, sans ordonnance, et informations de prise en charge sous conditions.",
         body, active="/pharmacie/")
    reg(route)

def build_journal():
    if not SITE["features"].get("enable_journal"):
        return
    route = "journal/"; rel = rel_for(route); L = linker(rel)
    arts = [a for a in JOURNAL["articles"] if a.get("published")]
    cats = sorted(set(a["category"] for a in arts))
    filters = '<button class="filter active" data-filter="all">Tout</button>' + "".join(
        f'<button class="filter" data-filter="{e(c)}">{e(c)}</button>' for c in cats)
    cards = "".join(journal_card_html(a, rel, L) for a in arts)
    body = f'''<section class="section"><div class="container">
      <div class="breadcrumb"><a href="{L('/')}">Maison</a><span class="sep">/</span><span>Journal</span></div>
      <span class="eyebrow">Les Cahiers Mirenza</span><h1>Matière, recherche, santé féminine.</h1>
      <p class="lead" style="margin-bottom:2.4rem">Santé menstruelle, endométriose, matières, recherche, innovation et coulisses de la Maison.</p>
      <div class="journal-filters">{filters}</div>
      <div class="journal-grid">{cards}</div></div></section>'''
    page(route, "Journal — Les Cahiers Mirenza", "Le journal de Maison Mirenza : santé menstruelle, endométriose, matières et recherche.",
         body, active="/journal/")
    reg(route)
    for a in arts:
        build_article(a)

FR_MONTHS = ["", "janvier", "février", "mars", "avril", "mai", "juin",
             "juillet", "août", "septembre", "octobre", "novembre", "décembre"]

def build_article(a):
    route = f"journal/{a['slug']}/"; rel = rel_for(route); L = linker(rel)
    d = datetime.date.fromisoformat(a["date"])
    date = f"{d.day} {FR_MONTHS[d.month]} {d.year}"
    paras = "".join(f'<p>{e(p)}</p>' for p in a["body"])
    body = f'''<section class="section"><div class="container article">
      <div class="breadcrumb"><a href="{L('/')}">Maison</a><span class="sep">/</span><a href="{L('/journal/')}">Journal</a><span class="sep">/</span><span>{e(a["category"])}</span></div>
      <div class="article-header"><div class="journal-meta"><span>{e(a["category"])}</span><span class="sep">·</span><span>{a["read_minutes"]} min</span><span class="sep">·</span><span>{date}</span></div>
      <h1>{e(a["title"])}</h1><p class="lead">{e(a["excerpt"])}</p></div>
      <div class="article-body">{paras}</div>
      <div class="cta-row" style="margin-top:3rem"><a class="cta" href="{L('/journal/')}">Retour au Journal</a></div>
    </div></section>'''
    jsonld = {"@context": "https://schema.org", "@type": "Article", "headline": a["title"],
              "datePublished": a["date"], "author": {"@type": "Organization", "name": "Maison Mirenza"},
              "publisher": {"@type": "Organization", "name": "Maison Mirenza"},
              "articleSection": a["category"], "url": BASE_URL + "/" + route}
    page(route, f'{a["title"]} — Journal Maison Mirenza', a["excerpt"], body,
         active="/journal/", og_type="article", jsonld=jsonld)
    reg(route)

def build_legal():
    for slug, doc in CONTENT["legal"].items():
        route = f"{slug}/"; rel = rel_for(route); L = linker(rel)
        secs = "".join(f'<h2 style="font-size:clamp(1.4rem,3vw,2rem)">{e(s["h"])}</h2><p class="prose">{e(s["p"])}</p>' for s in doc["sections"])
        body = f'''<section class="section"><div class="container" style="max-width:52rem">
          <div class="breadcrumb"><a href="{L('/')}">Maison</a><span class="sep">/</span><span>{e(doc["title"])}</span></div>
          <span class="eyebrow">Informations</span><h1 style="font-size:clamp(2rem,4vw,3.4rem)">{e(doc["title"])}</h1>
          <div class="prose" style="margin-top:2rem">{secs}</div></div></section>'''
        page(route, f'{doc["title"]} — Maison Mirenza', doc["title"], body)
        reg(route)

def build_404():
    rel = ""  # served from root; use root-absolute-safe inline
    L = linker("/")
    body = f'''<section class="section" style="min-height:70svh;display:flex;align-items:center"><div class="container" style="text-align:center">
      <span class="eyebrow">Erreur 404</span>
      <h1 style="margin-top:.4rem">Cette page n’existe pas.</h1>
      <p class="lead" style="margin:1rem auto 2rem">Le lien est peut-être ancien, ou la page n’est pas encore publiée.</p>
      <div class="cta-row" style="justify-content:center"><a class="btn btn--primary" href="/">Retour à la Maison</a><a class="cta" href="/creations/">Les Créations</a></div></div></section>'''
    # 404 must resolve assets regardless of base path -> use root-absolute
    critical = ('body{margin:0;background:#F3EFE7;color:#211E1B;'
                'font-family:"Suisse Intl","Helvetica Neue",Arial,sans-serif;line-height:1.5}'
                '.container{width:min(calc(100% - 48px),1320px);margin-inline:auto}'
                '.eyebrow{font-size:.8rem;letter-spacing:.16em;text-transform:uppercase;opacity:.7}'
                'h1{font-weight:400;font-size:clamp(2.4rem,6vw,4rem);letter-spacing:-.03em;margin:.3em 0}'
                '.lead{font-size:1.25rem;max-width:40ch}'
                'a{color:inherit}.btn{display:inline-flex;align-items:center;min-height:52px;padding:.9rem 1.6rem;'
                'border:1px solid #211E1B;border-radius:2px;text-decoration:none;background:#211E1B;color:#F3EFE7}'
                '.cta{display:inline-flex;text-decoration:none;border-bottom:1px solid currentColor;padding:.4rem 0}'
                '.cta-row{display:flex;gap:24px;flex-wrap:wrap;justify-content:center;margin-top:2rem}'
                '.site-header{border-bottom:1px solid rgba(33,30,27,.16)}'
                '.nav{min-height:76px;display:flex;align-items:center;justify-content:space-between}'
                '.brand{display:inline-flex;align-items:center;gap:.6rem;font-size:.8rem;letter-spacing:.2em;text-decoration:none}')
    doc = f'''<!doctype html><html lang="fr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Page introuvable — Maison Mirenza</title>
<meta name="robots" content="noindex">
<style>{critical}</style>
<link rel="icon" href="/assets/media/favicon-32.png"><link rel="stylesheet" href="/assets/css/styles.css"></head>
<body>{header_for_404()}<main id="main">{body}</main><script src="/assets/js/main.js"></script></body></html>'''
    from build_lib import write_page
    write_page("404.html", doc)

def header_for_404():
    # minimal header with root-absolute links
    return '''<header class="site-header"><div class="container nav">
    <a class="brand" href="/"><img class="mono" src="/assets/media/monogram.png" alt="" aria-hidden="true"><span>MAISON MIRENZA</span></a>
    <nav class="nav-main" aria-label="Navigation principale"><ul>
    <li><a href="/creations/">Les Créations</a></li><li><a href="/lab/">Mirenza Lab</a></li>
    <li><a href="/endometriose/">Endométriose</a></li><li><a href="/maison/">La Maison</a></li></ul></nav>
    <div class="nav-tools"><ul><li><a href="/journal/">Journal</a></li></ul></div></div></header>'''

# ============================================================ ASSETS + DEPLOY
def copy_assets():
    # css
    css_out = os.path.join(OUT, "assets", "css"); os.makedirs(css_out, exist_ok=True)
    shutil.copy(os.path.join(SRC, "css", "tokens.css"), os.path.join(css_out, "tokens.css"))
    shutil.copy(os.path.join(SRC, "css", "styles.css"), os.path.join(css_out, "styles.css"))
    # js
    js_out = os.path.join(OUT, "assets", "js"); os.makedirs(js_out, exist_ok=True)
    shutil.copy(os.path.join(SRC, "js", "main.js"), os.path.join(js_out, "main.js"))
    # media (favicons, monogram, og) + generated posters
    media_out = os.path.join(OUT, "assets", "media"); os.makedirs(media_out, exist_ok=True)
    for fn in os.listdir(os.path.join(SRC, "media")):
        shutil.copy(os.path.join(SRC, "media", fn), os.path.join(media_out, fn))
    # reference images (approved brand assets)
    ref_src = os.path.join(SRC, "reference")
    ref_out = os.path.join(OUT, "assets", "reference"); os.makedirs(ref_out, exist_ok=True)
    for fn in ("packaging_bordeaux.png", "logo_gold.png"):
        shutil.copy(os.path.join(ref_src, fn), os.path.join(ref_out, fn))
    # product_technology_reference.jpeg has ml figures baked in → kept in source, NOT shipped publicly (governance).
    # fonts readme placeholder
    fonts_out = os.path.join(OUT, "assets", "fonts"); os.makedirs(fonts_out, exist_ok=True)
    with open(os.path.join(fonts_out, "README.md"), "w", encoding="utf-8") as f:
        f.write("# Suisse Intl\nPlacez ici les fichiers WOFF2 licenciés (SuisseIntl-Regular.woff2, SuisseIntl-Medium.woff2)\n"
                "puis dé-commentez les @font-face dans assets/css/tokens.css.\n")

def generate_posters():
    posters = [
        ("mm_house_manifesto_loop_16x9_v01", "paper", "16x9"),
        ("mm_house_still_material_4x5_v01", "paper", "4x5"),
        ("mm_creations_questions_objects_master_16x9_v01", "dark", "16x9"),
        ("mm_lab_invisible_master_16x9_v01", "lab", "16x9"),
        ("mm_endo_research_master_16x9_v01", "endo", "16x9"),
        ("mm_period_family_master_16x9_v01", "product", "16x9"),
        ("mm_pharmacy_journey_master_16x9_v01", "paper", "16x9"),
        ("mm_period_classic-brief_front_3x4", "product", "4x3"),
        ("mm_period_hipster_front_3x4", "blush", "4x3"),
        ("mm_journal_template_4x3", "paper", "4x3"),
    ]
    os.makedirs(os.path.join(OUT, "assets", "media"), exist_ok=True)
    for name, theme, ratio in posters:
        write_poster(name, theme, ratio)

def write_public_data():
    """Ship only public-filtered data for transparency; confidential records are stripped."""
    out = os.path.join(OUT, "data"); os.makedirs(out, exist_ok=True)
    pub_research = {
        "manifesto": RESEARCH.get("manifesto"),
        "axes": public_axes(),
        "methods": RESEARCH.get("methods", []),
        "programs": [{k: v for k, v in p.items()} for p in public_programs()],
        "rule": RESEARCH.get("rule"),
    }
    pub_claims = {"claims": [c for c in CLAIMS["claims"] if claim_is_public(c)]}

    # Public catalog: strip unvalidated numeric targets so they never ship publicly.
    import copy
    pub_catalog = copy.deepcopy(CATALOG)
    for u in pub_catalog.get("universes", []):
        for fam in u.get("families", []):
            for line in fam.get("lines", []):
                for p in line.get("products", []):
                    for v in p.get("variants", []):
                        v.pop("capacity_ml_target", None)  # governance: unvalidated → not public
    pub_catalog["note"] = "Public catalog. Numeric absorbency targets are removed until validated as public claims."

    with open(os.path.join(out, "site.json"), "w", encoding="utf-8") as f:
        json.dump({k: SITE[k] for k in ("brand", "features", "navigation")}, f, ensure_ascii=False, indent=2)
    with open(os.path.join(out, "catalog.json"), "w", encoding="utf-8") as f:
        json.dump(pub_catalog, f, ensure_ascii=False, indent=2)
    with open(os.path.join(out, "research.public.json"), "w", encoding="utf-8") as f:
        json.dump(pub_research, f, ensure_ascii=False, indent=2)
    with open(os.path.join(out, "claims.public.json"), "w", encoding="utf-8") as f:
        json.dump(pub_claims, f, ensure_ascii=False, indent=2)

def write_meta():
    # .nojekyll
    open(os.path.join(OUT, ".nojekyll"), "w").close()
    # robots
    with open(os.path.join(OUT, "robots.txt"), "w", encoding="utf-8") as f:
        f.write(f"User-agent: *\nAllow: /\nSitemap: {BASE_URL}/sitemap.xml\n")
    # sitemap
    today = datetime.date.today().isoformat()
    urls = ""
    for r in sorted(set(ROUTES_FOR_SITEMAP)):
        loc = BASE_URL + "/" + r
        pr = "1.0" if r == "" else ("0.8" if r.count("/") <= 1 else "0.6")
        urls += f"<url><loc>{loc}</loc><lastmod>{today}</lastmod><priority>{pr}</priority></url>"
    with open(os.path.join(OUT, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write(f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>')

# ============================================================ MAIN
def main():
    if os.path.exists(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT, exist_ok=True)
    generate_posters()
    copy_assets()

    build_home()
    build_creations_index()
    for fam in published_families():
        build_family(fam)
    build_selector()
    build_technologie()
    build_lab()
    build_lab_programs()
    build_lab_methods()
    build_lab_publications()
    build_endometriose()
    build_mission()
    build_maison()
    build_pharmacie()
    build_journal()
    build_contact()
    build_legal()
    build_404()

    write_public_data()
    write_meta()
    print("Build complete →", OUT)
    print("Pages generated:", len(set(ROUTES_FOR_SITEMAP)) + 1, "(incl. 404)")

if __name__ == "__main__":
    main()
