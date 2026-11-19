/* ==========================================================================
   Danzflor · Componentes interactivos (Web Components, sin framework)
   Se cargan con <script type="module">. Todo funciona con teclado.
   ========================================================================== */

const REDUCED = matchMedia('(prefers-reduced-motion: reduce)');
const FINE = matchMedia('(hover: hover) and (pointer: fine)');
const FREE_SHIPPING = 75;          // € — confirmar con la marca antes de lanzar
const STORE = 'https://danzcollective.com';
const CDN = 'https://cdn.shopify.com/s/files/1/0991/7910/2555/files/';

export const eur = (n) =>
  new Intl.NumberFormat('es-ES', { style: 'currency', currency: 'EUR' }).format(n);
export const cdn = (file, w = 600) => `${CDN}${file}?width=${w}`;

const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]);
const emit = (name, detail) => document.dispatchEvent(new CustomEvent(name, { detail }));

/* ---------- Toast + región aria-live ---------- */
let toastRegion;
export function toast(msg) {
  toastRegion ??= Object.assign(document.body.appendChild(document.createElement('div')), {
    className: 'toast-region',
  });
  toastRegion.setAttribute('role', 'status');
  toastRegion.setAttribute('aria-live', 'polite');
  const t = document.createElement('div');
  t.className = 'toast';
  t.innerHTML = `<svg class="flor" aria-hidden="true"><use href="#i-flor"/></svg><span></span>`;
  t.querySelector('span').textContent = msg;
  toastRegion.append(t);
  setTimeout(() => {
    t.classList.add('is-leaving');
    t.addEventListener('animationend', () => t.remove(), { once: true });
  }, 2800);
}

/* ---------- Diálogos (carrito, modales, menú) ----------
   <dialog>.showModal() ya da: foco atrapado, Escape y fondo inerte.
   Añadimos animación de cierre, cierre al pulsar fuera y devolución del foco. */
export function openDialog(dlg, opener = document.activeElement) {
  if (!dlg || dlg.open) return;
  dlg._opener = opener;
  dlg.showModal();
  document.documentElement.style.overflow = 'hidden';
  if (!dlg._wired) {
    dlg._wired = true;
    dlg.addEventListener('cancel', (e) => { e.preventDefault(); closeDialog(dlg); });
    dlg.addEventListener('click', (e) => { if (e.target === dlg) closeDialog(dlg); });
    dlg.querySelectorAll('[data-close]').forEach((b) => b.addEventListener('click', () => closeDialog(dlg)));
  }
}
export function closeDialog(dlg) {
  if (!dlg?.open) return;
  let finished = false;
  const done = () => {
    if (finished) return;
    finished = true;
    dlg.classList.remove('is-closing');
    dlg.close();
    document.documentElement.style.overflow = '';
    dlg._opener?.focus?.();
  };
  if (REDUCED.matches) return done();
  dlg.classList.add('is-closing');
  dlg.addEventListener('animationend', done, { once: true });
  setTimeout(done, 350);   // por si la animación no llega a dispararse (pestaña en segundo plano)
}
document.addEventListener('click', (e) => {
  const btn = e.target.closest('[data-open]');
  if (!btn) return;
  const dlg = document.getElementById(btn.dataset.open);
  if (dlg) { e.preventDefault(); openDialog(dlg, btn); }
});

/* ---------- Carrito (localStorage, con fallback en memoria) ---------- */
const KEY = 'dz-cart-v1';
let memory = { items: [], note: '' };
export const cart = {
  read() {
    try { return JSON.parse(localStorage.getItem(KEY)) ?? memory; } catch { return memory; }
  },
  write(state) {
    memory = state;
    try { localStorage.setItem(KEY, JSON.stringify(state)); } catch { /* modo privado */ }
    emit('cart:change', state);
  },
  add(item) {
    const s = this.read();
    const hit = s.items.find((i) => i.id === item.id);
    if (hit) hit.qty = Math.min(hit.qty + 1, 10);
    else s.items.push({ ...item, qty: 1 });
    this.write(s);
    emit('cart:add', item);
  },
  setQty(id, qty) {
    const s = this.read();
    s.items = s.items.map((i) => (i.id === id ? { ...i, qty } : i)).filter((i) => i.qty > 0);
    this.write(s);
  },
  remove(id) { this.setQty(id, 0); },
  setNote(note) { const s = this.read(); s.note = note.slice(0, 500); this.write(s); },
  count() { return this.read().items.reduce((n, i) => n + i.qty, 0); },
  total() { return this.read().items.reduce((n, i) => n + i.qty * i.price, 0); },
  /* Enlace de carrito de Shopify: lleva al checkout oficial de la marca. */
  checkoutUrl() {
    const s = this.read();
    if (!s.items.length) return null;
    const path = s.items.map((i) => `${i.id}:${i.qty}`).join(',');
    const q = new URLSearchParams();
    if (s.note) q.set('note', s.note);
    q.set('ref', 'danzflor-web');
    return `${STORE}/cart/${path}?${q}`;
  },
};

/* Icono del carrito: contador + "pop" */
function syncCartButtons() {
  const n = cart.count();
  document.querySelectorAll('[data-cart-count]').forEach((el) => {
    el.textContent = n || '';
    el.dataset.count = n;
  });
  document.querySelectorAll('.cart-btn').forEach((b) =>
    b.setAttribute('aria-label', n ? `Abrir carrito, ${n} ${n === 1 ? 'producto' : 'productos'}` : 'Abrir carrito, vacío'));
}
document.addEventListener('cart:change', syncCartButtons);
document.addEventListener('cart:add', (e) => {
  document.querySelectorAll('.cart-btn').forEach((b) => {
    b.classList.remove('is-pop'); void b.offsetWidth; b.classList.add('is-pop');
  });
  toast(`${e.detail.title} · talla ${e.detail.size} añadida al carrito`);
});

/* ---------- <dz-cart>: carrito lateral ---------- */
class DzCart extends HTMLElement {
  connectedCallback() {
    this.dialog = this.querySelector('dialog');
    this.body = this.querySelector('[data-lines]');
    this.live = this.querySelector('[data-live]');
    this.note = this.querySelector('textarea');
    this.note?.addEventListener('change', () => cart.setNote(this.note.value));
    this.addEventListener('click', (e) => this.onClick(e));
    document.addEventListener('cart:change', () => this.render());
    document.addEventListener('cart:add', () => {
      if (this.dataset.openOnAdd !== 'false') openDialog(this.dialog);
    });
    this.render();
  }
  onClick(e) {
    const b = e.target.closest('button[data-act]');
    if (!b) return;
    const id = Number(b.closest('[data-id]')?.dataset.id);
    const line = cart.read().items.find((i) => i.id === id);
    if (b.dataset.act === 'inc' && line) cart.setQty(id, Math.min(line.qty + 1, 10));
    if (b.dataset.act === 'dec' && line) cart.setQty(id, line.qty - 1);
    if (b.dataset.act === 'rm' && line) {
      cart.remove(id);
      this.announce(`${line.title} eliminada del carrito`);
      this.dialog.querySelector('.drawer__head button')?.focus();
    }
    if (b.dataset.act === 'upsell') {
      cart.add(JSON.parse(b.dataset.item));
    }
  }
  announce(msg) { if (this.live) this.live.textContent = msg; }
  render() {
    const s = cart.read();
    const total = cart.total();
    const left = Math.max(FREE_SHIPPING - total, 0);
    const bar = this.querySelector('.ship-bar');
    bar.style.setProperty('--p', Math.min(total / FREE_SHIPPING, 1));
    bar.classList.toggle('is-done', left === 0 && total > 0);
    bar.querySelector('.ship-bar__text').innerHTML = !total
      ? `Envío gratis en España a partir de <strong>${eur(FREE_SHIPPING)}</strong>`
      : left
        ? `Te faltan <strong>${eur(left)}</strong> para el envío gratis en España`
        : `<strong>Tienes envío gratis</strong> en España. A celebrarlo.`;

    if (!s.items.length) {
      this.body.innerHTML = `
        <div class="empty-state">
          <svg aria-hidden="true"><use href="#i-martini"/></svg>
          <p class="h3">Tu copa está vacía</p>
          <p class="muted">Pásate por la colección y sírvete algo.</p>
          <a class="btn" href="/tienda/">Ver la colección</a>
        </div>`;
    } else {
      this.body.innerHTML = s.items.map((i) => `
        <div class="line" data-id="${i.id}">
          <img class="line__img" src="${cdn(i.img, 200)}" alt="" width="84" height="105" loading="lazy">
          <div>
            <p class="line__title">${esc(i.title)}</p>
            <p class="line__meta">Talla ${esc(i.size)}</p>
            <div class="line__actions">
              <div class="qty" role="group" aria-label="Cantidad de ${esc(i.title)}">
                <button type="button" data-act="dec" aria-label="Quitar una">−</button>
                <output aria-live="polite">${i.qty}</output>
                <button type="button" data-act="inc" aria-label="Añadir una">+</button>
              </div>
              <button type="button" class="link-btn" data-act="rm">Eliminar</button>
            </div>
          </div>
          <p class="price">${eur(i.price * i.qty)}</p>
        </div>`).join('') + this.upsellHtml(s);
    }
    this.querySelector('[data-total]').textContent = eur(total);
    const go = this.querySelector('[data-checkout]');
    const url = cart.checkoutUrl();
    go.toggleAttribute('hidden', !url);
    if (url) go.href = url;
    if (this.note && document.activeElement !== this.note) this.note.value = s.note ?? '';
  }
  upsellHtml(s) {
    const offers = JSON.parse(this.dataset.upsell || '[]');
    const pick = offers.find((o) => o.available && !s.items.some((i) => i.handle === o.handle));
    if (!pick) return '';
    return `
      <div class="upsell">
        <img src="${cdn(pick.img, 160)}" alt="" width="64" height="64" loading="lazy">
        <div><p class="small muted">Completa el look</p><p class="line__title">${esc(pick.title)}</p><p class="small">${eur(pick.price)} · talla ${esc(pick.size)}</p></div>
        <button type="button" class="btn btn--sm btn--secondary" data-act="upsell" data-item='${esc(JSON.stringify(pick))}'>Añadir</button>
      </div>`;
  }
}
customElements.define('dz-cart', DzCart);


/* ---------- <dz-sizes>: selector de talla con stock ---------- */
class DzSizes extends HTMLElement {
  connectedCallback() {
    this.hint = this.querySelector('.sizes__hint');
    this.addEventListener('change', () => this.update());
    this.update();
  }
  get selected() {
    const r = this.querySelector('input:checked');
    return r ? { id: Number(r.value), size: r.dataset.size, out: r.dataset.out === 'true' } : null;
  }
  update() {
    const s = this.selected;
    const buy = document.querySelector(this.dataset.buy);
    if (!this.hint) return;
    if (!s) { this.hint.textContent = this.dataset.model ? this.dataset.model : 'Elige tu talla'; buy && (buy.disabled = true); return; }
    if (s.out) {
      this.hint.innerHTML = `${s.size === 'Única' ? 'Agotada por ahora.' : `La ${esc(s.size)} está agotada.`} <button type="button" data-open="${this.dataset.notify}" data-size="${esc(s.size)}">Avísame cuando vuelva</button>`;
      buy && (buy.disabled = true);
    } else {
      this.hint.textContent = this.dataset.model || `Talla ${s.size} disponible`;
      buy && (buy.disabled = false);
    }
  }
}
customElements.define('dz-sizes', DzSizes);

/* ---------- Tarjeta de producto: compra rápida + inclinación ---------- */
document.addEventListener('click', (e) => {
  const open = e.target.closest('[data-quick-open]');
  const close = e.target.closest('[data-quick-close]');
  const pick = e.target.closest('[data-quick-add]');
  if (open) {
    const card = open.closest('.card');
    card.classList.add('is-quick-open');
    card.querySelector('.card__sizes button:not([disabled])')?.focus();
  }
  if (close) {
    const card = close.closest('.card');
    card.classList.remove('is-quick-open');
    card.querySelector('[data-quick-open]')?.focus();
  }
  if (pick) {
    const card = pick.closest('.card');
    cart.add(JSON.parse(pick.dataset.quickAdd));
    card.classList.remove('is-quick-open');
  }
});
document.addEventListener('keydown', (e) => {
  if (e.key !== 'Escape') return;
  const card = document.querySelector('.card.is-quick-open');
  if (card) { card.classList.remove('is-quick-open'); card.querySelector('[data-quick-open]')?.focus(); }
});

function wireTilt(root = document) {
  if (!FINE.matches || REDUCED.matches) return;
  root.querySelectorAll('.card__media').forEach((m) => {
    m.addEventListener('pointermove', (e) => {
      const r = m.getBoundingClientRect();
      const x = (e.clientX - r.left) / r.width - 0.5;
      const y = (e.clientY - r.top) / r.height - 0.5;
      m.style.setProperty('--rx', `${x * 6}deg`);
      m.style.setProperty('--ry', `${-y * 6}deg`);
    });
    m.addEventListener('pointerleave', () => { m.style.removeProperty('--rx'); m.style.removeProperty('--ry'); });
  });
}

/* ---------- Botones: brillo que sigue al ratón + magnéticos ---------- */
function wireButtons(root = document) {
  root.querySelectorAll('.btn').forEach((b) => {
    b.addEventListener('pointermove', (e) => {
      const r = b.getBoundingClientRect();
      b.style.setProperty('--mx', `${e.clientX - r.left}px`);
      b.style.setProperty('--my', `${e.clientY - r.top}px`);
    });
  });
  if (!FINE.matches || REDUCED.matches) return;
  root.querySelectorAll('[data-magnetic]').forEach((b) => {
    const strength = Number(b.dataset.magnetic) || 0.3;
    b.addEventListener('pointermove', (e) => {
      const r = b.getBoundingClientRect();
      const x = (e.clientX - r.left - r.width / 2) * strength;
      const y = (e.clientY - r.top - r.height / 2) * strength;
      b.style.transform = `translate(${x}px, ${y}px)`;
    });
    b.addEventListener('pointerleave', () => {
      b.style.transition = 'transform 500ms cubic-bezier(.34,1.56,.64,1)';
      b.style.transform = '';
      setTimeout(() => (b.style.transition = ''), 500);
    });
  });
}

/* ---------- Audio: un único iframe de SoundCloud para toda la web ----------
   Se crea SOLO cuando alguien pulsa play (rendimiento). En la web final vive
   en el layout con transition:persist, así sigue sonando al navegar. */
const audio = {
  widget: null, iframe: null, url: null, meta: null,
  playing: false, pos: 0, dur: 0, readyP: null,
  async ensure(url) {
    if (this.readyP) return this.readyP;
    this.readyP = new Promise((resolve, reject) => {
      const host = document.getElementById('dz-audio-host');
      this.iframe = document.createElement('iframe');
      this.iframe.title = 'Reproductor de SoundCloud';
      this.iframe.allow = 'autoplay; encrypted-media';
      this.iframe.loading = 'eager';
      this.iframe.src = `https://w.soundcloud.com/player/?${new URLSearchParams({
        url, auto_play: 'true', hide_related: 'true', show_comments: 'false',
        show_user: 'true', show_reposts: 'false', show_teaser: 'false', visual: 'false', color: '#ff7a3d',
      })}`;
      host.append(this.iframe);
      const s = document.createElement('script');
      s.src = 'https://w.soundcloud.com/player/api.js';
      s.onload = () => {
        const W = window.SC.Widget;
        this.widget = W(this.iframe);
        const E = W.Events;
        this.widget.bind(E.READY, () => {
          this.widget.getDuration((d) => { this.dur = d; this.notify(); });
          resolve();
          // iOS/Safari pueden bloquear el autoplay dentro del iframe:
          setTimeout(() => { if (!this.playing) this.needsTap(true); }, 2500);
        });
        this.widget.bind(E.PLAY, () => {
          this.playing = true; this.needsTap(false);
          this.widget.getDuration((d) => { this.dur = d; this.notify(); });
          emit('dz:music_play', { url: this.url, title: this.meta?.title });
          window.dataLayer?.push({ event: 'music_play', track: this.meta?.title });
          this.notify();
        });
        this.widget.bind(E.PAUSE, () => { this.playing = false; this.notify(); });
        this.widget.bind(E.FINISH, () => { this.playing = false; this.pos = 0; this.notify(); });
        this.widget.bind(E.PLAY_PROGRESS, (p) => { this.pos = p.currentPosition; this.notify(); });
      };
      s.onerror = () => reject(new Error('No se pudo cargar SoundCloud'));
      document.head.append(s);
    });
    return this.readyP;
  },
  async toggle(url, meta) {
    const same = url === this.url;
    if (same && this.widget) { this.playing ? this.widget.pause() : this.widget.play(); return; }
    this.url = url; this.meta = meta; this.pos = 0; this.dur = 0;
    emit('dz:audio', { loading: true });
    if (!this.widget) { await this.ensure(url); return; }
    this.widget.load(url, { auto_play: true, hide_related: true, show_comments: false, visual: false, callback: () => this.widget.play() });
  },
  seek(ratio) { if (this.widget && this.dur) this.widget.seekTo(ratio * this.dur); },
  needsTap(on) { document.getElementById('dz-audio-host')?.classList.toggle('needs-tap', on); },
  notify() { emit('dz:audio', { url: this.url, meta: this.meta, playing: this.playing, pos: this.pos, dur: this.dur }); },
};
const mmss = (ms) => { const s = Math.floor(ms / 1000); return `${Math.floor(s / 60)}:${String(s % 60).padStart(2, '0')}`; };

/* ---------- <dz-player>: interfaz propia sobre el widget ---------- */
class DzPlayer extends HTMLElement {
  connectedCallback() {
    this.url = this.dataset.url;
    this.meta = { title: this.dataset.title, artist: this.dataset.artist };
    this.btn = this.querySelector('.player__toggle');
    this.wave = this.querySelector('.wave');
    this.timeNow = this.querySelector('[data-now]');
    this.timeDur = this.querySelector('[data-dur]');
    this.buildWave();
    this.btn.addEventListener('click', () => {
      this.classList.add('is-loading');
      audio.toggle(this.url, this.meta).catch(() => {
        this.classList.remove('is-loading');
        toast('No hemos podido cargar SoundCloud. Prueba a escucharlo en su perfil.');
      });
    });
    this.wave.addEventListener('pointerdown', (e) => {
      const r = this.wave.getBoundingClientRect();
      if (audio.url === this.url) audio.seek((e.clientX - r.left) / r.width);
    });
    this.wave.addEventListener('keydown', (e) => {
      if (audio.url !== this.url || !audio.dur) return;
      const step = { ArrowRight: 0.05, ArrowLeft: -0.05 }[e.key];
      if (step) { e.preventDefault(); audio.seek(Math.min(Math.max(audio.pos / audio.dur + step, 0), 1)); }
    });
    document.addEventListener('dz:audio', (e) => this.sync(e.detail));
  }
  /* Barras decorativas (no es la forma de onda real del tema):
     pseudoaleatorias pero estables para cada URL. */
  buildWave() {
    let seed = [...this.url].reduce((a, c) => (a * 31 + c.charCodeAt(0)) >>> 0, 7);
    const rnd = () => ((seed = (seed * 1664525 + 1013904223) >>> 0) / 2 ** 32);
    const n = Number(this.dataset.bars) || 64;
    this.wave.innerHTML = Array.from({ length: n }, (_, i) => {
      const env = Math.sin((i / n) * Math.PI) * 0.6 + 0.4;
      return `<span style="--h:${(0.2 + rnd() * 0.8 * env).toFixed(2)};--i:${i}"></span>`;
    }).join('');
    this.bars = [...this.wave.children];
  }
  sync(d) {
    const mine = d.url === this.url;
    if (d.loading && !mine) this.classList.remove('is-loading');
    if (!mine) { this.classList.remove('is-playing'); this.btn.setAttribute('aria-label', `Reproducir ${this.meta.title}`); return; }
    if (d.playing !== undefined) this.classList.remove('is-loading');
    this.classList.toggle('is-playing', !!d.playing);
    this.btn.setAttribute('aria-label', `${d.playing ? 'Pausar' : 'Reproducir'} ${this.meta.title}`);
    this.btn.setAttribute('aria-pressed', String(!!d.playing));
    if (d.dur) {
      const r = d.pos / d.dur;
      const cut = Math.round(r * this.bars.length);
      this.bars.forEach((b, i) => b.classList.toggle('is-past', i < cut));
      this.wave.setAttribute('aria-valuenow', Math.round(r * 100));
      this.wave.setAttribute('aria-valuetext', `${mmss(d.pos)} de ${mmss(d.dur)}`);
      this.timeNow.textContent = mmss(d.pos);
      this.timeDur.textContent = mmss(d.dur);
    }
  }
}
customElements.define('dz-player', DzPlayer);

/* ---------- <dz-mini-player>: sigue sonando al navegar ---------- */
class DzMiniPlayer extends HTMLElement {
  connectedCallback() {
    this.box = this.querySelector('.mini-player');
    this.querySelector('[data-mini-toggle]').addEventListener('click', () => audio.toggle(audio.url, audio.meta));
    this.querySelector('[data-mini-close]').addEventListener('click', () => {
      audio.widget?.pause(); this.box.classList.remove('is-active');
    });
    document.addEventListener('dz:audio', (e) => {
      const d = e.detail;
      if (!d.url) return;
      if (d.playing) this.box.classList.add('is-active');
      this.box.classList.toggle('is-playing', !!d.playing);
      this.querySelector('strong').textContent = d.meta?.title ?? '';
      this.querySelector('.mini-player__text span').textContent = d.meta?.artist ?? '';
      const t = this.querySelector('[data-mini-toggle]');
      t.setAttribute('aria-label', d.playing ? 'Pausar' : 'Reproducir');
      t.querySelector('.i-play').style.display = d.playing ? 'none' : '';
      t.querySelector('.i-pause').style.display = d.playing ? '' : 'none';
      if (d.dur) this.box.querySelector('.mini-player__progress').style.setProperty('--p', d.pos / d.dur);
    });
  }
}
customElements.define('dz-mini-player', DzMiniPlayer);

/* ---------- <dz-countdown>: solo existe si hay una fecha real futura ---------- */
class DzCountdown extends HTMLElement {
  connectedCallback() {
    this.target = Date.parse(this.dataset.date || '');
    this.wrap = this.closest('[data-countdown-wrap]') || this;
    if (!Number.isFinite(this.target) || this.target <= Date.now()) { this.wrap.hidden = true; return; }
    this.units = Object.fromEntries([...this.querySelectorAll('[data-u]')].map((el) => [el.dataset.u, el]));
    this.tick();
    this.t = setInterval(() => this.tick(), 1000);
  }
  disconnectedCallback() { clearInterval(this.t); }
  tick() {
    let s = Math.max(0, Math.floor((this.target - Date.now()) / 1000));
    if (!s) { clearInterval(this.t); this.wrap.hidden = true; return; }
    const v = { d: Math.floor(s / 86400), h: Math.floor((s % 86400) / 3600), m: Math.floor((s % 3600) / 60), s: s % 60 };
    for (const [k, el] of Object.entries(this.units)) el.textContent = String(v[k]).padStart(2, '0');
  }
}
customElements.define('dz-countdown', DzCountdown);

/* ---------- Formularios: validación en español ---------- */
const MSG = {
  valueMissing: 'Este campo es obligatorio.',
  typeMismatch: { email: 'Revisa el email: falta algo (ej. nombre@correo.com).', url: 'Pega un enlace completo que empiece por https://' },
  patternMismatch: 'El formato no es correcto.',
  tooShort: (el) => `Escribe al menos ${el.minLength} caracteres.`,
};
function errorFor(el) {
  const v = el.validity;
  if (v.valueMissing) return el.type === 'checkbox' ? 'Necesitamos que aceptes para continuar.' : MSG.valueMissing;
  if (v.typeMismatch) return MSG.typeMismatch[el.type] ?? MSG.patternMismatch;
  if (v.patternMismatch) return el.dataset.patternMsg || MSG.patternMismatch;
  if (v.tooShort) return MSG.tooShort(el);
  return '';
}
function validateField(el) {
  const field = el.closest('.field') || el.closest('.check');
  const err = field?.querySelector('.field__error span') ?? field?.parentElement?.querySelector(`[data-error-for="${el.id}"] span`);
  const msg = el.checkValidity() ? '' : errorFor(el);
  field?.classList.toggle('is-invalid', !!msg);
  field?.classList.toggle('is-valid', !msg && el.value !== '' && el.type !== 'checkbox');
  el.setAttribute('aria-invalid', String(!!msg));
  if (err) err.textContent = msg;
  const errBox = field?.querySelector('.field__error') ?? field?.parentElement?.querySelector(`[data-error-for="${el.id}"]`);
  errBox?.classList.toggle('is-shown', !!msg);
  if (errBox) errBox.style.display = msg ? 'flex' : '';
  return !msg;
}
document.addEventListener('focusout', (e) => {
  const el = e.target;
  if (el.form?.hasAttribute('data-validate') && el.matches('input, textarea, select') && el.value !== '') validateField(el);
});
document.addEventListener('input', (e) => {
  const el = e.target;
  if (el.getAttribute('aria-invalid') === 'true') validateField(el);
});
document.addEventListener('submit', async (e) => {
  const form = e.target;
  if (!form.hasAttribute('data-validate')) return;
  e.preventDefault();
  const fields = [...form.querySelectorAll('input:not([type=hidden]), textarea, select')].filter((f) => !f.closest('[hidden]'));
  const ok = fields.map(validateField).every(Boolean);
  if (!ok) { fields.find((f) => f.getAttribute('aria-invalid') === 'true')?.focus(); return; }
  const btn = form.querySelector('[type=submit]');
  btn?.setAttribute('aria-busy', 'true');
  try {
    // En la página de estilos (data-demo) no se envía nada.
    if (!form.hasAttribute('data-demo')) {
      const body = new URLSearchParams(new FormData(form));
      const res = await fetch('/', { method: 'POST', headers: { 'Content-Type': 'application/x-www-form-urlencoded' }, body });
      if (!res.ok) throw new Error(res.status);
    } else {
      await new Promise((r) => setTimeout(r, 600));
    }
    form.classList.add('is-sent');
    form.querySelector('.form-success')?.focus();
  } catch {
    toast('Algo ha fallado al enviar. Inténtalo otra vez en un momento.');
  } finally {
    btn?.removeAttribute('aria-busy');
  }
});

/* ---------- Movimiento: GSAP + ScrollTrigger + Lenis, diferidos ----------
   Nada de esto bloquea el LCP: el contenido ya está pintado y visible. */
const loadScript = (src) => new Promise((res, rej) => {
  const s = Object.assign(document.createElement('script'), { src, async: true, onload: res, onerror: rej });
  document.head.append(s);
});
async function startMotion() {
  if (REDUCED.matches) return;
  await loadScript('https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js');
  await loadScript('https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/ScrollTrigger.min.js');
  const { gsap, ScrollTrigger } = window;
  gsap.registerPlugin(ScrollTrigger);
  document.documentElement.classList.add('js-motion');

  if (FINE.matches) {           // Lenis solo en escritorio con ratón
    await loadScript('https://unpkg.com/lenis@1.1.13/dist/lenis.min.js');
    const lenis = new window.Lenis({ lerp: 0.12, wheelMultiplier: 1 });
    lenis.on('scroll', ScrollTrigger.update);
    gsap.ticker.add((t) => lenis.raf(t * 1000));
    gsap.ticker.lagSmoothing(0);
  }

  // Titulares por líneas: el texto ya es visible; animamos solo al entrar en pantalla
  document.querySelectorAll('[data-reveal="lines"]').forEach((el) => {
    const lines = el.querySelectorAll('.line-mask > span');
    gsap.from(lines, {
      yPercent: 110, duration: 0.9, ease: 'power3.out', stagger: 0.08,
      scrollTrigger: { trigger: el, start: 'top 85%', once: true },
    });
  });
  document.querySelectorAll('[data-reveal="up"]').forEach((el) => {
    gsap.from(el, { y: 32, opacity: 0, duration: 0.8, ease: 'power3.out', scrollTrigger: { trigger: el, start: 'top 90%', once: true } });
  });
  document.querySelectorAll('[data-parallax]').forEach((el) => {
    gsap.to(el, { yPercent: Number(el.dataset.parallax) || -8, ease: 'none', scrollTrigger: { trigger: el.parentElement, scrub: true } });
  });
}

/* ---------- Arranque ---------- */
export function init(root = document) {
  syncCartButtons();
  wireTilt(root);
  wireButtons(root);
  const idle = window.requestIdleCallback || ((f) => setTimeout(f, 200));
  idle(() => startMotion().catch(() => { /* si falla la CDN, la web sigue intacta */ }));
}
