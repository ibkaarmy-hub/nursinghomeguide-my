// Google Sheets CSV URLs
// FACILITIES_CSV_URL → main "Facilities" tab (one row per facility, ~50 columns)
// DETAILS_CSV_URL    → "Details" tab (long-format key/value extras)
const FACILITIES_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ4_BgHIjnlgmITzjyUuGDpgpNzPL7MfjOY2069i0PtbVbXSxIAJk1tmBejwNo8aBBeLuRi62szF2sh/pub?gid=292378871&single=true&output=csv";
const DETAILS_CSV_URL    = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ4_BgHIjnlgmITzjyUuGDpgpNzPL7MfjOY2069i0PtbVbXSxIAJk1tmBejwNo8aBBeLuRi62szF2sh/pub?gid=1104748854&single=true&output=csv";

// ─── Healthcare Groups / Chains ────────────────────────────────────────────────
// Each key is the org slug (used in org.html?slug=<key>)
// branches: array of facility slugs that belong to this group
const GROUPS = {
  'eha-eldercare': {
    slug: 'eha-eldercare',
    name: 'EHA ElderCare',
    tagline: 'Premium private eldercare across Johor — 5 branches from JB to Kluang',
    website: 'https://ehaeldercare.com.my',
    founded: 'c. 2015',
    ownership: 'Private (Malaysian)',
    state: 'Johor',
    description: 'EHA ElderCare is a premium private nursing home group operating five branches across Johor, from central Johor Bahru to Kluang. Each branch is a purpose-adapted residential facility offering 24/7 nursing care, dementia programmes, palliative support, and respite admissions. EHA positions itself at the higher end of the private market with facilities branded as "Eldercare Mansions". Monthly fees range from approximately RM 2,300 (Kluang) to RM 3,200+ (JB branches). All branches are JKM-licensed.',
    branches: [
      'eha-golfview-eldercare-mansion-johor-jaya-1-nursing-home-joh',
      'eha-lakeview-eldercare-mansion-permas-branch-1-nursing-home',
      'eha-parkview-eldercare-perling-1-nursing-home-johor-bahru',
      'eha-sunview-eldercare-kempas-1-nursing-home-johor-bahru',
      'eha-elder-care-home-kluang-licensed-and-certified-by-govern',
      'eha-parkview-eldercare-perling',
    ],
  },

  'golden-age-care-centre': {
    slug: 'golden-age-care-centre',
    name: 'Golden Age Care Centre (GACC)',
    tagline: 'Multi-branch private nursing home chain across southern Johor',
    website: 'https://gacc.com.my',
    state: 'Johor',
    description: 'Golden Age Care Centre (GACC) operates three branches across Johor — its headquarters in Muar (JKM 4-Star rated, 3.9★/8 reviews), a second branch in Tangkak, and a third in Batu Pahat. Care quality varies significantly by branch: the Muar HQ has a strong reputation while the Batu Pahat branch has attracted poor reviews (1.3★/3). GACC offers residential care, memory care, rehabilitation therapy, and palliative services across its network.',
    branches: [
      'golden-age-care-centre',
      'golden-age-care-centre-tangkak',
      'golden-age-care-centre-batu-pahat',
    ],
  },

  'master-nursing-care': {
    slug: 'master-nursing-care',
    name: 'Master Nursing Care',
    tagline: 'Multi-branch nursing care group in Johor Bahru',
    website: 'https://www.masternursingcare.com',
    state: 'Johor',
    description: 'Master Nursing Care operates multiple residential care branches in Johor Bahru. The group provides 24-hour nursing care, dementia support, and rehabilitation services. Their Daya branch (MCC@Daya) is the best-documented, with 5.0★ across 4 reviews and an active web presence at masternursingcare.com.',
    branches: [
      'master-care-centre',
      'master-nursing-care-centre-daya',
      'master-care-centre-taman-abad',
    ],
  },

  'rebina-sunrise': {
    slug: 'rebina-sunrise',
    name: 'Rebina Sunrise Group',
    tagline: 'Three eldercare entities under one roof in Johor Bahru',
    website: 'https://www.rebinasunrise.com',
    founded: '2003',
    ownership: 'Private (Family-owned)',
    state: 'Johor',
    description: 'The Rebina Sunrise group operates three distinct but related eldercare entities sharing the rebinasunrise.com domain: Rebina House Care Centre (residential, est. 2003, 4.8★/17 reviews), Sunrise Care Centre Sdn Bhd (registered entity No. 567396-U, adjacent premises at Jalan Keranji), and Rebina Home Care Centre (home care / day care arm). The group has a long-standing reputation in Johor Bahru and is one of the more established independent operators in the city.',
    branches: [
      'rebina-house-care-centre',
      'sunrise-care-centre-sdn-bhd',
      'rebina-home-care-centre-sdn-bhd',
    ],
  },

  'green-acres': {
    slug: 'green-acres',
    name: 'Green Acres Residential',
    tagline: 'Elderly and disabled care — two JB locations',
    website: 'https://www.greenacreshome.com',
    state: 'Johor',
    description: 'Green Acres Residential operates two facilities in Johor Bahru providing care for elderly and physically disabled residents. The group offers 24-hour nursing care, doctor visits, physiotherapy, and occupational therapy. Both locations are managed under Green Acres Residential Sdn Bhd.',
    branches: [
      'green-acres-elderly-care-centre-managed-by-green-acres-resid',
      'green-acres-home-care-centre-managed-by-green-acres-residenc',
    ],
  },

  'cozzi-confinement': {
    slug: 'cozzi-confinement',
    name: 'Cozzi Confinement Centers',
    tagline: 'Postpartum confinement care — 4 locations across Johor',
    website: 'https://cozziconfinement.com.my',
    state: 'Johor',
    description: 'Cozzi operates four postpartum confinement centres across Johor (Yong Peng, Muar, Sri Jaya – Batu Pahat, and Tanah Merah – Batu Pahat). Note: Cozzi centres are confinement facilities for new mothers, not eldercare nursing homes. They appear in this directory because they are JKM-registered residential care facilities in Johor.',
    branches: [
      'cozzi-confinement-center-yong-peng',
      'cozzi-confinement-center-muar',
      'cozzi-confinement-center-sri-jaya',
      'cozzi-confinement-center-tanah-merah',
    ],
  },

  'graceville': {
    slug: 'graceville',
    name: 'Graceville Care Centres',
    tagline: 'Chinese-operated nursing homes in Muar District',
    state: 'Johor',
    description: 'Graceville (美好疗养中心) operates two residential nursing homes in the Muar district of Johor — one in central Muar and a second branch in Sungai Mati. Both serve primarily the Chinese-speaking community and provide 24-hour residential nursing care.',
    branches: [
      'graceville-senior-care-centre',
      'graceville-care-centre-sungai-mati',
    ],
  },

  'slg-nursing-home': {
    slug: 'slg-nursing-home',
    name: 'SLG Nursing Home',
    tagline: 'Two nursing home locations in Muar',
    state: 'Johor',
    description: 'SLG Nursing Home operates two residential care facilities in Muar, Johor. Both locations provide nursing care for the elderly. Minimal online presence.',
    branches: [
      'slg-nursing-home-muar',
      'slg-nursing-home',
    ],
  },

  'wcc-care': {
    slug: 'wcc-care',
    name: 'WCC Care Centres',
    tagline: 'Wound care nursing and home care in Muar',
    state: 'Johor',
    description: 'WCC operates two care-related services in Muar: WCC WoundCare & Nursing Centre (specialising in wound management and nursing) and WCC Home Care Muar (home care services). Together they offer a continuum from institutional nursing to community-based home care.',
    branches: [
      'wcc-woundcare-nursing-centre',
      'wcc-home-care-muar',
    ],
  },

  'pusat-sri-kenangan': {
    slug: 'pusat-sri-kenangan',
    name: 'Pusat Sri Kenangan',
    tagline: 'Three-branch welfare home network in Johor',
    state: 'Johor',
    description: 'Pusat Sri Kenangan operates three residential welfare homes for the elderly in Johor — one in Bukit Pasir and two in Muar. These are welfare-oriented (non-profit character) facilities providing basic residential care.',
    branches: [
      'pusat-sri-kenangan',
      'pusat-sri-kenangan-2',
      'pusat-sri-kenangan-3',
    ],
  },

  'roseville-villa': {
    slug: 'roseville-villa',
    name: 'Roseville Villa',
    tagline: 'Residential home care — two locations in Pontian District',
    state: 'Johor',
    description: 'Roseville Villa Residential Home Care operates two locations in the Pontian District of Johor, providing residential nursing and personal care services.',
    branches: [
      'roseville-villa-residential-home-care',
      'roseville-villa-residential-home-care-2',
    ],
  },

  'impian-syimah': {
    slug: 'impian-syimah',
    name: 'Pusat Jagaan Impian Syimah',
    tagline: 'Two-branch Muslim care home in Johor Bahru',
    state: 'Johor',
    description: 'Pusat Jagaan Impian Syimah (SSM No. JM0635898-M) operates two residential branches in Johor Bahru — Jalan Kemuncak (the larger, established branch with 61 residents of whom 23 are bedridden) and Jalan Kemaman (a newer, smaller second branch under the same operator). The home caters primarily to Muslim elderly residents.',
    branches: [
      'pusat-jagaan-impian-syimah-jalan-kemuncak',
      'pusat-jagaan-impian-syimah-jalan-kemaman',
    ],
  },

  'nur-ehsan': {
    slug: 'nur-ehsan',
    name: 'Pusat Jagaan Warga Emas Nur Ehsan',
    tagline: 'Muslim welfare homes — Kempas Baru and Tangkak',
    state: 'Johor',
    description: 'Pusat Jagaan Warga Emas Nur Ehsan is a Muslim welfare organisation operating two elderly care homes in Johor — the main branch in Kempas Baru, Johor Bahru (56 beds) and a second branch in Tangkak. Both homes serve underprivileged Muslim elderly and are run on a charitable basis with subsidised fees.',
    branches: [
      'pusat-jagaan-warga-emas-nur-ehsan',
      'pusat-jagaan-warga-emas-nur-ehsan-tangkak',
    ],
  },

  'fcc-family-care-centre': {
    slug: 'fcc-family-care-centre',
    name: 'FCC Family Care Centre',
    tagline: "Malaysia's first integrated senior living wellness village",
    website: 'https://www.familycarecentre.co',
    state: 'Johor',
    description: "FCC Family Care Centre markets itself as Malaysia's first integrated senior living wellness village, combining nursing care, day care, rehabilitation, and community programmes. The group has two listings in our database for the Johor Bahru location, reflecting different entity registrations for the same facility complex.",
    branches: [
      'fcc-family-care-centre-johor-bahru',
      'fcc-family-care-centre',
    ],
  },
};

// ─── Reverse index: slug → group info ─────────────────────────────────────────
const GROUPS_BY_SLUG = {};
Object.values(GROUPS).forEach(g => {
  g.branches.forEach(bSlug => {
    GROUPS_BY_SLUG[bSlug] = g;
  });
});

// ─── Data fetchers ─────────────────────────────────────────────────────────────
async function loadFacilities() {
  const res = await fetch(FACILITIES_CSV_URL);
  return parseCSV(await res.text()).filter(r => r.title);
}

// Returns { [slug]: { [section]: [ {label, value}, ... ] } }
async function loadDetails() {
  try {
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

// ─── CSV parser ────────────────────────────────────────────────────────────────
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
