/**
 * NursingHomeGuide.my — Drive verification folder generator
 *
 * ONE-SHOT SCRIPT. Builds the Drive folder skeleton described in
 * _research/verification-sop.md §1: a root folder, _templates/ and
 * _logs/ subfolders, and one folder per live facility (slug-named)
 * with the standard sub-folder set for evidence storage.
 *
 * HOW TO USE:
 *   1. Open script.google.com → New project
 *   2. Paste this entire file into the editor (replace the default Code.gs)
 *   3. Click "Save" (floppy icon)
 *   4. From the function dropdown at the top, choose: buildDriveFolders
 *   5. Click "Run". First run prompts for permissions — approve.
 *      (Drive + Sheets scopes; takes ~3–5 minutes for 350 facilities.)
 *   6. Open the "Execution log" pane. The root folder URL prints there.
 *
 * WHAT GETS CREATED:
 *   - A Drive folder: NursingHomeGuide-Verifications/
 *   - Subfolders: _templates/, _logs/
 *   - One <slug>/ folder per live facility (status column blank), each
 *     containing: operator-correspondence/, licence/, staffing/,
 *     pricing/, photos/
 *
 * AFTER CREATION:
 *   - Upload the four outreach templates from
 *     _research/templates/ into _templates/
 *   - Upload _logs/outreach-log.csv (header row only) into _logs/
 *   - Share the root folder read+write with the helper
 *
 * SAFE TO RE-RUN: idempotent. If a folder with the target name already
 * exists at any level, the script reuses it instead of creating a
 * duplicate. So re-running after new facilities are added to the Sheet
 * just creates the missing folders.
 */

const MASTER_SHEET_ID = '1HpAXH9aG1O27Cvhfu4MIOa9sRYhwIL4C_WUoFfC-9qk';
const FACILITIES_GID = 292378871;

const ROOT_FOLDER_NAME = 'NursingHomeGuide-Verifications';
const TOP_LEVEL_SUBFOLDERS = ['_templates', '_logs'];
const FACILITY_SUBFOLDERS = [
  'operator-correspondence',
  'licence',
  'staffing',
  'pricing',
  'photos'
];

function buildDriveFolders() {
  const startedAt = new Date();

  // ─── 1. Root + top-level subfolders ───────────────────────────────
  const root = getOrCreateFolder_(DriveApp.getRootFolder(), ROOT_FOLDER_NAME);
  TOP_LEVEL_SUBFOLDERS.forEach(name => getOrCreateFolder_(root, name));

  // ─── 2. Pull live facility slugs from master Sheet ────────────────
  const ss = SpreadsheetApp.openById(MASTER_SHEET_ID);
  const sheet = getSheetByGid_(ss, FACILITIES_GID);
  if (!sheet) {
    throw new Error('Could not find Facilities tab (gid=' + FACILITIES_GID + ') in master Sheet.');
  }

  const values = sheet.getDataRange().getValues();
  const header = values[0].map(h => String(h).trim().toLowerCase());
  const slugCol = header.indexOf('slug');
  const statusCol = header.indexOf('status');
  if (slugCol === -1) {
    throw new Error('No `slug` column on Facilities tab.');
  }

  const slugs = [];
  for (let i = 1; i < values.length; i++) {
    const slug = String(values[i][slugCol] || '').trim();
    const status = statusCol === -1 ? '' : String(values[i][statusCol] || '').trim().toLowerCase();
    if (!slug) continue;
    if (status === 'unverified' || status === 'removed') continue;
    slugs.push(slug);
  }

  // ─── 3. Per-facility folders + sub-folders ────────────────────────
  let createdFacility = 0;
  let reusedFacility = 0;
  let createdSub = 0;

  slugs.forEach(slug => {
    const before = folderExists_(root, slug);
    const facilityFolder = getOrCreateFolder_(root, slug);
    if (before) reusedFacility++; else createdFacility++;

    FACILITY_SUBFOLDERS.forEach(sub => {
      if (!folderExists_(facilityFolder, sub)) {
        facilityFolder.createFolder(sub);
        createdSub++;
      }
    });
  });

  const elapsedSec = Math.round((new Date() - startedAt) / 1000);

  // ─── Output ───────────────────────────────────────────────────────
  const log = [
    '',
    '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━',
    'DRIVE FOLDERS BUILT — NursingHomeGuide-Verifications',
    '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━',
    'Root folder URL:',
    '  ' + root.getUrl(),
    '',
    'Live facilities processed:    ' + slugs.length,
    '  • New facility folders:     ' + createdFacility,
    '  • Reused (already existed): ' + reusedFacility,
    '  • New sub-folders created:  ' + createdSub,
    '',
    'Elapsed: ' + elapsedSec + 's',
    '',
    'NEXT STEPS:',
    '  1. Upload the four templates from _research/templates/ into',
    '     _templates/ (operator-outreach-whatsapp.md, -email.md,',
    '     -followup-reminder.md, -decline-acknowledgment.md)',
    '  2. Upload _logs/outreach-log.csv (header row) into _logs/',
    '  3. Share root folder read+write with the helper',
    '  4. Walk the helper through _research/helper-onboarding.md',
    '',
    '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━',
    ''
  ].join('\n');
  Logger.log(log);
}

// ─── Helpers ────────────────────────────────────────────────────────
function getOrCreateFolder_(parent, name) {
  const it = parent.getFoldersByName(name);
  if (it.hasNext()) return it.next();
  return parent.createFolder(name);
}

function folderExists_(parent, name) {
  return parent.getFoldersByName(name).hasNext();
}

function getSheetByGid_(ss, gid) {
  const sheets = ss.getSheets();
  for (let i = 0; i < sheets.length; i++) {
    if (sheets[i].getSheetId() === gid) return sheets[i];
  }
  return null;
}
