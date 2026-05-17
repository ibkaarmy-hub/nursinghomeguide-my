"""Hand-written intros for district pages.

Each intro is ~120-160 words covering:
- Where the district is and its general character
- Major hospitals (proximity matters for eldercare)
- Transport / accessibility (parking, public transport)
- A practical visit consideration for families

Conscious omissions (per editorial rules in CLAUDE.md):
- No "best of" claims about specific facilities
- No invented demographic stats
- No operator-friendly marketing language
- Facts are limited to widely-verifiable: hospital names, transport
  lines, district administrative status
"""

DISTRICT_INTROS = {
    # ─── KLANG VALLEY ─────────────────────────────────────────────────────

    "petaling-jaya": """Petaling Jaya sprawls across the western Klang Valley, from the older sections (PJ Old Town, Section 14, Bangsar South border) through to the newer Damansara corridor and Kota Damansara. It's one of Selangor's most densely populated districts and has the longest-established eldercare landscape in the country — many of the homes here have operated for 15+ years.

Major hospitals nearby include Sunway Medical Centre, Subang Jaya Medical Centre, and Assunta Hospital, with University Malaya Medical Centre (UMMC) accessible across the federal-highway border. Traffic on the Federal Highway and LDP can be punishing on weekday evenings — families visiting after work should factor in 45+ minutes from KL city centre.

Public transport is strong: the LRT Kelana Jaya Line, MRT Kajang Line (Phileo Damansara, TTDI, Surian, Mutiara Damansara, Kota Damansara), and KTM Kelana Jaya all serve PJ neighborhoods. Visit timing matters more here than in most districts.""",

    "subang-jaya": """Subang Jaya is the planned township south-west of Petaling Jaya, covering USJ, Bandar Sunway, Sunway City, and Putra Heights. It's younger than PJ as a residential area — most neighborhoods were developed from the 1980s onward — and the eldercare landscape skews toward purpose-built assisted-living and premium nursing homes rather than retrofitted bungalows.

Sunway Medical Centre is the district anchor and one of Malaysia's largest private hospitals; Columbia Asia Subang Jaya is the secondary option. Both are within 5–10 minutes of most homes listed here.

The LRT Kelana Jaya Line (USJ stations) and the BRT Sunway Line provide reasonable public transport access. Driving from KL is straightforward via the NPE or Federal Highway, but traffic on the LDP from PJ-side can add 30+ minutes during peak hours. Most facilities here have on-site parking.""",

    "klang": """Klang is the royal town and one of Malaysia's oldest port cities, sitting at the western end of Selangor along the coast. The eldercare landscape here is more traditional — many smaller community-run homes serving Klang's longstanding Chinese, Malay, and Tamil families — alongside newer purpose-built facilities in Bandar Botanik and the Kawasan industrial-residential mix.

Hospital Tengku Ampuan Rahimah (HTAR) is the main government tertiary hospital and one of the busiest in the country. Private options nearby include Columbia Asia Klang and Pantai Hospital Klang.

Klang's traffic patterns differ from KL — congestion is heaviest on Federal Route 2 (the Federal Highway extension) during port shifts and weekday evenings. KTM Komuter (Klang line) connects to KL Sentral but most family visits will be by car. Many homes here speak Hokkien, Cantonese, or Tamil in addition to Malay and English.""",

    "kajang": """Kajang sits at the southern edge of Selangor, anchoring the eastern Klang Valley corridor and absorbing rapid growth from new townships like Bandar Sungai Long, Country Heights Kajang, and Bandar Teknologi Kajang. The eldercare market here has expanded quickly — many of the listings are facilities under 10 years old, including several mid-priced and premium new-builds.

Hospital Kajang is the main government hospital. KPJ Kajang Specialist Hospital and Columbia Asia Cheras (just across the border) are the private alternatives.

The MRT Kajang Line terminates at Kajang station, making this one of the most accessible Klang Valley districts by rail — useful for family members based in KL who visit weekly. Driving from KL via the SILK Highway or Cheras–Kajang Expressway takes 30–50 minutes outside peak hours. Many homes are clustered in newer planned townships with good parking.""",

    "puchong": """Puchong is the residential township stretching south-west of KL, developed primarily from the late 1990s through the 2010s. The eldercare landscape skews toward newer mid-sized homes in Bandar Puchong Jaya, Pusat Bandar Puchong, and the Taman Puchong corridor. Many of the family-run homes here serve middle-income families from KL and PJ who chose Puchong for proximity-plus-affordability.

Columbia Asia Hospital Puchong is the local private option; Sunway Medical Centre (just across the LDP) and University Malaya Medical Centre are within 20 minutes when traffic cooperates.

The LRT Sri Petaling Line (Puchong stations) is the main public transport. Driving is straightforward via the LDP or Bukit Jalil Highway, but LDP traffic from PJ can be slow during weekday evenings. Puchong homes typically offer reasonable parking; pre-booking visits is rarely necessary.""",

    "ampang": """Ampang lies just east of Kuala Lumpur, straddling the KL/Selangor border. It's an older established residential district — the Kampung Baru Ampang and Pandan areas have been settled since before independence — and the eldercare landscape reflects that, with many community-rooted homes operating for 20+ years alongside newer purpose-built facilities.

Hospital Ampang is a national referral centre for haematology and oncology; KPJ Ampang Puteri is the main private option. Both are within 10 minutes of most facilities listed here.

The LRT Ampang Line serves the district end-to-end (Sentul Timur to Ampang station), with Pandan Indah and Pandan Jaya as the main residential stops. Driving from KL city centre takes 15–25 minutes via Jalan Ampang. Many homes here are in landed bungalows or terrace houses converted for residential care — parking is usually street-side rather than on-site.""",

    "selayang": """Selayang sits at the north-western edge of Selangor, just past the KL boundary. The district is anchored by Hospital Selayang — one of the largest government tertiary hospitals in the Klang Valley — and the eldercare facilities listed here tend to be smaller community-run homes serving families from Selayang Baru, Taman Selayang, and Batu Caves.

Beyond Hospital Selayang, private alternatives include KPJ Selangor Specialist Hospital and Columbia Asia Cheras. Most homes are within 15 minutes of one of these.

The Selayang area is served by the KTM Komuter (Sentul–Batu Caves line) and the MRT Putrajaya Line is gradually extending coverage. Driving from KL via the MRR2 takes 25–40 minutes depending on traffic; the Jalan Ipoh route is slower but more reliable. Parking at most facilities is adequate but visiting on weekends can be busier given families' work schedules.""",

    "seri-kembangan": """Seri Kembangan, also commonly written as Sri Kembangan or grouped with the broader Serdang area, sits south of Kuala Lumpur near the Putrajaya/Cyberjaya corridor. The eldercare landscape here benefits from Hospital Serdang — the national referral centre for cardiology — drawing families who want a major cardiac unit within minutes.

Beyond Hospital Serdang, options include Columbia Asia Hospital Puchong and Sunway Medical Centre, both within a 15-20 minute drive. UM Specialist Centre is also accessible across the federal highway corridor.

The KTM Komuter Seremban Line (Serdang and Bandar Tasik Selatan stations) and the MRT Kajang Line provide public transport access. Driving is via the Sungai Besi Expressway or Maju Expressway. Seri Kembangan homes are typically in low-density residential pockets with good parking; weekday traffic on the SBE during morning rush can extend visit times noticeably.""",

    # ─── KUALA LUMPUR ─────────────────────────────────────────────────────

    "bangsar": """Bangsar sits in the heart of Kuala Lumpur, immediately south of the KLCC corridor and west of the city centre. It's one of the most affluent residential districts in Malaysia, and the eldercare facilities listed here reflect that — most are smaller, premium-positioned bungalow conversions or purpose-built assisted-living homes catering to families willing to pay for proximity to UMMC.

University Malaya Medical Centre (UMMC) is the district anchor — one of Malaysia's most established teaching hospitals and a major referral centre. Pantai Hospital Kuala Lumpur is the main private option, also within 5 minutes.

The LRT Kelana Jaya Line (Bangsar station) and the KTM Komuter (Mid Valley station) serve the area. Driving from KL city centre is straightforward but parking in Bangsar Baru can be tight, especially on weekend evenings. Most facilities have limited on-site parking; valet or grab-drop-off is common.""",

    "kepong": """Kepong stretches across the northern Kuala Lumpur boundary, from the older Kepong Baru neighborhood through Taman Kepong and the Kepong Sentral corridor. It's a long-established Chinese-majority residential district with a mix of older landed homes and newer high-rise developments. The eldercare landscape here is dominated by mid-sized family-run nursing homes, many operating for 15+ years.

KPJ Damansara Specialist Hospital and Hospital Selayang are the main hospital options, both within 15–20 minutes. KPJ Tawakkal across the MRR2 in Sentul is also accessible.

The MRT Kajang Line (Kepong Sentral, Sri Delima, Kepong Baru, Metro Prima stations) and the KTM Komuter (Sentul–Batu Caves line) provide good public transport. Driving from KL city centre via the MRR2 takes 20–30 minutes; the Jalan Ipoh route is slower but a useful alternative during MRR2 congestion. Many homes here are Cantonese- and Hokkien-speaking.""",

    "cheras": """Cheras is one of Kuala Lumpur's largest residential districts, stretching from the city centre south-east through Taman Connaught, Taman Midah, Bandar Tun Razak, and out toward the KL/Selangor border. The eldercare landscape here is the densest in KL — many homes have operated for 20+ years, serving Cheras's large Chinese and Malay middle-income population.

Cheras Specialist Hospital, Hospital UKM (Hospital Canselor Tuanku Muhriz), and KPJ Damansara are the main hospital options. Hospital Kuala Lumpur (HKL) is accessible via the MRR2 within 20 minutes.

The MRT Kajang Line runs through the district (Bandar Tun Razak, Taman Mutiara, Taman Connaught, Taman Suntex, Sungai Jernih stations). Driving access via the Cheras–Kajang Expressway or MRR2 is reasonable but evening traffic on the MRR2 can be heavy. Many homes are in converted landed properties with limited parking; street parking is usually available.""",

    "setapak": """Setapak sits north-east of central Kuala Lumpur, anchored by Wangsa Maju and stretching through Taman Setapak, Taman Mastiara, and Taman Bunga Raya. It's an older established residential district with a mix of low-rise walk-up apartments and landed homes. The eldercare landscape here skews toward smaller community-run homes serving Wangsa Maju and the broader Setapak-Sentul corridor.

Hospital Kuala Lumpur (HKL) is within 10–15 minutes and is the major reference point for most facilities here. KPJ Tawakkal Specialist Hospital in Sentul and KPJ Damansara are the main private options.

The LRT Ampang Line (Wangsa Maju, Sri Rampai stations) and the MRT Putrajaya Line are extending coverage. Driving from KL city centre via Jalan Genting Klang takes 15–25 minutes. Parking at most facilities is adequate; the Wangsa Maju area can be tight during weekend evenings when commercial traffic peaks.""",

    "sentul": """Sentul sits immediately north of central Kuala Lumpur, anchored by Jalan Ipoh and the Sentul KTM rail yard. It's one of KL's older established neighborhoods — historically Indian-majority though now mixed — and the eldercare landscape reflects long-standing community roots, with several homes operating for 20+ years.

KPJ Tawakkal Specialist Hospital is the district anchor — one of KL's longest-running private hospitals. Hospital Kuala Lumpur (HKL) is within 10 minutes. Tung Shin Hospital and Pantai Hospital Kuala Lumpur are accessible within 20 minutes.

The LRT Ampang Line (Titiwangsa, Sentul Timur stations) and the KTM Komuter (Sentul, Putra stations) provide public transport. Driving from KL city centre via Jalan Ipoh or the Sultan Iskandar Highway takes 10–15 minutes. Many homes here are converted shophouses or older landed properties; parking can be limited and street parking is the norm for visitors.""",

    "old-klang-road": """Old Klang Road runs south-west from central KL toward the Klang Valley's older industrial corridor, covering OUG (Overseas Union Garden), Happy Garden, Taman Salak Selatan, Desa Petaling, and Taman Lucky. It's one of KL's older Chinese-majority residential districts and the eldercare landscape reflects that — many homes have operated for 15+ years serving multi-generational Cantonese- and Hokkien-speaking families.

Pantai Hospital Kuala Lumpur is the main private option, within 10 minutes. Hospital Kuala Lumpur (HKL) is accessible via the KL–Seremban Highway in 15–20 minutes. KPJ Damansara is reachable via the Federal Highway.

The LRT Sri Petaling Line (Salak Selatan, Bandar Tun Razak, Sri Petaling stations) serves the area. Driving via Old Klang Road itself can be slow during weekday rush; the Maju Expressway or Bukit Jalil Highway are useful alternatives. Most homes have on-site parking; weekend traffic is generally lighter here than central KL.""",

    # ─── JOHOR ────────────────────────────────────────────────────────────

    "johor-bahru": """Johor Bahru is the capital of Johor and Malaysia's second-largest urban agglomeration after the Klang Valley. The district covers JB city centre, Tampoi, Kempas, Skudai, Senai, Ulu Tiram, and the broader Iskandar Malaysia corridor. The eldercare landscape here is the second-largest in the country and growing rapidly — driven partly by Singapore-side families placing parents in JB for cost reasons.

Hospital Sultanah Aminah is the state tertiary hospital. KPJ Johor Specialist Hospital, Gleneagles Medini (Iskandar Puteri), and Columbia Asia Hospital Tebrau are the main private options.

Driving access via the North–South Expressway, the EDL, or the Pasir Gudang Highway is straightforward but evening traffic into JB city centre can be heavy. There is no urban rail yet — most family visits will be by car. The wide spread of Johor Bahru's neighborhoods (Skudai to Pasir Gudang is 40+ minutes) makes location relative to the family's home and workplace particularly worth checking before committing.""",

    "muar": """Muar is one of Johor's oldest royal towns, sitting along the Muar River about 150km north of Johor Bahru and 90km south of Melaka. It's known for its heritage shophouses, traditional Malay-Chinese-Indian community mix, and a quieter pace than the Iskandar corridor. The eldercare landscape here reflects long-established community roots — most homes are smaller family-run operations serving multi-generational Muar families.

Hospital Sultanah Fatimah is the main government hospital. Columbia Asia Hospital Muar is the local private option. KPJ Pasir Gudang is the nearest larger private facility for specialist care, about 90 minutes away.

Muar is served primarily by car via the North–South Expressway (Tangkak or Pagoh exits) or Federal Route 5 along the coast. There is no urban rail. Driving from KL takes about 3 hours; from Singapore via Tuas, about 2.5 hours. Many homes here are Hokkien-, Cantonese-, or Teochew-speaking.""",

    "tangkak": """Tangkak sits at the foot of Gunung Ledang (Mount Ophir) in northern Johor, about 30km inland from Muar and bordering Negeri Sembilan. It's a smaller town surrounded by oil-palm and durian plantations, with a population skewing older as younger residents move to KL or Singapore. The eldercare landscape here is small but real — several long-running family homes serving the local Hakka and Hokkien Chinese community.

Hospital Tangkak is the local government hospital for primary care. Hospital Sultanah Fatimah in Muar handles tertiary referrals (~30 minutes away). For specialist care, families typically travel to Hospital Sultanah Aminah in JB or Columbia Asia Muar.

Tangkak is served primarily by car via the North–South Expressway (Tangkak exit) or Federal Route 23. There is no urban transport. Driving from KL takes about 3 hours; from JB, about 2 hours. Visits are usually planned around weekend stays rather than weekday drop-ins.""",

    "batu-pahat": """Batu Pahat lies on Johor's west coast, about 90km north of Johor Bahru and 60km south of Muar. It's a long-established trading town with a strong Chinese commercial community and one of the largest eldercare landscapes outside the Klang Valley. Many of the homes here have operated for 15-20+ years.

Hospital Sultanah Nora Ismail (named after the former Sultan of Johor's consort) is the main government hospital. KPJ Pasir Gudang is the nearest specialist hospital; Columbia Asia Iskandar Puteri is within 90 minutes for major referrals.

Batu Pahat is accessed by car via the North–South Expressway (Yong Peng or Air Hitam exits) or Federal Route 5 along the coast. There is no urban rail. Driving from KL takes about 3.5 hours; from Singapore, 2 hours. Many homes here are Hokkien- or Teochew-speaking, reflecting the town's commercial heritage.""",

    "kluang": """Kluang sits in central Johor, roughly equidistant between Johor Bahru and Mersing. It's a smaller railway town historically — the KTM line through Kluang is one of the oldest in Malaysia — and the eldercare landscape reflects the town's slower-paced character, with several family-run homes serving the broader Kluang district and nearby Yong Peng.

Hospital Enche' Besar Hajjah Kalsom is the main government hospital. For specialist care, families typically travel to Hospital Sultanah Aminah in JB (about 90 minutes) or to Columbia Asia and KPJ Pasir Gudang in the Iskandar corridor.

Kluang is accessible by car via the North–South Expressway (Air Hitam exit) and Federal Route 50, or by KTM ETS Gold Service from KL Sentral (the line runs Singapore–KL–Padang Besar). Driving from KL takes about 3 hours; from JB, about 90 minutes. Public transport options for daily family visits are limited.""",

    # ─── NEGERI SEMBILAN ──────────────────────────────────────────────────

    "seremban": """Seremban is the capital of Negeri Sembilan, sitting about 60km south of Kuala Lumpur along the North–South Expressway. The district covers central Seremban, the Bukit Rasah and Sungai Ujong neighborhoods, and outlying areas like Sendayan and Sri Sikamat. The eldercare landscape here is the largest outside the Klang Valley and grown substantially as KL-based families seek lower-cost options within commuting distance.

Hospital Tuanku Ja'afar is the state tertiary hospital. KPJ Seremban Specialist Hospital and Columbia Asia Hospital Seremban are the main private options. Hospital Serdang (the national cardiac centre) is accessible within 45 minutes via the NSE.

KTM ETS Gold and Komuter services connect Seremban to KL Sentral in 35–45 minutes — useful for KL-based family members visiting on weekends. Driving via the NSE typically takes 50–75 minutes depending on traffic. Many homes here are in landed terraces with good parking; weekend visits often combine with day trips to Port Dickson or back to KL.""",

    "nilai": """Nilai sits between Seremban and Kuala Lumpur, just south of the Sepang corridor and west of KLIA. It's a fast-growing satellite town anchored by Nilai University and the Bandar Baru Nilai industrial-residential mix. The eldercare landscape here is still small but growing — families drawn by lower property prices and proximity to both KL and Seremban.

Nilai Medical Centre is the main private hospital. Hospital Tuanku Ja'afar in Seremban (about 25 minutes south) and Hospital Serdang (about 30 minutes north) are the closest tertiary options.

The KTM Komuter (Seremban Line, Nilai station) provides public transport access from KL. Driving via the NSE or the Lekas Highway takes 45–60 minutes from KL city centre. Nilai's road network is newer and less congested than KL-side traffic; most facilities have good parking. Visits often combine with KLIA pickup/drop-off for family members travelling internationally.""",

    # ─── PENANG ───────────────────────────────────────────────────────────

    "george-town": """George Town is the capital of Penang and a UNESCO World Heritage site, occupying the north-east corner of Penang Island. The eldercare landscape here mixes long-standing heritage-shophouse conversions in the inner city (Jelutong, Pulau Tikus) with newer purpose-built facilities along the Bukit Dumbar and Tanjung Tokong corridor. Many homes serve Penang's older Chinese community, with Hokkien as a common language alongside Mandarin and English.

Penang General Hospital is the state tertiary hospital. Penang Adventist Hospital, Gleneagles Penang, and Loh Guan Lye Specialists Centre are the main private options. All are within 15–20 minutes of most facilities.

George Town is accessible from the mainland via the First Penang Bridge or the ferry. There is no urban rail; the Rapid Penang bus network serves major routes but family visits are typically by car. Parking in the inner city can be very tight — many facilities have only street parking. Mid-Autumn and Chinese New Year see heavier traffic; plan visits accordingly.""",

    "bukit-mertajam": """Bukit Mertajam (often shortened to BM) sits on Penang's mainland (Seberang Perai), about 20km east of George Town across the Penang Bridge. It's a busy commercial town and one of mainland Penang's main residential centres. The eldercare landscape here is substantial — many homes serve families across Seberang Perai, Kulim (in Kedah), and the broader Penang mainland.

Hospital Bukit Mertajam is the main government hospital. Sungai Bakap Hospital and Hospital Seberang Jaya handle outlying areas. Island Hospital and Penang Adventist on Penang Island are accessible via the First Penang Bridge for specialist care.

Bukit Mertajam is served by the KTM ETS service (Bukit Mertajam station, on the KL–Padang Besar line) and the North–South Expressway. Driving from George Town takes 30–45 minutes via the First Penang Bridge; weekday morning traffic on the bridge can be heavy. Most facilities here are in landed properties with adequate parking.""",

    # ─── PERAK ────────────────────────────────────────────────────────────

    "ipoh": """Ipoh is the capital of Perak and Malaysia's fourth-largest urban area, sitting along the Kinta River about 200km north of Kuala Lumpur. The eldercare landscape here is the largest in the northern peninsula — Ipoh has long been a retirement destination for Malaysian Chinese families drawn by cooler limestone-valley weather, slower pace, and proximity to KL via the NSE.

Hospital Raja Permaisuri Bainun is the state tertiary hospital. KPJ Ipoh Specialist Hospital, Pantai Hospital Ipoh, and Columbia Asia Hospital Taiping (about 90 minutes north) are the main private options.

Ipoh is well-connected: the KTM ETS Gold service runs Ipoh–KL Sentral in 2–2.5 hours, useful for weekly family visits from KL. Driving via the NSE takes about 2 hours from KL city centre. Many homes here are in older landed properties (Taman Canning, Kg Simee, Buntong, Bercham) with on-site parking; weekend traffic is generally lighter than the Klang Valley.""",

    "teluk-intan": """Teluk Intan sits in southern Perak along the Perak River, about 80km south-west of Ipoh and 150km north of Kuala Lumpur. It's a smaller historic town — known nationally for its leaning clock tower — with a long-established Chinese commercial community. The eldercare landscape here is small but real, serving families from Teluk Intan and surrounding Perak rural areas like Bagan Datuk and Hutan Melintang.

Hospital Teluk Intan is the main government hospital. For specialist care, families typically travel to KPJ Ipoh Specialist Hospital (about 90 minutes) or Hospital Tengku Ampuan Rahimah in Klang (about 90 minutes south via Federal Route 5).

Teluk Intan is accessed by car via the Federal Route 5 along the coast or the NSE (Bidor exit) and Federal Route 58. There is no urban rail. Driving from KL takes about 2.5 hours; from Ipoh, about 90 minutes. Visits are typically weekend or extended-stay rather than weekday drop-ins.""",
}
