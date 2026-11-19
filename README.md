# Web de Danz Collective · Guía de mantenimiento

Esta es la nueva web de **Danz Collective**: Danzflor, Danz In Records y Danzers by Danz Collective.

- Es una web rápida e independiente.
- **Los pagos siguen pasando por la tienda Shopify oficial** (danzcollective.com). Al pulsar "Ir al pago", el cliente llega al checkout de siempre con su carrito ya montado.
- Casi todo se cambia editando **dos archivos de texto**, sin tocar el diseño. Esta guía explica cómo.

---

## 1. Dónde está cada cosa

| Archivo | Qué contiene |
| --- | --- |
| `web/content/ajustes.json` | Contacto, envíos, política de cambios, redes, la home (foto, colección y tema destacados), **la próxima fiesta**, lanzamientos, artistas, colecciones, archivo y equipo |
| `web/static/data/productos.json` | Productos: nombre, descripción, tipo, color, tejido, talla del modelo, fotos con su texto alternativo, y tallas con stock |
| `web/static/img/` | Fotos propias: hero, lifestyle e imagen para redes |
| `PENDIENTES.md` y `CHECKLIST_LANZAMIENTO.md` | Datos que faltan y estado del lanzamiento. Son documentos internos y no están en este repositorio |

**Regla de oro: si un dato está vacío (`null`), la web no lo enseña.** Nunca aparecen huecos ni textos de relleno. En cuanto rellenas el dato, la sección aparece sola.

> Edita los `.json` con cuidado: cada texto va entre comillas `"…"` y los elementos se separan con comas. Si te equivocas, la publicación falla y Netlify te dice en qué línea. La web publicada sigue como estaba.

---

## 2. Tareas habituales

### Anunciar la próxima fiesta Danzers
En `ajustes.json`, cambia `"proximaFiesta": null` por:

```json
"proximaFiesta": {
  "nombre": "Danzers World · Edición de invierno",
  "fecha": "2026-12-20T23:00:00+01:00",
  "fecha_texto": "Sábado 20 de diciembre",
  "dia": "20",
  "mes": "Dic",
  "sala": "Nombre de la sala",
  "ciudad": "Madrid",
  "lineup": "Artista 1, Artista 2",
  "entradas": "https://enlace-de-venta-de-entradas"
}
```

Al publicar, aparecen solos:
- en la home y en Eventos, el bloque de la fiesta con **cuenta atrás** y el botón **Comprar entradas**;
- los datos estructurados de evento, para Google.

Cuando la fecha pasa, el contador desaparece. Vuelve a poner `null` hasta la siguiente.

### Cambiar el tema destacado de la home
En `ajustes.json` → `"home"` → `"lanzamientoDestacado"`, pon el `id` de uno de los `"lanzamientos"`: `"dnz13"`, `"dnz12"`, `"leoen"` o `"dnz10"`.

### Añadir un lanzamiento del sello
Añade un bloque a `"lanzamientos"`, con la URL pública del tema en el SoundCloud del sello:

```json
{ "id": "dnz14", "titulo": "Nombre del tema", "artista": "Artista", "catalogo": "DNZ14", "url": "https://soundcloud.com/collectivedanz/..." }
```

Para que salga en la ficha del artista, añade su `id` a la lista `"lanzamientos"` de ese artista en `"artistas"`.

### Cambiar la foto del hero o el texto pequeño de encima del titular
1. Sube la foto a `web/static/img/` en dos tamaños, 640 y 1200 px de ancho, en `.jpg` y `.avif` (en Mac: Vista Previa → Exportar). Por ejemplo `nueva-foto-640.jpg`, `nueva-foto-1200.jpg`, `nueva-foto-640.avif` y `nueva-foto-1200.avif`.
2. En `"home"`, pon `"heroImagen": "nueva-foto"` y describe la foto en `"heroAlt"`.

Esa descripción es lo que oye quien usa un lector de pantalla, y también ayuda en Google.

### Destacar otra colección (por ejemplo, un drop de invierno)
1. Crea la colección en `"colecciones"`, con `titulo`, `temporada` y `descripcion`.
2. Pon su clave en `"home"` → `"coleccionDestacada"`.
3. En cada producto de `productos.json`, pon esa clave en `"coleccion"`.

### Añadir un producto nuevo
1. **Primero, créalo en la tienda Shopify**, como siempre (fotos, precio y tallas).
2. Al publicar la web, el registro de Netlify dirá "producto NUEVO en la tienda".
3. Copia en `productos.json` el bloque de un producto parecido y cambia `handle` (el mismo que en Shopify), `nombre`, `precio`, `tipo`, `color`, `coleccion`, `tallaModelo`, `modelo`, `tejido`, `descripcion` y las `imagenes`.
4. Para las imágenes, usa el nombre de archivo que tienen en Shopify y escribe un `alt` que describa la foto.
5. **No hace falta copiar las tallas ni el stock**: se rellenan solos con los datos de la tienda.

Orden de las fotos: la primera es la frontal; la primera que empieza por `DSC` es la que sale al pasar el ratón por la tarjeta.

### Stock y precios
**No se tocan a mano.** Cada vez que se publica, `sync_stock.py` lee el stock y los precios reales de la tienda Shopify.

- Los productos agotados pasan solos al final y muestran "Agotado · edición limitada".
- Aunque el stock de la web tuviera unas horas de retraso, el checkout de Shopify lo vuelve a comprobar, así que nunca se vende algo que no hay.
- Recomendación: programar una publicación automática diaria (ver la sección 3).

### Datos de contacto
En `"contacto"`, rellena `telefono` (con +34), `whatsapp` (solo números, por ejemplo `34600000000`), `horario` y `localidad`. Al publicar aparecen en el pie de página, en Contacto y en la barra de confianza.

---

## 3. Publicar

### Vista previa rápida (sin cuenta de Git)
1. Entra en **app.netlify.com/drop** con la cuenta de Netlify de la marca.
2. Arrastra la carpeta `web/dist` (o descomprime `danz-vista-previa.zip`).
3. Netlify te da una URL para compartir.

En esta vista previa, los formularios ya funcionan con Netlify Forms. Los mensajes llegan en Netlify → *Forms*, y desde ahí se pueden reenviar a `info@`.

### Publicación normal (recomendada)
1. Sube esta carpeta a un repositorio de GitHub y conéctalo en Netlify. `netlify.toml` ya lo deja configurado: lee el stock, genera la web y la publica.
2. Cada cambio en los `.json` publica la web sola.
3. **Publicación diaria del stock:** en Netlify → *Build hooks*, crea un hook y prográmalo una vez al día, por ejemplo con un cron de GitHub Actions. Así el stock se refresca aunque nadie toque nada.

### Probar en tu ordenador
Hace falta Python 3, que viene con el Mac:

```bash
cd web
```

```bash
python3 build.py
```

```bash
python3 -m http.server 4322 --directory dist
```

Luego abre http://localhost:4322. En esta versión local, los formularios no envían nada, solo enseñan el mensaje de éxito.

---

## 4. Antes del lanzamiento oficial

Cuando la marca dé el visto bueno:

1. En `ajustes.json` → `"sitio"`, cambia `"conceptBar": true` por `false`. Con eso:
   - se quita la franja "Concepto de rediseño";
   - se permite que Google indexe la web;
   - se activa **Google Tag Manager (GTM-597VJ3MJ)**, que **solo se carga si la persona acepta las cookies**.
2. Revisa `CHECKLIST_LANZAMIENTO.md` y `PENDIENTES.md`. Sobre todo:
   - la revisión legal de las políticas;
   - las tarifas de envío;
   - la política de cambios en la tienda Shopify, que tiene que decir lo mismo que la web.
3. Si esta web pasa a ser danzcollective.com, las redirecciones 301 de `_redirects` llevan a la nueva página las URLs antiguas que tenga guardadas Google.
4. Pasa PageSpeed Insights (pagespeed.web.dev) en móvil sobre la home, la tienda y una ficha. El objetivo es 90 o más en todo.

---

## 5. Para quien programe

- **Generador:** `web/build.py` y `web/build_resto.py`, solo con la librería estándar de Python. Es un puente hasta pasar a **Astro**, cuando haya Node: las plantillas, el CSS (`static/css`) y los Web Components (`static/js`) se reutilizan tal cual.
- **Sistema de diseño:** `/estilos/`, una página interna con noindex.
- **QA automático:** `python3 -I qa/auditar.py web/dist` revisa enlaces, H1, títulos, alt, JSON-LD y textos prohibidos.
- **Pendiente técnico:** que la música siga sonando al navegar (necesita Astro con `transition:persist`) y servir GSAP y Lenis desde npm.
