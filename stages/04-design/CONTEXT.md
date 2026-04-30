# Stage 04 — Design

## Status: 🟡 Facility profile shipped; rest pending

## What's live

- **`facility.html`** — 4-tab layout (Overview / Pricing / Care & Medical / Location), photo gallery (up to 12 thumbs, click for full-size), sticky contact sidebar, hero with darkened background image
- **`style.css`** — design tokens, profile components, gallery
- **`photo-manager.html`** — admin tool

## What's pending

- **`index.html`** — currently bare. Needs: hero, search-by-state, featured listings (with hero photos), trust signals, BM toggle
- **`facilities.html`** (or state hub template) — paginated/filtered list view; right now there's a stub link in the nav but no real page
- **Mobile QA** — facility profile is responsive but hasn't been audited at 375px in detail
- **Language toggle UI** — need EN ↔ BM switcher in the nav once content exists
- **Design tokens consolidation** — colours/typography are inline in `style.css`; should extract to CSS custom properties at the top

## Decisions made

- Mobile-first
- Pricing visually prominent — never below the fold on facility pages
- Photo gallery is 4-col desktop, 2-col mobile; 12-image cap, lightbox via plain `target="_blank"`
- Hero uses gradient overlay on photo so white text stays readable
- Sticky sidebar for CTA buttons (call, WhatsApp, Maps, website)

## Audit before merging design changes

- [ ] Pricing visible above the fold on facility page
- [ ] No layout break at 375px width
- [ ] BM placeholder text doesn't break layout (BM strings tend to be longer)
- [ ] Photo gallery degrades gracefully when `photos` cell is empty
