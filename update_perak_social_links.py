"""
update_perak_social_links.py
For each of the 10 Perak facilities with editorials:
  1. Update column F (website) in Facilities tab
  2. Update column Z (facebook) in Facilities tab
  3. Append Details tab social section rows
  4. Re-upload editorials with social media mention added
"""

import csv, io, sys, time, urllib.request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

sys.stdout.reconfigure(encoding='utf-8')

SPREADSHEET_ID = '1HpAXH9aG1O27Cvhfu4MIOa9sRYhwIL4C_WUoFfC-9qk'
TOKEN_PATH     = r'C:\Users\ibkaa\nursinghomeguide-my\Nursing Home Guide Malaysia\token_sheets.json'
TAB            = 'google-sheets-facilities.csv'

CSV_URL = (
    'https://docs.google.com/spreadsheets/d/e/'
    '2PACX-1vQ4_BgHIjnlgmITzjyUuGDpgpNzPL7MfjOY2069i0PtbVbXSxIAJk1tmBejwNo8aBBeLuRi62szF2sh'
    '/pub?gid=292378871&single=true&output=csv'
)

# Verified and cleaned social/web data per facility
FACILITY_DATA = {
    'my-place-convalescent-home-care-centre': {
        'website':  'http://www.johnsonresidence.com.my/',
        'facebook': 'https://www.facebook.com/myplacecarecentre',
        'instagram': None,
    },
    'd-palace-care-centre': {
        'website':  'https://dpalacenursing.com/',
        'facebook': 'https://www.facebook.com/100049058575717',
        'instagram': None,
    },
    'dr-thomas-care-centre': {
        'website':  'https://drthomascarecentre.com/',
        # Cleaned from video URL — base page is /drthomas.carecentre
        'facebook': 'https://www.facebook.com/drthomas.carecentre',
        'instagram': None,
    },
    'ig-care-centre': {
        'website':  'http://igcare.com.my/',
        'facebook': 'https://www.facebook.com/igcareipoh',
        'instagram': None,
    },
    'pusat-jagaan-mesra-intan': {
        'website':  'https://www.pusatjagaanmesraintan.com/',
        # Cleaned from video URL — base page is /MesraLiving
        'facebook': 'https://www.facebook.com/MesraLiving',
        'instagram': None,
    },
    'pusat-jagaan-qaseh-murni': {
        'website':  'https://pusatjagaanqasehmurni.wordpress.com/',
        'facebook': 'https://www.facebook.com/p/Pusat-Jagaan-Qaseh-Murni-PJQM-61559010767489',
        'instagram': None,
    },
    'pusat-jagaan-rumah-orang-orang-tua-pkk-simee': {
        'website':  'http://www.kgsimeehome.com/',
        'facebook': 'https://www.facebook.com/p/Pusat-Jagaan-Rumah-Orang-Orang-Tua-PKK-Simee-100064488590548',
        'instagram': None,
    },
    'pusat-jagaan-yayasan-teratai': {
        'website':  'https://www.yayasanteratai.org.my/',
        'facebook': None,   # photo.php is invalid; no valid page found
        'instagram': None,
    },
    'starshine-care-centre': {
        'website':  'https://www.starshinecare.com/',
        # Page ID extracted from post URL
        'facebook': 'https://www.facebook.com/61558588282494',
        'instagram': None,
    },
    'the-salvation-army-perak-home-for-the-aged-care-ce': {
        'website':  'https://www.salvationarmy.org.my/',
        # National Malaysia page — no Perak-specific page found
        'facebook': 'https://www.facebook.com/SalvationArmyMalaysia',
        'instagram': None,
    },
}

# Full editorials with social links woven into paragraph 3
EDITORIALS = {
    'my-place-convalescent-home-care-centre': """JR My Place Care Centre is the Ipoh branch of Johnson Residence, a Malaysian care chain operating homes across Kuala Lumpur, Penang, Melaka, Pahang, and Johor. The Perak facility is organised around two residential areas — Garden Terrace and Garden Tower — both set within landscaped gardens in northern Ipoh. The Johnson Residence group's positioning is quality care at affordable prices, with a multilingual team serving residents in English and Mandarin.

Care at JR My Place covers the daily essentials — personal hygiene, laundry, tailored meals, and organised activities — alongside more clinical needs: 24-hour nursing, post-surgery recovery, physiotherapy, medication management, and scheduled hospital transport (additional charge). In-house care staff are trained in vital signs monitoring, repositioning, hand hygiene, and basic life support, supported by visiting geriatric specialists. The facility holds JKM registration A/PJB WT 054/2022.

Families have left 32 Google reviews averaging 4.6 stars, with comments consistently praising staff patience, cleanliness, and proactive communication with family members. Pricing is not published; contact the Ipoh branch directly on WhatsApp (+6017-449 6008) or through the Johnson Residence website at [johnsonresidence.com.my](http://www.johnsonresidence.com.my/) to request a quote. The centre is also active on Facebook at [facebook.com/myplacecarecentre](https://www.facebook.com/myplacecarecentre).

**What to ask on visit:**
- What is the monthly fee for shared vs private rooms, and what is included?
- What is current bed availability and the typical wait time for admission?
- How often does the visiting geriatric specialist attend, and can family be notified of visit findings?
- What post-surgery physiotherapy schedule is available?
- When was the last JKM inspection and can you share the result?""",

    'd-palace-care-centre': """D Palace Care Centre is a nursing home in Bandar Baru Sri Klebang, Ipoh, founded by Ms. C.P. Premalatha Chellapa — a registered nurse who holds a Master's in Education from Universiti Sains Malaysia and an Advanced Diploma in Palliative Care from Nanyang Polytechnic in Singapore. That combined clinical and academic background defines what D Palace is: a care-and-teaching centre where local university students complete clinical placements alongside residents who need round-the-clock nursing. The centre operates under the motto "We Treat Our Residents With Dignity."

Care at D Palace spans a wide clinical range — 24-hour nursing, assisted living, elderly care, palliative care for both cancer and non-cancer conditions, dementia and Parkinson's support, stroke and neurological care, physiotherapy, and day care. The operator emphasises personalised care plans for each resident and a home-like atmosphere. Staff are multilingual, serving in English, Bahasa Malaysia, and Chinese. The centre holds two JKM licences (A/PJB WT 063/2021 and A/PJB WT 031/2023), indicating it operates from more than one registered premises.

Pricing is not published. Contact the admissions team on +6016-555 4935 or +6016-444 3032. More information about services is available at [dpalacenursing.com](https://dpalacenursing.com/) and on the centre's Facebook page at [facebook.com/DPalaceCare](https://www.facebook.com/100049058575717).

**What to ask on visit:**
- What is the monthly fee for long-term residential vs. day care, and what does it include?
- How many beds and what is the current occupancy?
- What palliative protocols are in place for cancer patients and end-of-life care?
- Is there a dedicated area for dementia residents with secure access?
- When was the last JKM inspection and can you share the result?""",

    'dr-thomas-care-centre': """Dr Thomas Care Centre is an independent nursing home in Taman Pari, Ipoh, founded and run by Dr Thomas Arul — a physician with more than 40 years in medicine and over two decades operating nursing homes. The centre is located at 24 Jalan Labrooy, 30100 Ipoh, set within gardens and green space in a quiet residential neighbourhood. This is not a chain; it is an owner-operated facility where the founding doctor remains directly involved in resident care, conducting assessments in person.

Services span a wide range of complexity: wound care and management, stroke rehabilitation, general elderly care, palliative care, physiotherapy, post-hospitalisation recovery, day care, and specialised care for residents with higher clinical needs. Nursing cover is available 24/7. Google reviewers specifically note Dr Thomas's hands-on approach to assessing residents and the nursing team's attentiveness, with several mentioning faster-than-expected recovery for post-hospitalisation admissions. The garden-surrounded grounds are a recurring feature of positive reviews. The centre holds JKM licence A/PJB WT 045/2021.

Pricing is not published. Contact via email (contact@drthomascarecentre.com) or phone (+6012-581 9551). Visit the centre's website at [drthomascarecentre.com](https://drthomascarecentre.com/) for service details, and follow their Facebook page at [facebook.com/drthomas.carecentre](https://www.facebook.com/drthomas.carecentre) for resident activities and updates.

**What to ask on visit:**
- How often does Dr Thomas personally assess residents, and how is clinical deterioration escalated?
- What wound care is available on-site vs. requiring hospital referral?
- For stroke rehabilitation, is there a resident physiotherapist or do they visit on a schedule?
- What is the monthly cost for long-term care vs. short-stay post-hospitalisation?
- When was the last JKM inspection and can you see the result?""",

    'ig-care-centre': """IG Care Centre has operated in Ipoh since 2010, making it one of the longer-established private care groups in Perak. The group runs three facilities in the city: IGC at Ipoh Garden (the flagship, located beside Pantai Hospital Ipoh), Blissful Care at Gunung Rapat (a quieter setting with mountain views), and True Happiness Nursing Home at Polo Ground near the Perak Turf Club. Each site has a distinct character, with care delivered by qualified medical doctors and nurses across all three locations. IG Care holds JKM licence A/PJB WT 020/2020.

Services across the IG Care group include long-term residential care, short-term respite stays, day care, and caregiver training programmes — a relatively rare offering that suggests investment in the wider care sector, not just its own facilities. The flagship IGC location benefits from immediate proximity to Pantai Hospital Ipoh, which is relevant for residents with conditions that may require regular specialist visits or emergency access. Visiting hours vary by site: IGC accepts visitors from 9am to 8pm daily, while Blissful Care and True Happiness run to 6pm.

Pricing is not published. The admissions team can be reached via WhatsApp at +6012-694 2882. Full details on all three Ipoh locations are available at [igcare.com.my](http://igcare.com.my/), and the centre posts resident activities and updates on Facebook at [facebook.com/igcareipoh](https://www.facebook.com/igcareipoh).

**What to ask on visit:**
- Which of the three sites has current availability, and what are the differences in care level between them?
- What is the monthly fee and what does it include at each location?
- For the Ipoh Garden flagship, how does proximity to Pantai Hospital work in practice — formal referral or informal?
- How many nursing staff are on duty overnight at each site?
- When was the last JKM inspection and can you see the result?""",

    'pusat-jagaan-mesra-intan': """Pusat Jagaan Mesra Intan was established in Ipoh in 2012 by Ms. Chew Bee Teen, a registered nurse and midwife specialising in palliative and geriatric care, together with co-founder Mr. Inderjeet Singh. The facility sits within a green, elevated setting with mountain views, positioned within reach of four major hospitals: Hospital Raja Permaisuri Bainun, Fatimah Hospital, Pantai Hospital Ipoh, and KPJ Ipoh Specialist Hospital. That hospital proximity is a practical consideration — clinical events that exceed the home's on-site capabilities can be escalated quickly. The centre operates from two JKM-registered premises (A/PJB WT 015/2019 and A/PJB WT 049/2024).

Services focus on the post-acute spectrum: post-surgery recovery, post-stroke care, and day care alongside longer-term inpatient stays. Nursing is delivered by professionally trained registered nurses and caregivers. The centre emphasises emotional and social wellbeing alongside physical care, with the team mostly multilingual — English, Bahasa Malaysia, and Chinese are spoken. Resident testimonials mention cleanliness, good food, and attentive personalised care.

Pricing is not published. Contact the centre via email at indichew@pusatjagaanmesraintan.com or by phone (+6019-511 2242). More information is available at [pusatjagaanmesraintan.com](https://www.pusatjagaanmesraintan.com/) and on the centre's Facebook page at [facebook.com/MesraLiving](https://www.facebook.com/MesraLiving).

**What to ask on visit:**
- What is the monthly fee for post-surgery short stays vs. long-term residential care?
- What is the bed count at each registered location and what is the current availability?
- How is post-stroke rehabilitation structured — physiotherapy on-site or via visiting therapist?
- How are family members informed of changes in a resident's condition?
- When was the last JKM inspection and can you share the result?""",

    'pusat-jagaan-qaseh-murni': """Pusat Jagaan Qaseh Murni is a nursing home in Lumut, on the western coast of Perak, serving the Manjung district. The centre is located at No 223, Persiaran Venice Sutera 2, Desa Manjung Raya, 32200 Lumut — within reach of four hospitals: Hospital Seri Manjung, Pantai Hospital Manjung, KPJ Seri Manjung Specialist Hospital, and the military hospital 96 HAT. That cluster of medical facilities makes this a practical option for residents who anticipate regular specialist visits or may need emergency care. Qaseh Murni is registered with five agencies — JKM, KKM, SSM, MPM, and BOMBA — and holds JKM licence A/PJB WE 012/2025.

Care at Qaseh Murni includes 24-hour nursing with specialist doctor oversight, flexible stay options from hourly to permanent residence, and post-treatment elderly care. The centre runs a community programme called "Sahabat Senja" (Sunset Friends) — an adopted elderly initiative that connects residents with community support outside the home. The centre maintains an active online presence with promotional pricing available for new clients, though no figures are published.

Contact numbers: +60 12-547 9544, +60 19-220 6449, or +60 5-689 3544. Email: pjqasehmurni@gmail.com. More information is available at [pusatjagaanqasehmurni.wordpress.com](https://pusatjagaanqasehmurni.wordpress.com/) and on the centre's Facebook page at [facebook.com/PusatJagaanQasehMurni](https://www.facebook.com/p/Pusat-Jagaan-Qaseh-Murni-PJQM-61559010767489). The centre also posts on Instagram and TikTok under the PJQM account.

**What to ask on visit:**
- What are the monthly fees for different stay types — hourly, day care, and permanent residential?
- How does the Sahabat Senja adopted elderly programme work in practice?
- What level of specialist doctor involvement is provided on-site vs. hospital referrals?
- What is the bed count and current availability?
- When was the last JKM inspection and can you see the result?""",

    'pusat-jagaan-rumah-orang-orang-tua-pkk-simee': """Pusat Jagaan Rumah Orang-Orang Tua (PKK) Simee is a charitable home for the aged in the Simee area of Ipoh. Unlike most private nursing homes, PKK Simee operates as a welfare centre under the PKK (Pusat Khidmat Komuniti) framework, sustained by donations from individuals and corporations rather than market-rate fees. The centre is open every day including public holidays from 8:30am to 5:30pm, and welcomes organised group visits for birthday celebrations and CSR programmes. Families and corporations who donate RM5,000 or more are recognised on a Donor Recognition Wall; contributions of RM100,000 and above are featured on the Honorary Donor Board. The centre holds JKM licence A/PJB WT 046/2023.

Residents at PKK Simee receive daily care, meals, recreation, and essential provisions. The centre publishes a wishlist of in-kind donations and runs a volunteer programme open to individuals and groups — a community-integrated model that distinguishes it from private commercial homes.

As a charitable home, admission criteria, fees (if any), and waiting lists are not published on the website. Contact the centre directly at 05-545 2449 or via email at kgsimeehome@gmail.com. Further details are available at [kgsimeehome.com](http://www.kgsimeehome.com/) and on the centre's Facebook page at [facebook.com/PKKSimee](https://www.facebook.com/p/Pusat-Jagaan-Rumah-Orang-Orang-Tua-PKK-Simee-100064488590548).

**What to ask on visit:**
- What are the admission criteria, and is there a waiting list?
- Are there fees for residents, or is placement fully subsidised? What financial assessment applies?
- What level of nursing care is available for residents with medical or high-dependency needs?
- Are there specific capabilities for residents with dementia or limited mobility?
- When was the last JKM inspection and can you see the result?""",

    'pusat-jagaan-yayasan-teratai': """Pusat Jagaan Yayasan Teratai is an aged care home operated by Yayasan Teratai, an Ipoh-based charitable limited liability company incorporated in April 2001. The foundation's registered office is at 16 Jalan Raja Dihilir, 30350 Ipoh, and it also engages in education care alongside its aged care work. As a charitable entity with over two decades of presence in Ipoh, Yayasan Teratai predates most of the private nursing home operators that have entered the Perak market in recent years. The home holds JKM licence A/PJB WT 041/2022.

The foundation's website is minimal in public-facing detail — most operational information requires a login — which makes it difficult to assess the home's care model, capacity, or staffing from the outside. What is confirmed: Yayasan Teratai operates across health and aged care and has maintained JKM registration under the current licence cycle. The home's coordinates place it in central Ipoh.

Given the limited information available online, families considering Yayasan Teratai should visit in person to understand the home's current capacity, care model, and fee structure. Contact the home by phone (+6016-534 5679) or visit the foundation's website at [yayasanteratai.org.my](https://www.yayasanteratai.org.my/). Longer-established charitable homes in Malaysia sometimes maintain waiting lists for subsidised places.

**What to ask on visit:**
- Is this a subsidised charitable home, a fee-paying private home, or a mix?
- What is the bed count and current availability?
- What level of nursing care is provided — is there registered nursing cover overnight?
- Are there specific capabilities for residents with dementia, stroke, or high-dependency needs?
- When was the last JKM inspection and can you see the result?""",

    'starshine-care-centre': """Starshine Care Centre is a nursing home in Taman Sin Lok, central Ipoh, operating from No 65, Jalan Sin Lok, 30100 Ipoh. The centre offers a broad range of care including 24-hour nursing, doctor visits, physiotherapy, day care, assisted living, rehabilitation, post-hospitalisation recovery, and longer-term medical nursing and retirement care for residents with chronic conditions. Physical comforts are well specified: all rooms are air-conditioned and furnished, with 24-hour CCTV monitoring, a nurse calling system, WiFi, and Astro TV throughout. The centre holds two JKM licences (A/PJB WT 025/2024 and A/PJB WT 057/2024).

Starshine's service list is one of the more comprehensive among Ipoh's smaller nursing homes, covering both rehabilitation-focused short stays and longer chronic care needs. The presence of a doctor visit service — rather than just nursing cover — is notable for a centre of this size, as it allows medical review of residents without requiring repeated hospital trips. The dual JKM licences suggest Starshine operates from more than one registered site in the Ipoh area.

Pricing is not published. Contact the centre on 016-560 0317 or 05-506 3112, or by email at info@starshinecare.com. Service details are available at [starshinecare.com](https://www.starshinecare.com/) and the centre's Facebook page at [facebook.com/StarshineCareCentre](https://www.facebook.com/61558588282494). Families should confirm which physical location a potential resident would be placed at.

**What to ask on visit:**
- What is the monthly fee structure for residential care, day care, and short-stay rehabilitation?
- How frequently does the visiting doctor attend, and how is urgent escalation handled?
- Which of the two registered locations would my family member be placed in?
- What is current bed availability and the typical wait time?
- When was the last JKM inspection and can you share the result?""",

    'the-salvation-army-perak-home-for-the-aged-care-ce': """The Salvation Army Perak Home for the Aged is one of more than 20 care facilities operated by The Salvation Army Malaysia, a Christian charitable organisation with a longstanding presence in Malaysian welfare services. The Perak home is part of a national network providing residential care, meals, and daily support for older adults who need assistance with daily living. The Salvation Army's backing of institutional credibility and charitable governance gives this home an accountability structure that smaller private operators cannot replicate. The home holds JKM licence A/PJB WT 009/2023.

Specific operational details for the Perak home — its address, capacity, staffing, and fee structure — are not published on the Salvation Army Malaysia website, which is consistent with charitable welfare homes that operate with subsidised or means-tested admission rather than market rates. The home's coordinates place it in the Ipoh area. As a charitable entity, fees may be means-tested or subsidised depending on the resident's financial circumstances, and intake decisions typically involve an assessment of both care needs and financial situation.

Families interested in the Salvation Army Perak Home should contact the home directly at +605-526 2108. The national organisation's website at [salvationarmy.org.my](https://www.salvationarmy.org.my/) provides background on the broader network, and the Malaysia-wide Facebook page at [facebook.com/SalvationArmyMalaysia](https://www.facebook.com/SalvationArmyMalaysia) posts news and updates. A site visit to the Perak home is the most reliable way to understand current capacity and the admission process.

**What to ask on visit:**
- What is the fee structure — is it means-tested, subsidised, or a fixed monthly rate?
- What level of nursing care is provided, and is there registered nursing cover at night?
- What is the current capacity and is there a waiting list?
- What care needs can the home accommodate — is there support for dementia or high-dependency residents?
- When was the last JKM inspection and can you see the result?""",
}


def fetch_csv():
    print('Fetching published CSV...', flush=True)
    with urllib.request.urlopen(CSV_URL) as r:
        return r.read().decode('utf-8')


def sheet_write(svc, range_str, value, retries=3):
    for attempt in range(retries):
        try:
            svc.spreadsheets().values().update(
                spreadsheetId=SPREADSHEET_ID,
                range=range_str,
                valueInputOption='RAW',
                body={'values': [[value]]}
            ).execute()
            return True
        except Exception as e:
            print(f'  retry {attempt+1}: {e}', flush=True)
            time.sleep(10)
    return False


def main():
    data = fetch_csv()
    reader = csv.DictReader(io.StringIO(data))
    headers = list(reader.fieldnames)

    def col_letter(name):
        idx = headers.index(name) + 1  # 1-based
        # Convert 1-based index to spreadsheet column letter
        result = ''
        while idx > 0:
            idx, r = divmod(idx - 1, 26)
            result = chr(65 + r) + result
        return result

    col_web  = col_letter('website')
    col_fb   = col_letter('facebook')
    col_edit = col_letter('editorial_summary')
    print(f'Columns: website={col_web}, facebook={col_fb}, editorial={col_edit}')

    # Gather rows for each target slug
    slug_rows = {}
    for i, row in enumerate(reader, start=2):
        slug = row.get('slug', '').strip()
        if slug in FACILITY_DATA:
            slug_rows.setdefault(slug, []).append({
                'row': i,
                'title': row.get('title', '').strip(),
                'cur_website': row.get('website', '').strip(),
                'cur_facebook': row.get('facebook', '').strip(),
            })

    print(f'\nFound {len(slug_rows)} slugs in sheet')

    creds = Credentials.from_authorized_user_file(
        TOKEN_PATH, ['https://www.googleapis.com/auth/spreadsheets']
    )
    svc = build('sheets', 'v4', credentials=creds)

    details_rows = []
    updated_web = updated_fb = updated_edit = 0
    skipped_web = skipped_fb = 0

    for slug, row_list in sorted(slug_rows.items()):
        fdata = FACILITY_DATA[slug]
        editorial = EDITORIALS[slug]
        seen_details = set()  # avoid duplicate Details rows for same slug

        for r in row_list:
            row_n = r['row']
            title = r['title']
            print(f'\n{slug} row {row_n} ({title[:40]}):')

            # --- Website column ---
            if fdata['website']:
                if not r['cur_website']:
                    ok = sheet_write(svc, f"'{TAB}'!{col_web}{row_n}", fdata['website'])
                    print(f'  website → {fdata["website"][:50]}  {"OK" if ok else "FAILED"}')
                    if ok: updated_web += 1
                else:
                    print(f'  website already set: {r["cur_website"][:50]}')
                    skipped_web += 1
            time.sleep(0.4)

            # --- Facebook column ---
            if fdata['facebook']:
                if not r['cur_facebook']:
                    ok = sheet_write(svc, f"'{TAB}'!{col_fb}{row_n}", fdata['facebook'])
                    print(f'  facebook → {fdata["facebook"][:60]}  {"OK" if ok else "FAILED"}')
                    if ok: updated_fb += 1
                else:
                    print(f'  facebook already set: {r["cur_facebook"][:60]}')
                    skipped_fb += 1
            time.sleep(0.4)

            # --- Editorial ---
            ok = sheet_write(svc, f"'{TAB}'!{col_edit}{row_n}", editorial)
            print(f'  editorial → {"OK" if ok else "FAILED"} ({len(editorial)} chars)')
            if ok: updated_edit += 1
            time.sleep(0.8)

        # --- Details tab rows (once per slug, not per row) ---
        if slug not in seen_details:
            seen_details.add(slug)
            if fdata['website']:
                details_rows.append([slug, 'social', 'Website', fdata['website']])
            if fdata['facebook']:
                details_rows.append([slug, 'social', 'Facebook', fdata['facebook']])
            if fdata.get('instagram'):
                details_rows.append([slug, 'social', 'Instagram', fdata['instagram']])

    # --- Batch append to Details tab ---
    if details_rows:
        print(f'\nAppending {len(details_rows)} rows to Details tab...')

        # First, read existing Details rows to avoid duplicates
        existing = svc.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID,
            range="'Details'!A:D"
        ).execute().get('values', [])
        existing_keys = {(r[0], r[1], r[2]) for r in existing if len(r) >= 3}

        new_rows = [r for r in details_rows
                    if (r[0], r[1], r[2]) not in existing_keys]
        dup_rows = len(details_rows) - len(new_rows)
        print(f'  Skipping {dup_rows} duplicates, appending {len(new_rows)} new rows')

        if new_rows:
            svc.spreadsheets().values().append(
                spreadsheetId=SPREADSHEET_ID,
                range="'Details'!A:D",
                valueInputOption='RAW',
                insertDataOption='INSERT_ROWS',
                body={'values': new_rows}
            ).execute()
            print('  Details append OK')

    print(f'\n{"="*60}')
    print(f'PERAK SOCIAL LINKS UPDATE COMPLETE')
    print(f'  Website col updated:  {updated_web}  (skipped/existing: {skipped_web})')
    print(f'  Facebook col updated: {updated_fb}  (skipped/existing: {skipped_fb})')
    print(f'  Editorials updated:   {updated_edit}')
    print(f'  Details rows appended: {len(new_rows) if details_rows else 0}')


if __name__ == '__main__':
    main()
