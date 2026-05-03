/**
 * NursingHomeGuide.my — Verification schema upgrade
 *
 * ONE-SHOT SCRIPT. Adds the 10 verification columns from
 * _research/verification-sop.md §8 to the Facilities tab, then sets
 * sensible defaults on all live rows (status = blank).
 *
 * HOW TO USE:
 *   1. Open script.google.com → New project
 *   2. Name it: NHG — Verification schema upgrade
 *   3. Paste this entire file into the editor (replace the default Code.gs)
 *   4. Click "Save"
 *   5. From the function dropdown, choose: addVerificationColumns
 *   6. Click "Run". Approve permissions on first run.
 *   7. Check the execution log for a summary.
 *
 * WHAT IT DOES:
 *   - Appends 10 columns to the right of the Facilities tab header row
 *   - Sets defaults on all live rows (status column is blank):
 *       verification_tier      = 1
 *       outreach_status        = pending
 *       tier_2_review_pending  = FALSE
 *       licence_expiry_warning = FALSE
 *       all others             = blank
 *
 * SAFE TO RE-RUN: checks for existing columns before adding. If a column
 * already exists it is skipped — no duplicates created.
 */

const MASTER_SHEET_ID  = '1HpAXH9aG1O27Cvhfu4MIOa9sRYhwIL4C_WUoFfC-9qk';
const FACILITIES_GID   = 292378871;

const VERIFICATION_COLUMNS = [
  { name: 'verification_tier',      default: '1'       },
  { name: 'last_verified_on',       default: ''        },
  { name: 'verified_by',            default: ''        },
  { name: 'evidence_ref',           default: ''        },
  { name: 'licence_expiry',         default: ''        },
  { name: 'outreach_status',        default: 'pending' },
  { name: 'outreach_last_attempt',  default: ''        },
  { name: 'outreach_notes',         default: ''        },
  { name: 'tier_2_review_pending',  default: 'FALSE'   },
  { name: 'licence_expiry_warning', default: 'FALSE'   }
];

function addVerificationColumns() {
  const ss    = SpreadsheetApp.openById(MASTER_SHEET_ID);
  const sheet = getSheetByGid_(ss, FACILITIES_GID);
  if (!sheet) throw new Error('Facilities tab (gid=' + FACILITIES_GID + ') not found.');

  const data      = sheet.getDataRange().getValues();
  const header    = data[0].map(h => String(h).trim().toLowerCase());
  const statusCol = header.indexOf('status');

  // ─── 1. Add missing header columns ────────────────────────────────
  let added = 0, skipped = 0;
  VERIFICATION_COLUMNS.forEach(col => {
    if (header.includes(col.name)) {
      skipped++;
      return;
    }
    const newColIndex = sheet.getLastColumn() + 1;
    sheet.getRange(1, newColIndex).setValue(col.name);
    header.push(col.name); // keep header array in sync
    added++;
  });

  // ─── 2. Reload data after header changes ──────────────────────────
  const data2     = sheet.getDataRange().getValues();
  const header2   = data2[0].map(h => String(h).trim().toLowerCase());
  const lastCol   = sheet.getLastColumn();
  const numRows   = sheet.getLastRow();

  // ─── 3. Set defaults on live rows ─────────────────────────────────
  // Build a map: column name → 1-based column index
  const colIndex = {};
  VERIFICATION_COLUMNS.forEach(col => {
    const idx = header2.indexOf(col.name);
    if (idx !== -1) colIndex[col.name] = idx + 1; // 1-based
  });

  let liveRows = 0, skippedRows = 0;
  for (let r = 2; r <= numRows; r++) {
    const rowData = data2[r - 1];
    const status  = statusCol === -1 ? '' : String(rowData[statusCol] || '').trim().toLowerCase();

    // Only set defaults on live rows (blank status)
    if (status === 'unverified' || status === 'removed') {
      skippedRows++;
      continue;
    }

    // Only write default if cell is currently empty
    VERIFICATION_COLUMNS.forEach(col => {
      if (!col.default) return; // blank default — leave as-is
      const ci  = colIndex[col.name];
      if (!ci) return;
      const val = String(rowData[ci - 1] || '').trim();
      if (val === '') {
        sheet.getRange(r, ci).setValue(col.default);
      }
    });
    liveRows++;
  }

  // ─── Output ───────────────────────────────────────────────────────
  const log = [
    '',
    '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━',
    'VERIFICATION SCHEMA UPGRADE — Facilities tab',
    '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━',
    'Columns added:   ' + added,
    'Columns skipped (already existed): ' + skipped,
    '',
    'Live rows updated with defaults: ' + liveRows,
    'Hidden/removed rows skipped:     ' + skippedRows,
    '',
    'Default values set on live rows:',
    '  verification_tier     = 1',
    '  outreach_status       = pending',
    '  tier_2_review_pending = FALSE',
    '  licence_expiry_warning = FALSE',
    '  (all other new columns left blank)',
    '',
    'NEXT STEPS:',
    '  1. Open the Facilities tab and confirm the 10 new columns appear',
    '     at the right edge of the header row',
    '  2. Share the Sheet with the helper — edit access scoped to these',
    '     10 columns only (use protected ranges to lock the rest)',
    '  3. Helper can now start outreach — filter outreach_status = pending',
    '',
    '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━',
    ''
  ].join('\n');
  Logger.log(log);
}

function getSheetByGid_(ss, gid) {
  const sheets = ss.getSheets();
  for (let i = 0; i < sheets.length; i++) {
    if (sheets[i].getSheetId() === gid) return sheets[i];
  }
  return null;
}
