/* Página de estilos: pinta las tarjetas con los datos reales y conecta las demos. */
import { init, cart, cdn, eur } from './componentes.js';

const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]);

/* Estado de stock a partir de las variantes (la fuente de verdad es la tienda) */
export function stockOf(p) {
  const av = p.variantes.filter((v) => v.disponible).length;
  if (!av) return { key: 'out', label: 'Agotado · edición limitada', cls: 'badge--out' };
  if (av < p.variantes.length) return { key: 'low', label: 'Últimas tallas', cls: 'badge--low' };
  return { key: 'ok', label: 'Disponible', cls: 'badge--ok' };
}

/* La foto con modelo es la primera DSC; si no hay, la segunda imagen (espalda). */
const modelImage = (p) => p.imagenes.find((i) => i.src.startsWith('DSC')) ?? p.imagenes[1];

export function cardHtml(p, i) {
  const st = stockOf(p);
  const front = p.imagenes[0];
  const model = modelImage(p);
  const url = `#producto-${p.handle}`;
  const sizes = p.variantes.map((v) => {
    const item = { id: v.id, handle: p.handle, title: p.nombre, size: v.talla, price: p.precio, img: front.src };
    return v.disponible
      ? `<button type="button" class="size" data-quick-add='${esc(JSON.stringify(item))}' aria-label="Añadir ${esc(p.nombre)} talla ${v.talla}">${v.talla}</button>`
      : `<button type="button" class="size is-out" disabled aria-label="Talla ${v.talla} agotada">${v.talla}</button>`;
  }).join('');
  return `
  <article class="card ${st.key === 'out' ? 'is-soldout' : ''}" data-reveal="up">
    <div class="card__media">
      <div class="card__badges"><span class="badge ${st.cls}">${st.label}</span></div>
      <img class="card__img--front" src="${cdn(front.src, 700)}" srcset="${cdn(front.src, 400)} 400w, ${cdn(front.src, 700)} 700w, ${cdn(front.src, 1000)} 1000w"
           sizes="(min-width: 900px) 30vw, 48vw" width="${front.w}" height="${front.h}" alt="${esc(front.alt)}" loading="${i < 2 ? 'eager' : 'lazy'}" decoding="async">
      ${model ? `<img class="card__img--model" src="${cdn(model.src, 700)}" srcset="${cdn(model.src, 400)} 400w, ${cdn(model.src, 700)} 700w"
           sizes="(min-width: 900px) 30vw, 48vw" width="${model.w}" height="${model.h}" alt="" loading="lazy" decoding="async">` : ''}
      ${st.key !== 'out' ? `
      <div class="card__quick"><button type="button" class="card__quick-btn" data-quick-open aria-label="Compra rápida de ${esc(p.nombre)}"><svg aria-hidden="true"><use href="#i-plus"/></svg></button></div>
      <div class="card__sizes" role="group" aria-label="Elige talla de ${esc(p.nombre)}">
        <div class="card__sizes-head"><span>Elige talla</span><button type="button" class="btn btn--icon" data-quick-close aria-label="Cerrar compra rápida" style="width:36px;height:36px"><svg aria-hidden="true" style="width:18px;height:18px"><use href="#i-close"/></svg></button></div>
        <div class="sizes__grid">${sizes}</div>
      </div>` : ''}
    </div>
    <div class="card__info">
      <h3 class="card__title"><a href="${url}">${esc(p.nombre)}</a></h3>
      <p class="price">${eur(p.precio)}</p>
      <p class="card__meta">${esc(p.tipo)} · ${esc(p.color)}</p>
    </div>
  </article>`;
}

async function renderCards() {
  const box = document.getElementById('cards');
  try {
    const data = await (await fetch('/data/productos.json')).json();
    const order = { ok: 0, low: 1, out: 2 };
    const list = [...data.productos].sort((a, b) => order[stockOf(a).key] - order[stockOf(b).key]);
    box.innerHTML = list.map(cardHtml).join('');
  } catch {
    box.innerHTML = '<p class="muted">No se han podido cargar los productos. Abre la página con el servidor local.</p>';
  }
}

/* Demos del carrito */
document.getElementById('demo-add')?.addEventListener('click', () =>
  cart.add({ id: 52782613725531, handle: 'club-house-tee', title: 'Club House Tee', size: 'M', price: 38, img: 'danz_cocktails_-_Artboard_21-5.png' }));
document.getElementById('buy-demo')?.addEventListener('click', () => {
  const s = document.querySelector('dz-sizes').selected;
  if (s && !s.out) cart.add({ id: s.id, handle: 'disco-culture-tee', title: 'Disco Culture Tee', size: s.size, price: 38, img: 'danz_cocktails_-_Artboard_21.png' });
});
document.getElementById('demo-clear')?.addEventListener('click', () => cart.write({ items: [], note: '' }));

/* "Avísame cuando vuelva": rellena el producto y la talla en el formulario */
document.addEventListener('click', (e) => {
  const b = e.target.closest('[data-open="notify-modal"]');
  if (!b) return;
  const dlg = document.getElementById('notify-modal');
  const label = `Disco Culture Tee · talla ${b.dataset.size}`;
  dlg.querySelector('[data-notify-label]').textContent = label;
  dlg.querySelector('input[name="producto-talla"]').value = label;
  dlg.querySelector('form').classList.remove('is-sent');
}, true);

await renderCards();
init();
