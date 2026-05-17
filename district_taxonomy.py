"""District taxonomy for area page generation.

Maps the raw `area` column (often neighborhood-level: "SS 19", "Bandar Sungai
Long") to searchable district names ("Petaling Jaya", "Kajang") that match
how Malaysian families actually search.

Usage:
    from district_taxonomy import area_to_district
    slug, label = area_to_district("Selangor", "Bandar Sungai Long")
    # → ("kajang", "Kajang")

Run directly for a coverage report:
    python district_taxonomy.py
"""

# Map: (state, area_normalized) → (district_slug, district_label)
# area_normalized is lowercased, stripped, with common variations folded.
# Unmapped areas fall through to None (no district page).

# --- KUALA LUMPUR ---
_KL = {
    # Bangsar / Bukit Persekutuan / Bukit Bintang
    "bangsar": "bangsar",
    "bukit persekutuan": "bangsar",
    "klcc": "bukit-bintang",
    "bukit bintang": "bukit-bintang",
    # Kepong
    "kepong baru": "kepong",
    "taman kepong": "kepong",
    "taman kok lian": "kepong",
    "kepong": "kepong",
    "taman ehsan": "kepong",
    # Cheras
    "cheras": "cheras",
    "kampung cheras baru": "cheras",
    "taman connaught": "cheras",
    "taman cheras awana": "cheras",
    "bandar tun razak": "cheras",
    "taman bukit segar": "cheras",
    "bandar damai perdana": "cheras",
    "taman muda": "cheras",
    "taman ayer panas": "cheras",
    "taman taynton view": "cheras",
    "taman tayton view": "cheras",
    "taman bukit hijau": "cheras",
    "taman shanghai": "cheras",
    "taman p. ramlee": "cheras",
    # Setapak / Wangsa Maju
    "setapak": "setapak",
    "setapak indah": "setapak",
    "taman setapak indah": "setapak",
    "taman p. ramlee setapak": "setapak",
    "taman bunga raya": "setapak",
    "taman mastiara": "setapak",
    "taman sri bahtera": "setapak",
    "taman kaya": "setapak",
    # Sentul / Jalan Ipoh
    "sentul": "sentul",
    "jalan ipoh": "sentul",
    "taman city": "sentul",
    # Old Klang Road / OUG
    "taman oug": "old-klang-road",
    "happy garden": "old-klang-road",
    "taman lucky": "old-klang-road",
    "taman salak selatan": "old-klang-road",
    "desa petaling": "old-klang-road",
    "taman desa": "old-klang-road",
    "taman desa jaya": "old-klang-road",
    "desa jaya": "old-klang-road",
    "taman bukit": "old-klang-road",
    # Titiwangsa
    "titiwangsa": "titiwangsa",
    # Pudu
    "pudu": "pudu",
    "taman pertama": "pudu",
    # Mont Kiara / Segambut
    "phoenix business park": "segambut",
    # Damansara (KL side)
    "taman tun dr ismail": "damansara",
    "ttdi": "damansara",
}

# --- SELANGOR ---
_SELANGOR = {
    # Petaling Jaya — covers SS-numbers, PJS, Seksyens 1-22, Bukit Gasing,
    # Kampung Tunku, Sea Park, PJ Old Town
    "petaling jaya": "petaling-jaya",
    "pj old town": "petaling-jaya",
    "bukit gasing": "petaling-jaya",
    "kampung tunku": "petaling-jaya",
    "sea park": "petaling-jaya",
    "taman aman": "petaling-jaya",
    "sungai way": "petaling-jaya",
    "sungai way free trade industrial zone": "petaling-jaya",
    "kampung sungai kayu ara": "petaling-jaya",
    "damansara perdana": "petaling-jaya",
    "kota damansara": "petaling-jaya",
    "prima damansara": "petaling-jaya",
    "taman tan yew lai": "petaling-jaya",
    "taman petaling utama": "petaling-jaya",
    "taman bukit kuchai": "petaling-jaya",
    # PJ Seksyens (1-22 unambiguously PJ when paired with PJ-area neighbors)
    "seksyen 1": "petaling-jaya",
    "seksyen 6": "petaling-jaya",
    "seksyen 7": "petaling-jaya",
    "seksyen 8 petaling jaya": "petaling-jaya",
    "seksyen 11": "petaling-jaya",
    "section 12": "petaling-jaya",
    "seksyen 12": "petaling-jaya",
    "seksyen 12 petaling jaya": "petaling-jaya",
    "seksyen 13": "petaling-jaya",
    "seksyen 14": "petaling-jaya",
    "section 14": "petaling-jaya",
    "seksyen 17": "petaling-jaya",
    "section 17": "petaling-jaya",
    "seksyen 18": "petaling-jaya",
    # PJ SS-codes
    "ss 1": "petaling-jaya",
    "ss 2": "petaling-jaya",
    "ss 3": "petaling-jaya",
    "ss 14": "petaling-jaya",
    "ss 19": "petaling-jaya",
    "ss 1, kampung tunku, petaling jaya": "petaling-jaya",
    "ss 2, petaling jaya": "petaling-jaya",
    "pjs 3": "petaling-jaya",
    "pjs 4": "petaling-jaya",
    "pjs 6": "petaling-jaya",
    "pjs 7": "petaling-jaya",
    # Subang Jaya — USJ codes + Bandar Sunway + Sunway City + Putra Heights
    "subang jaya": "subang-jaya",
    "uep subang jaya": "subang-jaya",
    "taman seri subang": "subang-jaya",
    "persiaran subang 1": "subang-jaya",
    "usj 9": "subang-jaya",
    "usj 18": "subang-jaya",
    "usj sentral": "subang-jaya",
    "bandar sunway": "subang-jaya",
    "sunway city": "subang-jaya",
    "putra heights": "subang-jaya",
    # Shah Alam (proper) — Seksyen U-prefix
    "seksyen u11": "shah-alam",
    # Setia Alam — its own district (users search the brand-area name)
    "setia alam": "setia-alam",
    # Kota Kemuning — its own district
    "kota kemuning": "kota-kemuning",
    "mutiara bukit kemuning": "kota-kemuning",
    # Klang — Bandar Botanik + Taman Klang Jaya + Kawasan industrial sectors
    "taman klang jaya": "klang",
    "bandar botanik": "klang",
    "taman sri andalas": "klang",
    "taman chi liung": "klang",
    "taman sungai kapar indah": "klang",
    "taman teluk pulai": "klang",
    "bandar country homes": "klang",
    "kawasan 6": "klang",
    "kawasan 16": "klang",
    "kawasan 17": "klang",
    "kawasan 18": "klang",
    "kawasan perindustrian ria": "klang",
    "kawasan perusahaan pkns": "klang",
    "telok panglima garang": "klang",
    "amverton business centre": "klang",
    "tadisma business park": "klang",
    # Kajang — Bandar Sungai Long + Semenyih + Sungai Sekamat etc.
    "kajang": "kajang",
    "bandar kajang": "kajang",
    "bandar sungai long": "kajang",
    "kampung sungai sekamat": "kajang",
    "country heights": "kajang",
    "taman kajang jaya": "kajang",
    "bandar teknologi kajang": "kajang",
    "kampung baru semenyih": "kajang",
    "taman tasik semenyih": "kajang",
    "kampung sesapan kelubi": "kajang",
    "kampung baru balakong": "kajang",
    "kampung pulau meranti": "kajang",
    "kampung jln kebun": "kajang",
    "saujana akasia": "kajang",
    "lestari perdana": "kajang",
    # Puchong
    "bandar puchong jaya": "puchong",
    "pusat bandar puchong": "puchong",
    "taman puchong prima": "puchong",
    "taman puchong utama": "puchong",
    "taman perindustrian puchong": "puchong",
    "taman putra perdana": "puchong",
    "taman putra prima": "puchong",
    "bandar kinrara": "puchong",
    "taman putra permai": "puchong",
    "taman bukit kuchai puchong": "puchong",
    # Ampang
    "ampang jaya": "ampang",
    "kampung baru ampang": "ampang",
    "taman ampang utama": "ampang",
    "kuala ampang": "ampang",
    "pandan perdana": "ampang",
    "kampung datuk keramat": "ampang",
    "kampung lembah jaya selatan": "ampang",
    "taman kemacahaya": "ampang",
    # Selayang
    "selayang baru": "selayang",
    "taman selayang jaya": "selayang",
    "taman sri selayang": "selayang",
    "taman selayang": "selayang",
    "gombak": "selayang",
    # Sungai Buloh
    "kampung baru sungai buloh": "sungai-buloh",
    # Rawang
    "saujana rawang": "rawang",
    "bukit sentosa": "rawang",
    # Seri Kembangan / Serdang
    "kampung baru seri kembangan": "seri-kembangan",
    "taman serdang raya": "seri-kembangan",
    "taman serdang jaya": "seri-kembangan",
    "pusat perdagangan seri kembangan": "seri-kembangan",
    "taman sri serdang": "seri-kembangan",
    # Cheras Selangor (mostly groups with KL Cheras for searches)
    "cheras perdana": "cheras",
    # Hulu Langat (catch-all rural east)
    "hulu langat": "hulu-langat",
    "sepang": "sepang",
    "bandar mahkota banting": "banting",
    "bandar nusa rhu": "kuala-selangor",
}

# --- JOHOR ---
_JOHOR = {
    # Johor Bahru district — JB proper + all suburb tamans + Skudai + Tampoi
    # + Senai + Gelang Patah + Kempas + Iskandar Puteri (own district below)
    "johor bahru": "johor-bahru",
    "kempas baru, johor bahru": "johor-bahru",
    "kempas, johor bahru": "johor-bahru",
    "kawasan kempas lurah": "johor-bahru",
    "kampung kempas bahru": "johor-bahru",
    "tampoi, johor bahru": "johor-bahru",
    "taman kebun teh, johor bahru": "johor-bahru",
    "taman perling, johor bahru": "johor-bahru",
    "taman damansara aliff": "johor-bahru",
    "taman puteri wangsa": "johor-bahru",
    "taman sri tebrau": "johor-bahru",
    "taman sentosa": "johor-bahru",
    "taman century": "johor-bahru",
    "taman johor jaya": "johor-bahru",
    "kim teng park": "johor-bahru",
    "stulang darat": "johor-bahru",
    "bandar baru uda": "johor-bahru",
    "kampung ungku mohsin": "johor-bahru",
    "taman bakariah": "johor-bahru",
    "bandar selesa jaya": "johor-bahru",
    "taman seri orkid": "johor-bahru",
    "taman delima": "johor-bahru",
    "taman cempaka": "johor-bahru",
    "ulu tiram": "johor-bahru",
    "taman arosa": "johor-bahru",
    "skudai, johor bahru": "johor-bahru",
    "skudai": "johor-bahru",
    "senai": "johor-bahru",
    "senai, kulai, johor": "johor-bahru",
    "kulai, johor": "johor-bahru",
    "kulai": "johor-bahru",
    "gelang patah, johor bahru": "johor-bahru",
    # Iskandar Puteri (incl. Medini, Nusajaya, Horizon Hills)
    "johor bahru (medini / iskandar puteri)": "iskandar-puteri",
    "taman nusa peristis": "iskandar-puteri",
    "taman nusa perintis": "iskandar-puteri",
    "horizon hills, iskandar puteri": "iskandar-puteri",
    # Muar district
    "muar": "muar",
    "pekan muar": "muar",
    "sungai mati": "muar",
    "bukit siput": "muar",
    "kampung sri amar di raja": "muar",
    "taman seri bakri 2": "muar",
    "kampung chokro": "muar",
    "kampung dalam": "muar",
    "kampung masjid lama": "muar",
    "kampung parit payong": "muar",
    "kampung mengkibol": "muar",  # Actually Kluang — fix below
    # Tangkak district
    "tangkak": "tangkak",
    "84000 tangkak": "tangkak",
    "taman tangkak jaya": "tangkak",
    "taman soga sutera": "tangkak",
    # Batu Pahat district
    "batu pahat": "batu-pahat",
    "batu pahat, johor": "batu-pahat",
    "taman tan leng ann": "batu-pahat",
    "taman banang": "batu-pahat",
    "taman selatan": "batu-pahat",
    "taman scientex": "batu-pahat",
    # Kluang district
    "kluang": "kluang",
    "kluang, johor": "kluang",
    "taman saujana kluang": "kluang",
    # Pontian
    "pontian district": "pontian",
    # Segamat
    "segamat district": "segamat",
}
# Fix mis-mapping: Kampung Mengkibol is Kluang, not Muar
_JOHOR["kampung mengkibol"] = "kluang"

# --- NEGERI SEMBILAN ---
_NS = {
    # Seremban district
    "seremban": "seremban",
    "70400 seremban": "seremban",
    "taman seremban 3": "seremban",
    "bukit rasah": "seremban",
    "taman sungai ujong": "seremban",
    "taman bunga raya": "seremban",
    "taman sejahtera": "seremban",
    "taman negeri": "seremban",
    "taman ideal": "seremban",
    "taman desa melang": "seremban",
    "taman bukit bayu": "seremban",
    "kampung seri sikamat seremban": "seremban",
    "kg seri sekamat": "seremban",
    "tmn bukit blossom": "seremban",
    "bandar sri sendayan": "seremban",
    "sek 9": "seremban",
    # Nilai / Labu
    "labu": "nilai",
    "taman labu utama": "nilai",
    # Port Dickson
    "port dickson": "port-dickson",
    # Rembau
    "rembau": "rembau",
    # Tampin
    "tampin": "tampin",
    # Jelebu
    "kuala klawang": "jelebu",
}

# --- PENANG ---
_PENANG = {
    "george town": "george-town",
    "georgetown": "george-town",
    "jelutong": "george-town",
    "bukit dumbar": "george-town",
    "sungai ara": "george-town",
    "jalan thomas": "george-town",
    "beverly hills": "george-town",
    "taman jelita": "george-town",
    "taman desa murni": "george-town",
    # Bukit Mertajam / Butterworth mainland
    "alma, bukit mertajam": "bukit-mertajam",
    "14000 bukit mertajam": "bukit-mertajam",
    "taman bagan": "bukit-mertajam",
    "kampung raya baharu": "bukit-mertajam",
    "kampung permatang durian": "bukit-mertajam",
    "kampung permatang tinggi": "bukit-mertajam",
    "kampung sama gagah dalam": "bukit-mertajam",
    "kampung tersusun pongsu seribu": "bukit-mertajam",
    "taman david chen": "bukit-mertajam",
    "taman kota permai": "bukit-mertajam",
    "pusat perniagaan vorteks": "bukit-mertajam",
}

# Human-readable district labels
_DISTRICT_LABELS = {
    # KL
    "bangsar": "Bangsar",
    "bukit-bintang": "Bukit Bintang",
    "kepong": "Kepong",
    "cheras": "Cheras",
    "setapak": "Setapak",
    "sentul": "Sentul",
    "old-klang-road": "Old Klang Road",
    "titiwangsa": "Titiwangsa",
    "pudu": "Pudu",
    "segambut": "Segambut",
    "damansara": "Damansara",
    # Selangor
    "petaling-jaya": "Petaling Jaya",
    "subang-jaya": "Subang Jaya",
    "shah-alam": "Shah Alam",
    "klang": "Klang",
    "kajang": "Kajang",
    "puchong": "Puchong",
    "ampang": "Ampang",
    "selayang": "Selayang",
    "sungai-buloh": "Sungai Buloh",
    "rawang": "Rawang",
    "seri-kembangan": "Seri Kembangan",
    "hulu-langat": "Hulu Langat",
    "sepang": "Sepang",
    "banting": "Banting",
    "kuala-selangor": "Kuala Selangor",
    # Johor
    "johor-bahru": "Johor Bahru",
    "iskandar-puteri": "Iskandar Puteri",
    "muar": "Muar",
    "tangkak": "Tangkak",
    "batu-pahat": "Batu Pahat",
    "kluang": "Kluang",
    "pontian": "Pontian",
    "segamat": "Segamat",
    # NS
    "seremban": "Seremban",
    "nilai": "Nilai",
    "port-dickson": "Port Dickson",
    "rembau": "Rembau",
    "tampin": "Tampin",
    "jelebu": "Jelebu",
    # Penang
    "george-town": "George Town",
    "bukit-mertajam": "Bukit Mertajam",
    # Selangor (additions)
    "setia-alam": "Setia Alam",
    "kota-kemuning": "Kota Kemuning",
    # Perak
    "ipoh": "Ipoh",
    "sitiawan": "Sitiawan",
    "teluk-intan": "Teluk Intan",
    "taiping": "Taiping",
    "lumut": "Lumut",
}

# --- PERAK ---
_PERAK = {
    # Ipoh metro — city proper + suburbs
    "ipoh": "ipoh",
    "taman ipoh": "ipoh",
    "kg simee, ipoh": "ipoh",
    "kg simee": "ipoh",
    "taman canning": "ipoh",
    "taman seri dermawan": "ipoh",
    "rapat setia": "ipoh",
    "taman mayfair": "ipoh",
    "buntong": "ipoh",
    "rpt pengkalan pegoh seberang": "ipoh",
    "pengkalan pegoh": "ipoh",
    "gopeng": "ipoh",
    "taman seri klebang": "ipoh",
    "menglembu": "ipoh",
    "bercham": "ipoh",
    "chemor": "ipoh",
    # Other Perak towns (each likely <3, no page generated)
    "sitiawan": "sitiawan",
    "pekan teluk intan": "teluk-intan",
    "teluk intan": "teluk-intan",
    "taiping": "taiping",
    "lumut": "lumut",
}

_STATE_MAPS = {
    "Kuala Lumpur": _KL,
    "Selangor": _SELANGOR,
    "Johor": _JOHOR,
    "Negeri Sembilan": _NS,
    "Penang": _PENANG,
    "Perak": _PERAK,
}


def _normalize(area):
    return (area or "").strip().lower()


def area_to_district(state, area):
    """Return (district_slug, district_label) for a (state, area), or None.

    Falls through to None when the area is unmapped — those facilities
    will only appear on the state page, not on a district page.
    """
    state = (state or "").strip()
    norm = _normalize(area)
    if not state or not norm:
        return None
    state_map = _STATE_MAPS.get(state)
    if not state_map:
        return None
    slug = state_map.get(norm)
    if not slug:
        # Some area values include the state name as suffix; try stripping
        for suffix in (f", {state.lower()}", f" {state.lower()}"):
            if norm.endswith(suffix):
                slug = state_map.get(norm[: -len(suffix)].strip())
                if slug:
                    break
    if not slug:
        return None
    return slug, _DISTRICT_LABELS.get(slug, slug.replace("-", " ").title())


# --- Coverage report -----------------------------------------------------
def _coverage_report():
    import csv, io, urllib.request
    from collections import defaultdict, Counter

    url = (
        "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ4_BgHIjnlgmITzjyUuGDpgpNzPL7MfjOY2069i0PtbVbXSxIAJk1tmBejwNo8aBBeLuRi62szF2sh/pub"
        "?gid=292378871&single=true&output=csv"
    )
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        rows = list(csv.DictReader(io.StringIO(r.read().decode("utf-8"))))
    live = [r for r in rows if r.get("status", "").strip().lower() not in ("unverified", "removed")]

    # By category × district
    cat_label = {
        "nursing home": "NH",
        "assisted living": "AL",
        "day care": "DC",
        "home care": "HC",
    }

    def category_of(f):
        ct = (f.get("care_types") or "").lower()
        if "nursing home" in ct:
            return "nursing home"
        if "assisted living" in ct:
            return "assisted living"
        if "day care" in ct:
            return "day care"
        if "home care" in ct:
            return "home care"
        return "nursing home"  # default

    by_district = defaultdict(lambda: defaultdict(int))
    unmapped = defaultdict(Counter)
    mapped_count = 0

    for f in live:
        state = (f.get("state") or "").strip()
        area = (f.get("area") or "").strip()
        cat = category_of(f)
        d = area_to_district(state, area)
        if d:
            mapped_count += 1
            slug, label = d
            by_district[(state, slug, label)][cat] += 1
        elif state and area:
            unmapped[state][area] += 1

    print(f"Total live facilities: {len(live)}")
    print(f"Mapped to a district:  {mapped_count} ({mapped_count * 100 // len(live)}%)")
    print(f"Unmapped:              {len(live) - mapped_count}")
    print()

    print("=== Districts by NH count (>=3 = page-worthy) ===")
    pages = 0
    pages_per_cat = Counter()
    for key, counts in sorted(by_district.items(), key=lambda x: -x[1]["nursing home"]):
        state, slug, label = key
        nh = counts["nursing home"]
        line = f"  {nh:>3} NH"
        for cat in ("assisted living", "day care", "home care"):
            c = counts[cat]
            if c:
                line += f" / {c} {cat_label[cat]}"
        line += f"    {label}, {state}"
        if nh >= 3:
            pages += 1
            pages_per_cat["nursing home"] += 1
            line = "** " + line.lstrip()
        else:
            line = "   " + line.lstrip()
        print(line)
        for cat in ("assisted living", "day care", "home care"):
            if counts[cat] >= 3:
                pages_per_cat[cat] += 1
    print()
    print(f"Page-worthy districts (>=3 facilities in that category):")
    for cat, n in pages_per_cat.items():
        print(f"  {cat_label[cat]}: {n} pages")
    print()
    print("=== Top 30 unmapped areas (would benefit from taxonomy entries) ===")
    flat = []
    for state, counter in unmapped.items():
        for area, count in counter.items():
            flat.append((count, state, area))
    flat.sort(reverse=True)
    for count, state, area in flat[:30]:
        print(f"  {count:>3}  {area}, {state}")


if __name__ == "__main__":
    _coverage_report()
