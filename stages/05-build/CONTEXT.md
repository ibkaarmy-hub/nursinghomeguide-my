# Stage 05 — Build & Deploy

## Status: ⬜ Deferred

Originally planned as Next.js + Supabase + Vercel. Currently the project ships as static HTML on GitHub Pages reading from a published Google Sheets CSV — that's working well enough that a heavier stack isn't justified yet.

## When to revisit

Migrate when at least one of these becomes true:
- Sheet read latency or quota becomes a bottleneck (Google's published CSV is rate-limited)
- We need server-side rendering for SEO (currently relying on client-side fetch — Google does index it, but slow)
- Photos must be mirrored off `lh3.googleusercontent.com` to durable storage
- We add user accounts, lead capture, or any write path
- We point `nursinghomeguide.my` at this and want better caching/edge behavior than GitHub Pages provides

## Likely target stack when we migrate

- **Next.js (App Router)** with static generation per facility page; ISR on revalidate
- **Supabase** for the structured table (replace the sheet) plus Storage for photos
- **Vercel** for hosting and image optimisation
- Keep the Google Sheet as a non-technical edit interface; pipe writes into Supabase via a small sync job

## Pre-migration checklist (when the time comes)

- [ ] Lock the column schema — current shape is in CLAUDE.md
- [ ] Mirror photos to Supabase Storage; rewrite `photos` column to point at durable URLs
- [ ] Decide on slug stability (current slug column is fine)
- [ ] Set up a sheet → Supabase sync (Cloud Function or scheduled GitHub Action)
- [ ] Move secrets out of any local files

## Don't do prematurely

Building the Next.js app now means duplicating data flow that already works. Stay on the static stack until a real constraint forces a move.
