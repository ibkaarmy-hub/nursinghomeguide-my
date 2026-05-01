"""
MDAC.my scraper v3 — regex on HTML for precise field extraction.

Structure of MDAC listing pages:
  Address : <span> inside map-marker <a> link
  Phone   : <li class="lp-listing-phone"> -> <a href="tel:...">
  Website : <li class="lp-user-web"> -> <a href="...">
  Content : <div class="post-detail-content"> -> <p>
              Occupancy : N<br>Capacity : N beds<br>P.I.C : Name<br>P.I.C Email : ...

Login detection: post-detail-content absent = behind login wall.

State detection:
  1. Phone prefix: 07-=Johor, 03-=KL/Selangor area
  2. Address keywords for disambiguation
"""

import csv, io, re, time, urllib.request

FACILITIES_CSV = (
    "https://docs.google.com/spreadsheets/d/e/"
    "2PACX-1vQ4_BgHIjnlgmITzjyUuGDpgpNzPL7MfjOY2069i0PtbVbXSxIAJk1tmBejwNo8aBBeLuRi62szF2sh"
    "/pub?gid=292378871&single=true&output=csv"
)

MDAC_URLS = [
    # ── Johor ────────────────────────────────────────────────────────────────
    "https://mdac.my/listing/clover-healthcare-sdn-bhd/",
    "https://mdac.my/listing/jb-care-centre/",
    "https://mdac.my/listing/goodwill-care-centre-johor-bahru-jb/",
    "https://mdac.my/listing/alda-homes-eldercare/",
    "https://mdac.my/listing/jb-hometown-care-centre/",
    "https://mdac.my/listing/jb-hometown-care-centre-2/",
    "https://mdac.my/listing/green-acres-home-care/",
    "https://mdac.my/listing/green-acres-elderly-care-centre/",
    "https://mdac.my/listing/prestige-residence-care-group-sdn-bhd/",
    "https://mdac.my/listing/jeta-care-sdn-bhd/",
    "https://mdac.my/listing/pusat-warga-emas-hillville/",
    "https://mdac.my/listing/pusat-jagaan-v-r-melodies-old-folks-home/",
    "https://mdac.my/listing/happiness-care-centre/",
    "https://mdac.my/listing/kioh-care-centre/",
    "https://mdac.my/listing/calvary-old-folks-home-female/",
    "https://mdac.my/listing/calvary-old-folks-home-male/",
    "https://mdac.my/listing/city-heart-care-centre/",
    "https://mdac.my/listing/city-heart-care-licensed-nursing-home/",
    "https://mdac.my/listing/econ-medicare-centre-and-nursing-home/",
    "https://mdac.my/listing/summit-evershine-care/",
    "https://mdac.my/listing/noble-care/",
    "https://mdac.my/listing/rumah-seri-kenangan-johor-bahru/",
    "https://mdac.my/listing/persatuan-kebajikan-warga-tua-pleasure-johor-bahru/",
    "https://mdac.my/listing/persatuan-kebajikan-warga-tua-pleasure-johor-bahru-branch/",
    "https://mdac.my/listing/pusat-jagaan-orang-tua-ceria/",
    "https://mdac.my/listing/pusat-jagaan-warga-tua-sri-orkid-cawangan/",
    "https://mdac.my/listing/pusat-penjagaan-warga-tua-sri-orkid/",
    "https://mdac.my/listing/i-home-care-center/",
    "https://mdac.my/listing/pine-tree-home-care-centre/",
    "https://mdac.my/listing/green-garden-care-centre-sdn-bhd/",
    "https://mdac.my/listing/comfort-old-folks-home-centre/",
    "https://mdac.my/listing/pusat-jagaan-wargatua-amrita/",
    "https://mdac.my/listing/pusat-jagaan-bethany-elderly-home/",
    "https://mdac.my/listing/pusat-jagaan-health-life-old-folks-home/",
    "https://mdac.my/listing/pusat-jagaan-rumah-sejahtera-batu-pahat/",
    "https://mdac.my/listing/pusat-jagaan-warga-emas-banang/",
    "https://mdac.my/listing/pusat-jagaan-wargatua-parit-bilal-pusat-jagaan-wargatua-tci-ler/",
    "https://mdac.my/listing/bp-geriatrics-care-sdn-bhd/",
    "https://mdac.my/listing/rumah-sejahtera-yong-peng/",
    "https://mdac.my/listing/golden-age-care-centre-sdn-bhd/",
    "https://mdac.my/listing/golden-age-care-centre-sdn-bhd-branch/",
    "https://mdac.my/listing/pusat-jagaan-bakti-murni/",
    "https://mdac.my/listing/pusat-jagaan-indah-harapan/",
    "https://mdac.my/listing/pusat-jagaan-sri-kenangan/",
    "https://mdac.my/listing/pusat-jagaan-sri-kenangan-branch/",
    "https://mdac.my/listing/pusat-jagaan-warga-emas-al-jannah/",
    "https://mdac.my/listing/pusat-jagaan-warga-emas-nur-ehsan/",
    "https://mdac.my/listing/pusat-jagaan-teduhan-zafrah-male/",
    "https://mdac.my/listing/pusat-jagaan-teduhan-zafrah-female/",
    "https://mdac.my/listing/pusat-jagaan-titipan-kasih/",
    "https://mdac.my/listing/gm-care-centre/",
    "https://mdac.my/listing/justlife-care-home/",
    "https://mdac.my/listing/pusat-jagaan-miriam-home-for-the-aged/",
    "https://mdac.my/listing/pusat-jagaan-pawana-indah/",
    "https://mdac.my/listing/pusat-jagaan-pawana-sutera/",
    "https://mdac.my/listing/pusat-jagaan-sri-sentosa/",
    "https://mdac.my/listing/pusat-jagaan-warga-emas-bahagia/",
    "https://mdac.my/listing/pusat-jagaan-ler-lin/",
    "https://mdac.my/listing/medina-home-care-centre/",
    "https://mdac.my/listing/pusat-jagaan-superfun-pusat-rekreasi-warga-tua/",
    "https://mdac.my/listing/nursing-home-johor-bahru/",
    # ── Kuala Lumpur ─────────────────────────────────────────────────────────
    "https://mdac.my/listing/afh-elder-care/",
    "https://mdac.my/listing/acg-care-sdn-bhd/",
    "https://mdac.my/listing/amazing-grace-caring-home/",
    "https://mdac.my/listing/amitabha-malaysia-old-folks-home-kl/",
    "https://mdac.my/listing/attia-care-centers-bukit-damansara/",
    "https://mdac.my/listing/attia-care-centers-taman-wahyu/",
    "https://mdac.my/listing/dementia-care-centre/",
    "https://mdac.my/listing/dhaalia-elderly-care-centre/",
    "https://mdac.my/listing/eldercare-nursing-home-jalan-damai/",
    "https://mdac.my/listing/eldercare-nursing-home-cheras/",
    "https://mdac.my/listing/elderly-gardens-care-centre/",
    "https://mdac.my/listing/grace-villa-home-care-services/",
    "https://mdac.my/listing/his-grace-care-home/",
    "https://mdac.my/listing/his-grace-care-kl-taman-p-ramlee/",
    "https://mdac.my/listing/home-grace-sri-damansara/",
    "https://mdac.my/listing/i-care-haven/",
    "https://mdac.my/listing/jj-blessing-care-centre-tmn-oug/",
    "https://mdac.my/listing/lecadia-primecare-centre-sdn-bhd/",
    "https://mdac.my/listing/merry-care-centre-jln-belinggai/",
    "https://mdac.my/listing/merry-care-centre-jln-antoi/",
    "https://mdac.my/listing/opulence-care/",
    "https://mdac.my/listing/procare-care-centre/",
    "https://mdac.my/listing/sree-sai-elder-home-care-mental-health-old-age-residential-home/",
    "https://mdac.my/listing/pusat-jagaan-husna-arrashid/",
    "https://mdac.my/listing/rumah-orang-tua-charis/",
    "https://mdac.my/listing/rumah-warga-emas-nascom/",
    "https://mdac.my/listing/seavoy-nursing-home-taman-setapak-indah/",
    "https://mdac.my/listing/seavoy-nursing-home-desa-melawati/",
    "https://mdac.my/listing/serenity-lifecare/",
    "https://mdac.my/listing/siri-jayanti-metta-care-centre/",
    "https://mdac.my/listing/sri-seronok-retirement-village/",
    "https://mdac.my/listing/st-francis-xavie-home-for-the-elderly-little-sisters-of-the-poor/",
    "https://mdac.my/listing/st-marys-nursing-home-jalan-halimahton/",
    "https://mdac.my/listing/st-marys-nursing-home-jalan-penghulu-mat/",
    "https://mdac.my/listing/sunshine-nursing-home/",
    "https://mdac.my/listing/susheela-care-center/",
    "https://mdac.my/listing/ti-ratana-welfare-societys-elderly-home/",
    "https://mdac.my/listing/tong-sim-senior-citizens-care-centre-bukit-seputeh/",
    "https://mdac.my/listing/tong-sim-senior-citizens-care-centre-jalan-dewan-bahasa/",
    "https://mdac.my/listing/tai-kuk-wah-si-buddist-society/",
    "https://mdac.my/listing/persatuan-kebajikan-dan-social-kim-loo-ting/",
    "https://mdac.my/listing/klc-senior-care-center/",
    "https://mdac.my/listing/lyc-senior-living-care-center/",
    "https://mdac.my/listing/minty-green-wellness-residence-kepong-opening-in-dec-2020/",
    "https://mdac.my/listing/goodwill-family-care-centre/",
    "https://mdac.my/listing/pusat-jagaan-orang-tua-weng-da/",
    "https://mdac.my/listing/pusat-jagaan-an-xie/",
    "https://mdac.my/listing/pusat-jagaan-en-yuan-cheras/",
    "https://mdac.my/listing/pusat-jagaan-persatuan-kebajikan-warga-emas-chan-kl/",
    "https://mdac.my/listing/pusat-jagaan-pertubuhan-kebajikan-sri-mesra/",
    "https://mdac.my/listing/pusat-jagaan-rumah-orang-tua-ampang/",
    "https://mdac.my/listing/restu-villa-care-centre/",
    "https://mdac.my/listing/stillwaters-golden-villa-elder-care/",
    "https://mdac.my/listing/apple-old-folks-home-care-centre/",
    "https://mdac.my/listing/pusat-jagaan-orang-tua-cahaya-maju/",
    "https://mdac.my/listing/pusat-jagaan-warga-emas-oasis/",
    "https://mdac.my/listing/pj-care-centre/",
    "https://mdac.my/listing/retirement-home-midvalley/",
    "https://mdac.my/listing/nursing-home-datuk-keramat/",
    "https://mdac.my/listing/retirement-home-ampang/",
    "https://mdac.my/listing/nursing-home-cheras/",
    "https://mdac.my/listing/pj-mentalink-care-pj-old-folks/",
    "https://mdac.my/listing/shalom-nursing-home/",
    "https://mdac.my/listing/pusat-jagaan-warga-tua-damai-damai-home-care/",
    "https://mdac.my/listing/rumah-teduhan-kasih-lelaki/",
    "https://mdac.my/listing/rumah-sinar-kasih-wanita/",
    "https://mdac.my/listing/pusat-jagaan-rumah-warga-tua-cahaya/",
    "https://mdac.my/listing/rumah-victory-elderly-home/",
    "https://mdac.my/listing/de-luxe-retirement-home/",
    "https://mdac.my/listing/pusat-jagaan-warga-emas-murni-kaseh-lelaki/",
    "https://mdac.my/listing/pusat-jagaan-warga-emas-kaseh-bonda-perempuan/",
    "https://mdac.my/listing/vivekananda-shelter/",
    "https://mdac.my/listing/pusat-jagaan-dan-rawatan-orang-tua-al-ikhlas/",
    "https://mdac.my/listing/attia-nursing-care-centre/",
    "https://mdac.my/listing/pusat-jagaan-lekshmy-illam/",
    "https://mdac.my/listing/well-living-nursing-care-centre-sdn-bhd/",
    # ── Selangor ─────────────────────────────────────────────────────────────
    "https://mdac.my/listing/jj-blessing-care-centre-puchong-selangor/",
    "https://mdac.my/listing/aim-healthcare-senior-home-selangor/",
    "https://mdac.my/listing/pusat-jagaan-rumah-orang-tua-wesley/",
    "https://mdac.my/listing/pusat-jagaan-selangor-king-george-v-silver-jubilee-fund/",
    "https://mdac.my/listing/berniece-care-service-centre/",
    "https://mdac.my/listing/st-marys-nursing-home-22-jln-othman-selangor/",
    "https://mdac.my/listing/st-marys-nursing-home-31-jln-othman-selangor/",
    "https://mdac.my/listing/st-marys-nursing-home-taman-sri-sentosa-selangor/",
    "https://mdac.my/listing/minty-green-wellness-residence-sungai-long/",
    "https://mdac.my/listing/mintygreen-senior-care-center-kajang-balakong/",
    "https://mdac.my/listing/padma-care-centre/",
    "https://mdac.my/listing/sunrise-elderly-living-home/",
    "https://mdac.my/listing/pusat-jagaan-parameswary-old-folks-home-and-mother-care/",
    "https://mdac.my/listing/bandar-damai-home-care-female/",
    "https://mdac.my/listing/bandar-damai-home-care-male/",
    "https://mdac.my/listing/green-cottage-retirement-and-nursing-home/",
    "https://mdac.my/listing/zara-aisyah-care-centre/",
    "https://mdac.my/listing/columbia-asia-extended-care-hospital/",
    "https://mdac.my/listing/pusat-jagaan-ebenezer-home/",
    "https://mdac.my/listing/pusat-jagaan-warga-emas-zakat/",
    "https://mdac.my/listing/bethel-retirement-home-plt/",
    "https://mdac.my/listing/pusat-jagaan-chik-sin-thong-klang-dan-pantai-selangor/",
    "https://mdac.my/listing/pusat-jagaan-persatuan-kebajikan-rumah-jagaan-vcu-selangor-dan-wilayah-persekutuan-kuala-lumpur/",
    "https://mdac.my/listing/pusat-jagaan-persatuan-rumah-warga-emas-klang-selangor/",
    "https://mdac.my/listing/sahana-old-folks-home/",
    "https://mdac.my/listing/rumah-kebajikan-chong-keng-seong/",
    "https://mdac.my/listing/rumah-warisan-kaseh-darul-maghfiroh/",
    "https://mdac.my/listing/kajang-caring-home/",
    "https://mdac.my/listing/pusat-jagaan-beverly-care-home/",
    "https://mdac.my/listing/pusat-jagaan-rumah-love-and-care-kajang-2/",
    "https://mdac.my/listing/pusat-jagaan-rumah-love-and-care-kajang-1/",
    "https://mdac.my/listing/pusat-jagaan-warga-emas-semenyih/",
    "https://mdac.my/listing/rumah-penjagaan-pendidikan-warga-emas-darul-insyirah/",
    "https://mdac.my/listing/rumah-sejahtera-seri-kembangan/",
    "https://mdac.my/listing/pusat-jagaan-rumah-amal-murni-kajang/",
    "https://mdac.my/listing/pusat-jagaan-al-fikrah-malaysia/",
    "https://mdac.my/listing/24-angels-home-care-m-sdn-bhd/",
    "https://mdac.my/listing/mintygreen-nursing-home-eldercare-center/",
    "https://mdac.my/listing/missi-care-sdn-bhd/",
    "https://mdac.my/listing/kajang-nursing-home/",
    "https://mdac.my/listing/sam-ching-kong-old-folks-home-hulu-langat/",
    "https://mdac.my/listing/anns-care-centre/",
    "https://mdac.my/listing/pusat-jagaan-ai-sim/",
    "https://mdac.my/listing/pusat-jagaan-ee-dian/",
    "https://mdac.my/listing/p-w-e-penyayang-serdang-jaya/",
    "https://mdac.my/listing/pusat-jagaan-orang-tua-apex-way/",
    "https://mdac.my/listing/pusat-warga-mas-penyayang/",
    "https://mdac.my/listing/wan-hing-home-care/",
    "https://mdac.my/listing/pusat-jagaan-orang-tua-wan-hing/",
    "https://mdac.my/listing/wan-hing-care-center-sdn-bhd/",
    "https://mdac.my/listing/wan-hing-care-center-psk-sdn-bhd/",
    "https://mdac.my/listing/wellness-elderly-home-care-center/",
    "https://mdac.my/listing/pusat-jagaan-mahmudah-malaysia/",
    "https://mdac.my/listing/pusat-jagaan-dan-pendidikan-warga-emas-darul-insyirah/",
    "https://mdac.my/listing/pusat-jagaan-rumah-nur-hasanah/",
    "https://mdac.my/listing/pertubuhan-ikhlas-malaysia/",
    "https://mdac.my/listing/sincere-care-home/",
    "https://mdac.my/listing/sri-sayang-welfare-home/",
    "https://mdac.my/listing/bellevue-residential-homecare-m-sdn-bhd/",
    "https://mdac.my/listing/dr-teo-keng-huat-home-care/",
    "https://mdac.my/listing/evershine-elderly-retirement-home-sdn-bhd/",
    "https://mdac.my/listing/felicity-nursing-home/",
    "https://mdac.my/listing/ihm-nursing-care-sdn-bhd-sunshine-home/",
    "https://mdac.my/listing/moonleaf-medicare-centre/",
    "https://mdac.my/listing/evagayle-care-home/",
    "https://mdac.my/listing/stella-maris-home-plt-care-centre/",
    "https://mdac.my/listing/than-hsiang-wan-ching-yuen-pj/",
    "https://mdac.my/listing/corning-elderly-care-centre/",
    "https://mdac.my/listing/pusat-jagaan-psikologi-dan-emosi-eve/",
    "https://mdac.my/listing/my-aged-care-sdn-bhd/",
    "https://mdac.my/listing/summer-breeze-cottage-caring-home/",
    "https://mdac.my/listing/golden-cares-nursing-home/",
    "https://mdac.my/listing/star-nursing-home/",
    "https://mdac.my/listing/cherish-retirement-and-nursing-home/",
    "https://mdac.my/listing/multicare-nursing-home/",
    "https://mdac.my/listing/regal-care-nursing-home/",
    "https://mdac.my/listing/pusat-jagaan-jivi/",
    "https://mdac.my/listing/gracevilla-retirement-home/",
    "https://mdac.my/listing/white-dove-retirement-nursing-home/",
    "https://mdac.my/listing/rumah-ozanam/",
    "https://mdac.my/listing/nursing-home-rawang/",
    "https://mdac.my/listing/nursing-home-usj-9/",
    "https://mdac.my/listing/nursing-home-petaling-jaya/",
    "https://mdac.my/listing/nursing-home-klang/",
    "https://mdac.my/listing/retirement-home-kajang/",
    "https://mdac.my/listing/retirement-home-usj-18/",
    "https://mdac.my/listing/nursing-home-semenyih/",
    "https://mdac.my/listing/jasper-lodge-nursing-home-pj1/",
    "https://mdac.my/listing/jasper-lodge-nursing-home-pj2/",
    "https://mdac.my/listing/jasper-lodge-nursing-home-pj3/",
    "https://mdac.my/listing/jasper-lodge-nursing-home-pj5/",
    "https://mdac.my/listing/pusat-jagaan-pertubuhan-kebajikan-chester-selangor/",
    "https://mdac.my/listing/pusat-jagaan-rumah-kebajikan-warga-emas-st-mark/",
    "https://mdac.my/listing/pusat-jagaan-rumah-warga-tua-cahaya/",
    "https://mdac.my/listing/de-luxe-retirement-home/",
    "https://mdac.my/listing/serendah-nursing-home/",
    "https://mdac.my/listing/favourite-home-care/",
    "https://mdac.my/listing/pusat-jagaan-kanak-kanak-kurang-upaya-kirtash/",
    "https://mdac.my/listing/nurses-at-home/",
]

# ── State detection ──────────────────────────────────────────────────────────
ADDR_KW = [
    # Johor
    ("johor bahru", "Johor"), ("johor", "Johor"), ("j.b.", "Johor"),
    ("nusajaya", "Johor"), ("iskandar", "Johor"), ("perling", "Johor"),
    ("pasir gudang", "Johor"), ("kulai", "Johor"), ("senai", "Johor"),
    ("tebrau", "Johor"), ("tampoi", "Johor"), ("skudai", "Johor"),
    ("larkin", "Johor"), ("batu pahat", "Johor"), ("muar", "Johor"),
    ("segamat", "Johor"), ("kluang", "Johor"), ("kota tinggi", "Johor"),
    ("pontian", "Johor"), ("mersing", "Johor"), ("yong peng", "Johor"),
    ("81", "Johor"),  # 81xxx postcode = Johor (weak signal, used last)
    # Kuala Lumpur
    ("kuala lumpur", "Kuala Lumpur"), ("wilayah persekutuan", "Kuala Lumpur"),
    ("w.p.", "Kuala Lumpur"), ("bukit damansara", "Kuala Lumpur"),
    ("taman p.ramlee", "Kuala Lumpur"), ("p.ramlee", "Kuala Lumpur"),
    ("jalan damai", "Kuala Lumpur"), ("taman oug", "Kuala Lumpur"),
    ("kepong", "Kuala Lumpur"), ("setapak", "Kuala Lumpur"),
    ("wangsa maju", "Kuala Lumpur"), ("brickfields", "Kuala Lumpur"),
    ("bangsar", "Kuala Lumpur"), ("sri hartamas", "Kuala Lumpur"),
    ("mont kiara", "Kuala Lumpur"), ("mid valley", "Kuala Lumpur"),
    ("sentul", "Kuala Lumpur"), ("jalan ipoh", "Kuala Lumpur"),
    ("chow kit", "Kuala Lumpur"), ("bukit bintang", "Kuala Lumpur"),
    ("titiwangsa", "Kuala Lumpur"), ("alam damai", "Kuala Lumpur"),
    # Selangor
    ("selangor", "Selangor"), ("petaling jaya", "Selangor"),
    ("shah alam", "Selangor"), ("klang", "Selangor"),
    ("subang jaya", "Selangor"), ("subang", "Selangor"),
    ("kajang", "Selangor"), ("puchong", "Selangor"),
    ("rawang", "Selangor"), ("seri kembangan", "Selangor"),
    ("semenyih", "Selangor"), ("hulu langat", "Selangor"),
    ("serendah", "Selangor"), ("balakong", "Selangor"),
    ("serdang", "Selangor"), ("bangi", "Selangor"),
    ("sungai long", "Selangor"), ("sungai besi", "Selangor"),
    ("pandan", "Selangor"), ("kota damansara", "Selangor"),
    ("damansara damai", "Selangor"), ("usj", "Selangor"),
    ("bukit jalil", "Selangor"), ("cheras", "Selangor"),
    ("ampang", "Selangor"), ("sri damansara", "Selangor"),
    ("sun u", "Selangor"), ("sunway", "Selangor"),
    ("taman jaya", "Selangor"),
]


def detect_state(phone, address):
    """Detect state from phone prefix then address keywords."""
    ph = re.sub(r"[\s\-\+]", "", phone or "")
    # Strip leading 6 or 60
    if ph.startswith("60"): ph = ph[2:]
    elif ph.startswith("6"): ph = ph[1:]

    addr_lo = (address or "").lower()

    if ph.startswith("07"):
        return "Johor"
    elif ph.startswith("03"):
        # Disambiguate KL vs Selangor from address
        for kw, s in ADDR_KW:
            if kw in addr_lo:
                return s
        return "KL/Selangor"
    elif ph.startswith(("06","04","05","09","08")):
        return ""  # other states, skip

    # Mobile or unknown — rely on address
    for kw, s in ADDR_KW:
        if kw in addr_lo:
            return s
    return ""


def html_to_text(s):
    """Strip HTML tags and decode entities."""
    s = re.sub(r'<[^>]+>', ' ', s)
    s = s.replace('&#8211;', '-').replace('&#8217;', "'").replace('&#038;', '&')
    s = s.replace('&amp;', '&').replace('&nbsp;', ' ').replace('&lt;', '<').replace('&gt;', '>')
    return re.sub(r'\s+', ' ', s).strip()


def parse_page(html, url):
    slug = url.rstrip("/").split("/")[-1]
    rec = {
        "mdac_slug": slug, "mdac_url": url,
        "name": "", "address": "", "phone": "",
        "total_beds": "", "occupancy": "",
        "contact_person": "", "contact_email": "", "website": "",
        "state_detected": "", "login_required": "no",
    }

    # Name from <title>
    t = re.search(r'<title>([^<]+)</title>', html, re.I)
    if t:
        name = t.group(1)
        name = re.sub(r'\s*[–\-]\s*MYS.*$', '', name)
        name = re.sub(r'\s*[–\-]\s*MyAgeing.*$', '', name, flags=re.I)
        name = html_to_text(name)
        rec["name"] = name.strip()

    # Login detection: post-detail-content must be present for data access
    if 'post-detail-content' not in html:
        rec["login_required"] = "yes"
        return rec

    # Address: inside <span> near map-marker icon
    addr_m = re.search(
        r'fa-map-marker.*?<span[^>]*>\s*(.*?)\s*</span>',
        html, re.DOTALL | re.I
    )
    if addr_m:
        rec["address"] = html_to_text(addr_m.group(1))

    # Phone: <a href="tel:..."> inside lp-listing-phone
    phone_m = re.search(r'lp-listing-phone.*?href="tel:([^"]+)"', html, re.DOTALL | re.I)
    if phone_m:
        rec["phone"] = phone_m.group(1).strip()

    # Website: <a href="..."> inside lp-user-web
    web_m = re.search(r'lp-user-web.*?href="([^"]+)"', html, re.DOTALL | re.I)
    if web_m:
        wurl = web_m.group(1)
        if wurl.startswith("http") and "mdac.my" not in wurl:
            rec["website"] = wurl

    # Content block: Occupancy / Capacity / P.I.C
    content_m = re.search(
        r'post-detail-content[^>]*>\s*<p>(.*?)</p>',
        html, re.DOTALL | re.I
    )
    if content_m:
        block = html_to_text(content_m.group(1))
        # Parse lines like "Occupancy : 14 Capacity : 20 beds P.I.C : Name ..."
        occ  = re.search(r'Occupancy\s*:\s*(\d+)', block, re.I)
        cap  = re.search(r'Capacity\s*:\s*(\d+)', block, re.I)
        pic  = re.search(r'P\.I\.C\s*:\s*([^:]+?)(?:\s+P\.I\.C|$)', block, re.I)
        picm = re.search(r'P\.I\.C Email\s*:\s*(\S+)', block, re.I)
        if occ: rec["occupancy"]      = occ.group(1)
        if cap: rec["total_beds"]     = cap.group(1)
        if pic: rec["contact_person"] = pic.group(1).strip()
        if picm: rec["contact_email"] = picm.group(1).strip()

    rec["state_detected"] = detect_state(rec["phone"], rec["address"])
    return rec


def normalise(name):
    name = name.lower()
    for w in ("sdn bhd","sdn. bhd."," plt"," berhad",
              "pusat jagaan ","rumah ","warga emas","warga tua",
              "persatuan ","kebajikan ","pertubuhan ",
              "nursing home","care centre","care center",
              "elderly care","old folks home","senior home"):
        name = name.replace(w, " ")
    name = re.sub(r"[^a-z0-9 ]", " ", name)
    name = re.sub(r"\s+", " ", name).strip()
    return name


def fetch_html(url, retries=2):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=15) as resp:
                return resp.read().decode("utf-8", errors="replace")
        except Exception:
            if attempt < retries:
                time.sleep(2)
    return None


def load_sheet():
    req = urllib.request.Request(FACILITIES_CSV, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        raw = resp.read().decode("utf-8-sig")
    return list(csv.DictReader(io.StringIO(raw)))


def main():
    print("Loading Google Sheet...")
    sheet = load_sheet()
    print(f"  {len(sheet)} rows")

    # Build lookups
    by_phone = {}
    for r in sheet:
        ph = re.sub(r"[^\d]", "", r.get("phone",""))[-8:]
        if len(ph) >= 7:
            by_phone[ph] = r
    norm_names = {normalise(r.get("title","")): r for r in sheet}

    print(f"\nScraping {len(MDAC_URLS)} MDAC pages...")
    scraped = []
    for i, url in enumerate(MDAC_URLS):
        slug = url.rstrip("/").split("/")[-1][:40]
        print(f"  [{i+1}/{len(MDAC_URLS)}] {slug}", end="", flush=True)
        html = fetch_html(url)
        if not html:
            print(" FAIL")
            continue
        rec = parse_page(html, url)
        login = " [login]" if rec["login_required"] == "yes" else ""
        state = rec["state_detected"] or "?"
        beds  = rec["total_beds"] or "-"
        print(f"{login} {state} | {beds}b | {rec['name'][:35]}")
        scraped.append(rec)
        time.sleep(0.4)

    # Filter to our 3 states
    our = [r for r in scraped
           if r["state_detected"] in ("Johor", "Kuala Lumpur", "Selangor", "KL/Selangor")]
    print(f"\n{len(our)} facilities in Johor/KL/Selangor")

    # Cross-reference
    matched, new_fac = [], []
    for r in our:
        sheet_row = None

        # 1. Phone match
        ph_key = re.sub(r"[^\d]", "", r.get("phone",""))[-8:]
        if len(ph_key) >= 7 and ph_key in by_phone:
            sheet_row = by_phone[ph_key]

        # 2. Normalised name
        if not sheet_row:
            mn = normalise(r["name"])
            if mn and mn in norm_names:
                sheet_row = norm_names[mn]

        if sheet_row:
            r["matched_slug"]  = sheet_row.get("slug","")
            r["matched_title"] = sheet_row.get("title","")
            r["sheet_beds"]    = sheet_row.get("total_beds","")
            r["sheet_phone"]   = sheet_row.get("phone","")
            matched.append(r)
        else:
            r["matched_slug"]  = ""
            r["matched_title"] = ""
            r["sheet_beds"]    = ""
            r["sheet_phone"]   = ""
            new_fac.append(r)

    # Write CSVs
    fields = ["mdac_slug","mdac_url","name","address","phone","total_beds","occupancy",
              "contact_person","contact_email","website","state_detected","login_required",
              "matched_slug","matched_title","sheet_beds","sheet_phone"]

    for fname, rows in [("mdac_our_states.csv", our),
                        ("mdac_matched.csv", matched),
                        ("mdac_new.csv", new_fac)]:
        with open(fname, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
            w.writeheader()
            w.writerows(rows)

    print(f"\n=== RESULTS ===")
    print(f"Our states total : {len(our)}")
    print(f"  Matched        : {len(matched)}")
    print(f"  Potentially new: {len(new_fac)}")

    accessible = [r for r in our if r["login_required"]=="no"]
    with_beds  = [r for r in accessible if r["total_beds"]]
    print(f"\nAccessible (not login-gated): {len(accessible)}")
    print(f"  With bed data : {len(with_beds)}")

    update_able = [r for r in matched if r["total_beds"] and not r["sheet_beds"] and r["login_required"]=="no"]
    print(f"  Can update sheet (beds missing in sheet): {len(update_able)}")

    print(f"\n-- NEW facilities not in sheet --")
    for r in new_fac:
        login = " [login]" if r["login_required"]=="yes" else ""
        beds = r["total_beds"] or "?"
        print(f"  [{r['state_detected']}]{login} {r['name'][:50]} | {beds} beds | {r['address'][:50]}")

    print(f"\n-- Matched + have bed data to update --")
    for r in update_able:
        print(f"  {r['matched_title'][:40]} | MDAC:{r['total_beds']}b (occ:{r['occupancy']}) | sheet:blank")


if __name__ == "__main__":
    main()
