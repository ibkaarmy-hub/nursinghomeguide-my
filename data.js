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
    tagline: 'Premium private eldercare — 8 branches across Johor and KL',
    website: 'https://ehaeldercare.com.my',
    founded: 'c. 2015',
    ownership: 'Private (Malaysian)',
    state: 'Johor, Kuala Lumpur',
    description: 'EHA ElderCare is a premium private nursing home group operating eight branches across Johor and Kuala Lumpur. Johor branches (5) span central Johor Bahru to Kluang; KL branches (3) include Grandview Titiwangsa, Grandview Kepong, and Bayview Cheras/Kajang. Each branch offers 24/7 nursing care, dementia programmes, palliative support, and respite admissions. EHA positions itself at the higher end of the private market. Monthly fees range from approximately RM 2,300 (Kluang) to RM 3,500+ (KL branches). All branches are JKM-licensed.',
    branches: [
      'eha-golfview-eldercare-mansion-johor-jaya-1-nursing-home-joh',
      'eha-lakeview-eldercare-mansion-permas-branch-1-nursing-home',
      'eha-parkview-eldercare-perling-1-nursing-home-johor-bahru',
      'eha-sunview-eldercare-kempas-1-nursing-home-johor-bahru',
      'eha-elder-care-home-kluang-licensed-and-certified-by-govern',
      'eha-parkview-eldercare-perling',
      'eha-grandview-titiwangsa-kl-elderly-care',
      'eha-grandview-eldercare-甲洞温馨疗养别墅-1-nursi',
      'eha-bayview-eldercare-cheras-sungai-long',
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

  // ── KL / Selangor groups ─────────────────────────────────────────────────
  'haywood-senior-living': {
    slug: 'haywood-senior-living',
    name: 'Haywood Senior Living',
    tagline: 'Premium senior living — Bangsar KL and Medini Iskandar',
    website: 'https://haywoodliving.co',
    state: 'Kuala Lumpur, Johor',
    description: 'Haywood Senior Living operates two premium eldercare residences — one in Bangsar, Kuala Lumpur (4.9★/45 reviews) and one in Medini Iskandar, Johor Bahru. Both are positioned as boutique, hotel-style senior living environments with 24/7 nursing, concierge services, and activity programmes.',
    branches: [
      'haywood-senior-living-medini-johor-bahru',
      'haywood-senior-living-bangsar',
    ],
  },

  'noble-care': {
    slug: 'noble-care',
    name: 'Noble Care',
    tagline: 'Malaysia\'s largest private nursing home chain — 16+ locations nationwide',
    website: 'http://www.mynoblecare.com',
    state: 'Johor, Kuala Lumpur, Selangor',
    description: 'Noble Care is one of Malaysia\'s largest private nursing home operators, with facilities across Johor, KL, and Selangor. The group operates under a standardised care model offering 24-hour nursing care, dementia programmes, and rehabilitation. Quality varies by location — individual branch ratings range from 2.8★ to 5.0★. Families should review each branch independently.',
    branches: [
      'noble-care',
      'noble-care-nursing-home-old-folks-home-r',
      'noble-care-retirement-resort',
      'noble-care-retirement-home',
      'noble-care-malaysia-ampang',
      'noble-care-nursing-home-klang-selangor',
      'noble-care-nursing-home-in-jalan-ipoh-ku',
      'noble-care-retirement-home-jalan-usj-18',
      'noble-care-nursing-home',
      'noble-care-malaysia',
      'noble-care-nursing-home-nursing-home-sub',
    ],
  },

  'mintygreen': {
    slug: 'mintygreen',
    name: 'Mintygreen Care Centres',
    tagline: 'Multi-branch eldercare across Klang Valley — 5 locations',
    website: 'https://mintygreen.com.my',
    state: 'Kuala Lumpur, Selangor',
    description: 'Mintygreen operates five eldercare branches across the Klang Valley: Cheras (home care suites), Sungai Long/Kajang, Kepong/PJ Batu, USJ21 Subang Jaya, and a care suites model in Cheras KL. The group offers residential nursing, memory care, and rehabilitation services. Well-reviewed across branches (4.1–4.8★).',
    branches: [
      'mintygreen-senior-care-center-cherassung',
      'mintygreen-nursing-homesungai-long-kajan',
      'mintygreen-nursing-retirement-home-kepon',
      'mintygreen-care-suites-home-care-nursing',
      'mintygreen-care-centre-usj21-subang-jaya',
    ],
  },

  'genesis-life-care': {
    slug: 'genesis-life-care',
    name: 'Genesis Life Care Centre',
    tagline: 'Private nursing home group — Johor, Puchong, Kajang, PJ, Klang',
    website: 'https://genesiscare.com.my',
    state: 'Johor, Selangor',
    description: 'Genesis Life Care Centre is a growing private nursing home group with five branches: one in Johor Bahru and four across Selangor (Puchong, Kajang, Petaling Jaya, Klang). The group is consistently well-rated (4.3–5.0★) across locations and offers 24/7 nursing care, dementia programmes, stroke rehabilitation, and palliative support.',
    branches: [
      'genesis-life-care-centre-jb',
      'genesis-life-care-centre-puchong',
      'genesis-life-care-centre-kajang',
      'genesis-life-care-centre-klang',
      'genesis-life-care-centre-pj',
    ],
  },

  'oasis-nursing-home': {
    slug: 'oasis-nursing-home',
    name: 'Oasis Nursing Home (安康之家)',
    tagline: 'Chinese-operated nursing home group in Shah Alam and Klang',
    state: 'Selangor',
    description: 'Oasis Nursing Home (安康之家疗养院) operates three branches in Selangor: two in Shah Alam (Setia Alam and the main Shah Alam branch) and one in Klang (Kapar). The group is Chinese-operated and caters primarily to Chinese-speaking residents. All branches are consistently well-reviewed (5.0★).',
    branches: [
      'oasis-nursing-home-setia-alam',
      'oasis-nursing-home-shah-alam-安康之家疗养院',
      'oasis-nursing-home-klang-安康之家巴生疗养院',
    ],
  },

  'my-aged-care': {
    slug: 'my-aged-care',
    name: 'My Aged Care Nursing Home',
    tagline: 'Three locations in Petaling Jaya — PJ Old Town, My Manor, Jalan Assam',
    state: 'Selangor',
    description: 'My Aged Care operates three nursing home facilities in Petaling Jaya, Selangor. The PJ Old Town branch (4.8★/92 reviews) and My Manor (4.5★/142 reviews) are the most established, with strong review bases. A third branch on Jalan Assam PJ adds further capacity. The group focuses on eldercare with nursing, dementia, and rehabilitation services.',
    branches: [
      'my-aged-care-nursing-home-in-pj-my-manor',
      'my-aged-care-nursing-home-in-pj-old-town',
      'my-aged-care-nursing-home-in-petaling-ja',
    ],
  },

  'mona-elder-care': {
    slug: 'mona-elder-care',
    name: 'Mona Elder Care',
    tagline: 'Four-branch eldercare network across Kuala Lumpur',
    state: 'Kuala Lumpur',
    description: 'Mona Elder Care operates four nursing home branches in Kuala Lumpur: Taman Bunga Raya, Taman P. Ramlee (Setapak), Jalan Sri Kemuning (Lembah Jaya), and Pandan Perdana. All branches serve the Chinese-speaking community and are rated 4.5–5.0★.',
    branches: [
      'mona-elder-care-nursing-home-in-taman-bu',
      'mona-elder-care-nursing-home-in-taman-p-',
      'mona-elder-care-nursing-home-in-jalan-sr',
      'mona-elder-care-nursing-home-in-pandan-p',
    ],
  },

  'golden-years-senior-residence': {
    slug: 'golden-years-senior-residence',
    name: 'Golden Years Senior Residence',
    tagline: 'Premium senior residences in Puchong and Shah Alam',
    state: 'Selangor',
    description: 'Golden Years Senior Residence operates two premium senior living facilities in Selangor: Kinrara Puchong (4.7★/14 reviews) and Kota Kemuning Shah Alam (4.7★/24 reviews). Both offer residential eldercare with nursing, rehabilitation, and activity programmes.',
    branches: [
      'golden-years-senior-residence-kinrara-pu',
      'golden-years-senior-residence-kota-kemun',
    ],
  },

  'happy-family-nursing-home': {
    slug: 'happy-family-nursing-home',
    name: 'Happy Family Nursing Home',
    tagline: 'Chinese-operated nursing home chain — 5 locations in KL',
    state: 'Kuala Lumpur',
    description: 'Happy Family Nursing Home (快乐家庭护理中心) operates five branches in Kuala Lumpur: Taman Kepong, Kepong, Jalan Ipoh, Cheras, and Taman Desa Jaya. The group is Chinese-community operated and provides 24-hour nursing care. Rating quality varies by branch (2.8★–5.0★); families should review each branch individually.',
    branches: [
      'happy-family-nursing-home-kepong',
      'happy-family-nursing-home-taman-kepong-p',
      'happy-family-nursing-home-cheras-pusat-j',
      'happy-family-nursing-home-taman-desa-jay',
      'happy-family-nursing-home-jalan-ipoh-pus',
    ],
  },

  'woodrose-senior-residences': {
    slug: 'woodrose-senior-residences',
    name: 'Woodrose Senior Residences',
    tagline: 'Syariah-compliant senior residences — 4 locations in Shah Alam',
    state: 'Selangor',
    description: 'Woodrose Senior Residences operates four Syariah-compliant senior living facilities in Shah Alam, Selangor, across Seksyen 11 (female), Seksyen 11 (male), Seksyen 13 (female, Syariah), and an additional site. The group caters to Muslim elderly with gender-segregated and Syariah-compliant care environments.',
    branches: [
      'woodrose-senior-residences',
      'woodrose-senior-residences-1-seksyen-11-',
      'woodrose-senior-residences-2-seksyen-11-',
      'woodrose-senior-residences-3-seksyen-13-',
    ],
  },

  'attia-global-care': {
    slug: 'attia-global-care',
    name: 'Attia Global Care',
    tagline: 'Muslim nursing home group — Klang and Subang Jaya',
    state: 'Selangor',
    description: 'Attia Global Care operates two facilities in Selangor: Klang (4.7★/77 reviews) and Subang Jaya (4.5★/24 reviews). Both cater to Muslim elderly with Halal meals and Islamic activities. The Klang branch is the larger and more established of the two.',
    branches: [
      'attia-global-care-klang',
      'attia-global-care-centre-subang-jaya',
    ],
  },

  'harvestars-care': {
    slug: 'harvestars-care',
    name: 'Harvestars Care Centre',
    tagline: 'Two-branch eldercare in Puchong and Klang',
    state: 'Selangor',
    description: 'Harvestars Care Centre operates two facilities in Selangor — D\'Island Puchong (4.9★/8 reviews) and H-Residence Klang (4.8★/17 reviews). Both offer residential nursing care and rehabilitation services.',
    branches: [
      'harvestars-care-centre-puchong-disland',
      'harvestars-care-centre-klang-h-residence',
    ],
  },

  'amazing-grace-senior-home': {
    slug: 'amazing-grace-senior-home',
    name: 'Amazing Grace Senior Home',
    tagline: 'Well-reviewed senior care — Subang Jaya and Petaling Jaya',
    state: 'Selangor',
    description: 'Amazing Grace operates two highly-rated senior care facilities in Selangor: Amazing Grace Senior Home in Subang Jaya (5.0★/156 reviews) and Amazing Grace Retirement Home in Petaling Jaya (4.9★/140 reviews). Both are among the most-reviewed nursing homes in the Klang Valley, suggesting genuine family engagement.',
    branches: [
      'amazing-grace-senior-home',
      'amazing-grace-retirement-home',
    ],
  },

  'pearl-care-elderly': {
    slug: 'pearl-care-elderly',
    name: 'Pearl Care Elderly',
    tagline: 'Two nursing home facilities in Petaling Jaya',
    state: 'Selangor',
    description: 'Pearl Care Elderly operates two nursing home facilities in Petaling Jaya, Selangor: Pearl Care Elderly Center Sdn. Bhd. (4.9★/16 reviews) and Pearl Care Elderly Home (4.6★/62 reviews). Both serve the PJ community with 24-hour nursing and personal care.',
    branches: [
      'pearl-care-elderly-center',
      'pearl-care-elderly-home',
    ],
  },

  'elderlove-living': {
    slug: 'elderlove-living',
    name: 'Elderlove Living Care Centre',
    tagline: 'Two-branch eldercare in Puchong and Sungai Long',
    state: 'Selangor',
    description: 'Elderlove Living Care Centre operates two branches in Selangor — Puchong D\'Island (5.0★/15 reviews) and Sungai Long/Kajang (4.1★/31 reviews). Both offer residential nursing care, dementia support, and rehabilitation.',
    branches: [
      'elderlove-living-care-centre-puchong',
      'elderlove-living-care-centre-sglong',
    ],
  },

  'green-acres': {
    slug: 'green-acres',
    name: 'Green Acres Residence Care',
    tagline: 'Multi-branch eldercare in Johor Bahru — residential and home care arms',
    website: 'https://www.greenacreshome.com',
    ownership: 'Private (Green Acres Residence Care (Group) Sdn. Bhd.)',
    state: 'Johor',
    description: 'Green Acres Residence Care (Group) Sdn. Bhd. operates multiple eldercare entities in Johor Bahru under the Green Acres brand: a flagship Elderly Care Centre (4.8★/4 reviews) offering residential nursing care, a Home Care Centre arm, and a separate Home Care service in Kim Teng Park. The group runs from greenacreshome.com and serves the southern Johor market with both residential and home-based care options.',
    branches: [
      'green-acres-elderly-care-centre-managed-by-green-acres-resid',
      'green-acres-home-care-centre-managed-by-green-acres-residenc',
      'green-acres-home-care',
    ],
  },

  'genesis-life-care': {
    slug: 'genesis-life-care',
    name: 'Genesis Life Care',
    tagline: 'Multi-branch nursing home group across Klang Valley and Johor',
    state: 'Selangor, Kuala Lumpur, Johor',
    description: 'Genesis Life Care operates five branches under one group — flagship in Petaling Jaya (Taman Petaling Utama, est. 2020, 50+ beds), plus Kajang (founding branch est. 2018, Amverton Business Centre, 120+ beds), Klang (near TAR Hospital), Puchong (Taman Perindustrian Puchong, 120+ beds), and Johor Bahru. The group is JKM-licensed and AgeCope-certified. Pricing starts from RM 2,500/month. Notable for psychologist-led memory care programmes, weekly doctor visits, and on-site rehabilitation suites.',
    branches: [
      'genesis-life-care-centre-pj',
      'genesis-life-care-centre-kajang',
      'genesis-life-care-centre-klang',
      'genesis-life-care-centre-puchong',
      'genesis-life-care-centre-jb',
    ],
  },

  'my-aged-care': {
    slug: 'my-aged-care',
    name: 'My Aged Care',
    tagline: 'Multi-branch nursing home network across Petaling Jaya',
    state: 'Selangor',
    description: 'My Aged Care Sdn. Bhd. (founded 2008) operates a network of nursing homes concentrated in Petaling Jaya, with the flagship My Manor branch in PJS 7 occupying a 10,000 sq ft low-density property. Other branches include PJ Old Town (Jalan Othman) and Jalan Assunta (adjacent to Assunta Hospital — clinically the strongest location for high-acuity transfers). The group cares for bedridden, palliative, post-stroke, and dementia residents with 24-hour hourly rounds. Pricing is in the RM 3,001–5,000/month range.',
    branches: [
      'my-aged-care-sdn-bhd',
      'my-aged-care-nursing-home-in-pj-my-manor',
      'my-aged-care-nursing-home-in-pj-old-town',
      'my-aged-care-nursing-home-in-petaling-jaya-jalan-assunta',
    ],
  },

  'mintygreen': {
    slug: 'mintygreen',
    name: 'Mintygreen Nursing Homes',
    tagline: '7-branch chain across Klang Valley with TCM integration',
    state: 'Selangor, Kuala Lumpur',
    description: 'Mintygreen (碧绿疗养院) is a private nursing home chain founded in 2017, operating multiple branches across the Klang Valley — Sungai Long & Kajang HQ, Cheras (Sungai Long), Subang Jaya USJ 21, Kepong/PJ Bandar Sri Damansara (Sphere Damansara), plus a home care/care suites arm in Cheras KL. The group is AgeCope-certified and integrates Traditional Chinese Medicine (acupuncture, Tui Na) alongside conventional nursing care, with bi-weekly GP visits and full nursing capabilities including NG, catheter, and PEG. Long-term care from RM 4,000/month, day care RM 220/day.',
    branches: [
      'mintygreen-nursing-homesungai-long-kajang-eldercare-center-加影碧绿疗养院',
      'mintygreen-senior-care-center-cherassungai-long-蕉赖碧绿疗养院',
      'mintygreen-nursing-retirement-home-kepong-and-pj-bandar-sri-damansara',
      'mintygreen-care-suites-home-care-nursing-cheras-kl',
      'mintygreen-care-centre-usj21-subang-jaya',
      'mintygreen-nursing-home-eldercare-center',
    ],
  },

  'attia-care': {
    slug: 'attia-care',
    name: 'Attia Nursing Care',
    tagline: 'Multi-branch rehabilitation-oriented nursing care chain',
    state: 'Selangor',
    description: 'Attia Nursing Care (established 2011) operates multiple branches across Selangor with a rehabilitation focus — stroke recovery, coma care, post-amputation, and orthopaedic recovery. Branches include Klang (Jalan Raja Bot), Subang Jaya (SS19), and the original Attia Nursing Care Centre. Each branch has on-site physiotherapy, occupational therapy, and speech therapy capabilities, plus weekly doctor visits. The group also offers tracheostomy care, NGT/PEG feeding, and acupuncture.',
    branches: [
      'attia-nursing-care-centre',
      'attia-global-care-klang',
      'attia-global-care-centre-subang-jaya',
    ],
  },

  'woodrose-senior-residences': {
    slug: 'woodrose-senior-residences',
    name: 'Woodrose Senior Residences',
    tagline: 'Shariah-compliant eldercare in Shah Alam — multi-residence campus',
    state: 'Selangor',
    description: 'Woodrose Senior Residences operates a multi-building Shariah-compliant eldercare campus in Shah Alam Seksyen 11 and Seksyen 13. Residence 1 (Jalan Silat, female) and Residence 3 (Seksyen 13, female) are female-only wings; Residence 2 (Seksyen 11, male) is the male wing. All residences operate under in-house Ustaz-governed SOPs and offer dementia care, palliative care, rehabilitation, respite, and day care. Residence 1 includes a swimming pool. The campus is among the most established Shariah-compliant eldercare offerings in the Klang Valley.',
    branches: [
      'woodrose-senior-residences',
      'woodrose-senior-residences-1-seksyen-11-female-syariah-complaint',
      'woodrose-senior-residences-2-seksyen-11-male-syariah-compliant',
      'woodrose-senior-residences-3-seksyen-13-female-syariah-compliant',
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
  return parseCSV(await res.text()).filter(r => r.title && r.status !== 'unverified' && r.status !== 'removed');
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
