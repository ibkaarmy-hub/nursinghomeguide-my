"""
Editorial cleanup: remove speculative ethnic / cultural inference from facility
editorials (e.g. "X-sounding name suggests it serves the X community"). Keeps
verified facts — documented org identities, name etymologies, and visit
questions are left intact; only the unsupported demographic inferences go.

Triggered by the jivi review ("Tamil-sounding names that suggest..."). All 25
regex-flagged editorials were read; the 15 below carried genuine speculation.
The other 10 were either factual (non-discrimination statements, documented
welfare-association identities) or non-ethnic care-type speculation.

Targets rows by number with a col A+B identity check (19 duplicate slugs).
Each (old -> new) is applied only if `old` is present; misses warn, don't abort.
Dry-run by default; pass --apply to write. Run from the repo root.
"""
import os, sys, csv, time

sys.path.insert(0, os.path.dirname(__file__))
from fix_audit_round import col_letter, TAB, SPREADSHEET_ID, TOKEN_PATH

sys.stdout = __import__('io').TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
CSV_PATH = 'facilities_local.csv'
APPLY = '--apply' in sys.argv
EDITORIAL_COL = 51  # `editorial_summary` (1-based)

# slug -> list of (old, new) literal replacements
EDITS = {
    'jj-blessing-care-centre-puchong': [(
        "The facility's name and multi-branch footprint suggest it targets primarily "
        "Chinese-speaking families — the Chinese name translates roughly as 'Mutual "
        "Love Elder Care and Nursing Centre' — though no detailed service menu is "
        "publicly available.",
        "The facility's Chinese name translates roughly as 'Mutual Love Elder Care and "
        "Nursing Centre', though no detailed service menu is publicly available.",
    )],
    'pusat-jagaan-lekshmy-illam-nursing-home': [
        ("The name 'Lekshmy Illam' is Tamil — 'illam' meaning home — and the "
         "contact email (Mariammahms@gmail.com) points to an Indian-managed operation "
         "likely serving the Indian community in and around Rawang, though the facility's "
         "admissions policy is not publicly stated.",
         "The name 'Lekshmy Illam' is Tamil — 'illam' meaning home. The facility's "
         "admissions policy is not publicly stated."),
        ("The Tamil-language cultural orientation may be an asset for Indian families in "
         "Rawang seeking a culturally familiar environment — confirm the primary "
         "language of caregiving when you call +60 16-448 2421.",
         "Confirm the primary language of caregiving when you call +60 16-448 2421."),
    ],
    'mona-elder-care-nursing-home-in-pandan-perdana': [(
        "the primary languages spoken by caregivers on the website — the latter is "
        "relevant for Chinese-speaking families given the Cheras/Pandan Perdana demographic.",
        "the primary languages spoken by caregivers on the website.",
    )],
    'oasis-nursing-home-klang-安康之家巴生疗养院': [(
        "The Chinese-language name (安康之家, literally 'home of health "
        "and tranquility') suggests the facility is oriented toward the Chinese-speaking "
        "community, consistent with the Kapar area's demographics, though the team includes "
        "Malay staff names indicating a mixed-language environment.",
        "The Chinese-language name (安康之家) translates literally as "
        "'home of health and tranquility'. The care team includes both Chinese and Malay "
        "staff names, indicating a mixed-language environment.",
    )],
    'emerald-nursing-care-home-usj-subang-jaya-elderly-home-梳邦再也疗养院': [(
        "The Mandarin name (梳邦再也疗养院) suggests the home "
        "likely serves the local Chinese community in Putra Heights and surrounding USJ "
        "neighbourhoods. Care scope, bed count, staffing, and JKM registration are best "
        "confirmed on a call.",
        "Care scope, bed count, staffing, and JKM registration are best confirmed on a call.",
    )],
    'vivekananda-shelter': [
        ("The name Vivekananda carries strong associations with the Indian Hindu tradition "
         "— Swami Vivekananda is a revered figure across the South Asian community in "
         "Malaysia — and the home likely serves primarily the Tamil-speaking Indian "
         "community, possibly with a Hindu cultural or religious orientation to daily life "
         "and dietary practice. With only 7 beds listed,",
         "With only 7 beds listed,"),
        ("When calling, ask about the languages spoken by staff — Tamil fluency is "
         "likely relevant for some prospective residents — as well as whether the "
         "home accepts bedridden or post-stroke residents at this small scale,",
         "When calling, ask about the languages spoken by staff, whether the home accepts "
         "bedridden or post-stroke residents at this small scale,"),
    ],
    'sri-sayang-welfare-home': [(
        "Sri Sayang is evidenced as a Chinese community-associated home: a 2014 Wesak Day "
        "visit organised by corporate volunteers, and a 2018 Chinese New Year visit by Main "
        "Place Mall that included ang pao distribution and Tai Chi, both confirm a "
        "predominantly Chinese Buddhist resident population and cultural programming aligned "
        "with that community.",
        "Sri Sayang has received documented community visits, including a 2014 Wesak Day "
        "visit organised by corporate volunteers and a 2018 Chinese New Year visit by Main "
        "Place Mall.",
    )],
    'pusat-jagaan-jivi': [
        ("Pusat Jagaan Jivi is a small residential care centre in Section 11, Petaling "
         "Jaya, reachable on +603-7931 9497, with additional contact persons listed as Ms "
         "Lucy and Mdm Avayee — Tamil-sounding names that suggest the facility likely "
         "serves, or was founded to serve, the Indian community in the Petaling Jaya area. "
         "Section 11 is a mature mixed-residential neighbourhood",
         "Pusat Jagaan Jivi is a small residential care centre in Section 11, Petaling "
         "Jaya, reachable on +603-7931 9497. Section 11 is a mature mixed-residential "
         "neighbourhood"),
        (" The Tamil connection, if accurate, may mean Jivi serves seniors who are more "
         "comfortable in Tamil or other South Indian languages, which can be a significant "
         "advantage for Indian families in PJ who want a culturally familiar placement.",
         ""),
        (" A short physical visit is the most reliable way to assess whether it suits a "
         "particular resident's needs, especially for smaller community homes where the "
         "right cultural and linguistic fit matters.",
         " A short physical visit is the most reliable way to assess whether it suits a "
         "particular resident's needs."),
    ],
    'pusat-jagaan-fortune-senior-care-centre': [(
        "The facility name suggests a Chinese-managed operation, which is typical in the "
        "Mentakab area given the town's established Chinese community. No operator website "
        "is publicly listed;",
        "No operator website is publicly listed;",
    )],
    'pusat-jagaan-kuantan-care-home-for-the-aged': [(
        "The facility name uses both Malay and English, and its Facebook page (linked as "
        "the primary contact channel) features Chinese characters in the page name, "
        "suggesting a Chinese-managed operation serving the Kuantan Chinese community.",
        "The facility name uses both Malay and English, and its Facebook page is linked as "
        "the primary contact channel.",
    )],
    'pusat-jagaan-orang-tua-berkat': [(
        "The dual name — Berkat (Malay) and En-Fu (likely Chinese dialect) — "
        "points to a multilingual, multi-ethnic community orientation consistent with the "
        "Jasin demographic profile.",
        "The home carries a dual name — Berkat and En-Fu.",
    )],
    'pusat-jagaan-pertubuhan-kebajikan-warga-emas-xiang': [
        ("is a Chinese welfare association nursing home located at",
         "is a welfare association nursing home located at"),
        (" — an area that has seen growth in care facilities serving the Chinese "
         "community.", "."),
        ("The Xiang An name (翔安) and the pertubuhan kebajikan (welfare "
         "association) designation indicate a non-profit community model,",
         "The pertubuhan kebajikan (welfare association) designation indicates a "
         "non-profit community model,"),
    ],
    'pusat-jagaan-sibu-benevolent-society': [(
        "should expect a lower monthly fee than commercial homes, a more communal living "
        "arrangement, and culturally Chinese routines, but a more limited clinical scope",
        "should expect a lower monthly fee than commercial homes and a more communal "
        "living arrangement, but a more limited clinical scope",
    )],
    'rumah-jagaan-warga-emas-jc': [(
        " and signals a Chinese-managed home serving the rural Chinese community of the "
        "Bera-Temerloh corridor", "",
    )],
    'sarawak-hun-nam-siang-tng-care-centre': [(
        " The Chinese-Malaysian community in Kuching is the primary user base.", "",
    )],
    # Not an insensitivity edit — repairs leaked JSON quoting that corrupted the
    # paragraph breaks in this editorial.
    'caring-hearts-elder-care-centre': [
        ('through research.",\n\n      "The breadth', 'through research.\n\nThe breadth'),
        ('confirmed directly with the home.",\n\n      "Visiting the home',
         'confirmed directly with the home.\n\nVisiting the home'),
    ],
}


def main():
    rows = list(csv.DictReader(open(CSV_PATH, encoding='utf-8')))
    by_row = {}
    for i, r in enumerate(rows):
        s = (r.get('slug') or '').strip()
        if s in EDITS:
            by_row.setdefault(s, (i + 2, r))  # first occurrence

    plan = []  # (row, slug, title, old_text, new_text)
    for slug, edits in EDITS.items():
        if slug not in by_row:
            print(f"  !! {slug}: not found in CSV — SKIPPED")
            continue
        row, r = by_row[slug]
        text = r.get('editorial_summary') or ''
        new = text
        applied = 0
        for old, repl in edits:
            if old in new:
                new = new.replace(old, repl, 1)
                applied += 1
            else:
                print(f"  ?? {slug} row{row}: replacement not found, skipped one edit")
        if new != text:
            plan.append((row, slug, (r.get('title') or '').strip(), text, new))
            print(f"  {slug} row{row}: {applied} edit(s)")

    print(f"\n{'APPLY' if APPLY else 'DRY-RUN'} — {len(plan)} editorials to rewrite\n")
    for row, slug, title, old, new in plan:
        print(f"--- {slug} (row {row}) ---")
        print(f"  BEFORE: {old[:300]}...")
        print(f"  AFTER : {new[:300]}...")
        print()
    if not APPLY:
        print("Dry run only. Re-run with --apply to write.")
        return

    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    svc = build('sheets', 'v4', credentials=Credentials.from_authorized_user_file(TOKEN_PATH))

    def call(req):
        for attempt in range(6):
            try:
                return req.execute()
            except HttpError as e:
                if e.resp.status == 429:
                    w = 30 * (attempt + 1)
                    print(f"     ...429, sleeping {w}s", flush=True); time.sleep(w); continue
                raise
        raise RuntimeError('repeated 429s')

    ok = 0
    for row, slug, title, old, new in plan:
        cur = call(svc.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID, range=f"'{TAB}'!A{row}:B{row}")).get('values', [['', '']])[0]
        ct, cs = (cur[0] if cur else '').strip(), (cur[1] if len(cur) > 1 else '').strip()
        if cs != slug or ct.lower() != title.lower():
            print(f"  !! row {row}: DRIFT expected ({title!r},{slug!r}) found ({ct!r},{cs!r}) — SKIPPED")
            continue
        call(svc.spreadsheets().values().update(
            spreadsheetId=SPREADSHEET_ID,
            range=f"'{TAB}'!{col_letter(EDITORIAL_COL)}{row}",
            valueInputOption='RAW', body={'values': [[new]]}))
        verify = call(svc.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID, range=f"'{TAB}'!B{row}")).get('values', [['']])[0][0].strip()
        assert verify == slug, f"POST-WRITE DRIFT row {row}"
        ok += 1
        print(f"  ok  row {row}  {slug}", flush=True)
        time.sleep(3.2)
    print(f"\nRewrote {ok}/{len(plan)} editorials.")


if __name__ == '__main__':
    main()
