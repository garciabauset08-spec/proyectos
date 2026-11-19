/* Danzflor · Arranque de la web: componentes comunes + funciones de cada página. */
import { init, cart, openDialog, closeDialog } from './componentes.js';

const $ = (s, r = document) => r.querySelector(s);
const $$ = (s, r = document) => [...r.querySelectorAll(s)];

/* ---------- "Avísame cuando vuelva": rellena producto y talla ---------- */
document.addEventListener('click', (e) => {
  const b = e.target.closest('[data-open="notify-modal"]');
  if (!b) return;
  const product = b.closest('dz-sizes')?.dataset.product || $('.buybox__title')?.textContent || 'este producto';
  const label = b.dataset.size ? `${product} · talla ${b.dataset.size}` : product;
  const dlg = $('#notify-modal');
  $('[data-notify-label]', dlg).textContent = label;
  $('input[name="producto-talla"]', dlg).value = label;
  $('form', dlg).classList.remove('is-sent');
}, true);

/* ---------- Tienda: filtros, orden y URL compartible ---------- */
class DzFilters extends HTMLElement {
  connectedCallback() {
    this.grid = $('[data-grid]');
    this.cards = $$('.card', this.grid);
    this.empty = $('[data-empty]');
    this.count = $('[data-count]', this);
    this.readUrl();
    this.addEventListener('change', () => this.apply(true));
    $('[data-clear]')?.addEventListener('click', () => {
      $$('input', this).forEach((i) => (i.checked = false));
      $('select', this).value = 'destacados';
      this.apply(true);
    });
    this.apply(false);
  }
  readUrl() {
    const q = new URLSearchParams(location.search);
    for (const name of ['tipo', 'talla']) {
      const vals = q.getAll(name).flatMap((v) => v.split(','));
      $$(`input[name="${name}"]`, this).forEach((i) => (i.checked = vals.includes(i.value.toLowerCase()) || vals.includes(i.value)));
    }
    $('input[name="disponible"]', this).checked = q.get('disponible') === '1';
    if (q.get('orden')) $('select', this).value = q.get('orden');
  }
  apply(push) {
    const tipos = $$('input[name="tipo"]:checked', this).map((i) => i.value);
    const tallas = $$('input[name="talla"]:checked', this).map((i) => i.value);
    const solo = $('input[name="disponible"]', this).checked;
    const orden = $('select', this).value;
    let n = 0;
    this.cards.forEach((c) => {
      const t = c.dataset.tallas.split(' ');
      const ok = (!tipos.length || tipos.includes(c.dataset.tipo))
        && (!tallas.length || tallas.some((s) => t.includes(s)))
        && (!solo || c.dataset.disponible === '1');
      c.classList.toggle('is-hidden', !ok);
      if (ok) n++;
    });
    const sorted = [...this.cards].sort((a, b) => {
      // Los agotados siempre al final, ordenes como ordenes
      const d = Number(b.dataset.disponible) - Number(a.dataset.disponible);
      if (d) return d;
      if (orden === 'precio-asc') return a.dataset.precio - b.dataset.precio;
      if (orden === 'precio-desc') return b.dataset.precio - a.dataset.precio;
      return a.dataset.orden - b.dataset.orden;
    });
    sorted.forEach((c) => this.grid.append(c));
    this.count.textContent = n === 1 ? '1 producto' : `${n} productos`;
    this.empty.classList.toggle('is-shown', n === 0);
    if (push) {
      const q = new URLSearchParams();
      tipos.forEach((t) => q.append('tipo', t));
      tallas.forEach((t) => q.append('talla', t));
      if (solo) q.set('disponible', '1');
      if (orden !== 'destacados') q.set('orden', orden);
      history.replaceState(null, '', `${location.pathname}${q.size ? `?${q}` : ''}${location.hash}`);
    }
  }
}
customElements.define('dz-filters', DzFilters);

/* ---------- Ficha de producto ---------- */
function pdp() {
  const root = $('[data-product]');
  if (!root) return;
  const prod = JSON.parse(root.dataset.product);
  const sizes = $('dz-sizes');
  const buy = $('[data-add-to-cart]');
  const buyNow = $('[data-buy-now]');

  // Talla del modelo en la guía de tallas
  const model = sizes?.dataset.model;
  const gm = $('[data-size-model]');
  if (model && gm) { gm.textContent = model; gm.hidden = false; }

  const selected = () => sizes?.selected;
  const syncBuyNow = () => {
    const s = selected();
    if (!buyNow) return;
    const ok = s && !s.out;
    buyNow.hidden = !ok;
    if (ok) buyNow.href = `https://danzcollective.com/cart/${s.id}:1?ref=danzflor-web`;
  };
  const syncLabel = () => {
    if (!buy) return;
    const s = selected();
    buy.textContent = !s ? 'Elige una talla' : s.out ? `Talla ${s.size} agotada` : 'Añadir al carrito';
  };
  sizes?.addEventListener('change', () => { syncBuyNow(); syncLabel(); });
  syncBuyNow();
  syncLabel();

  buy?.addEventListener('click', () => {
    const s = selected();
    if (!s || s.out) return;
    cart.add({ id: s.id, handle: prod.handle, title: prod.title, size: s.size, price: prod.price, img: prod.img });
    window.dataLayer?.push({ event: 'add_to_cart', ecommerce: { currency: 'EUR', value: prod.price, items: [{ item_id: s.id, item_name: prod.title, item_variant: s.size, price: prod.price }] } });
  });

  // Fecha de entrega estimada (España): preparación 1–3 + tránsito 2–5 días laborables
  const eta = $('[data-eta]');
  if (eta) {
    const addBusiness = (d, n) => { const x = new Date(d); while (n > 0) { x.setDate(x.getDate() + 1); if (x.getDay() % 6) n--; } return x; };
    const f = (d) => {
      const p = Object.fromEntries(new Intl.DateTimeFormat('es-ES', { weekday: 'long', day: 'numeric', month: 'long' })
        .formatToParts(d).map((x) => [x.type, x.value]));
      return `${p.weekday} ${p.day} de ${p.month}`;
    };
    const now = new Date();
    eta.textContent = `En España llega entre el ${f(addBusiness(now, 3))} y el ${f(addBusiness(now, 8))}.`;
  }

  // Contador de la galería en móvil
  const track = $('[data-gallery]');
  const now = $('[data-gallery-now]');
  if (track && now && 'IntersectionObserver' in window) {
    const io = new IntersectionObserver((entries) => {
      entries.forEach((en) => { if (en.isIntersecting) now.textContent = Number(en.target.dataset.zoom) + 1; });
    }, { root: track, threshold: 0.6 });
    $$('.gallery__item', track).forEach((i) => io.observe(i));
  }

  // Zoom a pantalla completa
  const zoom = $('#zoom');
  if (zoom) {
    const imgs = JSON.parse(zoom.dataset.images);
    const img = $('[data-zoom-img]', zoom);
    const stage = $('[data-zoom-stage]', zoom);
    const count = $('[data-zoom-count]', zoom);
    let i = 0;
    const show = (k) => {
      i = (k + imgs.length) % imgs.length;
      stage.classList.remove('is-zoomed');
      img.src = imgs[i].src; img.alt = imgs[i].alt;
      count.textContent = `Foto ${i + 1} de ${imgs.length}`;
    };
    $$('[data-zoom]').forEach((b) => b.addEventListener('click', () => { show(Number(b.dataset.zoom)); openDialog(zoom, b); }));
    $('[data-zoom-prev]', zoom).addEventListener('click', () => show(i - 1));
    $('[data-zoom-next]', zoom).addEventListener('click', () => show(i + 1));
    zoom.addEventListener('keydown', (e) => {
      if (e.key === 'ArrowRight') show(i + 1);
      if (e.key === 'ArrowLeft') show(i - 1);
    });
    img.addEventListener('click', (e) => {
      const r = img.getBoundingClientRect();
      img.style.transformOrigin = `${((e.clientX - r.left) / r.width) * 100}% ${((e.clientY - r.top) / r.height) * 100}%`;
      stage.classList.toggle('is-zoomed');
    });
  }

  // Barra de compra fija en móvil: aparece cuando el botón principal sale de pantalla
  const bar = $('[data-buy-bar]');
  const actions = $('#buy-actions');
  if (bar && actions) {
    const barBtn = $('[data-buy-bar-btn]', bar);
    let shown = null;
    const check = () => {
      const show = actions.getBoundingClientRect().bottom < 0;
      if (show === shown) return;
      shown = show;
      bar.classList.toggle('is-shown', show);
      bar.setAttribute('aria-hidden', String(!show));
      barBtn.tabIndex = show ? 0 : -1;
    };
    addEventListener('scroll', check, { passive: true });
    check();
    const label = () => {
      const s = selected();
      if (!buy) return;
      barBtn.textContent = s && !s.out ? `Añadir · talla ${s.size}` : 'Elegir talla';
    };
    sizes?.addEventListener('change', label);
    barBtn.addEventListener('click', () => {
      const s = selected();
      if (!buy) { $('[data-open="notify-modal"]')?.click(); return; }
      if (s && !s.out) buy.click();
      else { sizes.scrollIntoView({ behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth', block: 'center' }); sizes.querySelector('input:not([data-out])')?.focus(); }
    });
  }

  window.dataLayer?.push({ event: 'view_item', ecommerce: { currency: 'EUR', value: prod.price, items: [{ item_id: prod.handle, item_name: prod.title, price: prod.price }] } });
}

/* begin_checkout: al salir hacia el pago */
document.addEventListener('click', (e) => {
  if (e.target.closest('[data-checkout], [data-buy-now]')) {
    window.dataLayer?.push({ event: 'begin_checkout', ecommerce: { currency: 'EUR', value: cart.total() } });
  }
});

/* ---------- Búsqueda predictiva ---------- */
const norm = (s) => s.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '');
const escHtml = (s) => String(s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]);
const mark = (text, q) => {
  const i = norm(text).indexOf(norm(q));
  if (!q || i < 0) return escHtml(text);
  return `${escHtml(text.slice(0, i))}<mark>${escHtml(text.slice(i, i + q.length))}</mark>${escHtml(text.slice(i + q.length))}`;
};
class DzSearch extends HTMLElement {
  async connectedCallback() {
    this.input = $('input[type=search]', this);
    this.list = $('#suggest', this);
    this.results = $('[data-results]', this);
    this.popular = $('[data-popular]', this);
    try { this.index = await (await fetch('/data/busqueda.json')).json(); } catch { this.index = []; }
    this.index.forEach((x) => (x.n = norm(`${x.t} ${x.q}`)));
    const q = new URLSearchParams(location.search).get('q') || '';
    this.input.value = q;
    if (q) this.renderResults(q);
    this.active = -1;
    this.input.addEventListener('input', () => this.suggest(this.input.value.trim()));
    this.input.addEventListener('keydown', (e) => this.keys(e));
    this.input.addEventListener('blur', () => setTimeout(() => this.close(), 150));
    $('form', this).addEventListener('submit', (e) => {
      e.preventDefault();
      const v = this.input.value.trim();
      history.replaceState(null, '', v ? `?q=${encodeURIComponent(v)}` : location.pathname);
      this.close();
      this.renderResults(v);
    });
  }
  find(q) {
    const words = norm(q).split(/\s+/).filter(Boolean);
    if (!words.length) return [];
    return this.index
      .map((x) => ({ x, score: words.every((w) => x.n.includes(w)) ? (norm(x.t).startsWith(words[0]) ? 3 : norm(x.t).includes(words[0]) ? 2 : 1) : 0 }))
      .filter((r) => r.score).sort((a, b) => b.score - a.score).map((r) => r.x);
  }
  suggest(q) {
    const hits = this.find(q).slice(0, 6);
    this.active = -1;
    if (!q || !hits.length) { this.close(); return; }
    this.list.innerHTML = hits.map((h, i) => `
      <li role="option" id="sg-${i}" aria-selected="false"><a href="${h.u}">
        ${h.img ? `<img src="${h.img}" alt="" width="48" height="48">` : `<span class="flor" aria-hidden="true" style="width:48px;height:48px;display:grid;place-items:center"><svg width="24" height="24" style="color:var(--accent)"><use href="#i-${h.k === 'Música' || h.k === 'Artista' ? 'play' : 'arrow'}"/></svg></span>`}
        <span><span class="kind">${escHtml(h.k)}</span><br>${mark(h.t, q)}</span>
        ${h.p ? `<span class="price small">${h.p}</span>` : '<span></span>'}
      </a></li>`).join('');
    this.list.hidden = false;
    this.input.setAttribute('aria-expanded', 'true');
  }
  keys(e) {
    const opts = $$('[role=option]', this.list);
    if (this.list.hidden || !opts.length) return;
    if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
      e.preventDefault();
      this.active = (this.active + (e.key === 'ArrowDown' ? 1 : -1) + opts.length) % opts.length;
      opts.forEach((o, i) => o.setAttribute('aria-selected', String(i === this.active)));
      this.input.setAttribute('aria-activedescendant', opts[this.active].id);
    } else if (e.key === 'Enter' && this.active >= 0) {
      e.preventDefault();
      location.href = $('a', opts[this.active]).href;
    } else if (e.key === 'Escape') this.close();
  }
  close() {
    this.list.hidden = true;
    this.input.setAttribute('aria-expanded', 'false');
    this.input.removeAttribute('aria-activedescendant');
  }
  renderResults(q) {
    this.popular.hidden = !!q;
    if (!q) { this.results.innerHTML = ''; return; }
    const hits = this.find(q);
    const prods = hits.filter((h) => h.img);
    const rest = hits.filter((h) => !h.img);
    if (!hits.length) {
      this.results.innerHTML = `<div class="empty-state"><svg aria-hidden="true"><use href="#i-martini"/></svg>
        <p class="h3">Nada con «${escHtml(q)}»</p><p class="muted">Prueba con otra palabra o echa un vistazo a la colección.</p>
        <div class="cluster" style="justify-content:center"><a class="btn" href="/tienda/">Ver la tienda</a><a class="btn btn--secondary" href="/ayuda/">Ir a ayuda</a></div></div>`;
      this.popular.hidden = false;
      return;
    }
    this.results.innerHTML = `<p class="muted">${hits.length} ${hits.length === 1 ? 'resultado' : 'resultados'} para «${escHtml(q)}»</p>
      ${prods.length ? `<div class="grid-products">${prods.map((h) => `
        <article class="card"><div class="card__media"><div class="card__badges"><span class="badge badge--plain">${escHtml(h.s)}</span></div>
          <img class="card__img--front" src="${h.img.replace('width=120', 'width=600')}" alt="" loading="lazy" width="600" height="600"></div>
          <div class="card__info"><h2 class="card__title"><a href="${h.u}">${mark(h.t, q)}</a></h2><p class="price">${h.p}</p><p class="card__meta">${escHtml(h.k)}</p></div></article>`).join('')}</div>` : ''}
      ${rest.length ? `<ul class="results__pages" role="list">${rest.map((h) => `<li><a href="${h.u}"><span class="small muted">${escHtml(h.k)}</span><span class="h4">${mark(h.t, q)}</span></a></li>`).join('')}</ul>` : ''}`;
  }
}
customElements.define('dz-search', DzSearch);

/* ---------- Consentimiento de cookies + GTM solo si aceptas ---------- */
function consent() {
  const box = $('[data-consent]');
  if (!box) return;
  const KEY = 'dz-consent';
  const read = () => { try { return JSON.parse(localStorage.getItem(KEY)); } catch { return null; } };
  const save = (v) => { try { localStorage.setItem(KEY, JSON.stringify({ analytics: v, at: Date.now() })); } catch {} };
  const loadGtm = () => {
    const id = box.dataset.gtm;
    if (!id || window.__gtm) return;     // vacío mientras la web es un concepto
    window.__gtm = true;
    window.dataLayer = window.dataLayer || [];
    window.dataLayer.push({ 'gtm.start': Date.now(), event: 'gtm.js' });
    const s = document.createElement('script');
    s.async = true; s.src = `https://www.googletagmanager.com/gtm.js?id=${id}`;
    document.head.append(s);
  };
  const c = read();
  const expired = !c || Date.now() - c.at > 365 * 864e5;
  if (expired) box.hidden = false;
  else if (c.analytics) loadGtm();
  box.addEventListener('click', (e) => {
    const b = e.target.closest('[data-consent-choice]');
    if (!b) return;
    const ok = b.dataset.consentChoice === 'accept';
    save(ok);
    box.hidden = true;
    if (ok) loadGtm();
  });
  document.addEventListener('click', (e) => {
    if (e.target.closest('[data-consent-open]')) { box.hidden = false; $('[data-consent-choice="reject"]', box).focus(); }
  });
}

consent();
pdp();
init();
