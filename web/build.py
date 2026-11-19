#!/usr/bin/env python3
"""
Danzflor · Generador estático provisional (fase 3).

Genera HTML estático en dist/ a partir de content/ajustes.json y
static/data/productos.json. Es un puente hasta tener Node: en la web final
estas mismas plantillas pasan a componentes de Astro.

Uso:  python3 build.py            (vista previa local, formularios en modo demo)
      python3 build.py --prod     (formularios reales de Netlify)
"""
import html
import json
import pathlib
import shutil
import sys

ROOT = pathlib.Path(__file__).resolve().parent
DIST = ROOT / "dist"
P = json.loads((ROOT / "static/data/productos.json").read_text(encoding="utf-8"))
A = json.loads((ROOT / "content/ajustes.json").read_text(encoding="utf-8"))
SPRITE = (ROOT / "partials/sprite.svg").read_text(encoding="utf-8")
PROD = "--prod" in sys.argv

CDN = P["cdn"]
STORE = P["tienda"]
SITE = A["sitio"]["url"]
FREE = A["envios"]["gratisDesde"]
# GTM de la marca: solo se carga con consentimiento y NUNCA mientras la web sea un concepto (no ensuciar su analítica).
GTM = "" if A["sitio"]["conceptBar"] else "GTM-597VJ3MJ"
e = html.escape
ARIA_CUR = ' aria-current="page"'
PRIO = 'fetchpriority="high" loading="eager"'
LAZY = 'loading="lazy"'
OUT_ATTR = 'data-out="true"'
SOLD_SR = '<span class="visually-hidden"> (agotada)</span>'


# ---------------------------------------------------------------- utilidades
def eur(n):
    return f"{n:.2f}".replace(".", ",") + " €"


def cdn(f, w):
    return f"{CDN}{f}?width={w}"


def icon(name, cls="", size=None, label=None):
    dims = f' width="{size}" height="{size}"' if size else ""
    aria = f' role="img" aria-label="{e(label)}"' if label else ' aria-hidden="true"'
    c = f' class="{cls}"' if cls else ""
    return f'<svg{c}{dims}{aria}><use href="#i-{name}"/></svg>'


def flor(cls="flor"):
    return icon("flor", cls)


def wordmark(tag="a", href="/", label="Danzflor, inicio"):
    inner = f'DANZFL{flor()}R'
    if tag == "a":
        return f'<a class="wordmark" href="{href}" aria-label="{label}">{inner}</a>'
    return f'<span class="wordmark" aria-hidden="true">{inner}</span>'


def jsonld(obj):
    return f'<script type="application/ld+json">{json.dumps(obj, ensure_ascii=False)}</script>'


def stock(p):
    av = sum(v["disponible"] for v in p["variantes"])
    if av == 0:
        return {"key": "out", "label": "Agotado · edición limitada", "cls": "badge--out"}
    if av < len(p["variantes"]):
        return {"key": "low", "label": "Últimas tallas", "cls": "badge--low"}
    return {"key": "ok", "label": "Disponible", "cls": "badge--ok"}


ORDER = {"ok": 0, "low": 1, "out": 2}
PRODUCTS = sorted(P["productos"], key=lambda p: ORDER[stock(p)["key"]])  # agotados al final
BY_HANDLE = {p["handle"]: p for p in P["productos"]}
IN_STOCK = [p for p in PRODUCTS if stock(p)["key"] != "out"]
RELEASES = {r["id"]: r for r in A["lanzamientos"]}


def model_image(p):
    return next((i for i in p["imagenes"] if i["src"].startswith("DSC")), p["imagenes"][1] if len(p["imagenes"]) > 1 else None)


def cart_item(p, v):
    return {"id": v["id"], "handle": p["handle"], "title": p["nombre"], "size": v["talla"],
            "price": p["precio"], "img": p["imagenes"][0]["src"]}


def local_img(name, alt, sizes, priority=False, cls=""):
    """Foto lifestyle propia: AVIF + JPG en 640 y 1200 px."""
    pr = 'fetchpriority="high" loading="eager"' if priority else 'loading="lazy"'
    c = f' class="{cls}"' if cls else ""
    return (f'<picture{c}>'
            f'<source type="image/avif" srcset="/img/{name}-640.avif 640w, /img/{name}-1200.avif 1200w" sizes="{sizes}">'
            f'<img src="/img/{name}-1200.jpg" srcset="/img/{name}-640.jpg 640w, /img/{name}-1200.jpg 1200w" sizes="{sizes}" '
            f'width="900" height="1200" {pr} decoding="async" alt="{e(alt)}"></picture>')


# ---------------------------------------------------------------- componentes
def card(p, i=0, sizes="(min-width: 1100px) 23vw, 48vw"):
    st = stock(p)
    front, model = p["imagenes"][0], model_image(p)
    url = f"/tienda/{p['handle']}/"
    avail = " ".join(v["talla"] for v in p["variantes"] if v["disponible"])
    load = "eager" if i < 2 else "lazy"
    sizes_btns = "".join(
        f'<button type="button" class="size" data-quick-add=\'{e(json.dumps(cart_item(p, v), ensure_ascii=False))}\' '
        f'aria-label="Añadir {e(p["nombre"])} talla {v["talla"]}">{v["talla"]}</button>'
        if v["disponible"] else
        f'<button type="button" class="size is-out" disabled aria-label="Talla {v["talla"]} agotada">{v["talla"]}</button>'
        for v in p["variantes"])
    one_size = len(p["variantes"]) == 1
    quick = ""
    if st["key"] != "out":
        if one_size:
            quick = (f'<div class="card__quick"><button type="button" class="card__quick-btn" '
                     f'data-quick-add=\'{e(json.dumps(cart_item(p, p["variantes"][0]), ensure_ascii=False))}\' '
                     f'aria-label="Añadir {e(p["nombre"])} al carrito">{icon("plus")}</button></div>')
        else:
            quick = (f'<div class="card__quick"><button type="button" class="card__quick-btn" data-quick-open '
                     f'aria-label="Compra rápida de {e(p["nombre"])}">{icon("plus")}</button></div>'
                     f'<div class="card__sizes" role="group" aria-label="Elige talla de {e(p["nombre"])}">'
                     f'<div class="card__sizes-head"><span>Elige talla</span>'
                     f'<button type="button" class="btn btn--icon" data-quick-close aria-label="Cerrar compra rápida">{icon("close")}</button></div>'
                     f'<div class="sizes__grid">{sizes_btns}</div></div>')
    model_html = ""
    if model:
        model_html = (f'<img class="card__img--model" src="{cdn(model["src"], 700)}" '
                      f'srcset="{cdn(model["src"], 400)} 400w, {cdn(model["src"], 700)} 700w" sizes="{sizes}" '
                      f'width="{model["w"]}" height="{model["h"]}" alt="" loading="lazy" decoding="async">')
    return f'''
<article class="card{' is-soldout' if st['key'] == 'out' else ''}" data-reveal="up"
  data-tipo="{e(p['tipo'].lower())}" data-tallas="{avail}" data-precio="{p['precio']}" data-orden="{i}"
  data-disponible="{'1' if st['key'] != 'out' else '0'}" data-coleccion="{p['coleccion']}">
  <div class="card__media">
    <div class="card__badges"><span class="badge {st['cls']}">{st['label']}</span></div>
    <img class="card__img--front" src="{cdn(front['src'], 700)}" srcset="{cdn(front['src'], 400)} 400w, {cdn(front['src'], 700)} 700w, {cdn(front['src'], 1000)} 1000w"
      sizes="{sizes}" width="{front['w']}" height="{front['h']}" alt="{e(front['alt'])}" loading="{load}" decoding="async">
    {model_html}
    {quick}
  </div>
  <div class="card__info">
    <h3 class="card__title"><a href="{url}">{e(p['nombre'])}</a></h3>
    <p class="price">{eur(p['precio'])}</p>
    <p class="card__meta">{e(p['tipo'])} · {e(p['color'])}</p>
  </div>
</article>'''


def player(r, bars=64):
    sub = f"{r['artista']}{' · ' + r['catalogo'] if r.get('catalogo') else ''}"
    return f'''
<dz-player class="player" data-url="{e(r['url'])}" data-title="{e(r['titulo'])}" data-artist="{e(sub)}" data-bars="{bars}">
  <div class="player__cover"><div class="vinyl" aria-hidden="true"></div></div>
  <div class="player__main">
    <div class="player__top">
      <button class="player__toggle" type="button" aria-label="Reproducir {e(r['titulo'])}" aria-pressed="false">{icon("play", "i-play")}{icon("pause", "i-pause")}</button>
      <div class="player__titles"><p class="player__title">{e(r['titulo'])}</p><p class="player__artist">{e(sub)}</p></div>
      <span class="eq" style="color:var(--accent);margin-left:auto" aria-hidden="true"><span></span><span></span><span></span><span></span></span>
    </div>
    <div class="wave" role="slider" tabindex="0" aria-label="Posición del tema" aria-valuemin="0" aria-valuemax="100" aria-valuenow="0"></div>
    <div class="player__time"><span data-now>0:00</span><span data-dur>–:––</span></div>
  </div>
  <p class="player__credit">Se reproduce desde el <a href="https://soundcloud.com/collectivedanz" rel="noopener" target="_blank">SoundCloud de Danz In Records<span class="visually-hidden"> (se abre en otra pestaña)</span></a>.</p>
</dz-player>'''


def field_error():
    return f'<p class="field__error">{icon("alert", size=16)}<span></span></p>'


def form_attrs(name):
    if PROD:
        return f'name="{name}" method="POST" data-netlify="true" netlify-honeypot="bot-field" data-validate novalidate'
    return f'name="{name}" data-validate data-demo novalidate'


def form_hidden(name):
    return (f'<input type="hidden" name="form-name" value="{name}">'
            f'<p hidden><label>No rellenar: <input name="bot-field" tabindex="-1" autocomplete="off"></label></p>')


def newsletter(context="drop"):
    copy = {
        "drop": ("Acceso anticipado", "El próximo drop llega antes a tu email. Sin spam, palabra de DJ.", "acceso-anticipado"),
        "musica": ("Nuevos lanzamientos", "Te avisamos cuando salga un tema nuevo de Danz In Records.", "newsletter-musica"),
        "fiestas": ("Primero en enterarte", "Fechas, line-up y entradas de la próxima Danzers antes que nadie.", "newsletter-fiestas"),
    }[context]
    t, sub, name = copy
    return f'''
<section id="newsletter" class="container section" aria-labelledby="nl-t">
  <div class="newsletter" data-reveal="up">
    {flor("flor newsletter__flor")}
    <div class="stack">
      <h2 id="nl-t" class="h2">{t}</h2>
      <p>{sub}</p>
    </div>
    <form class="stack" {form_attrs(name)}>
      {form_hidden(name)}
      <div class="form-fields stack">
        <div class="field">
          <label class="field__label" for="nl-email">Tu email</label>
          <div class="inline-form">
            <input class="input" id="nl-email" name="email" type="email" autocomplete="email" required placeholder="tu@email.com">
            <button class="btn" type="submit">Apuntarme</button>
          </div>
          {field_error()}
        </div>
        <label class="check"><input type="checkbox" name="acepto-privacidad" required id="nl-ok"><span>Acepto la <a href="/ayuda/privacidad/">política de privacidad</a> y recibir emails de Danz Collective.</span></label>
        <p class="field__error" data-error-for="nl-ok">{icon("alert", size=16)}<span></span></p>
      </div>
      <div class="form-success" tabindex="-1">{icon("check")}<p><strong>Estás dentro.</strong> Te avisamos antes que a nadie.</p></div>
    </form>
  </div>
</section>'''


def marquee():
    items = [("No es una colección", ""), ("Es una actitud", " marquee__item--outline"),
             ("Celebrate life", ""), ("The art of Mixing", " marquee__item--outline")]
    row = "".join(f'<span class="marquee__item{c}">{t}</span>{flor("flor flor--spin")}' for t, c in items)
    return (f'<div class="marquee" role="marquee" aria-label="No es una colección. Es una actitud. Celebrate life. The art of Mixing.">'
            f'<div class="marquee__track" aria-hidden="true">{row}</div><div class="marquee__track" aria-hidden="true">{row}</div></div>')


def trust():
    c = A["contacto"]
    items = [
        ("truck", f"Envío gratis desde {FREE} €", "En España"),
        ("swap", f"Cambios en {A['cambios']['dias']} días", "Prenda sin usar y con etiqueta"),
        ("pin", "Hecho en Madrid", "Impreso en nuestro estudio"),
    ]
    if c.get("whatsapp"):
        items.append(("chat", "Atención por WhatsApp", c.get("horario") or ""))
    else:
        items.append(("chat", "Te contestamos rápido", f"Escríbenos a {c['email']}"))
    li = "".join(f'<li class="trust__item">{icon(i)}<div><strong>{t}</strong><span class="muted">{s}</span></div></li>' for i, t, s in items)
    return f'<ul class="trust" role="list" aria-label="Compra tranquilo">{li}</ul>'


# ---------------------------------------------------------------- layout
NAV = [("Tienda", "/tienda/"), ("Música", "/musica/"), ("Eventos", "/eventos/"), ("Nosotros", "/nosotros/"), ("Ayuda", "/ayuda/")]


def header(active):
    links = "".join(f'<li><a href="{h}"{ARIA_CUR if active == h else ""}>{t}</a></li>' for t, h in NAV)
    return f'''
<header class="header">
  <div class="container header__row">
    {wordmark()}
    <nav class="nav" aria-label="Principal"><ul>{links}</ul></nav>
    <div class="header__actions">
      <a class="btn btn--icon hide-sm" href="/buscar/" aria-label="Buscar">{icon("search")}</a>
      <a class="btn btn--icon hide-sm" href="{STORE}/account" aria-label="Mi cuenta">{icon("user")}</a>
      <button class="btn btn--icon cart-btn" type="button" data-open="cart-drawer" aria-label="Abrir carrito, vacío">{icon("bag")}<span class="cart-btn__count" data-cart-count></span></button>
      <button class="btn btn--icon header__menu-btn" type="button" data-open="menu" aria-label="Abrir menú">{icon("menu")}</button>
    </div>
  </div>
</header>'''


def footer():
    c = A["contacto"]
    contact = [f'<li><a href="mailto:{c["email"]}">{c["email"]}</a></li>']
    if c.get("telefono"):
        contact.append(f'<li><a href="tel:{c["telefono"].replace(" ", "")}">{e(c["telefono"])}</a></li>')
    if c.get("whatsapp"):
        contact.append(f'<li><a href="https://wa.me/{c["whatsapp"]}" rel="noopener">WhatsApp</a></li>')
    addr = c["direccion"] + (f", {c['localidad']}" if c.get("localidad") else "")
    social = "".join(f'<li><a href="{r["url"]}" rel="noopener" target="_blank">{e(r["nombre"])}<span class="visually-hidden"> (se abre en otra pestaña)</span></a></li>' for r in A["redes"])
    return f'''
<footer class="footer">
  <div class="container">
    <p class="footer__big" aria-hidden="true">DANZFL{flor()}R</p>
    <div class="footer__cols">
      <div class="footer__about">
        <p class="h4">No es una colección. Es una actitud.</p>
        <p class="muted small">Danz Collective: ropa, música house y fiestas desde Madrid. Danzflor, Danz In Records y Danzers by Danz Collective.</p>
        <address class="small muted" style="font-style:normal">{e(addr)}</address>
        <ul class="small" role="list">{"".join(contact)}</ul>
      </div>
      <nav class="footer__col" aria-labelledby="f-tienda"><h2 id="f-tienda">Tienda</h2><ul role="list">
        <li><a href="/tienda/">Toda la colección</a></li>
        <li><a href="/tienda/?tipo=camiseta">Camisetas</a></li>
        <li><a href="/tienda/?tipo=baño">Baño</a></li>
        <li><a href="/tienda/?tipo=accesorio">Accesorios</a></li>
        <li><a href="/tienda/#archivo">Archivo</a></li></ul></nav>
      <nav class="footer__col" aria-labelledby="f-col"><h2 id="f-col">Colectivo</h2><ul role="list">
        <li><a href="/musica/">Danz In Records</a></li>
        <li><a href="/eventos/">Danzers</a></li>
        <li><a href="/nosotros/">Nosotros</a></li>
        {social}</ul></nav>
      <nav class="footer__col" aria-labelledby="f-ayuda"><h2 id="f-ayuda">Ayuda</h2><ul role="list">
        <li><a href="/ayuda/envios/">Envíos</a></li>
        <li><a href="/ayuda/cambios/">Cambios y devoluciones</a></li>
        <li><a href="/ayuda/tallas/">Guía de tallas</a></li>
        <li><a href="/ayuda/faq/">Preguntas frecuentes</a></li>
        <li><a href="/ayuda/contacto/">Contacto</a></li></ul></nav>
    </div>
    <div class="footer__legal">
      <p>© 2026 Danz Collective. Todos los derechos reservados.</p>
      <p class="cluster" style="--cluster:var(--sp-4)"><a href="/ayuda/aviso-legal/">Aviso legal</a><a href="/ayuda/privacidad/">Privacidad</a><a href="/ayuda/cookies/">Cookies</a><button type="button" class="link-btn" data-consent-open>Configurar cookies</button></p>
    </div>
  </div>
</footer>'''


def shared_end():
    swim, bag = BY_HANDLE["swim-short"], BY_HANDLE["yepo-bag"]
    upsell = []
    for p in (swim, bag):
        v = next((v for v in p["variantes"] if v["disponible"]), p["variantes"][0])
        upsell.append({**cart_item(p, v), "available": v["disponible"]})
    menu = "".join(f'<li style="--i:{i}"><a href="{h}">{t}{" <small>" + s + "</small>" if s else ""}</a></li>'
                   for i, (t, h, s) in enumerate([("Tienda", "/tienda/", "Danzflor"), ("Música", "/musica/", "Danz In Records"),
                                                  ("Eventos", "/eventos/", "Danzers"), ("Nosotros", "/nosotros/", ""), ("Ayuda", "/ayuda/", "")]))
    return f'''
<nav class="tabbar" aria-label="Accesos rápidos">
  <a href="/tienda/">{icon("shop")}Tienda</a>
  <a href="/buscar/">{icon("search")}Buscar</a>
  <button type="button" class="cart-btn" data-open="cart-drawer" aria-label="Abrir carrito, vacío">{icon("bag")}Carrito<span class="cart-btn__count" data-cart-count style="right:calc(50% - 22px)"></span></button>
  <a href="{STORE}/account">{icon("user")}Cuenta</a>
</nav>

<dialog id="menu" class="menu-full" aria-label="Menú">
  <div class="container header__row">{wordmark("span")}<button class="btn btn--icon" type="button" data-close aria-label="Cerrar menú">{icon("close")}</button></div>
  <ul class="menu-full__list" role="list">{menu}</ul>
</dialog>

<dz-cart data-upsell='{e(json.dumps(upsell, ensure_ascii=False))}' data-free="{FREE}">
  <dialog id="cart-drawer" class="drawer" aria-labelledby="cart-title">
    <div class="drawer__head"><p id="cart-title" class="h3">Tu carrito</p><button class="btn btn--icon" type="button" data-close aria-label="Cerrar carrito">{icon("close")}</button></div>
    <div class="drawer__body">
      <div class="ship-bar"><p class="ship-bar__text"></p><div class="ship-bar__track" aria-hidden="true"><div class="ship-bar__fill"></div></div></div>
      <div data-lines></div>
      <p class="visually-hidden" aria-live="polite" data-live></p>
    </div>
    <div class="drawer__foot stack" style="--stack:var(--sp-3)">
      <details class="acc" style="border-top:0"><summary class="small">Añadir nota al pedido</summary><div class="acc__body"><label class="visually-hidden" for="cart-note">Nota del pedido</label><textarea id="cart-note" class="textarea" maxlength="500" placeholder="¿Es un regalo? ¿Algo que debamos saber?"></textarea></div></details>
      <div class="cluster" style="justify-content:space-between"><span>Subtotal</span><span class="price price--lg" data-total>0,00&nbsp;€</span></div>
      <p class="small muted">IVA incluido. El envío se calcula en el pago.</p>
      <a class="btn btn--block" data-checkout hidden href="{STORE}/cart" rel="noopener">Ir al pago seguro {icon("arrow")}</a>
      <p class="small subtle" style="text-align:center">Pagas en la tienda oficial de Danz Collective, con el pago seguro de Shopify.</p>
    </div>
  </dialog>
</dz-cart>

<dialog id="size-guide" class="modal" aria-labelledby="sg-title">
  <div class="modal__head"><p id="sg-title" class="h3">Guía de tallas</p><button class="btn btn--icon" type="button" data-close aria-label="Cerrar guía de tallas">{icon("close")}</button></div>
  <div class="modal__body stack">
    <p data-size-model hidden></p>
    <p><strong>Corte fácil de llevar.</strong> Si estás entre dos tallas y te gusta holgada, coge la grande.</p>
    <p class="muted">Cómo medirte: pon una camiseta que te quede bien sobre una superficie plana y mide el ancho de axila a axila y el largo desde el hombro hasta el bajo.</p>
    <p class="muted">¿Dudas? Escríbenos a <a href="mailto:{A['contacto']['email']}">{A['contacto']['email']}</a> y te ayudamos a elegir.</p>
  </div>
</dialog>

<dialog id="notify-modal" class="modal" aria-labelledby="nt-title">
  <div class="modal__head"><p id="nt-title" class="h3">Avísame cuando vuelva</p><button class="btn btn--icon" type="button" data-close aria-label="Cerrar">{icon("close")}</button></div>
  <div class="modal__body">
    <form class="stack" {form_attrs("aviso-stock")}>
      {form_hidden("aviso-stock")}
      <div class="form-fields stack">
        <p class="muted">Te escribimos una sola vez, cuando haya reposición de <strong data-notify-label>este producto</strong>.</p>
        <input type="hidden" name="producto-talla" value="">
        <div class="field">
          <label class="field__label" for="nt-email">Email</label>
          <input class="input" id="nt-email" name="email" type="email" autocomplete="email" required placeholder="tu@email.com">
          {field_error()}
        </div>
        <button class="btn btn--block" type="submit">Avisarme</button>
      </div>
      <div class="form-success" tabindex="-1">{icon("check")}<p><strong>Hecho.</strong> En cuanto vuelva, te llega un email.</p></div>
    </form>
  </div>
</dialog>

<dz-mini-player>
  <div class="mini-player" role="region" aria-label="Reproductor">
    <span class="eq" aria-hidden="true"><span></span><span></span><span></span><span></span></span>
    <p class="mini-player__text"><strong></strong><span></span></p>
    <button class="btn btn--icon" type="button" data-mini-toggle aria-label="Pausar"><svg class="i-play" aria-hidden="true" style="display:none"><use href="#i-play"/></svg><svg class="i-pause" aria-hidden="true"><use href="#i-pause"/></svg></button>
    <button class="btn btn--icon" type="button" data-mini-close aria-label="Cerrar reproductor">{icon("close")}</button>
    <span class="mini-player__progress" aria-hidden="true"></span>
  </div>
</dz-mini-player>
<div id="dz-audio-host"></div>

<div class="consent" data-consent role="region" aria-labelledby="consent-t" hidden data-gtm="{GTM}">
  <div class="consent__text"><p id="consent-t" class="h4">¿Unas cookies?</p>
  <p class="small muted">Usamos las imprescindibles para que la web funcione. Con tu permiso, también analítica para saber qué funciona y mejorar. Más en la <a href="/ayuda/cookies/">política de cookies</a>.</p></div>
  <div class="consent__actions"><button class="btn btn--secondary btn--sm" type="button" data-consent-choice="reject">Rechazar</button><button class="btn btn--sm" type="button" data-consent-choice="accept">Aceptar analítica</button></div>
</div>
<script type="module" src="/js/app.js"></script>'''


ORG = {
    "@context": "https://schema.org", "@type": "Organization", "name": "Danz Collective",
    "url": SITE, "email": A["contacto"]["email"],
    "sameAs": [r["url"] for r in A["redes"]],
    "address": {"@type": "PostalAddress", "streetAddress": "Calle Moral 14", "postalCode": "28807", "addressCountry": "ES"},
}


def page(path, title, desc, body, active=None, ld=None, og_image=None, body_cls="", preload="", og_alt=None, og_type="website", extra_meta=""):
    og_image = og_image or f"{SITE}/img/og-default.jpg"
    og_alt = og_alt or "Danz Collective: ropa, música house y fiestas desde Madrid"
    canonical = SITE + path
    lds = "".join(jsonld(x) for x in (ld or []))
    bar = '<aside class="concept-bar" aria-label="Aviso">Concepto de rediseño · no es la web oficial</aside>' if A["sitio"]["conceptBar"] else ""
    doc = f'''<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{canonical}">
<meta name="theme-color" content="#0a0a0a">
{'<meta name="robots" content="noindex">' if A["sitio"]["conceptBar"] else ''}
<meta property="og:type" content="{og_type}">
<meta property="og:locale" content="es_ES">
<meta property="og:site_name" content="Danz Collective">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{og_image}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{e(og_alt)}">
{extra_meta}
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<link rel="preconnect" href="https://cdn.shopify.com" crossorigin>
<link rel="preload" href="/fonts/unbounded-latin-var.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/fonts/inter-latin-var.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/css/fuentes.css">
{preload}
<link rel="stylesheet" href="/css/tokens.css">
<link rel="stylesheet" href="/css/base.css">
<link rel="stylesheet" href="/css/componentes.css">
<link rel="stylesheet" href="/css/paginas.css">
<link rel="stylesheet" href="/css/secciones.css">
{lds}
</head>
<body class="{body_cls}">
{SPRITE}
<a class="skip-link" href="#contenido">Saltar al contenido</a>
{bar}
{header(active)}
<main id="contenido">
{body}
</main>
{footer()}
{shared_end()}
</body>
</html>
'''
    out = DIST / path.strip("/") / "index.html" if path != "/" else DIST / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(doc, encoding="utf-8")
    return out


def breadcrumbs(items):
    """items: [(nombre, ruta)] — el último es la página actual."""
    li = []
    for i, (n, h) in enumerate(items):
        last = i == len(items) - 1
        li.append(f'<li><span aria-current="page">{e(n)}</span></li>' if last else f'<li><a href="{h}">{e(n)}</a></li>')
    ld = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": SITE + h} for i, (n, h) in enumerate(items)]}
    return f'<nav class="breadcrumbs container" aria-label="Migas de pan"><ol>{"".join(li)}</ol></nav>', ld


# ---------------------------------------------------------------- páginas
def build_home():
    h = A["home"]
    rel = RELEASES[h["lanzamientoDestacado"]]
    party = A.get("proximaFiesta")
    if party:  # solo con fecha real
        party_html = f'''
      <div class="stack">
        <p class="eyebrow">Danzers by Danz Collective</p>
        <h2 class="h2">{e(party["nombre"])}</h2>
        <p class="lead">{e(party["fecha_texto"])} · {e(party["sala"])}, {e(party["ciudad"])}</p>
      </div>
      <div class="stack" data-countdown-wrap>
        <dz-countdown data-date="{e(party["fecha"])}"><div class="countdown" role="timer" aria-label="Cuenta atrás">
          <div class="countdown__unit"><span class="countdown__num" data-u="d">00</span><span class="countdown__label">días</span></div>
          <div class="countdown__unit"><span class="countdown__num" data-u="h">00</span><span class="countdown__label">horas</span></div>
          <div class="countdown__unit"><span class="countdown__num" data-u="m">00</span><span class="countdown__label">min</span></div>
          <div class="countdown__unit"><span class="countdown__num" data-u="s" aria-hidden="true">00</span><span class="countdown__label">seg</span></div>
        </div></dz-countdown>
        <a class="btn" href="{e(party["entradas"])}" rel="noopener">Comprar entradas {icon("arrow")}</a>
      </div>'''
    else:
        party_html = f'''
      <div class="stack">
        <p class="eyebrow">Danzers by Danz Collective</p>
        <h2 class="h2">La próxima<br><em>está en camino</em></h2>
        <p class="lead">House y tech house en Madrid desde enero de 2023. Apúntate y te mandamos la fecha antes de anunciarla.</p>
      </div>
      <div class="cluster">
        <a class="btn" href="#newsletter">Avísame de la fecha</a>
        <a class="btn btn--secondary" href="/eventos/">Ediciones pasadas</a>
      </div>'''

    body = f'''
<section class="hero grain" aria-labelledby="hero-title">
  {local_img(h["heroImagen"], h["heroAlt"], "(min-width: 900px) 45vw, 100vw", priority=True, cls="hero__media")}
  <div class="hero__scrim" aria-hidden="true"></div>
  <div class="vinyl hero__vinyl" aria-hidden="true" data-parallax="-12"></div>
  <span class="sticker sticker--round hero__sticker" style="--rot:8deg" aria-hidden="true">Hecho en<br>Madrid</span>
  <div class="container hero__content">
    <p class="eyebrow">{e(h["heroEyebrow"])}</p>
    <h1 id="hero-title" class="display hero__title" data-reveal="lines-now">
      <span class="line-mask"><span style="--i:0">Ropa,</span></span>
      <span class="line-mask"><span style="--i:1">música house</span></span>
      <span class="line-mask"><span style="--i:2">y fiestas.</span></span>
      <span class="line-mask"><span style="--i:3"><em>Desde Madrid.</em></span></span>
    </h1>
    <div class="cluster">
      <a class="btn" href="/tienda/" data-magnetic="0.25"><span class="btn__label-swap"><span>Comprar la colección</span><span aria-hidden="true">Comprar la colección</span></span>{icon("arrow")}</a>
      <a class="btn btn--secondary" href="{'#proxima-fiesta' if party else '/eventos/'}" data-magnetic="0.25">Próxima fiesta</a>
    </div>
  </div>
</section>
{marquee()}
<div class="container">{trust()}</div>

<section class="container section" aria-labelledby="dest-t">
  <div class="section-head">
    <div class="section-head__text">
      <p class="eyebrow">{e(A["colecciones"][h["coleccionDestacada"]]["titulo"])} · {e(A["colecciones"][h["coleccionDestacada"]]["temporada"] or "")}</p>
      <h2 id="dest-t" class="h2" data-reveal="up">La colección</h2>
    </div>
    <a class="btn btn--ghost" href="/tienda/">Ver toda la tienda {icon("arrow")}</a>
  </div>
  <div class="grid-products">{"".join(card(p, i) for i, p in enumerate(IN_STOCK[:4]))}</div>
</section>

<section class="container section" aria-label="Próxima fiesta y último lanzamiento">
  <div class="duo">
    <article id="proxima-fiesta" class="panel panel--party grain" data-reveal="up">{flor("flor panel__flor")}{party_html}</article>
    <article class="panel" data-reveal="up">
      <div class="stack">
        <p class="eyebrow">Danz In Records · Último lanzamiento</p>
        <h2 class="h2">{e(rel["titulo"])}</h2>
        <p class="lead">{e(rel["artista"])}{" · " + rel["catalogo"] if rel.get("catalogo") else ""}. House internacional desde Madrid. Dale al play: suena aquí mismo.</p>
      </div>
      {player(rel, 48)}
      <a class="btn btn--ghost" href="/musica/">Escucha el catálogo {icon("arrow")}</a>
    </article>
  </div>
</section>

<section class="container section" aria-labelledby="fam-t">
  <div class="section-head"><div class="section-head__text"><p class="eyebrow">Danz Collective</p><h2 id="fam-t" class="h2" data-reveal="up">Tres proyectos, una familia</h2>
  <p class="lead">Nacimos en Madrid en 2024, entre amigos. Come inside and become part of the family.</p></div></div>
  <div class="pillars">
    <a class="pillar" href="/tienda/" data-reveal="up"><span class="pillar__num" aria-hidden="true">01</span><h3 class="h3">Danzflor</h3><p class="muted">Streetwear de cultura club. Camisetas heavyweight impresas en nuestro estudio.</p><span class="pillar__go">Descubre la colección {icon("arrow")}</span>{flor("flor pillar__art")}</a>
    <a class="pillar" href="/musica/" data-reveal="up"><span class="pillar__num" aria-hidden="true">02</span><h3 class="h3">Danz In Records</h3><p class="muted">Nuestro sello de house internacional. Keanu Callister, Santacruz y Chicharro ES.</p><span class="pillar__go">Escucha el sello {icon("arrow")}</span><span class="vinyl pillar__art" style="--vinyl-size:140px" aria-hidden="true"></span></a>
    <a class="pillar" href="/eventos/" data-reveal="up"><span class="pillar__num" aria-hidden="true">03</span><h3 class="h3">Danzers</h3><p class="muted">Danzers by Danz Collective: nuestra fiesta de house y tech house en Madrid.</p><span class="pillar__go">Ver las fiestas {icon("arrow")}</span>{icon("martini", "pillar__art")}</a>
  </div>
</section>

<section class="container section" aria-labelledby="com-t">
  <div class="section-head"><div class="section-head__text"><p class="eyebrow">Comunidad</p><h2 id="com-t" class="h2" data-reveal="up">Celebrate life</h2></div>
  <a class="btn btn--secondary" href="https://www.instagram.com/danzflor.clothing/" rel="noopener" target="_blank">Ver la colección en Instagram<span class="visually-hidden"> (se abre en otra pestaña)</span></a></div>
  <div class="community">
    <figure class="grain">{local_img("club-house-espalda-terraza", "Chico de espaldas con la Club House Tee en una terraza de Madrid, con cielo azul, sombrilla y auriculares", "(min-width: 900px) 40vw, 100vw")}<figcaption><span class="sticker">Club House Tee</span></figcaption></figure>
    <figure class="grain">{local_img("tracks-cocktails-gafas", "Chico con gafas de sol naranjas y la Tracks & Cocktails Tee, foto contrapicada con tejados y cielo", "(min-width: 900px) 30vw, 50vw")}<figcaption><span class="sticker sticker--pool" style="--rot:3deg">Tracks &amp; Cocktails</span></figcaption></figure>
    <figure class="grain">{local_img("club-house-piscina-ibiza", "Chico de espaldas con la Club House Tee cruzando una piscina en Ibiza", "(min-width: 900px) 30vw, 50vw")}<figcaption><span class="sticker sticker--accent" style="--rot:-3deg">Ibiza</span></figcaption></figure>
  </div>
</section>

<section class="container section" aria-labelledby="rev-t">
  <div class="reviews-empty" data-reveal="up">
    <div class="stars" aria-hidden="true">{"".join(icon("flor") for _ in range(5))}</div>
    <h2 id="rev-t" class="h3">Todavía no hay opiniones publicadas</h2>
    <p class="muted" style="max-width:48ch">Si ya llevas algo de Danzflor, enséñanoslo: etiquétanos en Instagram con @danzflor.clothing.</p>
    <a class="btn btn--secondary" href="https://www.instagram.com/danzflor.clothing/" rel="noopener" target="_blank">Ir a @danzflor.clothing<span class="visually-hidden"> (se abre en otra pestaña)</span></a>
  </div>
</section>
{newsletter("drop")}'''
    ld = [ORG, {"@context": "https://schema.org", "@type": "WebSite", "name": "Danz Collective", "url": SITE + "/", "inLanguage": "es-ES"}]
    page("/", "Danz Collective · Ropa, música house y fiestas desde Madrid",
         "Danzflor, Danz In Records y Danzers by Danz Collective: streetwear de cultura club, música house y fiestas desde Madrid. Envío gratis en España desde 75 €.",
         body, ld=ld,
         preload='<link rel="preload" as="image" type="image/avif" imagesrcset="/img/club-house-piscina-ibiza-640.avif 640w, /img/club-house-piscina-ibiza-1200.avif 1200w" imagesizes="(min-width: 900px) 45vw, 100vw" fetchpriority="high">')


def build_shop():
    col = A["colecciones"]["tracks-cocktails"]
    types = sorted({p["tipo"] for p in PRODUCTS})
    chip = lambda name, val, label: f'<label class="chip"><input type="checkbox" name="{name}" value="{e(val)}">{e(label)}</label>'
    crumbs, crumbs_ld = breadcrumbs([("Inicio", "/"), ("Tienda", "/tienda/")])
    rel = RELEASES["dnz12"]
    archive = "".join(f'''
    <article data-reveal="up">
      <div class="no-photo" style="--ratio:4/3">{flor()}<p class="no-photo__text">{e(a["titulo"])}</p></div>
      <h3 class="h4">{e(a["titulo"])}</h3><p class="small muted">{e(a["texto"])} Ya no está a la venta.</p>
    </article>''' for a in A["archivo"])
    body = f'''
{crumbs}
<section class="container shop-hero" aria-labelledby="shop-t">
  <div class="stack" style="--stack:var(--sp-5)">
    <p class="eyebrow" style="color:var(--accent)">Danzflor · {e(col["titulo"])} · {e(col["temporada"])}</p>
    <h1 id="shop-t" class="h1" data-reveal="lines-now"><span class="line-mask"><span style="--i:0">No es una colección.</span></span><span class="line-mask"><span style="--i:1" class="accent">Es una actitud.</span></span></h1>
    <p class="lead">{e(col["descripcion"])}</p>
    <div class="cluster"><a class="btn" href="#productos">Ver los productos</a><a class="btn btn--ghost" href="#banda-sonora">{icon("play")}La banda sonora</a></div>
  </div>
  <div class="shop-hero__media grain">
    {local_img("club-house-espalda-terraza", "Chico de espaldas con la Club House Tee en una terraza de Madrid, con cielo azul, sombrilla y auriculares Danz In", "(min-width: 900px) 38vw, 100vw", priority=True)}
    <span class="sticker">Impreso en Madrid</span>
  </div>
</section>

<section id="productos" class="container" aria-labelledby="prod-t">
  <h2 id="prod-t" class="visually-hidden">Productos</h2>
  <dz-filters class="toolbar">
    <div class="filters" role="group" aria-label="Filtros">
      <div class="filters__row"><span class="filters__label" id="fl-tipo">Tipo</span>{"".join(chip("tipo", t.lower(), t) for t in types)}</div>
      <div class="filters__row"><span class="filters__label">Talla</span>{"".join(chip("talla", s, s) for s in ["S", "M", "L", "XL"])}</div>
      <div class="filters__row"><label class="chip"><input type="checkbox" name="disponible" value="1">Solo disponibles</label>
        <div class="select-wrap"><label class="visually-hidden" for="orden">Ordenar</label>
        <select id="orden" class="select" name="orden"><option value="destacados">Destacados</option><option value="precio-asc">Precio: de menor a mayor</option><option value="precio-desc">Precio: de mayor a menor</option></select></div></div>
    </div>
    <p class="toolbar__count" aria-live="polite" data-count>{len(PRODUCTS)} productos</p>
  </dz-filters>
  <div class="grid-products grid-products--3" data-grid>{"".join(card(p, i, "(min-width: 1100px) 30vw, 48vw") for i, p in enumerate(PRODUCTS))}</div>
  <div class="empty-state no-results" data-empty>{icon("martini")}<p class="h3">Nada con esos filtros</p><p class="muted">Prueba con otra talla o quita algún filtro.</p><button class="btn btn--secondary" type="button" data-clear>Quitar filtros</button></div>
</section>

<section id="banda-sonora" class="container section" aria-labelledby="bs-t">
  <div class="soundtrack">
    <div class="stack"><p class="eyebrow" style="color:var(--accent)">Danz In Records</p><h2 id="bs-t" class="h2" data-reveal="up">La banda sonora de la colección</h2>
      <p class="lead">Ponte la Club House, dale al play y sal a la terraza. Música de nuestro sello.</p>
      <a class="btn btn--ghost" href="/musica/">Más música del sello {icon("arrow")}</a></div>
    {player(rel)}
  </div>
</section>

<section id="archivo" class="container section" aria-labelledby="arch-t">
  <div class="section-head"><div class="section-head__text"><p class="eyebrow">Archivo</p><h2 id="arch-t" class="h2" data-reveal="up">Colecciones pasadas</h2><p class="lead">Lo que ya se agotó y no vuelve. Para quien estuvo.</p></div></div>
  <div class="archive">{archive}</div>
</section>
{newsletter("drop")}'''
    items = {"@context": "https://schema.org", "@type": "ItemList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "url": f"{SITE}/tienda/{p['handle']}/", "name": p["nombre"]} for i, p in enumerate(PRODUCTS)]}
    page("/tienda/", "Tienda Danzflor · Camisetas y streetwear de cultura club | Danz Collective",
         "Compra la colección Tracks & Cocktails de Danzflor: camisetas heavyweight de algodón orgánico, bañador y bolsa, impresos en Madrid. Envío gratis en España desde 75 €.",
         body, active="/tienda/", ld=[crumbs_ld, items])


def build_product(p):
    st = stock(p)
    out = st["key"] == "out"
    one = len(p["variantes"]) == 1
    imgs = p["imagenes"]
    n = len(imgs)
    gallery = []
    for i, im in enumerate(imgs):
        flat = im["src"].lower().endswith(".png")
        sizes = "(min-width: 1000px) 60vw, 88vw" if i == 0 else "(min-width: 1000px) 30vw, 88vw"
        gallery.append(
            f'<button type="button" class="gallery__item{" is-flat" if flat else ""}" data-zoom="{i}" aria-label="Ampliar foto {i + 1} de {n}">'
            f'<img src="{cdn(im["src"], 900)}" srcset="{cdn(im["src"], 500)} 500w, {cdn(im["src"], 900)} 900w, {cdn(im["src"], 1400)} 1400w" '
            f'sizes="{sizes}" width="{im["w"]}" height="{im["h"]}" alt="{e(im["alt"])}" '
            f'{PRIO if i == 0 else LAZY} decoding="async"></button>')
    zoom_data = [{"src": cdn(im["src"], 2000), "alt": im["alt"]} for im in imgs]
    model_txt = f'{p["modelo"]} lleva una {p["tallaModelo"]}.' if p.get("tallaModelo") else ""
    if one:
        v = p["variantes"][0]
        sizes_html = (f'<input type="hidden" value="{v["id"]}"><p class="small muted">Talla única · {e(p["color"])}</p>')
        sel = f'<dz-sizes data-buy="#buy" data-notify="notify-modal" data-product="{e(p["nombre"])}">{sizes_html}<div hidden><label class="size{" is-out" if not v["disponible"] else ""}"><input type="radio" name="talla" value="{v["id"]}" data-size="Única" {OUT_ATTR if not v["disponible"] else ""} checked>Única</label></div><p class="sizes__hint" aria-live="polite"></p></dz-sizes>'
    else:
        labels = "".join(
            f'<label class="size{" is-out" if not v["disponible"] else ""}"><input type="radio" name="talla" value="{v["id"]}" data-size="{v["talla"]}"'
            f'{" " + OUT_ATTR if not v["disponible"] else ""}>{v["talla"]}{SOLD_SR if not v["disponible"] else ""}</label>'
            for v in p["variantes"])
        sel = f'''
<dz-sizes data-buy="#buy" data-notify="notify-modal" data-model="{e(model_txt)}" data-product="{e(p["nombre"])}">
  <fieldset class="sizes">
    <div class="sizes__top"><legend>Talla</legend><button class="btn btn--ghost" type="button" data-open="size-guide">{icon("ruler")}Guía de tallas</button></div>
    <div class="sizes__grid">{labels}</div>
  </fieldset>
  <p class="sizes__hint" aria-live="polite"></p>
</dz-sizes>'''
    buy_btn = (f'<button id="buy" class="btn btn--block" type="button" disabled aria-disabled="true">Agotado · edición limitada</button>'
               f'<button class="btn btn--secondary btn--block" type="button" data-open="notify-modal" data-size="">Avísame cuando vuelva</button>'
               if out else
               f'<button id="buy" class="btn btn--block" type="button" data-add-to-cart disabled>Añadir al carrito</button>'
               f'<a class="btn btn--secondary btn--block" href="{STORE}/cart" data-buy-now hidden rel="noopener">Comprar ya</a>')
    ship = A["envios"]
    rows = "".join(f'<tr><th scope="row">{e(t["destino"])}</th><td>{e(t["precio"])}{" · " + e(t["nota"]) if t.get("nota") else ""}</td><td>{e(t["plazo"])}</td></tr>' for t in ship["tarifas"])
    others = [x for x in IN_STOCK if x["handle"] != p["handle"]]
    others.sort(key=lambda x: (x["tipo"] == p["tipo"]))  # primero los de otro tipo: completan el look
    look = others[:4]
    rel = RELEASES["dnz13"]
    crumbs, crumbs_ld = breadcrumbs([("Inicio", "/"), ("Tienda", "/tienda/"), (p["nombre"], f"/tienda/{p['handle']}/")])
    product_json = {"handle": p["handle"], "title": p["nombre"], "price": p["precio"], "img": imgs[0]["src"]}
    body = f'''
{crumbs}
<div class="container pdp" data-product='{e(json.dumps(product_json, ensure_ascii=False))}'>
  <div class="gallery">
    <div class="gallery__track" data-gallery tabindex="0" aria-label="Fotos de {e(p["nombre"])}" role="region">{"".join(gallery)}</div>
    <p class="gallery__count" aria-hidden="true"><span data-gallery-now>1</span> / {n}</p>
  </div>
  <div class="buybox">
    <div class="buybox__head">
      <div class="cluster"><span class="badge {st["cls"]}">{st["label"]}</span><span class="badge badge--plain">{e(p["tipo"])}</span></div>
      <h1 class="buybox__title">{e(p["nombre"])}</h1>
      <div class="buybox__price"><p class="price price--lg">{eur(p["precio"])}</p><p class="small muted">IVA incluido · {e(p["color"])}</p></div>
    </div>
    {sel}
    <div class="buybox__actions" id="buy-actions">{buy_btn}</div>
    <div class="buybox__meta">
      {"" if out else f'<p>{icon("truck")}<span><strong>Si lo pides hoy, sale en {e(ship["preparacion"])}.</strong> <span data-eta></span></span></p>'}
      <p>{icon("swap")}<span>Envío gratis en España desde {FREE} €. Cambios en {A["cambios"]["dias"]} días.</span></p>
      <p>{icon("pin")}<span>{e(p["tejido"])}. Impreso en nuestro estudio de Madrid.</span></p>
    </div>
    <div>
      <details class="acc" open><summary>Descripción</summary><div class="acc__body"><p>{e(p["descripcion"])}</p><p><strong>Color:</strong> {e(p["color"])}<br><strong>Tejido:</strong> {e(p["tejido"])}</p></div></details>
      <details class="acc"><summary>Envíos</summary><div class="acc__body"><p>Preparamos tu pedido en {e(ship["preparacion"])}.</p>
        <div class="table-wrap"><table class="table"><caption class="visually-hidden">Tarifas de envío</caption><thead><tr><th scope="col">Destino</th><th scope="col">Precio</th><th scope="col">Plazo</th></tr></thead><tbody>{rows}</tbody></table></div>
        <p><a href="/ayuda/envios/">Toda la información de envíos</a></p></div></details>
      <details class="acc"><summary>Cambios y devoluciones</summary><div class="acc__body"><p>{e(A["cambios"]["texto"])}</p><p><a href="/ayuda/cambios/">Cómo hacer un cambio</a></p></div></details>
    </div>
  </div>
</div>

<section class="container section" aria-labelledby="look-t">
  <div class="section-head"><div class="section-head__text"><p class="eyebrow">Tracks &amp; Cocktails</p><h2 id="look-t" class="h2" data-reveal="up">Completa el look</h2></div></div>
  <div class="grid-products">{"".join(card(x, 9) for x in look)}</div>
</section>

<section class="container section" aria-labelledby="bs-t">
  <div class="soundtrack">
    <div class="stack"><p class="eyebrow" style="color:var(--accent)">Danz In Records</p><h2 id="bs-t" class="h2" data-reveal="up">La banda sonora de la colección</h2>
    <p class="lead">Para escuchar mientras eliges talla.</p></div>
    {player(rel)}
  </div>
</section>

<section class="container section" aria-labelledby="rev-t">
  <div class="reviews-empty">
    <div class="stars" aria-hidden="true">{"".join(icon("flor") for _ in range(5))}</div>
    <h2 id="rev-t" class="h3">Todavía no hay opiniones de la {e(p["nombre"])}</h2>
    <p class="muted" style="max-width:48ch">Si ya la tienes, enséñanosla: etiquétanos en Instagram con @danzflor.clothing.</p>
  </div>
</section>

<div class="buy-bar" data-buy-bar aria-hidden="true">
  <div class="buy-bar__info"><strong>{e(p["nombre"])}</strong><span>{eur(p["precio"])}{" · " + st["label"] if out else ""}</span></div>
  <button class="btn" type="button" data-buy-bar-btn tabindex="-1">{"Avísame" if out else "Elegir talla"}</button>
</div>

<dialog id="zoom" class="zoom" aria-label="Fotos ampliadas de {e(p["nombre"])}" data-images='{e(json.dumps(zoom_data, ensure_ascii=False))}'>
  <div class="zoom__bar"><p class="small muted" data-zoom-count></p><button class="btn btn--icon" type="button" data-close aria-label="Cerrar">{icon("close")}</button></div>
  <div class="zoom__stage" data-zoom-stage><img alt="" data-zoom-img></div>
  <div class="zoom__nav"><button class="btn btn--dark btn--sm" type="button" data-zoom-prev>Anterior</button><button class="btn btn--dark btn--sm" type="button" data-zoom-next>Siguiente</button></div>
</dialog>'''
    offers = [{"@type": "Offer", "sku": str(v["id"]), "name": f'{p["nombre"]} · {v["talla"]}', "price": f'{p["precio"]:.2f}', "priceCurrency": "EUR",
               "availability": "https://schema.org/InStock" if v["disponible"] else "https://schema.org/OutOfStock",
               "url": f"{SITE}/tienda/{p['handle']}/", "itemCondition": "https://schema.org/NewCondition",
               "seller": {"@type": "Organization", "name": "Danz Collective"}} for v in p["variantes"]]
    product_ld = {"@context": "https://schema.org", "@type": "Product", "name": p["nombre"], "description": p["descripcion"],
                  "image": [cdn(im["src"], 1200) for im in imgs], "brand": {"@type": "Brand", "name": "Danzflor"},
                  "color": p["color"], "material": p["tejido"], "category": p["tipo"], "offers": offers}
    m = model_image(p)
    if m and m["src"].startswith("DSC"):
        og_img, og_alt = f'{CDN}{m["src"]}?width=1200&height=630&crop=center', m["alt"]
    else:
        og_img, og_alt = None, None
    desc = f'{p["nombre"]} de Danzflor, {p["color"].lower()}. {p["tejido"]}. {eur(p["precio"])}, IVA incluido. Envío gratis en España desde {FREE} €.'
    page(f"/tienda/{p['handle']}/", f'{p["nombre"]} · {p["tipo"]} Danzflor | Danz Collective', desc, body,
         active="/tienda/", ld=[product_ld, crumbs_ld], og_image=og_img, og_alt=og_alt, og_type="product", body_cls="pdp-page",
         extra_meta=f'<meta property="product:price:amount" content="{p["precio"]:.2f}">\n<meta property="product:price:currency" content="EUR">\n<meta property="product:availability" content="{"out of stock" if out else "in stock"}">',
         preload=f'<link rel="preload" as="image" imagesrcset="{cdn(imgs[0]["src"], 500)} 500w, {cdn(imgs[0]["src"], 900)} 900w, {cdn(imgs[0]["src"], 1400)} 1400w" imagesizes="(min-width: 1000px) 60vw, 88vw" fetchpriority="high">')


def favicon():
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="-12 -12 24 24"><rect x="-12" y="-12" width="24" height="24" rx="5" fill="#0a0a0a"/>'
           '<mask id="m"><rect x="-12" y="-12" width="24" height="24" fill="#fff"/><circle r="2.2" fill="#000"/></mask>'
           '<g mask="url(#m)" fill="#ff7a3d" transform="scale(.82)"><circle cy="-6.4" r="4.3"/><circle cx="5.54" cy="-3.2" r="4.3"/><circle cx="5.54" cy="3.2" r="4.3"/>'
           '<circle cy="6.4" r="4.3"/><circle cx="-5.54" cy="3.2" r="4.3"/><circle cx="-5.54" cy="-3.2" r="4.3"/><circle r="5"/></g></svg>')
    (DIST / "favicon.svg").write_text(svg, encoding="utf-8")


def main():
    if DIST.exists():
        shutil.rmtree(DIST)
    shutil.copytree(ROOT / "static", DIST)
    favicon()
    build_home()
    build_shop()
    for p in P["productos"]:
        build_product(p)
    import build_resto
    build_resto.run()
    pages = sorted(str(x.relative_to(DIST)) for x in DIST.rglob("index.html"))
    print(f"OK · {len(pages)} páginas:\n  " + "\n  ".join(pages))


if __name__ == "__main__":
    main()
