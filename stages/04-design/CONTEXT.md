# Stage 04 — Design

## Status: ✅ All page templates shipped

## What's live

| Page | Description |
|------|-------------|
| `index.html` | State picker landing: hero, 3-state grid (Johor/KL/Selangor), why section, how it works |
| `johor.html` | State listing: search, filter bar (area pills), sort select, list/map toggle, Leaflet map |
| `kuala-lumpur.html` | Same template as johor, KL state filter |
| `selangor.html` | Same template as johor, Selangor state filter |
| `facility.html` | 4-tab profile: Overview / Pricing / Care & Medical / Amenities + Map; photo carousel, sticky sidebar, mobile CTA bar |
| `org.html` | Organisation/chain profile: purple hero, branch grid with "Branch" tags |
| `style.css` | All shared styles — design tokens, card components, filter bar, map, skeleton loaders |
| `photo-manager.html` | Admin-only photo curation tool |

## Key design decisions

- **Logo-only header** — no nav links (user decision, cleaner on mobile)
- **Photo cards** with price badge overlay (green, bottom-left) and group tag (purple, top-left)
- **Map view** — Leaflet + OpenStreetMap, blue dots = independent, purple dots = chain members
- **Sticky filter bar** — IntersectionObserver shadow on scroll
- **Mobile sticky CTA bar** — fixed Call + WhatsApp at bottom of facility profiles
- **Skeleton loaders** — shimmer animation while CSV loads
- **Area normalisation** — 40+ raw Johor strings → 10 clean canonical areas (client-side, AREA_NORMALIZE map)
- **Status filter** — `loadFacilities()` silently drops `status=unverified|removed` rows

## Pending / future design work

- **sitemap.xml + robots.txt** — not yet created (technical, not design, but needed)
- **Schema.org structured data** — LocalBusiness, ItemList, BreadcrumbList on all pages
- **Guide page template** — new HTML template for content pages (cost guide, how-to-choose, etc.)
- **BM language toggle** — once BM content exists
- **Clean URL migration** — `facility.html?slug=X` → `/facilities/slug/index.html` (requires build step)
- **Photo CDN migration** — Google CDN URLs to durable storage (Supabase/Vercel Blob)

## Design tokens (style.css)

```css
--primary: #2563eb;
--text: #0f172a;
--text-muted: #64748b;
--border: #e2e8f0;
--bg: #f8fafc;
```

## Mobile breakpoints

- `≤ 640px` — nav collapses, filter bar stacks, single-column grid
- `≤ 680px` — facility card grid → single column
- `≤ 780px` — facility profile sidebar stacks below main content
- `≤ 960px` — facility profile sidebar stacks (wider breakpoint for full sidebar)
