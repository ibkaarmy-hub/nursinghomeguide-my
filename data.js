// Google Sheets CSV URLs
// FACILITIES_CSV_URL → main "Facilities" tab (one row per facility, ~50 columns)
// DETAILS_CSV_URL    → "Details" tab (long-format key/value extras: rooms, schedule, etc.)
//                      → publish that tab and replace DETAILS_TAB_GID below with its gid number
const FACILITIES_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ4_BgHIjnlgmITzjyUuGDpgpNzPL7MfjOY2069i0PtbVbXSxIAJk1tmBejwNo8aBBeLuRi62szF2sh/pub?output=csv";
const DETAILS_CSV_URL    = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ4_BgHIjnlgmITzjyUuGDpgpNzPL7MfjOY2069i0PtbVbXSxIAJk1tmBejwNo8aBBeLuRi62szF2sh/pub?gid=DETAILS_TAB_GID&single=true&output=csv";

async function loadFacilities() {
  const res = await fetch(FACILITIES_CSV_URL);
  return parseCSV(await res.text()).filter(r => r.title);
}

// Returns { [slug]: { [section]: [ {label, value}, ... ] } }
async function loadDetails() {
  try {
    if (DETAILS_CSV_URL.includes('DETAILS_TAB_GID')) return {};
    const res = await fetch(DETAILS_CSV_URL);
    if (!res.ok) return {};
    const rows = parseCSV(await res.text());
    const out = {};
    for (const r of rows) {
      const slug = (r.slug || '').trim();
      const section = (r.section || '').trim();
      const label = (r.label || '').trim();
      if (!slug || !section || !label) continue;
      if (!out[slug]) out[slug] = {};
      if (!out[slug][section]) out[slug][section] = [];
      out[slug][section].push({ label, value: (r.value || '').trim() });
    }
    return out;
  } catch (e) {
    console.warn('Details sheet not available:', e);
    return {};
  }
}

async function loadFacilityWithDetails(slug) {
  const [facilities, details] = await Promise.all([loadFacilities(), loadDetails()]);
  const facility = facilities.find(f => f.slug === slug);
  if (!facility) return null;
  facility._details = details[slug] || {};
  return facility;
}

function parseCSV(text) {
  const rows = [];
  let cur = '', q = false, fields = [];
  for (let i = 0; i < text.length; i++) {
    const c = text[i], n = text[i+1];
    if (c === '"') {
      if (q && n === '"') { cur += '"'; i++; }
      else q = !q;
    } else if (c === ',' && !q) { fields.push(cur); cur = ''; }
    else if ((c === '\n' || c === '\r') && !q) {
      if (c === '\r' && n === '\n') i++;
      fields.push(cur); rows.push(fields); fields = []; cur = '';
    } else cur += c;
  }
  if (cur || fields.length) { fields.push(cur); rows.push(fields); }
  if (!rows.length) return [];
  const headers = rows[0].map(h => h.trim());
  return rows.slice(1).filter(r => r.length > 1).map(r => {
    const o = {};
    headers.forEach((h, i) => o[h] = (r[i] || '').trim());
    return o;
  });
}
