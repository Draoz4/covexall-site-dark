# Covexall — Version B (dark theme)

Static multi-page site (HTML + CSS + vanilla JS) built from the "template 2" dark mockups. Same pages, copy and behaviour as Version A (https://github.com/Draoz4/covexall-site) with the dark palette applied.

Pages: index, products, pocket-hand-sanitizer, daily-defense-hand-sanitizer, family-size-hand-sanitizer,
how-it-works, where-its-used, proof, about, contact, education, faq — the same twelve pages as Version A.

- `src/pages/*.html` — page content (edit these). Front-matter comment sets title / description / active nav.
- `src/partials/*.html` — header, footer, cart drawer, chat, and reusable sections (`{{include:name}}`)
- `src/layout.html` — page shell
- `tools/build.py` — assembles `src/` into the root `*.html` files. **Run `python tools/build.py` after editing `src/`.**
- `styles.css` — design tokens + home/shared styles; `pages.css` — page components + cart drawer
- `main.js` — nav, reveal-on-scroll, cart (localStorage), product filters/sort, galleries, tabs, FAQ search, forms (front-end only), "Ask Cove" chat (n8n RAG webhook)
- `assets/` — optimized WebP cutouts of the 3D crew (Cove, Viro, Bac, Snot, Maya, Mom), photos, product renders
- `tools/prep_assets.py` — regenerates the character cutouts from `../creatives/animation/*.png`
- `tools/crop_mockups.py` — crops every piece of artwork out of `../creatives/template 2/*.png` into `assets/mk/`

## Before launch
1. Set the checkout / account / social URLs in `LINKS` and confirm names, sizes, prices and images in `PRODUCTS` at the top of `main.js` (prices are the mockup's placeholders). Replace the bottle renders in `assets/` when final product photography is available.
2. Replace the sample reviews in the "Loved by families" section with verified customer reviews (and delete the `.sample-note` line).
3. Wire the newsletter and contact forms to your email/CRM provider (currently front-end only). Confirm the phone number and email on the Contact page.

## Deploy
Pushes to `main` deploy automatically via Vercel. Local preview: `npx serve .`
