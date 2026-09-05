# Covexall — Version B (Dark Theme) build brief

Read this whole file before touching anything. It records how Version A was built, what went wrong
the first time, and the exact procedure that produced a result the client accepted.

## What Version B is

The **same website** as Version A (this repo) with the **dark theme** applied. Same twelve pages, same
section order, same copy, same products and prices, same navigation and footer, same cart/chat behaviour.
Only the visual theme changes, following the dark mockups the client supplies.

Version A is live at https://covexall-site.vercel.app and its source is this repo
(https://github.com/Draoz4/covexall-site). **Start Version B by copying this repo**, not from scratch.

## Non-negotiable rules (learned the hard way)

1. **Each mockup PNG is one page. Reproduce it verbatim.** The client rejected two earlier attempts that
   "reinterpreted" the mockups. Do not redesign, do not simplify sections, do not swap layouts, do not
   substitute your own icons or photos when the mockup shows specific art.
2. **Crop artwork straight out of the mockup PNGs.** Hero scenes, product shots, 3D icons, photos, chalkboards,
   footer splash — all of it comes from the mockups via `tools/crop_mockups.py`. Only generate new art when
   the mockup art cannot be used (e.g. text is baked over it), and then generate it *from* the mockup with the
   character sheets as references so it matches.
3. **Characters are canonical.** Cove, Viro, Bac, Snot, Maya, Mom must match `../creatives/animation/*.png`.
   Cutouts already exist in `assets/` (`cove-*.webp`, `viro-*.webp`, `bac-*.webp`, `snot-*.webp`, `maya-*.webp`,
   `mom-*.webp`); reuse them. Never recolour the villains to match the UI.
4. **Every page in the nav, always.** Products, How It Works, Where It's Used, Proof, About Us, Education,
   FAQ, Contact Us. Do not hide links behind an "active only" rule.
5. **Show the client screenshots of every page before calling it done.** Render each page headless, compare
   against its mockup side by side, fix, re-render. Do not describe pages you have not looked at.
6. **Do not invent content.** Prices, phone numbers, reviews and copy come from the mockups. Where the
   mockup has a placeholder, keep it and flag it in the summary.

## How this repo is built

- `src/layout.html` — page shell. `src/partials/*.html` — header, footer, cart drawer, chat, and reusable
  sections (`{{include:name}}`). `src/pages/*.html` — one file per page with a front-matter comment
  (`title`, `description`, `nav`, `body`).
- `python tools/build.py` assembles `src/` into the root `*.html`. **Run it after every edit to `src/`.**
- `site.css` — single stylesheet; all colours are CSS variables at the top (`:root`). `main.js` — nav,
  cart (localStorage), product filters, galleries, tabs, FAQ search, forms, "Ask Cove" chat.
- `tools/crop_mockups.py` — `SPEC` dict of `(name, (x0,y0,x1,y1), mode)` per mockup file → `assets/mk/*.webp`.
  Modes: `photo` (keep), `cut` (flood-fill background → transparent), `glow` (transparent but keeps Cove's glow).
  Run `python tools/crop_mockups.py` (all) or `python tools/crop_mockups.py hero- step-` (name prefixes).
- `tools/prep_assets.py` — character cutouts from the 3D sheets. `tools/cut_generated.py` — cuts generated
  bottle renders / hero scene.
- `vercel.json` uses `cleanUrls`; internal links are root-relative (`/products`, `/faq`).

## Procedure for Version B

1. Copy this repo to a sibling folder, e.g. `Clients/Covexall/covexall-site-dark/`. Remove `.git`, `.vercel`,
   `_shots/`, `assets/gen/`. `git init`.
2. Put the client's dark mockups in `../creatives/template 2/` (one PNG per page, same page names as
   `template 1`). Note each PNG's pixel size — the crop boxes in `SPEC` are in mockup pixels. If the dark
   mockups are the same size and layout as the light ones the boxes may only need small nudges; otherwise
   re-measure every box (view the PNG with a coordinate grid, as was done for `viro` sheets).
3. Point `SRC` in `tools/crop_mockups.py` at `template 2`, re-crop, and build a contact sheet of
   `assets/mk/` to check every crop (no label text caught, no neighbouring elements, backgrounds clean).
   For `cut` mode on dark backgrounds the flood fill works the same (it samples the corner colour).
4. Re-theme `site.css`: replace the `:root` tokens with the dark palette below, then walk every component
   (nav, panels, tiles, cards, tables, forms, cart drawer, chat, footer) converting white/light surfaces to the
   layered dark surfaces. Keep layout, spacing and geometry identical.
5. Re-check hero handling: the inner-page hero art is the right-hand crop of each mockup, masked to fade
   into the section background on its left edge (`.ph-art` mask + `.ph-fade`). Update the fade colours to
   the dark background or the seam will show. The home hero is a full-bleed scene (`assets/hero-scene.webp`);
   for Version B crop the dark home mockup's hero band and, if text is baked over it, remove the text with
   the image-edit tool (`gemini_edit_image`, prompt: remove all text/buttons/nav, fill with matching
   background, keep characters exactly) — that is what produced the accepted Version A hero.
6. Product bottles: reuse `assets/bottle-*.webp` (transparent). On dark surfaces add a soft radial glow
   behind them (`background: radial-gradient(...)`) so the clear packaging stays visible.
7. Build, then render **every page** headless and review. Fix. Repeat until each page matches its mockup.
8. `gh repo create Draoz4/covexall-site-dark --public --source=. --push`, then
   `vercel link --yes --project covexall-site-dark`, `vercel git connect --yes`, `vercel --prod --yes`.
   Verify every clean URL returns 200 on the production domain.
9. Report with the live URL, one line per page, and the list of placeholders still in the copy.

## Dark palette (from the client's master spec)

```
--bg-deep:    #050B14   page background
--bg-surface: #0B1622   cards / sections
--bg-raised:  #142433   hover / elevated
--border:     #1E3346   dividers
--cove-cyan:  #22D3EE   primary, CTAs, active states   (never #00A4C4 on dark — goes muddy)
--cove-light: #7FE3F5   secondary accents
--cove-glow:  #C4F4FF   halos / highlights
--text:       #EAF4F8   headings, body
--text-muted: #8CA3B3   captions, secondary
--accent:     #F5B841   prices, ratings, badges, sale — sparingly, never louder than cyan
```

Primary CTA: bright cyan / cyan gradient. Secondary CTA: dark navy with cyan border. Cove gets
`filter: drop-shadow(0 0 40px rgba(34,211,238,.35))` instead of a dark shadow. Photography stays natural
and warm — do not darken family/customer photos. No neon overload, no particles, no fog, no sci-fi clutter.
Premium and polished, not "AI cyberpunk".

## Tooling gotchas (Windows, this machine)

- Long bash heredocs with apostrophes can fail to parse in the Bash tool; write scripts with the Write tool
  and run them.
- Headless Edge screenshots: use a **fresh `--user-data-dir` per run** or you get cached CSS/JS. Add `?noanim`
  to the URL so reveal animations don't blur the capture (supported by `main.js`).
- `preview_start` uses the root `.claude/launch.json` (config name `covexall-site`, `npx serve`); add a
  `covexall-site-dark` entry pointing at the new folder.
- Image generation (`gemini_generate_image`) intermittently returns 503; retry later rather than
  substituting different art.

## Placeholders carried from the mockups (flag them, don't "fix" them silently)

Prices $3.99 / $7.99 / $11.99 / bundle $19.99 (`PRODUCTS` in `main.js`); phone (833) 268-3925 and
hello@covexall.com; review quotes and "Trusted by millions"; checkout/account/social URLs (`LINKS` in
`main.js`); newsletter and contact forms only store locally.
