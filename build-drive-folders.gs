/**
 * NursingHomeGuide.my — Drive verification folder generator
 *
 * Builds the Drive folder skeleton described in
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
 *   6. Open the "Execution log" pane to see progress.
 *   7. If it times out, just click "Run" again — it resumes where it
 *      stopped. Keep running until the log says "ALL DONE".
 *
 * WHAT GETS CREATED:
 *   - A Drive folder: NursingHomeGuide-Verifications/
 *   - Subfolders: _templates/, _logs/
 *   - One <slug>/ folder per live facility (status column blank), each
 *     containing: operator-correspondence/, licence/, staffing/,
 *     pricing/, photos/
 *
 * AFTER CREATION:
 *   - Upload the four outreach templates from _research/templates/ into _templates/
 *   - Upload _logs/outreach-log.csv (header row only) into _logs/
 *   - Share the root folder read+write with the helper
 *   - Call resetProgress() to clear the resume checkpoint if you ever
 *     want a clean re-run from scratch.
 */

const MASTER_SHEET_ID = '1HpAXH9aG1O27Cvhfu4MIOa9sRYhwIL4C_WUoFfC-9qk';
const FACILITIES_GID  = 292378871;
const BATCH_SIZE      = 50;   // facilities per run — safe within 6-min limit

const ROOT_FOLDER_NAME   = 'NursingHomeGuide-Verifications';
const TOP_LEVEL_SUBFOLDERS = ['_templates', '_logs'];
const FACILITY_SUBFOLDERS  = [
  'operator-correspondence',
  'licence',
  'staffing',
  'pricing',
  'photos'
];

function buildDriveFolders() {
  const props     = PropertiesService.getScriptProperties();
  const startedAt = new Date();

  // ─── 1. Root + top-level subfolders (always fast) ─────────────────
  const root = getOrCreateFolder_(DriveApp.getRootFolder(), ROOT_FOLDER_NAME);
  TOP_LEVEL_SUBFOLDERS.forEach(name => getOrCreateFolder_(root, name));

  // ─── 2. Pull live slugs once; cache slug list in Script Properties ─
  let slugs;
  const cachedSlugs = props.getProperty('SLUGS');
  if (cachedSlugs) {
    slugs = JSON.parse(cachedSlugs);
  } else {
    slugs = loadSlugs_();
    props.setProperty('SLUGS', JSON.stringify(slugs));
  }

  // ─── 3. Resume from last checkpoint ───────────────────────────────
  const startIdx = parseInt(props.getProperty('NEXT_INDEX') || '0', 10);
  if (startIdx >= slugs.length) {
    Logger.log(summary_(root, slugs.length, 0, 0, 0, 0, 'ALL DONE — nothing left to create.'));
    props.deleteAllProperties();
    return;
  }

  const endIdx = Math.min(startIdx + BATCH_SIZE, slugs.length);
  const batch  = slugs.slice(startIdx, endIdx);

  // ─── 4. Per-facility folders + sub-folders ────────────────────────
  let createdFacility = 0, reusedFacility = 0, createdSub = 0;

  batch.forEach(slug => {
    const existed      = folderExists_(root, slug);
    const facilityDir  = getOrCreateFolder_(root, slug);
    if (existed) reusedFacility++; else createdFacility++;

    FACILITY_SUBFOLDERS.forEach(sub => {
      if (!folderExists_(facilityDir, sub)) {
        facilityDir.createFolder(sub);
        createdSub++;
      }
    });
  });

  const nextIdx    = endIdx;
  const elapsedSec = Math.round((new Date() - startedAt) / 1000);
  const done       = nextIdx >= slugs.length;

  if (done) {
    props.deleteAllProperties();
  } else {
    props.setProperty('NEXT_INDEX', String(nextIdx));
  }

  Logger.log(summary_(
    root, slugs.length, startIdx, endIdx - 1,
    createdFacility, reusedFacility, createdSub,
    elapsedSec, done
  ));
}

/** Call this to wipe the resume checkpoint and start fresh. */
function resetProgress() {
  PropertiesService.getScriptProperties().deleteAllProperties();
  Logger.log('Progress reset. Next buildDriveFolders() run starts from index 0.');
}

// ─── Helpers ─────────────────────────────────────────────────────────
function loadSlugs_() {
  const ss     = SpreadsheetApp.openById(MASTER_SHEET_ID);
  const sheet  = getSheetByGid_(ss, FACILITIES_GID);
  if (!sheet) throw new Error('Facilities tab (gid=' + FACILITIES_GID + ') not found.');

  const values    = sheet.getDataRange().getValues();
  const header    = values[0].map(h => String(h).trim().toLowerCase());
  const slugCol   = header.indexOf('slug');
  const statusCol = header.indexOf('status');
  if (slugCol === -1) throw new Error('No `slug` column on Facilities tab.');

  const slugs = [];
  for (let i = 1; i < values.length; i++) {
    const slug   = String(values[i][slugCol]   || '').trim();
    const status = statusCol === -1 ? '' : String(values[i][statusCol] || '').trim().toLowerCase();
    if (!slug) continue;
    if (status === 'unverified' || status === 'removed') continue;
    slugs.push(slug);
  }
  return slugs;
}

function getOrCreateFolder_(parent, name) {
  const it = parent.getFoldersByName(name);
  return it.hasNext() ? it.next() : parent.createFolder(name);
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

function summary_(root, total, fromIdx, toIdx, created, reused, createdSub, elapsed, done) {
  const status = done
    ? '✓ ALL DONE — all ' + total + ' facilities processed.'
    : '⏳ PARTIAL — run again to continue (next start: ' + (toIdx + 1) + ')';
  return [
    '',
    '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━',
    'DRIVE FOLDERS — NursingHomeGuide-Verifications',
    '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━',
    status,
    '',
    'Root folder:  ' + root.getUrl(),
    'Total slugs:  ' + total,
    'This batch:   facilities ' + fromIdx + '–' + toIdx,
    '  • New facility folders:  ' + created,
    '  • Already existed:       ' + reused,
    '  • New sub-folders:       ' + createdSub,
    'Elapsed: ' + elapsed + 's',
    '',
    done ? 'NEXT STEPS:\n  1. Upload templates + log CSV into Drive\n  2. Share folder with helper\n  3. Run build-intake-form.gs' : 'Just click Run again.',
    '',
    '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━',
    ''
  ].join('\n');
}
