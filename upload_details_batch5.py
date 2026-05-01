"""
Append Details rows for facilities researched in sessions 4-5:
EHA Golfview, Lakeview, Sunview, Kluang; Alda Homes; Agape; Blissful; Manna;
ECON Medicare; Fu Ka; Nur Ehsan; Impian Syimah Kemuncak; Lotus Ville; Golden Age Muar;
Master Nursing Daya; Sunrise/Rebina; Lee Nursing; AX; Elim; Healthlife; Parit Bilal;
Impian Syimah Kemaman; Ren Ai; Yeo JB; Hang Gelang Patah; Yang Xin
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SPREADSHEET_ID = '1HpAXH9aG1O27Cvhfu4MIOa9sRYhwIL4C_WUoFfC-9qk'
TOKEN_FILE = 'token_sheets.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
DETAILS_TAB = 'Details'

creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
service = build('sheets', 'v4', credentials=creds)
ss = service.spreadsheets()

# Read existing details to avoid duplicates
existing = ss.values().get(
    spreadsheetId=SPREADSHEET_ID, range=f"'{DETAILS_TAB}'"
).execute().get('values', [])

existing_keys = set()
for row in existing[1:]:
    if len(row) >= 3:
        existing_keys.add((row[0], row[1], row[2]))

NEW_ROWS = [

# ─── EHA GOLFVIEW ────────────────────────────────────────────────────────────
['eha-golfview-eldercare-mansion-johor-jaya-1-nursing-home-joh','policies','Operating hours','Mon–Sun 9:00am – 6:00pm (24-hr residential)'],
['eha-golfview-eldercare-mansion-johor-jaya-1-nursing-home-joh','policies','Setting','Adjacent to Daiman 18 Golf Club with golf course views'],
['eha-golfview-eldercare-mansion-johor-jaya-1-nursing-home-joh','policies','Group affiliation','EHA Eldercare Group Sdn Bhd (1478860-U)'],
['eha-golfview-eldercare-mansion-johor-jaya-1-nursing-home-joh','policies','JKM licence','Not published — verify on-site'],
['eha-golfview-eldercare-mansion-johor-jaya-1-nursing-home-joh','rooms','Assisted Living (RM/mo)','3,200'],
['eha-golfview-eldercare-mansion-johor-jaya-1-nursing-home-joh','rooms','Respite / Short-term (RM/day)','120'],
['eha-golfview-eldercare-mansion-johor-jaya-1-nursing-home-joh','rooms','Day Care (RM/mo)','1,500'],
['eha-golfview-eldercare-mansion-johor-jaya-1-nursing-home-joh','included','Meals (chef-prepared)','yes'],
['eha-golfview-eldercare-mansion-johor-jaya-1-nursing-home-joh','included','Housekeeping','yes'],
['eha-golfview-eldercare-mansion-johor-jaya-1-nursing-home-joh','included','Wi-Fi','yes'],
['eha-golfview-eldercare-mansion-johor-jaya-1-nursing-home-joh','included','Utilities','yes'],
['eha-golfview-eldercare-mansion-johor-jaya-1-nursing-home-joh','included','Vital signs monitoring','yes'],
['eha-golfview-eldercare-mansion-johor-jaya-1-nursing-home-joh','included','ADL assistance (feeding/washing/dressing/toileting)','yes'],
['eha-golfview-eldercare-mansion-johor-jaya-1-nursing-home-joh','included','Recreational activities','yes'],
['eha-golfview-eldercare-mansion-johor-jaya-1-nursing-home-joh','clinical','Special nursing procedures (NGT/catheter/suction/stoma/trach)','yes'],
['eha-golfview-eldercare-mansion-johor-jaya-1-nursing-home-joh','clinical','Wound management','yes'],
['eha-golfview-eldercare-mansion-johor-jaya-1-nursing-home-joh','clinical','Physiotherapy','yes'],
['eha-golfview-eldercare-mansion-johor-jaya-1-nursing-home-joh','clinical','Traditional Chinese Medicine (acupuncture/herbal)','yes'],
['eha-golfview-eldercare-mansion-johor-jaya-1-nursing-home-joh','clinical','Dementia care','yes'],
['eha-golfview-eldercare-mansion-johor-jaya-1-nursing-home-joh','clinical','Post-surgery recovery','yes'],
['eha-golfview-eldercare-mansion-johor-jaya-1-nursing-home-joh','staffing','24/7 caregiver cover','Yes'],
['eha-golfview-eldercare-mansion-johor-jaya-1-nursing-home-joh','outdoor','Setting','Golf course precinct with landscaped gardens'],
['eha-golfview-eldercare-mansion-johor-jaya-1-nursing-home-joh','checklist','Request JKM licence certificate number',''],
['eha-golfview-eldercare-mansion-johor-jaya-1-nursing-home-joh','checklist','Ask for room type options and current availability',''],
['eha-golfview-eldercare-mansion-johor-jaya-1-nursing-home-joh','checklist','Confirm RN overnight vs caregiver only',''],
['eha-golfview-eldercare-mansion-johor-jaya-1-nursing-home-joh','checklist','Confirm doctor visit schedule and panel doctor',''],
['eha-golfview-eldercare-mansion-johor-jaya-1-nursing-home-joh','nearby','Daiman 18 Golf Club','Adjacent'],

# ─── EHA LAKEVIEW ────────────────────────────────────────────────────────────
['eha-lakeview-eldercare-mansion-permas-branch-1-nursing-home','policies','Operating hours','Mon–Sun 9:00am – 6:00pm (24-hr residential)'],
['eha-lakeview-eldercare-mansion-permas-branch-1-nursing-home','policies','Setting','Lakeside in Taman Bayu Puteri with lake views'],
['eha-lakeview-eldercare-mansion-permas-branch-1-nursing-home','policies','Group affiliation','EHA Eldercare Group Sdn Bhd (1478860-U)'],
['eha-lakeview-eldercare-mansion-permas-branch-1-nursing-home','policies','Award','Most Beautiful Elderly Care Mansion (Facebook-announced)'],
['eha-lakeview-eldercare-mansion-permas-branch-1-nursing-home','rooms','Assisted Living (RM/mo)','3,200'],
['eha-lakeview-eldercare-mansion-permas-branch-1-nursing-home','rooms','Respite / Short-term (RM/day)','120'],
['eha-lakeview-eldercare-mansion-permas-branch-1-nursing-home','rooms','Day Care (RM/mo)','1,500'],
['eha-lakeview-eldercare-mansion-permas-branch-1-nursing-home','included','Meals (chef-prepared)','yes'],
['eha-lakeview-eldercare-mansion-permas-branch-1-nursing-home','included','Housekeeping','yes'],
['eha-lakeview-eldercare-mansion-permas-branch-1-nursing-home','included','Wi-Fi','yes'],
['eha-lakeview-eldercare-mansion-permas-branch-1-nursing-home','included','ADL assistance','yes'],
['eha-lakeview-eldercare-mansion-permas-branch-1-nursing-home','clinical','Special nursing procedures (NGT/catheter/suction/stoma/trach)','yes'],
['eha-lakeview-eldercare-mansion-permas-branch-1-nursing-home','clinical','Wound management','yes'],
['eha-lakeview-eldercare-mansion-permas-branch-1-nursing-home','clinical','Physiotherapy','yes'],
['eha-lakeview-eldercare-mansion-permas-branch-1-nursing-home','clinical','Traditional Chinese Medicine','yes'],
['eha-lakeview-eldercare-mansion-permas-branch-1-nursing-home','clinical','Dementia care','yes'],
['eha-lakeview-eldercare-mansion-permas-branch-1-nursing-home','staffing','24/7 caregiver cover','Yes'],
['eha-lakeview-eldercare-mansion-permas-branch-1-nursing-home','outdoor','Setting','Lakeside with abundant greenery'],
['eha-lakeview-eldercare-mansion-permas-branch-1-nursing-home','checklist','Request JKM licence certificate number',''],
['eha-lakeview-eldercare-mansion-permas-branch-1-nursing-home','checklist','Confirm RN overnight vs caregiver only',''],
['eha-lakeview-eldercare-mansion-permas-branch-1-nursing-home','nearby','Permas Jaya commercial hub','~2 km'],

# ─── EHA SUNVIEW ─────────────────────────────────────────────────────────────
['eha-sunview-eldercare-kempas-1-nursing-home-johor-bahru','policies','Operating hours','Mon–Sun 9:00am – 6:00pm (24-hr residential)'],
['eha-sunview-eldercare-kempas-1-nursing-home-johor-bahru','policies','Concept','Malaysia\'s first theme-styled therapeutic villa (self-claimed)'],
['eha-sunview-eldercare-kempas-1-nursing-home-johor-bahru','policies','Group affiliation','EHA Eldercare Group Sdn Bhd (1478860-U)'],
['eha-sunview-eldercare-kempas-1-nursing-home-johor-bahru','rooms','Assisted Living (RM/mo)','From 3,200'],
['eha-sunview-eldercare-kempas-1-nursing-home-johor-bahru','rooms','Respite / Short-term (RM/day)','120'],
['eha-sunview-eldercare-kempas-1-nursing-home-johor-bahru','rooms','Day Care (RM/mo)','1,500'],
['eha-sunview-eldercare-kempas-1-nursing-home-johor-bahru','included','Meals','yes'],
['eha-sunview-eldercare-kempas-1-nursing-home-johor-bahru','included','Wi-Fi','yes'],
['eha-sunview-eldercare-kempas-1-nursing-home-johor-bahru','included','ADL assistance','yes'],
['eha-sunview-eldercare-kempas-1-nursing-home-johor-bahru','clinical','Special nursing procedures','yes'],
['eha-sunview-eldercare-kempas-1-nursing-home-johor-bahru','clinical','Physiotherapy (in-house)','yes (claimed at launch)'],
['eha-sunview-eldercare-kempas-1-nursing-home-johor-bahru','clinical','Dementia care','yes'],
['eha-sunview-eldercare-kempas-1-nursing-home-johor-bahru','clinical','Fully automatic medical beds','yes'],
['eha-sunview-eldercare-kempas-1-nursing-home-johor-bahru','staffing','24/7 caregiver cover','Yes'],
['eha-sunview-eldercare-kempas-1-nursing-home-johor-bahru','checklist','Request JKM licence certificate number',''],
['eha-sunview-eldercare-kempas-1-nursing-home-johor-bahru','checklist','Verify current doctor/nurse/physio roster vs launch claims',''],
['eha-sunview-eldercare-kempas-1-nursing-home-johor-bahru','nearby','Kempas town centre','~2 km'],

# ─── EHA KLUANG ──────────────────────────────────────────────────────────────
['eha-elder-care-home-kluang-licensed-and-certified-by-govern','policies','Operating hours','Mon–Sun 9:00am – 6:00pm (24-hr residential)'],
['eha-elder-care-home-kluang-licensed-and-certified-by-govern','policies','Group affiliation','EHA Eldercare Group Sdn Bhd (1478860-U)'],
['eha-elder-care-home-kluang-licensed-and-certified-by-govern','policies','JKM licence','Claimed on Google listing — verify licence number on-site'],
['eha-elder-care-home-kluang-licensed-and-certified-by-govern','rooms','Assisted Living (RM/mo)','2,300'],
['eha-elder-care-home-kluang-licensed-and-certified-by-govern','rooms','Respite / Short-term (RM/day)','80'],
['eha-elder-care-home-kluang-licensed-and-certified-by-govern','rooms','Day Care (RM/mo)','1,300'],
['eha-elder-care-home-kluang-licensed-and-certified-by-govern','included','Meals (chef-prepared)','yes'],
['eha-elder-care-home-kluang-licensed-and-certified-by-govern','included','Wi-Fi','yes'],
['eha-elder-care-home-kluang-licensed-and-certified-by-govern','included','ADL assistance','yes'],
['eha-elder-care-home-kluang-licensed-and-certified-by-govern','clinical','Special nursing procedures','yes'],
['eha-elder-care-home-kluang-licensed-and-certified-by-govern','clinical','Physiotherapy','yes'],
['eha-elder-care-home-kluang-licensed-and-certified-by-govern','clinical','Dementia care','yes'],
['eha-elder-care-home-kluang-licensed-and-certified-by-govern','staffing','Owner-operated feel','Yes — management praised by name in reviews'],
['eha-elder-care-home-kluang-licensed-and-certified-by-govern','checklist','Request specific JKM licence number',''],
['eha-elder-care-home-kluang-licensed-and-certified-by-govern','checklist','Confirm nearest hospital with emergency capability','Kluang Hospital ~3 km'],
['eha-elder-care-home-kluang-licensed-and-certified-by-govern','nearby','Kluang Hospital (government)','~3 km estimated'],
['eha-elder-care-home-kluang-licensed-and-certified-by-govern','nearby','Johor Bahru (nearest major hospital hub)','~100 km'],

# ─── ECON MEDICARE TAMAN PERLING ─────────────────────────────────────────────
['econ-medicare-centre-nursing-home-taman-perling-branch','policies','Visiting hours','10am – 7pm daily'],
['econ-medicare-centre-nursing-home-taman-perling-branch','policies','Visitors per visit','Maximum 2'],
['econ-medicare-centre-nursing-home-taman-perling-branch','policies','Operating hours','24 hours / 7 days a week'],
['econ-medicare-centre-nursing-home-taman-perling-branch','policies','Email','tp@econhealthcare.com'],
['econ-medicare-centre-nursing-home-taman-perling-branch','policies','Phone (main)','07-234 4680'],
['econ-medicare-centre-nursing-home-taman-perling-branch','rooms','Total beds','199'],
['econ-medicare-centre-nursing-home-taman-perling-branch','rooms','Building','4 storeys + basement carpark; 57,000 sq ft purpose-built'],
['econ-medicare-centre-nursing-home-taman-perling-branch','rooms','Monthly fee range (group-wide MY)','RM 1,950 – RM 6,600'],
['econ-medicare-centre-nursing-home-taman-perling-branch','included','24-hour nursing care','yes'],
['econ-medicare-centre-nursing-home-taman-perling-branch','included','Physiotherapy','yes'],
['econ-medicare-centre-nursing-home-taman-perling-branch','included','Wound dressing','yes'],
['econ-medicare-centre-nursing-home-taman-perling-branch','included','Rehabilitation programme','yes'],
['econ-medicare-centre-nursing-home-taman-perling-branch','included','Social activities programme','yes'],
['econ-medicare-centre-nursing-home-taman-perling-branch','clinical','Dementia care','yes'],
['econ-medicare-centre-nursing-home-taman-perling-branch','clinical','Parkinson\'s care','yes'],
['econ-medicare-centre-nursing-home-taman-perling-branch','clinical','Stroke rehabilitation','yes'],
['econ-medicare-centre-nursing-home-taman-perling-branch','clinical','Palliative care','yes'],
['econ-medicare-centre-nursing-home-taman-perling-branch','clinical','Cancer care','yes'],
['econ-medicare-centre-nursing-home-taman-perling-branch','clinical','Occupational therapy','yes'],
['econ-medicare-centre-nursing-home-taman-perling-branch','clinical','Traditional Chinese Medicine / acupuncture','yes'],
['econ-medicare-centre-nursing-home-taman-perling-branch','staffing','Registered Nurses','Yes — confirmed'],
['econ-medicare-centre-nursing-home-taman-perling-branch','staffing','Physiotherapist','Yes — on-site'],
['econ-medicare-centre-nursing-home-taman-perling-branch','staffing','Occupational therapist','Yes — confirmed'],
['econ-medicare-centre-nursing-home-taman-perling-branch','services','Ambulance service','yes (in-house)'],
['econ-medicare-centre-nursing-home-taman-perling-branch','services','Home care coordination','yes'],
['econ-medicare-centre-nursing-home-taman-perling-branch','services','Short-term / respite admission','yes'],
['econ-medicare-centre-nursing-home-taman-perling-branch','nearby','Singapore Woodlands Checkpoint','~45 min drive'],
['econ-medicare-centre-nursing-home-taman-perling-branch','nearby','Johor Bahru city centre','~10–15 min drive'],
['econ-medicare-centre-nursing-home-taman-perling-branch','checklist','Ask for current room-type pricing breakdown',''],
['econ-medicare-centre-nursing-home-taman-perling-branch','checklist','Confirm JKM Private Aged Healthcare Facility licence number',''],
['econ-medicare-centre-nursing-home-taman-perling-branch','checklist','Confirm halal meal availability if required',''],
['econ-medicare-centre-nursing-home-taman-perling-branch','checklist','Note: ownership changed to TPG (US private equity) mid-2025',''],

# ─── NUR EHSAN ───────────────────────────────────────────────────────────────
['pusat-jagaan-warga-emas-nur-ehsan','policies','Address','Lot 3353, MLD 1034, No. 3, Jalan Denai 1, Kempas Baru, 81200 Johor Bahru'],
['pusat-jagaan-warga-emas-nur-ehsan','policies','Visiting hours','10am – 6pm daily'],
['pusat-jagaan-warga-emas-nur-ehsan','policies','Operator','Persatuan Kebajikan Nur Ehsan Negeri Johor (PKNENJ)'],
['pusat-jagaan-warga-emas-nur-ehsan','policies','Operating since','November 2008 (incorporated June 2009)'],
['pusat-jagaan-warga-emas-nur-ehsan','policies','Admission eligibility','Elderly Muslims without heirs; destitute; converts (muallaf); disabled'],
['pusat-jagaan-warga-emas-nur-ehsan','policies','Referral sources','JKM officers; hospital social work; MAIJ; JAIJ'],
['pusat-jagaan-warga-emas-nur-ehsan','policies','Capacity (Kempas Baru)','56 beds'],
['pusat-jagaan-warga-emas-nur-ehsan','policies','Number of branches','4 (JB, Ledang, Bukit Indah, Simpang Renggam)'],
['pusat-jagaan-warga-emas-nur-ehsan','policies','Fee model','Donation-based; families with means asked to contribute modestly'],
['pusat-jagaan-warga-emas-nur-ehsan','policies','Manager contact','Encik Saiful — 013-794 0350'],
['pusat-jagaan-warga-emas-nur-ehsan','clinical','Physiotherapy','yes'],
['pusat-jagaan-warga-emas-nur-ehsan','clinical','Regular medical examinations','yes'],
['pusat-jagaan-warga-emas-nur-ehsan','clinical','24-hour CCTV security','yes'],
['pusat-jagaan-warga-emas-nur-ehsan','checklist','Confirm current gender policy (male-only or mixed)',''],
['pusat-jagaan-warga-emas-nur-ehsan','checklist','Request JKM licence number before referral',''],
['pusat-jagaan-warga-emas-nur-ehsan','checklist','Clarify monthly contribution expected for family-placed residents',''],
['pusat-jagaan-warga-emas-nur-ehsan','nearby','Hospital Permai Johor Bahru','~10 km (referring hospital for mental health cases)'],

# ─── FU KA ───────────────────────────────────────────────────────────────────
['fu-ka-care-center','policies','Address','PTD 14521, Jalan Persiaran Kempas Baru, Kempas Baru, 81200 Johor Bahru'],
['fu-ka-care-center','policies','Email','fukanursinghome14521@gmail.com'],
['fu-ka-care-center','policies','Established','2023 (incorporated May 2023)'],
['fu-ka-care-center','clinical','24/7 nursing care','yes'],
['fu-ka-care-center','clinical','Dementia care','yes'],
['fu-ka-care-center','clinical','Physiotherapy','yes'],
['fu-ka-care-center','clinical','Specialist care','yes'],
['fu-ka-care-center','nearby','Kempas Medical Centre','~1–2 km'],
['fu-ka-care-center','checklist','Confirm JKM licence number',''],
['fu-ka-care-center','checklist','Verify halal food certification',''],
['fu-ka-care-center','checklist','Ask for monthly pricing by room type',''],
['fu-ka-care-center','checklist','Confirm RN staffing ratio day/night',''],

# ─── IMPIAN SYIMAH KEMUNCAK ──────────────────────────────────────────────────
['pusat-jagaan-impian-syimah-jalan-kemuncak','policies','Address','No 3, Lorong 3, Jalan Kemuncak 3, Kampung Nong Chik, 80000 Johor Bahru'],
['pusat-jagaan-impian-syimah-jalan-kemuncak','policies','Management','Run by Rosmi and Hasyimah (husband and wife; ~10 years)'],
['pusat-jagaan-impian-syimah-jalan-kemuncak','policies','SSM Registration','JM0635898-M'],
['pusat-jagaan-impian-syimah-jalan-kemuncak','policies','Resident capacity','~61 elderly residents (Sunway 2026 figure)'],
['pusat-jagaan-impian-syimah-jalan-kemuncak','clinical','Bedridden care','Yes — 23 bedridden residents noted across operator'],
['pusat-jagaan-impian-syimah-jalan-kemuncak','checklist','Ask to see JKM licence — confirm current and displayed on-site',''],
['pusat-jagaan-impian-syimah-jalan-kemuncak','checklist','Ask about bedridden care protocol — turning schedule, wound care',''],
['pusat-jagaan-impian-syimah-jalan-kemuncak','checklist','Note 3.5-star rating — only 11 reviews; ask other families',''],

# ─── LOTUS VILLE ─────────────────────────────────────────────────────────────
['lotus-ville-care-centre','policies','AGECOPE member','Yes'],
['lotus-ville-care-centre','policies','Act 586 licensed','Yes (Johor)'],
['lotus-ville-care-centre','policies','Operating hours','9:00am – 5:00pm daily (closed Sunday)'],
['lotus-ville-care-centre','clinical','Dementia care','yes'],
['lotus-ville-care-centre','clinical','Palliative care','yes'],
['lotus-ville-care-centre','clinical','Assisted living','yes'],
['lotus-ville-care-centre','clinical','Physiotherapy','yes'],
['lotus-ville-care-centre','checklist','Confirm address (two locations listed in aggregators)',''],
['lotus-ville-care-centre','checklist','Request JKM licence number',''],
['lotus-ville-care-centre','checklist','Request monthly pricing for shared and private rooms',''],

# ─── GOLDEN AGE MUAR ─────────────────────────────────────────────────────────
['golden-age-care-centre','policies','Address','28-10 Jalan Ria 2, Taman Ria, 84000 Muar, Johor'],
['golden-age-care-centre','policies','Visiting hours','9:00am – 6:00pm daily (Mon–Sun)'],
['golden-age-care-centre','policies','Phone (branch)','06-952 7711'],
['golden-age-care-centre','policies','JKM Rating','4-Star (Jabatan Kebajikan Masyarakat)'],
['golden-age-care-centre','policies','Operator','Golden Age Care Centre Sdn. Bhd. (Co. 1122813-K)'],
['golden-age-care-centre','policies','Other branches','Batu Pahat | Tangkak | Melaka'],
['golden-age-care-centre','clinical','Memory Care','yes'],
['golden-age-care-centre','clinical','Physiotherapy','yes'],
['golden-age-care-centre','clinical','Occupational therapy','yes'],
['golden-age-care-centre','clinical','Speech therapy','yes'],
['golden-age-care-centre','clinical','CCTV monitoring','24/7'],
['golden-age-care-centre','nearby','Hospital Pakar Sultanah Fatimah Muar','~1–2 km (same road — Jalan Salleh)'],
['golden-age-care-centre','checklist','Confirm which branch — Muar vs Batu Pahat (1.3 star poor reviews)',''],
['golden-age-care-centre','checklist','Ask about halal meal provision',''],
['golden-age-care-centre','checklist','Confirm 24/7 nursing coverage',''],

# ─── MASTER NURSING DAYA ─────────────────────────────────────────────────────
['master-nursing-care-centre-daya','policies','Operating hours','Monday–Sunday 9am–7pm'],
['master-nursing-care-centre-daya','policies','Email','mastercarecentre@gmail.com'],
['master-nursing-care-centre-daya','policies','Branch type','One of three MCC branches in JB'],
['master-nursing-care-centre-daya','services','Post-surgery care','yes'],
['master-nursing-care-centre-daya','services','Stroke rehabilitation','yes'],
['master-nursing-care-centre-daya','services','Dementia / memory care','yes'],
['master-nursing-care-centre-daya','services','Palliative & comfort care','yes'],
['master-nursing-care-centre-daya','checklist','Confirm which branch (3 branches exist)',''],
['master-nursing-care-centre-daya','checklist','Ask for JKM licence number',''],
['master-nursing-care-centre-daya','nearby','Klinik Komuniti Taman Daya','Adjacent (Jalan Nipah 13)'],

# ─── SUNRISE / REBINA ────────────────────────────────────────────────────────
['sunrise-care-centre-sdn-bhd','policies','Operator group','Rebina Sunrise Elderly Care (family-owned since 2003)'],
['sunrise-care-centre-sdn-bhd','policies','Sister facility','Rebina House Care Centre — 15 & 17 Jalan Keranji (same road)'],
['sunrise-care-centre-sdn-bhd','policies','Email','care@rebinasunrise.com'],
['sunrise-care-centre-sdn-bhd','clinical','CAPD (peritoneal dialysis)','yes'],
['sunrise-care-centre-sdn-bhd','clinical','Ryle\'s tube feeding & replacement','yes'],
['sunrise-care-centre-sdn-bhd','clinical','Phlegm suction','yes'],
['sunrise-care-centre-sdn-bhd','clinical','Nebuliser therapy','yes'],
['sunrise-care-centre-sdn-bhd','clinical','Balloon catheter management','yes'],
['sunrise-care-centre-sdn-bhd','clinical','Post-operative wound dressing','yes'],
['sunrise-care-centre-sdn-bhd','clinical','Oxygen supply','yes'],
['sunrise-care-centre-sdn-bhd','clinical','Acupuncture','yes'],
['sunrise-care-centre-sdn-bhd','clinical','Physiotherapy','yes'],
['sunrise-care-centre-sdn-bhd','clinical','Palliative / hospice care','yes'],
['sunrise-care-centre-sdn-bhd','checklist','Ask for pricing — not published online',''],
['sunrise-care-centre-sdn-bhd','checklist','Confirm JKM facility licence number',''],
['sunrise-care-centre-sdn-bhd','nearby','Rebina House Care Centre','~50 m (same operator, same road)'],

# ─── LEE NURSING ─────────────────────────────────────────────────────────────
['lee-nursing','policies','Visiting hours','9am–12pm and 4pm–7pm daily'],
['lee-nursing','policies','Short-term stays','Yes'],
['lee-nursing','included','3 meals per day + tea break','yes'],
['lee-nursing','included','Diaper changes','yes'],
['lee-nursing','included','Laundry','yes'],
['lee-nursing','included','Transport to clinic/hospital','yes'],
['lee-nursing','clinical','Ryle\'s tube / nasogastric feeding','yes'],
['lee-nursing','clinical','Tracheal suctioning','yes'],
['lee-nursing','clinical','Catheter management','yes'],
['lee-nursing','clinical','Wound care','yes'],
['lee-nursing','staffing','Registered nurse (24-hour)','yes'],
['lee-nursing','staffing','Key contact (admin)','Richard How — +60 12-777 6673'],
['lee-nursing','staffing','Key contact (nursing)','Mdm Lee — +60 19-779 6688'],
['lee-nursing','checklist','Verify current address — multiple addresses in directories','Call before visiting'],
['lee-nursing','checklist','Ask for JKM licence number',''],
['lee-nursing','checklist','Google rating 3★ from 2 reviews — ask for family references',''],
['lee-nursing','nearby','Hibiscus Serenity Care Centre (same operator)','Larkin, JB'],

# ─── AX NURSING ──────────────────────────────────────────────────────────────
['ax-nursing-home-plt','policies','Pricing information','Contact facility directly — not published online'],
['ax-nursing-home-plt','policies','Ownership structure','Private (PLT — Perkongsian Liabiliti Terhad)'],
['ax-nursing-home-plt','checklist','Verify JKM nursing home licence number',''],
['ax-nursing-home-plt','checklist','Confirm bed count and room types available',''],
['ax-nursing-home-plt','checklist','Ask for full monthly fee breakdown',''],

# ─── ELIM BATU PAHAT ─────────────────────────────────────────────────────────
['elim-nursing-home-batu-pahat','policies','Chinese name','冠冕疗养院 (Crown Nursing Home)'],
['elim-nursing-home-batu-pahat','policies','Religious character','Likely Christian faith-based — verify with facility'],
['elim-nursing-home-batu-pahat','checklist','Confirm JKM or MOH licence number',''],
['elim-nursing-home-batu-pahat','checklist','Verify church or NGO affiliation',''],
['elim-nursing-home-batu-pahat','checklist','Ask whether halal meals available for non-Christian residents',''],
['elim-nursing-home-batu-pahat','nearby','KPJ Batu Pahat Specialist Hospital','In Batu Pahat town'],

# ─── HEALTHLIFE BATU PAHAT ───────────────────────────────────────────────────
['healthlife-old-folks-home','policies','Address','No. 85-4, Jalan Haji Basir, Jalan Kluang, Taman Limpoon, 83000 Batu Pahat'],
['healthlife-old-folks-home','policies','Chinese name','爱心疗养中心 (Ai Xin Liao Yang Zhong Xin — Love Heart Care Centre)'],
['healthlife-old-folks-home','policies','Languages','Mandarin / Chinese dialects (inferred)'],
['healthlife-old-folks-home','checklist','Confirm current bed availability by phone',''],
['healthlife-old-folks-home','checklist','Request JKM registration / licence number',''],

# ─── PARIT BILAL ─────────────────────────────────────────────────────────────
['pusat-jagaan-wargatua-parit-bilal','policies','Address','POS 8A, Jalan Batu 3, Parit Bilal, 83000 Batu Pahat, Johor'],
['pusat-jagaan-wargatua-parit-bilal','policies','Location notes','Rural township ~15 km north of Batu Pahat town'],
['pusat-jagaan-wargatua-parit-bilal','checklist','Confirm ownership type (welfare society vs private business)',''],
['pusat-jagaan-wargatua-parit-bilal','checklist','Verify JKM licence / registration status',''],
['pusat-jagaan-wargatua-parit-bilal','checklist','Confirm halal food and solat facilities available',''],

# ─── IMPIAN SYIMAH KEMAMAN ───────────────────────────────────────────────────
['pusat-jagaan-impian-syimah-jalan-kemaman','policies','Address','Lot 1818, No. 7, Jalan Kemaman, Kampung Tarom, 80100 Johor Bahru'],
['pusat-jagaan-impian-syimah-jalan-kemaman','policies','Email','pusatjagaanimpiansyimah12@gmail.com'],
['pusat-jagaan-impian-syimah-jalan-kemaman','policies','SSM Registration','JM0635898-M'],
['pusat-jagaan-impian-syimah-jalan-kemaman','policies','Sister branch','Jalan Kemuncak branch at 40N Jalan Kemuncak 1 Taman Nong Chik'],
['pusat-jagaan-impian-syimah-jalan-kemaman','checklist','Confirm capacity at this branch specifically (not Kemuncak)',''],
['pusat-jagaan-impian-syimah-jalan-kemaman','checklist','Verify JKM licence number for this branch',''],

# ─── REN AI SENAI ────────────────────────────────────────────────────────────
['pusat-perjagaan-orang-tua-ren-ai','policies','Area','Senai / Kulai District — near Senai International Airport'],
['pusat-perjagaan-orang-tua-ren-ai','policies','Online presence','Facebook only (RenAiSenai); not listed in major directories'],
['pusat-perjagaan-orang-tua-ren-ai','checklist','Verify JKM registration','Check jkm.gov.my for Kulai District listing'],
['pusat-perjagaan-orang-tua-ren-ai','checklist','Confirm address before visiting — exact street not confirmed online',''],
['pusat-perjagaan-orang-tua-ren-ai','checklist','Ask about care model (nursing vs residential)',''],

# ─── YEO JB ──────────────────────────────────────────────────────────────────
['pusat-jagaan-orang-tua-yeo-jb','policies','Operator','Family-operated; proprietor surname Yeo'],
['pusat-jagaan-orang-tua-yeo-jb','checklist','Verify current address — two addresses in public data',''],
['pusat-jagaan-orang-tua-yeo-jb','checklist','Address (Waze) — Taman Bukit Kempas 81200 JB (likely current)',''],
['pusat-jagaan-orang-tua-yeo-jb','checklist','Verify JKM registration',''],

# ─── HANG GELANG PATAH ───────────────────────────────────────────────────────
['hang-nursing-home-gelang-patah-branch','policies','Location area','Gelang Patah — western JB near Second Link'],
['hang-nursing-home-gelang-patah-branch','policies','Operator','Likely family-operated; "Hang" probable family surname'],
['hang-nursing-home-gelang-patah-branch','checklist','Confirm exact address — no street address found online',''],
['hang-nursing-home-gelang-patah-branch','checklist','Verify JKM registration',''],
['hang-nursing-home-gelang-patah-branch','checklist','Ask about other branches — JKM data suggests multiple locations',''],

# ─── YANG XIN ────────────────────────────────────────────────────────────────
['yang-xin-nursing-home','policies','Chinese name','养心托管安老院 (Yǎng Xīn Tuōguǎn Ān Lǎo Yuàn)'],
['yang-xin-nursing-home','policies','Care model note','"托管" (tuoguan) = full-custody residential care (not day care)'],
['yang-xin-nursing-home','policies','Online presence','Facebook only (newer facility, high-ID profile)'],
['yang-xin-nursing-home','checklist','Confirm address before visiting — no street address found online',''],
['yang-xin-nursing-home','checklist','Verify JKM registration',''],
['yang-xin-nursing-home','checklist','Language of care — likely Mandarin/Cantonese (unverified)',''],

# ─── MANNA SINAR CAHAYA ──────────────────────────────────────────────────────
['pusat-jagaan-kebajikan-manna-sinar-cahaya','policies','Care model','Welfare home (kebajikan) — not a private nursing home'],
['pusat-jagaan-kebajikan-manna-sinar-cahaya','policies','Religious orientation','Christian (based on name etymology — unconfirmed)'],
['pusat-jagaan-kebajikan-manna-sinar-cahaya','policies','Admission route','Direct application or JKM social worker referral'],
['pusat-jagaan-kebajikan-manna-sinar-cahaya','policies','Target residents','Low-income elderly; JKM-referred cases'],
['pusat-jagaan-kebajikan-manna-sinar-cahaya','checklist','Verify JKM berdaftar certificate before admission',''],
['pusat-jagaan-kebajikan-manna-sinar-cahaya','checklist','Ask for monthly fee and subsidy eligibility',''],
['pusat-jagaan-kebajikan-manna-sinar-cahaya','checklist','Visit in person — check hygiene and staffing',''],
['pusat-jagaan-kebajikan-manna-sinar-cahaya','checklist','Confirm emergency medical protocol',''],

# ─── ALDA HOMES ──────────────────────────────────────────────────────────────
['alda-homes-eldercare','policies','Established','2016'],
['alda-homes-eldercare','policies','Operating model','Residential home (converted house — home-like environment)'],
['alda-homes-eldercare','policies','AGECOPE member','Not listed'],
['alda-homes-eldercare','policies','JKM licence','Not publicly confirmed — verify on-site'],
['alda-homes-eldercare','activities','Group exercise','Yes — evidenced on Instagram reels'],
['alda-homes-eldercare','activities','Social events','Yes — evidenced on Instagram reels'],
['alda-homes-eldercare','checklist','Verify JKM licence on-site',''],
['alda-homes-eldercare','checklist','Confirm RN staffing day + night',''],
['alda-homes-eldercare','checklist','Clarify which Facebook page is the active contact channel',''],

# ─── AGAPE CARE CENTRE ───────────────────────────────────────────────────────
['agape-care-centre','policies','Visiting hours','Unknown — contact facility'],
['agape-care-centre','policies','Religious programming','Possibly Christian — unconfirmed'],
['agape-care-centre','checklist','Verify JKM licence number with facility',''],
['agape-care-centre','checklist','Confirm whether religious programming is optional or compulsory',''],
['agape-care-centre','checklist','Ask for nurse-to-resident ratio and overnight staffing model',''],
['agape-care-centre','nearby','Kempas Medical Centre','~1.5 km'],
['agape-care-centre','nearby','Woon Ho Family Care Centre (Jalan Lurah 23)','~0.5 km'],

# ─── BLISSFUL SENIOR KLUANG ──────────────────────────────────────────────────
['blissful-senior-care-centre-licensed-and-certified-by-gover','policies','JKM registration','Act 506 — confirmed via Google listing; licence number unverified'],
['blissful-senior-care-centre-licensed-and-certified-by-gover','policies','Distance from JB','~106 km / ~1h 20m drive'],
['blissful-senior-care-centre-licensed-and-certified-by-gover','nearby','Hospital Enche\' Besar Hajjah Khalsom','~5 km (public district hospital)'],
['blissful-senior-care-centre-licensed-and-certified-by-gover','nearby','KPJ Kluang Specialist Hospital','~5 km (private, JCI-accredited)'],
['blissful-senior-care-centre-licensed-and-certified-by-gover','checklist','Confirm JKM licence number',''],
['blissful-senior-care-centre-licensed-and-certified-by-gover','checklist','Ask for pricing breakdown',''],
['blissful-senior-care-centre-licensed-and-certified-by-gover','checklist','Confirm nursing staff level — RN vs attendant',''],

]

# Filter out already-existing rows
new_rows = [r for r in NEW_ROWS if (r[0], r[1], r[2]) not in existing_keys]
skipped = len(NEW_ROWS) - len(new_rows)

print(f"Total rows to upload: {len(NEW_ROWS)}")
print(f"Already exist (skipped): {skipped}")
print(f"New rows to append: {len(new_rows)}")

if new_rows:
    next_row = len(existing) + 1
    ss.values().append(
        spreadsheetId=SPREADSHEET_ID,
        range=f"'{DETAILS_TAB}'!A{next_row}",
        valueInputOption='RAW',
        insertDataOption='INSERT_ROWS',
        body={'values': new_rows}
    ).execute()
    print(f"\n✅ Done — {len(new_rows)} Details rows appended.")
else:
    print("\nAll rows already exist — nothing to append.")
