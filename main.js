/* ===========================================================
   Covexall — site behaviour (shared by every page)
   Edit LINKS / PRODUCTS below to point at the live store.
   =========================================================== */
const LINKS = {
  checkout: 'https://covexall.com',      // where the cart "Checkout" button goes
  account: 'https://covexall.com',
  'store-locator': 'https://covexall.com',
  video: 'https://www.youtube.com/@covexall',
  printables: '#',
  privacy: '#',
  terms: '#',
  facebook: '#',
  instagram: '#',
  tiktok: '#',
  youtube: '#',
};
const PRODUCTS = {
  pocket: { name: 'Covexall Pocket Hand Sanitizer', size: '50ml', price: 3.99, img: 'assets/bottle-pocket.webp', url: '/pocket-hand-sanitizer' },
  daily:  { name: 'Covexall Daily Defense Hand Sanitizer', size: '250ml', price: 7.99, img: 'assets/bottle-daily.webp', url: '/daily-defense-hand-sanitizer' },
  family: { name: 'Covexall Family Size Hand Sanitizer', size: '500ml', price: 11.99, img: 'assets/bottle-family.webp', url: '/family-size-hand-sanitizer' },
  bundle: { name: 'Covexall Protection Bundle', size: 'Pocket + Daily Defense + Family Size', price: 19.99, img: 'assets/bottle-bundle.webp', url: '/products#bundles' },
};
const FREE_SHIP_AT = 25;
const CHAT_WEBHOOK = 'https://n8n.nutricove.co/webhook/covexall-rag';

const $ = (s, r = document) => r.querySelector(s);
const $$ = (s, r = document) => [...r.querySelectorAll(s)];
const money = (n) => '$' + n.toFixed(2);

/* ---------- link wiring ---------- */
$$('[data-link]').forEach((a) => {
  const target = LINKS[a.dataset.link];
  if (!target || target === '#') return;
  a.href = target;
  if (/^https?:/.test(target)) { a.target = '_blank'; a.rel = 'noopener'; }
});

/* ---------- nav ---------- */
const navWrap = $('.nav-wrap');
const toggle = $('.nav-toggle');
const links = $('#nav-links');
if (navWrap) {
  const onScroll = () => navWrap.classList.toggle('scrolled', window.scrollY > 24);
  onScroll();
  window.addEventListener('scroll', onScroll, { passive: true });
}
if (toggle && links) {
  toggle.addEventListener('click', () => {
    const open = links.classList.toggle('open');
    toggle.setAttribute('aria-expanded', String(open));
    toggle.classList.toggle('active', open);
    document.body.classList.toggle('menu-open', open);
  });
  $$('a', links).forEach((a) => a.addEventListener('click', () => {
    links.classList.remove('open'); toggle.classList.remove('active');
    toggle.setAttribute('aria-expanded', 'false'); document.body.classList.remove('menu-open');
  }));
}

/* ---------- reveal on scroll ---------- */
const reveals = $$('.reveal');
if (location.search.includes('noanim')) {
  document.documentElement.classList.add('noanim');
  reveals.forEach((el) => el.classList.add('in'));
} else if ('IntersectionObserver' in window) {
  const io = new IntersectionObserver((entries) => {
    entries.forEach((e) => { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } });
  }, { threshold: 0.1, rootMargin: '0px 0px -30px 0px' });
  reveals.forEach((el, i) => { el.style.setProperty('--d', `${(i % 4) * 70}ms`); io.observe(el); });
  // safety net: never leave a section invisible (full-page captures, odd scroll containers)
  setTimeout(() => reveals.forEach((el) => el.classList.add('in')), 1800);
} else {
  reveals.forEach((el) => el.classList.add('in'));
}

/* ---------- hero parallax (home) ---------- */
const hero = $('.hero-visual');
if (hero && matchMedia('(pointer:fine)').matches) {
  const layers = $$('.hv-bac, .hv-viro, .hv-snot, .hv-cove', hero);
  hero.parentElement.addEventListener('mousemove', (ev) => {
    const r = hero.getBoundingClientRect();
    const dx = (ev.clientX - (r.left + r.width / 2)) / r.width;
    const dy = (ev.clientY - (r.top + r.height / 2)) / r.height;
    layers.forEach((l, i) => {
      const k = [10, 16, 22, 6][i];
      l.style.setProperty('--px', `${dx * k}px`);
      l.style.setProperty('--py', `${dy * k}px`);
    });
  });
}

/* ---------- accordions: one open per group ---------- */
$$('.faq-list, .faq-2col').forEach((group) => {
  const items = $$('details', group);
  items.forEach((d) => d.addEventListener('toggle', () => {
    if (d.open) items.forEach((o) => { if (o !== d) o.open = false; });
  }));
});

/* ---------- toast ---------- */
const toastEl = $('[data-toast]');
let toastTimer;
const toast = (msg) => {
  if (!toastEl) return;
  toastEl.textContent = msg; toastEl.classList.add('show');
  clearTimeout(toastTimer); toastTimer = setTimeout(() => toastEl.classList.remove('show'), 2400);
};

/* ---------- quantity steppers ---------- */
$$('[data-qty]').forEach((q) => {
  const input = $('input', q);
  $('[data-minus]', q).addEventListener('click', () => { input.value = Math.max(1, (+input.value || 1) - 1); });
  $('[data-plus]', q).addEventListener('click', () => { input.value = (+input.value || 1) + 1; });
  input.addEventListener('change', () => { input.value = Math.max(1, Math.floor(+input.value || 1)); });
});

/* ---------- cart (localStorage) ---------- */
const cart = (() => {
  const KEY = 'cvx_cart';
  let items = [];
  try { items = JSON.parse(localStorage.getItem(KEY) || '[]'); } catch (_) { items = []; }
  const save = () => { try { localStorage.setItem(KEY, JSON.stringify(items)); } catch (_) {} render(); };
  const count = () => items.reduce((n, i) => n + i.qty, 0);
  const subtotal = () => items.reduce((n, i) => n + i.qty * PRODUCTS[i.id].price, 0);

  const drawer = $('#cart-drawer');
  const backdrop = $('.cart-backdrop');
  const list = $('[data-cart-items]');
  const empty = $('[data-cart-empty]');

  function render() {
    const n = count();
    $$('[data-cart-count]').forEach((el) => { el.textContent = n; el.hidden = n === 0 && el.classList.contains('cart-count'); });
    if (!list) return;
    list.innerHTML = items.map((i) => {
      const p = PRODUCTS[i.id];
      return `<div class="cart-item" data-id="${i.id}">
        <img src="${p.img}" alt="">
        <div><b>${p.name}</b><small>${p.size} · ${money(p.price)}</small>
          <div class="qty" data-cart-qty><button type="button" data-minus aria-label="Decrease">−</button><input type="number" min="1" value="${i.qty}" aria-label="Quantity"><button type="button" data-plus aria-label="Increase">+</button></div>
        </div>
        <div><span class="line">${money(p.price * i.qty)}</span><button class="rm" type="button" data-remove>Remove</button></div>
      </div>`;
    }).join('');
    if (empty) empty.hidden = items.length > 0;
    const sub = subtotal();
    const st = $('[data-cart-subtotal]'); if (st) st.textContent = money(sub);
    const ship = $('[data-cart-ship]');
    if (ship) ship.textContent = items.length === 0 ? '' : sub >= FREE_SHIP_AT ? '✓ You qualify for free shipping!' : `Add ${money(FREE_SHIP_AT - sub)} more for free shipping.`;
  }
  function add(id, qty = 1) {
    if (!PRODUCTS[id]) return;
    const found = items.find((i) => i.id === id);
    if (found) found.qty += qty; else items.push({ id, qty });
    save();
    toast(`${PRODUCTS[id].name} added to cart`);
    open();
  }
  function setQty(id, qty) {
    const it = items.find((i) => i.id === id); if (!it) return;
    it.qty = Math.max(1, qty); save();
  }
  function remove(id) { items = items.filter((i) => i.id !== id); save(); }
  function open() {
    if (!drawer) return;
    drawer.classList.add('open'); drawer.setAttribute('aria-hidden', 'false');
    if (backdrop) backdrop.hidden = false;
    document.body.classList.add('menu-open');
  }
  function close() {
    if (!drawer) return;
    drawer.classList.remove('open'); drawer.setAttribute('aria-hidden', 'true');
    if (backdrop) backdrop.hidden = true;
    document.body.classList.remove('menu-open');
  }

  $$('[data-cart-open]').forEach((b) => b.addEventListener('click', open));
  $$('[data-cart-close]').forEach((b) => b.addEventListener('click', close));
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape') close(); });
  if (list) list.addEventListener('click', (e) => {
    const row = e.target.closest('.cart-item'); if (!row) return;
    const id = row.dataset.id; const input = $('input', row);
    if (e.target.closest('[data-remove]')) remove(id);
    else if (e.target.closest('[data-minus]')) setQty(id, (+input.value || 1) - 1);
    else if (e.target.closest('[data-plus]')) setQty(id, (+input.value || 1) + 1);
  });
  if (list) list.addEventListener('change', (e) => {
    const row = e.target.closest('.cart-item'); if (!row) return;
    setQty(row.dataset.id, +e.target.value || 1);
  });
  $$('[data-add]').forEach((btn) => btn.addEventListener('click', () => {
    const scope = btn.closest('.pcard, .buybox, .product, .price-box, .buy-row') || document;
    const q = $('[data-qty] input', scope);
    add(btn.dataset.add, q ? Math.max(1, +q.value || 1) : 1);
  }));
  render();
  return { add, open, close };
})();

/* ---------- wishlist (visual only) ---------- */
$$('[data-wish]').forEach((b) => b.addEventListener('click', () => {
  const on = b.classList.toggle('on');
  if (b.classList.contains('wish')) b.textContent = on ? '♥' : '♡';
  else b.textContent = on ? '♥ Saved to Wishlist' : '♡ Add to Wishlist';
  toast(on ? 'Saved to your wishlist' : 'Removed from wishlist');
}));

/* ---------- product listing: filter + sort ---------- */
(() => {
  const grid = $('[data-pgrid]'); if (!grid) return;
  const cards = $$('.pcard', grid);
  const countEl = $('[data-shop-count]');
  const none = $('[data-shop-none]');
  const sizeBoxes = $$('[data-size]');
  let cat = 'all';
  const apply = () => {
    const sizes = sizeBoxes.filter((b) => b.checked).map((b) => b.dataset.size);
    let shown = 0;
    cards.forEach((c) => {
      const isBundle = c.dataset.cat === 'bundle';
      const ok = (cat === 'all' ? !isBundle : c.dataset.cat === cat) && (sizes.length === 0 || sizes.includes(c.dataset.cat));
      c.classList.toggle('hidden', !ok); if (ok) shown++;
    });
    if (countEl) countEl.textContent = `Showing ${shown} of ${cards.length - 1} products`;
    if (none) none.hidden = shown > 0;
  };
  $$('[data-filter-cats] button').forEach((b) => b.addEventListener('click', () => {
    $$('[data-filter-cats] button').forEach((o) => o.classList.remove('active'));
    b.classList.add('active'); cat = b.dataset.cat; apply();
  }));
  sizeBoxes.forEach((b) => b.addEventListener('change', apply));
  $$('[data-cat-jump]').forEach((a) => a.addEventListener('click', () => {
    const b = $(`[data-filter-cats] button[data-cat="${a.dataset.catJump}"]`); if (b) b.click();
  }));
  const sort = $('[data-sort]');
  if (sort) sort.addEventListener('change', () => {
    const dir = sort.value;
    const sorted = [...cards].sort((a, b) => dir === 'low' ? a.dataset.price - b.dataset.price : dir === 'high' ? b.dataset.price - a.dataset.price : 0);
    if (dir === 'featured') cards.forEach((c) => grid.appendChild(c)); else sorted.forEach((c) => grid.appendChild(c));
  });
  apply();
  if (location.hash === '#bundles') { const b = $('[data-filter-cats] button[data-cat="bundle"]'); if (b) b.click(); }
})();

/* ---------- product gallery ---------- */
$$('[data-gallery]').forEach((g) => {
  const main = $('[data-gallery-main]', g);
  const thumbs = $$('.thumbs button', g);
  let idx = 0;
  const show = (i) => {
    idx = (i + thumbs.length) % thumbs.length;
    thumbs.forEach((t, j) => t.classList.toggle('active', j === idx));
    main.style.opacity = 0;
    setTimeout(() => { main.src = thumbs[idx].dataset.src; main.style.opacity = 1; }, 150);
  };
  thumbs.forEach((t, i) => t.addEventListener('click', () => show(i)));
  const prev = $('[data-gal-prev]', g), next = $('[data-gal-next]', g);
  if (prev) prev.addEventListener('click', () => show(idx - 1));
  if (next) next.addEventListener('click', () => show(idx + 1));
});

/* ---------- tabs ---------- */
$$('[data-tabs]').forEach((t) => {
  $$('[data-tab]', t).forEach((b) => b.addEventListener('click', () => {
    $$('[data-tab]', t).forEach((o) => o.classList.remove('active'));
    $$('[data-panel]', t).forEach((p) => p.classList.toggle('active', p.dataset.panel === b.dataset.tab));
    b.classList.add('active');
  }));
});

/* ---------- FAQ page: categories + search ---------- */
(() => {
  const list = $('[data-faq-list]'); if (!list) return;
  const items = $$('details', list);
  const none = $('[data-faq-none]');
  const search = $('[data-faq-search]');
  let cat = 'all';
  const apply = () => {
    const q = (search ? search.value : '').trim().toLowerCase();
    let shown = 0;
    items.forEach((d) => {
      const ok = (cat === 'all' || d.dataset.cat === cat) && (!q || d.textContent.toLowerCase().includes(q));
      d.classList.toggle('hidden', !ok); if (ok) shown++;
    });
    if (none) none.hidden = shown > 0;
  };
  $$('[data-faq-cats] button').forEach((b) => b.addEventListener('click', () => {
    $$('[data-faq-cats] button').forEach((o) => o.classList.remove('active'));
    b.classList.add('active'); cat = b.dataset.cat; apply();
  }));
  if (search) search.addEventListener('input', apply);
})();

/* ---------- contact: topic buttons fill the subject ---------- */
$$('[data-topic]').forEach((b) => b.addEventListener('click', () => {
  $$('[data-topic]').forEach((o) => o.classList.remove('active')); b.classList.add('active');
  const subj = $('[data-form="contact"] input[name="subject"]');
  if (subj) { subj.value = b.dataset.topic; subj.focus(); subj.scrollIntoView({ behavior: 'smooth', block: 'center' }); }
}));

/* ---------- forms (front-end only, stored locally) ---------- */
$$('[data-form]').forEach((form) => {
  form.addEventListener('submit', (e) => {
    e.preventDefault();
    const kind = form.dataset.form;
    const data = Object.fromEntries(new FormData(form).entries());
    const status = $('.nl-status', form);
    try {
      const key = 'cvx_' + kind;
      const list = JSON.parse(localStorage.getItem(key) || '[]');
      list.push({ ...data, at: new Date().toISOString() });
      localStorage.setItem(key, JSON.stringify(list));
    } catch (_) { /* storage unavailable */ }
    if (status) status.textContent = kind === 'contact' ? "Thanks! We'll get back to you within 24 hours." : "You're in! Cove will keep you posted.";
    form.reset();
  });
});

/* ---------- footer year ---------- */
$$('[data-year]').forEach((el) => { el.textContent = new Date().getFullYear(); });

/* ---------- Ask Cove chat ---------- */
(() => {
  const btn = $('#cx-toggle'), win = $('#cx-window'), close = $('#cx-close');
  const list = $('#cx-messages'), form = $('#cx-form'), input = $('#cx-input'), send = $('#cx-send');
  if (!btn || !win) return;

  let chatId = null;
  try {
    chatId = sessionStorage.getItem('cx_session_id');
    if (!chatId) { chatId = 'cx-' + Date.now() + '-' + Math.random().toString(36).slice(2, 8); sessionStorage.setItem('cx_session_id', chatId); }
  } catch (_) { chatId = 'cx-' + Date.now(); }

  const esc = (t) => t.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  const fmt = (t) => esc(t).replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>').replace(/\n/g, '<br>');
  const add = (type, text) => {
    const el = document.createElement('div');
    el.className = 'cx-msg ' + type;
    el.innerHTML = type === 'typing' ? '<span></span><span></span><span></span>' : fmt(text);
    list.appendChild(el); list.scrollTop = list.scrollHeight; return el;
  };

  let greeted = false, sending = false;
  const open = () => {
    win.hidden = false; btn.setAttribute('aria-expanded', 'true'); btn.classList.add('open');
    requestAnimationFrame(() => win.classList.add('visible'));
    if (!greeted) { greeted = true; add('bot', "Hey! 👋 I'm Cove. Ask me anything about Covexall — how long it protects, what it's tested against, sizes, or which bottle is right for you."); }
    setTimeout(() => input.focus(), 250);
  };
  const shut = () => {
    win.classList.remove('visible'); btn.setAttribute('aria-expanded', 'false'); btn.classList.remove('open');
    setTimeout(() => { win.hidden = true; }, 220);
  };
  btn.addEventListener('click', () => (win.hidden ? open() : shut()));
  close.addEventListener('click', shut);
  $$('[data-open-chat]').forEach((b) => b.addEventListener('click', open));
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape' && !win.hidden) shut(); });

  const ask = async () => {
    const text = input.value.trim();
    if (!text || sending) return;
    add('user', text); input.value = ''; input.style.height = '';
    sending = true; send.disabled = true;
    const typing = add('typing');
    try {
      const res = await fetch(CHAT_WEBHOOK, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ message: text, chatId }) });
      const data = await res.json();
      const reply = data.output || data.text || data.response || data.message || "Sorry, I didn't catch that. Try again?";
      typing.remove(); add('bot', reply);
    } catch (_) {
      typing.remove(); add('bot', 'Something went wrong on my end. Please try again in a moment.');
    }
    sending = false; send.disabled = false; input.focus();
  };
  form.addEventListener('submit', (e) => { e.preventDefault(); ask(); });
  input.addEventListener('keydown', (e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); ask(); } });
  input.addEventListener('input', () => { input.style.height = 'auto'; input.style.height = Math.min(input.scrollHeight, 120) + 'px'; });
})();
