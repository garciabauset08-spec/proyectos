"""
Danzflor · Fase 4: música, eventos, nosotros, ayuda, políticas, búsqueda y 404.
Lo llama build.py. Mismas reglas: un dato vacío no se pinta.
"""
import json

import build as B

A, P, e, icon, flor = B.A, B.P, B.e, B.icon, B.flor
C = A["contacto"]
EMAIL = C["email"]
TODAY = "19 de noviembre de 2026"
EU = ["Alemania", "Austria", "Bélgica", "Bulgaria", "Chipre", "Croacia", "Dinamarca", "Eslovaquia", "Eslovenia",
      "Estonia", "Finlandia", "Francia", "Grecia", "Hungría", "Irlanda", "Italia", "Letonia", "Lituania",
      "Luxemburgo", "Malta", "Países Bajos", "Polonia", "Portugal", "Chequia", "Rumanía", "Suecia"]  # + España = 27


def legal_flag():
    """Marca de 'pendiente de revisión legal'. Solo visible mientras la web es un concepto."""
    if not A["sitio"]["conceptBar"]:
        return "<!-- Texto pendiente de revisión legal -->"
    return f'<p class="legal-flag">{icon("alert", size=14)}Borrador pendiente de revisión legal</p>'


def address():
    return C["direccion"] + (f", {C['localidad']}" if C.get("localidad") else "")


# ---------------------------------------------------------------- MÚSICA
def build_music():
    rel = A["lanzamientos"]
    by_id = {r["id"]: r for r in rel}
    releases = "".join(f'''
    <article class="release" data-reveal="up">
      <div class="release__meta">{f'<span class="release__cat">{e(r["catalogo"])}</span>' if r.get("catalogo") else ""}<span class="badge badge--plain">{e(r["artista"])}</span></div>
      {B.player(r, 56)}
    </article>''' for r in rel)
    artists = []
    for a in A["artistas"]:
        links = "".join(f'<li><a href="{e(by_id[i]["url"])}" rel="noopener" target="_blank">{icon("play")}{e(by_id[i]["titulo"])}<span class="visually-hidden"> en SoundCloud (se abre en otra pestaña)</span></a></li>' for i in a["lanzamientos"])
        bio = f'<p class="muted">{e(a["bio"])}</p>' if a.get("bio") else ""
        origin = f'<p class="eyebrow">{e(a["origen"])}</p>' if a.get("origen") else ""
        artists.append(f'''
    <article class="artist" data-reveal="up">
      <span class="artist__initial" aria-hidden="true">{e(a["nombre"][0])}</span>
      {origin}<h3 class="h3">{e(a["nombre"])}</h3>{bio}
      <div><p class="small subtle">En Danz In Records</p><ul role="list">{links}</ul></div>
    </article>''')
    demo_name = "demos"
    body = f'''
<section class="type-hero grain" aria-labelledby="mus-t">
  <div class="vinyl type-hero__art" aria-hidden="true" data-parallax="-10"></div>
  <div class="container type-hero__inner">
    <p class="eyebrow">Danz In Records · Sello de Danz Collective</p>
    <h1 id="mus-t" class="display" data-reveal="lines-now"><span class="line-mask"><span style="--i:0">The art</span></span><span class="line-mask"><span style="--i:1" class="accent">of Mixing</span></span></h1>
    <p class="lead">Nuestro sello de house internacional, desde Madrid. Dale al play: todo suena aquí mismo, desde nuestro SoundCloud.</p>
    <div class="cluster"><a class="btn" href="#lanzamientos">Escucha el catálogo</a><a class="btn btn--secondary" href="#demos">Envía tu demo</a></div>
  </div>
</section>
{B.marquee()}

<section id="lanzamientos" class="container section" aria-labelledby="rel-t">
  <div class="section-head"><div class="section-head__text"><p class="eyebrow">Catálogo</p><h2 id="rel-t" class="h2" data-reveal="up">Lanzamientos</h2></div>
  <a class="btn btn--ghost" href="https://soundcloud.com/collectivedanz" rel="noopener" target="_blank">Perfil en SoundCloud {icon("arrow")}<span class="visually-hidden"> (se abre en otra pestaña)</span></a></div>
  <div class="releases">{releases}</div>
</section>

<section class="container section" aria-labelledby="art-t">
  <div class="section-head"><div class="section-head__text"><p class="eyebrow">Familia</p><h2 id="art-t" class="h2" data-reveal="up">Artistas</h2></div></div>
  <div class="artists">{"".join(artists)}</div>
</section>

<section class="container section" aria-labelledby="look-t">
  <div class="split split--center">
    <div class="media-frame grain">{B.local_img("club-house-espalda-terraza", "Chico de espaldas con la Club House Tee y auriculares Danz In en una terraza de Madrid", "(min-width: 900px) 40vw, 100vw")}</div>
    <div class="stack" style="--stack:var(--sp-5)"><p class="eyebrow" style="color:var(--accent)">Danzflor</p><h2 id="look-t" class="h2" data-reveal="up">Lo que se escucha, se lleva</h2>
      <p class="lead">La Club House Tee lleva en la espalda "The art of Mixing": el mismo lema del sello. Música y ropa salen de la misma familia.</p>
      <a class="btn" href="/tienda/club-house-tee/">Ver la Club House Tee</a></div>
  </div>
</section>

<section id="demos" class="container section" aria-labelledby="demo-t">
  <div class="split">
    <div class="stack" style="--stack:var(--sp-4)"><p class="eyebrow" style="color:var(--accent)">Demos</p><h2 id="demo-t" class="h2">¿Haces house? Mándanoslo</h2>
      <p class="lead">Escuchamos todo lo que llega. Pásanos un enlace privado y te respondemos en un máximo de 2 semanas.</p>
      <ul class="small muted" style="padding-left:1.2em"><li>Solo enlaces: SoundCloud privado, Dropbox o Drive.</li><li>Nada de archivos adjuntos.</li><li>Temas terminados o casi.</li></ul></div>
    <form class="sg-card stack" style="padding:var(--sp-5);border-radius:var(--radius-l);background:var(--surface-1);box-shadow:inset 0 0 0 1px var(--line)" {B.form_attrs(demo_name)}>
      {B.form_hidden(demo_name)}
      <div class="form-fields stack">
        <div class="field"><label class="field__label" for="d-name">Nombre artístico</label><input class="input" id="d-name" name="artista" required minlength="2" autocomplete="nickname">{B.field_error()}</div>
        <div class="field"><label class="field__label" for="d-email">Email</label><input class="input" id="d-email" name="email" type="email" required autocomplete="email">{B.field_error()}</div>
        <div class="field"><label class="field__label" for="d-link">Enlace privado</label><input class="input" id="d-link" name="enlace" type="url" required placeholder="https://soundcloud.com/…" aria-describedby="d-link-hint"><p class="field__hint" id="d-link-hint">Que se pueda escuchar sin pedir permiso.</p>{B.field_error()}</div>
        <div class="field"><label class="field__label" for="d-msg">Cuéntanos algo (opcional)</label><textarea class="textarea" id="d-msg" name="mensaje" maxlength="1000"></textarea></div>
        <label class="check"><input type="checkbox" name="acepto-privacidad" required id="d-ok"><span>Acepto la <a href="/ayuda/privacidad/">política de privacidad</a>.</span></label>
        <p class="field__error" data-error-for="d-ok">{icon("alert", size=16)}<span></span></p>
        <button class="btn" type="submit">Enviar demo</button>
      </div>
      <div class="form-success" tabindex="-1">{icon("check")}<p><strong>Recibido.</strong> Lo escuchamos con calma y te contestamos en 2 semanas como mucho.</p></div>
    </form>
  </div>
</section>
{B.newsletter("musica")}'''
    recordings = [{"@context": "https://schema.org", "@type": "MusicRecording" if "/sets/" not in r["url"] else "MusicAlbum",
                   "name": r["titulo"], "url": r["url"], "byArtist": {"@type": "MusicGroup", "name": r["artista"]},
                   "recordLabel" if "/sets/" in r["url"] else "publisher": {"@type": "Organization", "name": "Danz In Records"}} for r in rel]
    label = {"@context": "https://schema.org", "@type": "Organization", "name": "Danz In Records", "url": B.SITE + "/musica/",
             "parentOrganization": {"@type": "Organization", "name": "Danz Collective"}, "sameAs": ["https://soundcloud.com/collectivedanz"]}
    _, crumbs = B.breadcrumbs([("Inicio", "/"), ("Música", "/musica/")])
    B.page("/musica/", "Danz In Records · Sello de música house de Danz Collective",
           "Escucha los lanzamientos de Danz In Records, el sello de house de Danz Collective: Chicharro ES, Santacruz y Keanu Callister. Envía tu demo.",
           body, active="/musica/", ld=[label, crumbs, *recordings])


# ---------------------------------------------------------------- EVENTOS
def build_events():
    party = A.get("proximaFiesta")
    hist = A["eventosHistoria"]
    tee = B.BY_HANDLE["danzers-world-white-tee"]
    ld = []
    if party:
        agenda = f'''
    <article class="event" data-countdown-wrap>
      <p class="event__date"><span>{e(party["dia"])}</span>{e(party["mes"])}</p>
      <div class="stack"><h3 class="h3">{e(party["nombre"])}</h3><p class="muted">{e(party["sala"])} · {e(party["ciudad"])}</p>
        {f'<p class="small">Line-up: {e(party["lineup"])}</p>' if party.get("lineup") else ""}
        <dz-countdown data-date="{e(party["fecha"])}"><div class="countdown" role="timer" aria-label="Cuenta atrás">
          <div class="countdown__unit"><span class="countdown__num" data-u="d">00</span><span class="countdown__label">días</span></div>
          <div class="countdown__unit"><span class="countdown__num" data-u="h">00</span><span class="countdown__label">horas</span></div>
          <div class="countdown__unit"><span class="countdown__num" data-u="m">00</span><span class="countdown__label">min</span></div>
          <div class="countdown__unit"><span class="countdown__num" data-u="s" aria-hidden="true">00</span><span class="countdown__label">seg</span></div>
        </div></dz-countdown></div>
      <a class="btn" href="{e(party["entradas"])}" rel="noopener">Comprar entradas {icon("arrow")}</a>
    </article>'''
        ld.append({"@context": "https://schema.org", "@type": "Event", "name": party["nombre"], "startDate": party["fecha"],
                   "eventStatus": "https://schema.org/EventScheduled", "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
                   "location": {"@type": "Place", "name": party["sala"], "address": {"@type": "PostalAddress", "addressLocality": party["ciudad"], "addressCountry": "ES"}},
                   "organizer": {"@type": "Organization", "name": "Danz Collective", "url": B.SITE},
                   "offers": {"@type": "Offer", "url": party["entradas"], "availability": "https://schema.org/InStock"}})
    else:
        agenda = f'''
    <div class="agenda-empty" data-reveal="up">
      <div class="vinyl" aria-hidden="true"></div>
      <p class="eyebrow">Próximas fechas</p>
      <h3 class="h2">Estamos cerrando<br><span class="accent">la próxima</span></h3>
      <p class="lead" style="max-width:46ch">Fecha, sala y line-up muy pronto. Apúntate abajo y te llegan antes de anunciarlo, con acceso anticipado a las entradas.</p>
      <a class="btn" href="#newsletter">Quiero enterarme el primero</a>
    </div>'''
    editions = ""
    if A["ediciones"]:
        editions = '<section class="container section"><h2 class="h2">Ediciones pasadas</h2>' + "".join(
            f'<figure><img src="{e(x["foto"])}" alt="{e(x["alt"])}" loading="lazy"><figcaption>{e(x["pie"])}</figcaption></figure>' for x in A["ediciones"]) + '</section>'
    body = f'''
<section class="type-hero type-hero--party grain" aria-labelledby="ev-t">
  {flor("flor type-hero__flor flor--spin")}
  <div class="container type-hero__inner">
    <p class="eyebrow">Danzers by Danz Collective · Madrid</p>
    <h1 id="ev-t" class="display" data-reveal="lines-now"><span class="line-mask"><span style="--i:0">Come inside</span></span><span class="line-mask"><span style="--i:1" class="accent">and dance</span></span></h1>
    <p class="lead">Danzers by Danz Collective es nuestra fiesta de house y tech house en Madrid. Come inside and become part of the family.</p>
    <div class="cluster"><a class="btn" href="#agenda">Próximas fechas</a><a class="btn btn--secondary" href="#historia">Nuestra historia</a></div>
  </div>
</section>
{B.marquee()}

<section id="agenda" class="container section" aria-labelledby="ag-t">
  <div class="section-head"><div class="section-head__text"><p class="eyebrow">Agenda</p><h2 id="ag-t" class="h2" data-reveal="up">Próximas fiestas</h2></div></div>
  {agenda}
</section>

<section id="historia" class="container section" aria-labelledby="hi-t">
  <div class="split">
    <div class="stack" style="--stack:var(--sp-4)"><p class="eyebrow" style="color:var(--accent)">Desde {e(hist["inicio"].lower())}</p><h2 id="hi-t" class="h2" data-reveal="up">Nuestra historia</h2><p class="lead">{e(hist["texto"])}</p></div>
    <ol class="timeline" data-reveal="up">
      <li><time>{e(hist["inicio"])}</time><p class="h4">Primera Danzers</p><p class="small muted">Arranca la fiesta en Madrid.</p></li>
      <li><time>Danzers World</time><p class="h4">Las ediciones crecen</p><p class="small muted">Nace Danzers World y, con ella, su merch exclusivo: la V1 y la V2.</p></li>
      <li><time>2024</time><p class="h4">Nace Danz Collective</p><p class="small muted">La fiesta se junta con Danzflor y Danz In Records en un mismo colectivo.</p></li>
    </ol>
  </div>
</section>
{editions}

<section class="container section" aria-labelledby="merch-t">
  <div class="split split--center">
    <div class="stack" style="--stack:var(--sp-5)"><p class="eyebrow" style="color:var(--accent)">Merch del evento</p><h2 id="merch-t" class="h2" data-reveal="up">La camiseta de la última Danzers</h2>
      <p class="lead">{e(A["colecciones"]["danzers-world-v2"]["descripcion"])}</p>
      <p class="muted small">Las piezas del evento se hacen en tiradas cortas. Si te la perdiste, apúntate al aviso de reposición.</p></div>
    <div class="grid-products" style="grid-template-columns:minmax(0,1fr);max-width:420px">{B.card(tee, 9, "(min-width: 900px) 30vw, 100vw")}</div>
  </div>
</section>
{B.newsletter("fiestas")}'''
    _, crumbs = B.breadcrumbs([("Inicio", "/"), ("Eventos", "/eventos/")])
    B.page("/eventos/", "Danzers by Danz Collective · Fiestas de house y tech house en Madrid",
           "Danzers by Danz Collective: fiestas de house y tech house en Madrid desde 2023. Consulta las próximas fechas, entradas, la historia y el merch del evento.",
           body, active="/eventos/", ld=[crumbs, *ld])


# ---------------------------------------------------------------- NOSOTROS
def build_about():
    team = ""
    if A["equipo"]:
        team = '<section class="container section"><h2 class="h2">El equipo</h2><div class="artists">' + "".join(
            f'<article class="artist"><h3 class="h3">{e(m["nombre"])}</h3><p class="muted">{e(m["rol"])}</p></article>' for m in A["equipo"]) + '</div></section>'
    body = f'''
<section class="type-hero grain" aria-labelledby="ab-t">
  {flor("flor type-hero__flor")}
  <div class="container type-hero__inner">
    <p class="eyebrow">Nosotros · Madrid, 2024</p>
    <h1 id="ab-t" class="display" data-reveal="lines-now"><span class="line-mask"><span style="--i:0">Celebrate</span></span><span class="line-mask"><span style="--i:1" class="accent">life</span></span></h1>
    <p class="lead">Danz Collective nació en Madrid en 2024, entre amigos. Queríamos juntar en un mismo sitio lo que nos mueve: la ropa, la música house y las fiestas.</p>
  </div>
</section>

<section class="container section" aria-labelledby="hist-t">
  <div class="split split--center">
    <div class="media-frame grain">{B.local_img("tracks-cocktails-gafas", "Chico sonriendo con gafas de sol naranjas y la Tracks & Cocktails Tee, foto contrapicada con tejados y cielo", "(min-width: 900px) 40vw, 100vw")}</div>
    <div class="prose" style="max-width:none">
      <h2 id="hist-t" class="h2" style="margin-top:0">Para quien no necesita explicar dónde estuvo anoche</h2>
      <p class="lead">Empezamos con una fiesta, Danzers, y unas camisetas para la familia. Luego llegó el sello. Hoy somos tres proyectos que se alimentan entre sí: la música que pinchamos inspira la ropa, y la ropa se estrena en la pista.</p>
      <p>Todo lo hacemos desde Madrid. Las camisetas se imprimen en nuestro estudio, en algodón orgánico. La música sale por Danz In Records. Y las fiestas son el sitio donde todo se junta.</p>
      <p><strong>No es una colección. Es una actitud.</strong></p>
    </div>
  </div>
</section>

<section class="container section" aria-labelledby="pil-t">
  <div class="section-head"><div class="section-head__text"><p class="eyebrow">Los tres pilares</p><h2 id="pil-t" class="h2" data-reveal="up">Tres proyectos, una familia</h2></div></div>
  <div class="pillars">
    <a class="pillar" href="/tienda/" data-reveal="up"><span class="pillar__num" aria-hidden="true">01</span><h3 class="h3">Danzflor</h3><p class="muted">Streetwear de cultura club. Camisetas heavyweight de algodón orgánico, impresas en Madrid.</p><span class="pillar__go">Ir a la tienda {icon("arrow")}</span>{flor("flor pillar__art")}</a>
    <a class="pillar" href="/musica/" data-reveal="up"><span class="pillar__num" aria-hidden="true">02</span><h3 class="h3">Danz In Records</h3><p class="muted">Sello de house internacional con artistas de Madrid, Colombia y Países Bajos.</p><span class="pillar__go">Escuchar {icon("arrow")}</span><span class="vinyl pillar__art" style="--vinyl-size:140px" aria-hidden="true"></span></a>
    <a class="pillar" href="/eventos/" data-reveal="up"><span class="pillar__num" aria-hidden="true">03</span><h3 class="h3">Danzers</h3><p class="muted">Danzers by Danz Collective, nuestra fiesta de house y tech house en Madrid.</p><span class="pillar__go">Ver fiestas {icon("arrow")}</span>{icon("martini", "pillar__art")}</a>
  </div>
</section>
{team}
<section class="container section" aria-labelledby="cta-t">
  <div class="newsletter" style="grid-template-columns:1fr">{flor("flor newsletter__flor")}
    <h2 id="cta-t" class="h2">Come inside and become part of the family</h2>
    <div class="cluster"><a class="btn" href="/tienda/">Ver la colección</a><a class="btn" href="https://www.instagram.com/danzflor.clothing/" rel="noopener" target="_blank">Síguenos en Instagram<span class="visually-hidden"> (se abre en otra pestaña)</span></a></div>
  </div>
</section>'''
    _, crumbs = B.breadcrumbs([("Inicio", "/"), ("Nosotros", "/nosotros/")])
    B.page("/nosotros/", "Nosotros · Danz Collective, nacido en Madrid en 2024",
           "Danz Collective nació en Madrid en 2024 entre amigos: Danzflor (ropa), Danz In Records (música house) y Danzers (fiestas). Conoce nuestra historia.",
           body, active="/nosotros/", ld=[B.ORG, crumbs])


# ---------------------------------------------------------------- AYUDA
HELP = [
    ("envios", "Envíos", "truck", "Tarifas, plazos y destinos."),
    ("cambios", "Cambios y devoluciones", "swap", f"{A['cambios']['dias']} días para cambiar de idea."),
    ("tallas", "Guía de tallas", "ruler", "Cómo elegir tu talla."),
    ("faq", "Preguntas frecuentes", "chat", "Lo que más nos preguntáis."),
    ("contacto", "Contacto", "pin", "Escríbenos, te contestamos."),
    ("aviso-legal", "Aviso legal", "alert", "Quiénes somos."),
    ("privacidad", "Privacidad", "user", "Qué hacemos con tus datos."),
    ("cookies", "Cookies", "check", "Qué guardamos en tu navegador."),
]


def help_page(slug, title, meta_title, desc, content, ld=None):
    nav = "".join(f'<li><a href="/ayuda/{s}/"{B.ARIA_CUR if s == slug else ""}>{t}</a></li>' for s, t, _, _ in HELP)
    crumbs, crumbs_ld = B.breadcrumbs([("Inicio", "/"), ("Ayuda", "/ayuda/"), (title, f"/ayuda/{slug}/")])
    body = f'''{crumbs}
<div class="container help-layout">
  <nav class="help-nav" aria-label="Secciones de ayuda"><ul role="list">{nav}</ul></nav>
  <article class="prose">{content}</article>
</div>'''
    B.page(f"/ayuda/{slug}/", meta_title, desc, body, active="/ayuda/", ld=[crumbs_ld, *(ld or [])])


def ship_table():
    rows = "".join(f'<tr><th scope="row">{e(t["destino"])}</th><td>{e(t["precio"])}{" · " + e(t["nota"]) if t.get("nota") else ""}</td><td>{e(t["plazo"])}</td></tr>' for t in A["envios"]["tarifas"])
    return f'<div class="table-wrap"><table class="table"><caption class="visually-hidden">Tarifas y plazos de envío</caption><thead><tr><th scope="col">Destino</th><th scope="col">Precio</th><th scope="col">Plazo de entrega</th></tr></thead><tbody>{rows}</tbody></table></div>'


FAQ = [
    ("Pedidos y envíos", [
        ("¿Hacéis envíos internacionales?", f"Sí. Enviamos a toda España, a los 27 países de la Unión Europea y al resto del mundo. Consulta tarifas y plazos en <a href=\"/ayuda/envios/\">Envíos</a>."),
        ("¿Cuánto cuesta el envío?", f"En España, 4,99 € y gratis a partir de {B.FREE} €. A la Unión Europea, 12,99 €. Al resto del mundo, 21,99 €."),
        ("¿Cuánto tarda en llegar mi pedido?", f"Preparamos tu pedido en {A['envios']['preparacion']}. Después, en España tarda 2–5 días laborables, en la UE 5–10 y en el resto del mundo 10–20."),
        ("¿Tengo que pagar aduanas si vivo fuera de la UE?", "Puede que sí. Los envíos fuera de la Unión Europea pueden tener aranceles e impuestos de importación que cobra la aduana de tu país al recibir el paquete. No dependen de nosotros."),
        ("¿Dónde pago mi pedido?", "En el checkout oficial de Danz Collective, gestionado por Shopify. Nosotros nunca vemos ni guardamos los datos de tu tarjeta."),
    ]),
    ("Cambios y devoluciones", [
        ("¿Puedo cambiar de talla?", f"Sí. Tienes {A['cambios']['dias']} días desde que recibes el pedido. La prenda tiene que estar sin usar y con su etiqueta. Mira cómo en <a href=\"/ayuda/cambios/\">Cambios y devoluciones</a>."),
        ("¿Cómo me devolvéis el dinero?", "Al mismo método de pago que usaste, en cuanto recibamos y revisemos la prenda."),
    ]),
    ("Producto", [
        ("¿De qué están hechas las camisetas?", "De algodón orgánico de 240 g/m²: heavyweight, gruesas y extra suaves."),
        ("¿Dónde se hacen?", "Las imprimimos en nuestro estudio de Madrid."),
        ("¿Qué talla me pido?", "El corte es fácil de llevar. En cada producto te decimos qué talla lleva el modelo. Si dudas entre dos y te gusta holgada, coge la grande. Más en la <a href=\"/ayuda/tallas/\">Guía de tallas</a>."),
        ("Lo que quiero está agotado. ¿Volverá?", "Algunas piezas son de edición limitada y no vuelven. Para el resto, pulsa \"Avísame cuando vuelva\" en la ficha y te escribimos si hay reposición."),
    ]),
    ("Danz Collective", [
        ("¿Qué es Danz Collective?", "Un colectivo de Madrid que junta tres proyectos: Danzflor (ropa), Danz In Records (sello de música house) y Danzers by Danz Collective (fiestas)."),
        ("¿Cómo envío mi música al sello?", "Desde el <a href=\"/musica/#demos\">formulario de demos</a>, con un enlace privado. Respondemos en un máximo de 2 semanas."),
        ("¿Cuándo es la próxima Danzers?", "Lo anunciamos en <a href=\"/eventos/\">Eventos</a>. Si te apuntas a la newsletter, te llega antes."),
    ]),
]


def strip_tags(s):
    import re
    return re.sub(r"<[^>]+>", "", s)


def build_help():
    cards = "".join(f'<a class="help-card" href="/ayuda/{s}/">{icon(i)}<span class="h4">{t}</span><span class="small muted">{d}</span></a>' for s, t, i, d in HELP)
    crumbs, crumbs_ld = B.breadcrumbs([("Inicio", "/"), ("Ayuda", "/ayuda/")])
    body = f'''{crumbs}
<section class="container section" style="padding-top:var(--sp-5)" aria-labelledby="help-t">
  <div class="stack" style="--stack:var(--sp-4);margin-bottom:var(--sp-6)"><p class="eyebrow" style="color:var(--accent)">Ayuda</p><h1 id="help-t" class="h1">¿En qué te echamos una mano?</h1>
  <p class="lead">Envíos, cambios, tallas y todo lo demás. Si no lo encuentras, escríbenos a <a href="mailto:{EMAIL}">{EMAIL}</a>.</p></div>
  <div class="help-grid">{cards}</div>
</section>'''
    B.page("/ayuda/", "Ayuda · Envíos, cambios, tallas y contacto | Danz Collective",
           "Centro de ayuda de Danz Collective: envíos, cambios y devoluciones, guía de tallas, preguntas frecuentes y contacto.",
           body, active="/ayuda/", ld=[crumbs_ld])

    # --- Envíos
    help_page("envios", "Envíos", "Envíos · Tarifas y plazos de entrega | Danz Collective",
              f"Envíos de Danz Collective: España 4,99 € (gratis desde {B.FREE} €), Unión Europea 12,99 € y resto del mundo 21,99 €. Preparación en 1–3 días laborables.", f'''
<h1 class="h1">Envíos</h1>
{legal_flag()}
<p class="lead">Preparamos tu pedido en <strong>{e(A["envios"]["preparacion"])}</strong>. Te mandamos el número de seguimiento por email en cuanto sale.</p>
{ship_table()}
<p>Los plazos cuentan en días laborables desde que el pedido sale de nuestro estudio.</p>
<h2>Unión Europea</h2>
<p>Enviamos a los 27 países de la UE: España, {", ".join(EU[:-1])} y {EU[-1]}.</p>
<h2>Canarias, Ceuta y Melilla</h2>
<p>Estamos cerrando las condiciones para estos destinos porque tienen su propio régimen de impuestos. Antes de hacer tu pedido, escríbenos a <a href="mailto:{EMAIL}">{EMAIL}</a> y te decimos el precio y el plazo.</p>
<h2>Fuera de la Unión Europea</h2>
<p>Los envíos fuera de la UE pueden tener aranceles, IVA de importación o gastos de gestión que cobra la aduana del país de destino al entregar el paquete. Esos importes no están incluidos en el precio y corren a cargo de quien lo recibe.</p>
<h2>¿Algún problema con tu envío?</h2>
<p>Escríbenos a <a href="mailto:{EMAIL}">{EMAIL}</a> con tu número de pedido y lo miramos.</p>
<p class="updated">Última actualización: {TODAY}</p>''')

    # --- Cambios
    d = A["cambios"]["dias"]
    help_page("cambios", "Cambios y devoluciones", "Cambios y devoluciones en 14 días | Danz Collective",
              f"Tienes {d} días desde la entrega para cambiar o devolver tu pedido de Danzflor. Prenda sin usar y con etiqueta. Reembolso al mismo método de pago.", f'''
<h1 class="h1">Cambios y devoluciones</h1>
{legal_flag()}
<p class="lead">Tienes <strong>{d} días naturales desde que recibes tu pedido</strong> para cambiarlo o devolverlo, sin dar explicaciones.</p>
<h2>Condiciones</h2>
<ul><li>La prenda tiene que estar sin usar, sin lavar y con su etiqueta.</li><li>Si la prenda llega con un defecto o nos hemos equivocado, el envío de vuelta lo pagamos nosotros.</li><li>En el resto de casos, el envío de vuelta corre de tu cuenta.</li></ul>
<h2>Cómo hacerlo</h2>
<ol><li>Escríbenos a <a href="mailto:{EMAIL}">{EMAIL}</a> con tu número de pedido y qué quieres hacer: cambiar de talla o devolver.</li><li>Te respondemos con la dirección a la que enviarlo.</li><li>Cuando recibimos y revisamos la prenda, te mandamos la nueva talla o te hacemos el reembolso.</li></ol>
<h2>Reembolso</h2>
<p>Te devolvemos el dinero <strong>al mismo método de pago</strong> que usaste, en un máximo de 14 días desde que nos comunicas la devolución. Podemos esperar a recibir la prenda antes de hacerlo. Si eliges un envío más caro que el estándar, solo devolvemos el coste del envío estándar.</p>
<h2>Derecho de desistimiento</h2>
<p>Como persona consumidora en la UE tienes derecho a desistir de la compra en un plazo de 14 días naturales desde la entrega, según el Real Decreto Legislativo 1/2007 (Ley General para la Defensa de los Consumidores y Usuarios). Puedes ejercerlo escribiéndonos o usando este modelo:</p>
<div class="model-form"><p><strong>Modelo de formulario de desistimiento</strong></p><p>A la atención de Danz Collective, {e(address())}, {EMAIL}:</p><p>Por la presente le comunico que desisto de mi contrato de venta del siguiente bien: [producto y talla]. Pedido recibido el: [fecha]. Nombre: [tu nombre]. Dirección: [tu dirección]. Fecha y firma.</p></div>
<p class="updated">Última actualización: {TODAY}</p>''')

    # --- Tallas
    rows = "".join(f'<tr><th scope="row"><a href="/tienda/{p["handle"]}/">{e(p["nombre"])}</a></th><td>{e(p["modelo"])} lleva una {e(p["tallaModelo"])}</td></tr>' for p in B.PRODUCTS if p.get("tallaModelo"))
    help_page("tallas", "Guía de tallas", "Guía de tallas Danzflor · Cómo elegir tu talla | Danz Collective",
              "Guía de tallas de Danzflor: corte fácil de llevar, tallas de S a XL y la talla que lleva el modelo en cada prenda.", f'''
<h1 class="h1">Guía de tallas</h1>
<p class="lead">Nuestras camisetas tienen un <strong>corte fácil de llevar</strong>. Las hacemos de la S a la XL. Si estás entre dos tallas y te gusta holgada, coge la grande.</p>
<h2>Qué talla lleva el modelo</h2>
<div class="table-wrap"><table class="table"><caption class="visually-hidden">Talla que lleva el modelo en cada producto</caption><thead><tr><th scope="col">Producto</th><th scope="col">Talla en las fotos</th></tr></thead><tbody>{rows}</tbody></table></div>
<h2>Cómo medirte</h2>
<ol><li>Coge una camiseta que te quede como te gusta.</li><li>Ponla sobre una superficie plana.</li><li>Mide el ancho de axila a axila y el largo desde el hombro hasta el bajo.</li></ol>
<p>¿Dudas? Escríbenos a <a href="mailto:{EMAIL}">{EMAIL}</a> con tus medidas y te recomendamos talla.</p>''')

    # --- FAQ
    groups = []
    faq_ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": []}
    for g, qs in FAQ:
        items = "".join(f'<details class="acc"><summary>{e(q)}</summary><div class="acc__body"><p>{a}</p></div></details>' for q, a in qs)
        groups.append(f'<section class="faq-group"><h2>{e(g)}</h2>{items}</section>')
        faq_ld["mainEntity"] += [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": strip_tags(a)}} for q, a in qs]
    help_page("faq", "Preguntas frecuentes", "Preguntas frecuentes · Envíos, tallas y pedidos | Danz Collective",
              "Respuestas a las preguntas más habituales sobre envíos internacionales, aduanas, cambios, tallas, materiales y Danz Collective.",
              f'<h1 class="h1">Preguntas frecuentes</h1><p class="lead">Lo que más nos preguntáis. Si te falta algo, <a href="/ayuda/contacto/">escríbenos</a>.</p>{"".join(groups)}', ld=[faq_ld])

    # --- Contacto
    items = [f'<li>{icon("chat")}<div><strong>Email</strong><br><a href="mailto:{EMAIL}">{EMAIL}</a></div></li>']
    if C.get("whatsapp"):
        items.append(f'<li>{icon("chat")}<div><strong>WhatsApp</strong><br><a href="https://wa.me/{C["whatsapp"]}" rel="noopener">Escríbenos por WhatsApp</a></div></li>')
    if C.get("telefono"):
        items.append(f'<li>{icon("chat")}<div><strong>Teléfono</strong><br><a href="tel:{C["telefono"].replace(" ", "")}">{e(C["telefono"])}</a></div></li>')
    if C.get("horario"):
        items.append(f'<li>{icon("check")}<div><strong>Horario</strong><br>{e(C["horario"])}</div></li>')
    items.append(f'<li>{icon("pin")}<div><strong>Dirección</strong><br>{e(address())}</div></li>')
    name = "contacto"
    help_page("contacto", "Contacto", "Contacto · Escríbenos | Danz Collective",
              f"Contacta con Danz Collective: formulario, email {EMAIL} y dirección en Madrid. Te respondemos lo antes posible.", f'''
<h1 class="h1">Contacto</h1>
<p class="lead">¿Un pedido, una colaboración o una duda? Escríbenos y te contestamos lo antes posible.</p>
<div class="contact-grid" style="margin-top:var(--sp-6)">
  <form class="stack" {B.form_attrs(name)}>
    {B.form_hidden(name)}
    <div class="form-fields stack">
      <div class="field"><label class="field__label" for="c-name">Nombre</label><input class="input" id="c-name" name="nombre" required autocomplete="name">{B.field_error()}</div>
      <div class="field"><label class="field__label" for="c-email">Email</label><input class="input" id="c-email" name="email" type="email" required autocomplete="email">{B.field_error()}</div>
      <div class="field"><label class="field__label" for="c-topic">Motivo</label><div class="select-wrap"><select class="select" id="c-topic" name="motivo" style="border-radius:var(--radius-s);min-height:52px"><option>Un pedido</option><option>Cambios y devoluciones</option><option>Colaboraciones y prensa</option><option>Fiestas Danzers</option><option>Otra cosa</option></select></div></div>
      <div class="field"><label class="field__label" for="c-order">Número de pedido (si lo tienes)</label><input class="input" id="c-order" name="pedido" inputmode="numeric"></div>
      <div class="field"><label class="field__label" for="c-msg">Mensaje</label><textarea class="textarea" id="c-msg" name="mensaje" required minlength="10"></textarea>{B.field_error()}</div>
      <label class="check"><input type="checkbox" name="acepto-privacidad" required id="c-ok"><span>Acepto la <a href="/ayuda/privacidad/">política de privacidad</a>.</span></label>
      <p class="field__error" data-error-for="c-ok">{icon("alert", size=16)}<span></span></p>
      <button class="btn" type="submit">Enviar mensaje</button>
    </div>
    <div class="form-success" tabindex="-1">{icon("check")}<p><strong>Mensaje enviado.</strong> Te respondemos a tu email lo antes posible.</p></div>
  </form>
  <ul class="contact-list" role="list">{"".join(items)}</ul>
</div>''')

    # --- Aviso legal
    help_page("aviso-legal", "Aviso legal", "Aviso legal | Danz Collective",
              "Aviso legal de danzcollective.com: datos del titular, condiciones de uso y propiedad intelectual.", f'''
<h1 class="h1">Aviso legal</h1>
{legal_flag()}
<h2>Titular de la web</h2>
<p>En cumplimiento de la Ley 34/2002, de Servicios de la Sociedad de la Información y de Comercio Electrónico (LSSI), te informamos de que esta web pertenece a <strong>Danz Collective</strong>.</p>
<ul><li>Dirección: {e(address())}</li><li>Email: <a href="mailto:{EMAIL}">{EMAIL}</a></li></ul>
<h2>Condiciones de uso</h2>
<p>Al navegar por esta web aceptas usarla de forma lícita y no dañar su funcionamiento. Las compras se completan en el checkout oficial de la tienda, gestionado por Shopify, y se rigen por las condiciones que se muestran en ese momento.</p>
<h2>Propiedad intelectual</h2>
<p>Los diseños, logotipos, fotos, textos y música de esta web son de Danz Collective o de sus artistas y colaboradores. No puedes copiarlos ni usarlos sin permiso.</p>
<h2>Enlaces a terceros</h2>
<p>Enlazamos a Instagram y SoundCloud. No somos responsables del contenido ni de las políticas de esas plataformas.</p>
<h2>Legislación aplicable</h2>
<p>Esta web se rige por la legislación española.</p>
<p class="updated">Última actualización: {TODAY}</p>''')

    # --- Privacidad
    help_page("privacidad", "Privacidad", "Política de privacidad | Danz Collective",
              "Cómo trata Danz Collective tus datos personales: pedidos, newsletter, formularios, analítica con tu consentimiento y tus derechos según el RGPD.", f'''
<h1 class="h1">Política de privacidad</h1>
{legal_flag()}
<p class="lead">Te contamos, sin letra pequeña, qué datos recogemos, para qué y qué derechos tienes. Aplicamos el Reglamento (UE) 2016/679 (RGPD) y la Ley Orgánica 3/2018 (LOPDGDD).</p>
<h2>Quién es el responsable</h2>
<p>Danz Collective · {e(address())} · <a href="mailto:{EMAIL}">{EMAIL}</a></p>
<h2>Qué datos tratamos y para qué</h2>
<div class="table-wrap"><table class="table"><caption class="visually-hidden">Tratamientos de datos</caption>
<thead><tr><th scope="col">Para qué</th><th scope="col">Qué datos</th><th scope="col">Base legal</th></tr></thead><tbody>
<tr><th scope="row">Gestionar tu pedido, el envío y los cambios</th><td>Nombre, email, dirección, teléfono y datos del pedido</td><td>Ejecución del contrato</td></tr>
<tr><th scope="row">Newsletter y acceso anticipado</th><td>Email</td><td>Tu consentimiento (puedes darte de baja cuando quieras)</td></tr>
<tr><th scope="row">Avisos de reposición</th><td>Email y producto</td><td>Tu consentimiento</td></tr>
<tr><th scope="row">Responder a contacto y demos</th><td>Nombre, email, mensaje y enlace</td><td>Tu consentimiento e interés legítimo en responderte</td></tr>
<tr><th scope="row">Analítica de la web</th><td>Datos de navegación anónimos o seudónimos</td><td>Tu consentimiento en el banner de cookies</td></tr>
</tbody></table></div>
<h2>Con quién compartimos tus datos</h2>
<ul>
<li><strong>Shopify</strong>: gestiona el checkout y los pagos. Nosotros nunca vemos los datos de tu tarjeta.</li>
<li><strong>Netlify</strong>: aloja la web y recibe los formularios.</li>
<li><strong>Google (Google Tag Manager)</strong>: solo si aceptas las cookies de analítica.</li>
<li><strong>SoundCloud</strong>: solo cuando pulsas play en un tema.</li>
<li>La empresa de transporte que entrega tu pedido.</li>
</ul>
<p>Algunos de estos proveedores pueden tratar datos fuera del Espacio Económico Europeo con garantías adecuadas, como las cláusulas contractuales tipo de la Comisión Europea o el Marco de Privacidad de Datos UE-EE. UU.</p>
<h2>Cuánto tiempo los guardamos</h2>
<p>Los datos de pedidos, el tiempo que exige la ley fiscal y mercantil. Los de la newsletter y los avisos, hasta que te des de baja. Los mensajes, el tiempo necesario para responderte.</p>
<h2>Tus derechos</h2>
<p>Puedes pedir acceso, rectificación, supresión, oposición, limitación del tratamiento y portabilidad de tus datos, y retirar tu consentimiento cuando quieras. Escríbenos a <a href="mailto:{EMAIL}">{EMAIL}</a>. Si crees que no lo hemos hecho bien, puedes reclamar ante la Agencia Española de Protección de Datos (aepd.es).</p>
<p class="updated">Última actualización: {TODAY}</p>''')

    # --- Cookies
    help_page("cookies", "Cookies", "Política de cookies | Danz Collective",
              "Qué cookies y almacenamiento usa danzcollective.com, para qué sirven y cómo aceptarlas, rechazarlas o cambiar de opinión.", f'''
<h1 class="h1">Política de cookies</h1>
{legal_flag()}
<p class="lead">Usamos solo lo imprescindible para que la web funcione. Las cookies de analítica se cargan únicamente si las aceptas.</p>
<h2>Qué usamos</h2>
<div class="table-wrap"><table class="table"><caption class="visually-hidden">Cookies y almacenamiento</caption>
<thead><tr><th scope="col">Nombre</th><th scope="col">Tipo</th><th scope="col">Para qué</th><th scope="col">Duración</th></tr></thead><tbody>
<tr><th scope="row">dz-cart-v1</th><td>Técnica (almacenamiento local)</td><td>Recordar tu carrito</td><td>Hasta que lo vacíes</td></tr>
<tr><th scope="row">dz-consent</th><td>Técnica (almacenamiento local)</td><td>Recordar tu elección sobre las cookies</td><td>12 meses</td></tr>
<tr><th scope="row">Google Tag Manager y las herramientas que carga</th><td>Analítica (de terceros)</td><td>Medir visitas y compras de forma agregada</td><td>Según la herramienta, hasta 2 años</td></tr>
<tr><th scope="row">SoundCloud</th><td>De terceros</td><td>Reproducir música. Solo se carga cuando pulsas play</td><td>Según SoundCloud</td></tr>
<tr><th scope="row">Shopify</th><td>Técnica (de terceros)</td><td>Funcionamiento del checkout cuando vas a pagar</td><td>Según Shopify</td></tr>
</tbody></table></div>
<h2>Cómo cambiar de opinión</h2>
<p>Puedes aceptar o rechazar la analítica en el banner que aparece en tu primera visita, y cambiarlo cuando quieras desde el enlace "Configurar cookies" del pie de página. También puedes borrar las cookies desde los ajustes de tu navegador.</p>
<p>Base legal: artículo 22.2 de la LSSI y la Guía sobre el uso de las cookies de la AEPD.</p>
<p class="updated">Última actualización: {TODAY}</p>''')


# ---------------------------------------------------------------- BÚSQUEDA
def build_search():
    index = []
    for p in B.PRODUCTS:
        st = B.stock(p)
        index.append({"t": p["nombre"], "u": f"/tienda/{p['handle']}/", "k": p["tipo"], "img": B.cdn(p["imagenes"][0]["src"], 120),
                      "p": B.eur(p["precio"]), "s": st["label"], "q": " ".join([p["nombre"], p["tipo"], p["color"], p["tejido"], p["descripcion"]]).lower()})
    for r in A["lanzamientos"]:
        index.append({"t": f'{r["titulo"]} · {r["artista"]}', "u": "/musica/#lanzamientos", "k": "Música", "q": f'{r["titulo"]} {r["artista"]} {r.get("catalogo") or ""} danz in records house'.lower()})
    for a in A["artistas"]:
        index.append({"t": a["nombre"], "u": "/musica/", "k": "Artista", "q": f'{a["nombre"]} {a.get("bio") or ""} artista dj'.lower()})
    for s, t, _, d in HELP:
        index.append({"t": t, "u": f"/ayuda/{s}/", "k": "Ayuda", "q": f"{t} {d} ayuda".lower()})
    index += [
        {"t": "Danzers by Danz Collective", "u": "/eventos/", "k": "Fiestas", "q": "danzers fiesta fiestas eventos entradas house tech house madrid danzers world"},
        {"t": "Nosotros", "u": "/nosotros/", "k": "Danz Collective", "q": "nosotros historia equipo madrid colectivo"},
    ]
    (B.DIST / "data").mkdir(exist_ok=True)
    (B.DIST / "data/busqueda.json").write_text(json.dumps(index, ensure_ascii=False), encoding="utf-8")
    popular = ["Club House", "Camiseta", "Bañador", "Envíos", "Chicharro ES", "Danzers"]
    chips = "".join(f'<a class="chip" href="/buscar/?q={e(x)}">{e(x)}</a>' for x in popular)
    crumbs, crumbs_ld = B.breadcrumbs([("Inicio", "/"), ("Buscar", "/buscar/")])
    body = f'''{crumbs}
<section class="container section" style="padding-top:var(--sp-5)" aria-labelledby="s-t">
  <h1 id="s-t" class="h1" style="margin-bottom:var(--sp-5)">Buscar</h1>
  <dz-search>
    <form class="search-box" role="search" action="/buscar/" method="get">
      {icon("search")}
      <label class="visually-hidden" for="q">Buscar en Danz Collective</label>
      <input class="input" id="q" name="q" type="search" autocomplete="off" placeholder="Camisetas, música, envíos…" role="combobox" aria-expanded="false" aria-controls="suggest" aria-autocomplete="list">
      <ul id="suggest" class="suggest" role="listbox" aria-label="Sugerencias" hidden></ul>
    </form>
    <div class="stack" style="margin-top:var(--sp-5)" data-popular><p class="small muted">Lo más buscado</p><div class="popular">{chips}</div></div>
    <div class="results" style="margin-top:var(--sp-7)" data-results aria-live="polite"></div>
  </dz-search>
</section>'''
    B.page("/buscar/", "Buscar | Danz Collective", "Busca camisetas, música, fiestas y ayuda en Danz Collective.", body, ld=[crumbs_ld])


# ---------------------------------------------------------------- 404 y archivos de servidor
def build_404():
    body = f'''
<section class="not-found container" aria-labelledby="nf-t">
  <div class="stack" style="--stack:var(--sp-5)">
    <p class="not-found__num" aria-hidden="true">4<span class="vinyl"></span>4</p>
    <h1 id="nf-t" class="h2">Esta pista no existe</h1>
    <p class="lead">Se nos ha rayado el disco. La página que buscas no está, o ha cambiado de sitio.</p>
    <div class="cluster" style="justify-content:center"><a class="btn" href="/">Volver al inicio</a><a class="btn btn--secondary" href="/tienda/">Ir a la tienda</a><a class="btn btn--ghost" href="/buscar/">Buscar</a></div>
  </div>
</section>'''
    out = B.page("/404/", "Página no encontrada | Danz Collective", "La página que buscas no existe en Danz Collective.", body)
    (B.DIST / "404.html").write_text(out.read_text(encoding="utf-8").replace('<link rel="canonical" href="https://danzcollective.com/404/">', '<meta name="robots" content="noindex">'), encoding="utf-8")
    import shutil
    shutil.rmtree(B.DIST / "404")


def build_server_files():
    # Redirecciones 301 desde las URLs de la web actual (Netlify)
    redirects = """# URLs antiguas de danzcollective.com → nueva web (301)
/pages/danzflor          /tienda/            301
/pages/danzin            /musica/            301
/pages/danz-in-records   /musica/            301
/pages/danzers           /eventos/           301
/pages/special-content   /eventos/           301
/pages/about-us          /nosotros/          301
/pages/contact           /ayuda/contacto/    301
/pages/faq               /ayuda/faq/         301
/policies/shipping-policy  /ayuda/envios/    301
/policies/refund-policy    /ayuda/cambios/   301
/policies/privacy-policy   /ayuda/privacidad/ 301
/policies/legal-notice     /ayuda/aviso-legal/ 301
/collections/all         /tienda/            301
/collections/*           /tienda/            301
/products/swim-short     /tienda/swim-short/ 301
/products/:handle        /tienda/:handle/    301
/search                  /buscar/            301
"""
    (B.DIST / "_redirects").write_text(redirects, encoding="utf-8")
    headers = """/*
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin
  Permissions-Policy: camera=(), microphone=(), geolocation=()
/img/*
  Cache-Control: public, max-age=31536000, immutable
/css/*
  Cache-Control: public, max-age=86400
/js/*
  Cache-Control: public, max-age=86400
"""
    (B.DIST / "_headers").write_text(headers, encoding="utf-8")
    urls = sorted(str(x.parent.relative_to(B.DIST)) for x in B.DIST.rglob("index.html"))
    urls = [u for u in urls if u not in ("estilos",)]
    loc = "".join(f"<url><loc>{B.SITE}/{'' if u == '.' else u + '/'}</loc></url>" for u in urls)
    (B.DIST / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{loc}</urlset>', encoding="utf-8")
    robots = "User-agent: *\nDisallow: /estilos/\n" + ("Disallow: /\n" if A["sitio"]["conceptBar"] else "") + f"Sitemap: {B.SITE}/sitemap.xml\n"
    (B.DIST / "robots.txt").write_text(robots, encoding="utf-8")


def run():
    build_music()
    build_events()
    build_about()
    build_help()
    build_search()
    build_404()
    build_server_files()
