/* Capability badges — Phase C
 *
 * Two-state model: Confirmed (positive evidence) / Unverified (greyed)
 *
 * The card shows trust label + (if any) confirmed-capability summary.
 * The profile shows the full Group A + Group B grid.
 *
 * All columns read here must exist in the documented schema (CLAUDE.md).
 * Definitions: _research/badge_definitions.md
 */
(function (root) {
  'use strict';

  // ── Field-value helpers ──────────────────────────────────────────────
  function isYes(v) {
    if (!v) return false;
    return ['yes', 'y', 'true', '1', 'confirmed'].includes(String(v).trim().toLowerCase());
  }

  // Group A — Clinical capability badges
  // Each entry: { key, label, tip, isConfirmed: (f) => bool }
  const CLINICAL_BADGES = [
    {
      key: 'peg',
      label: 'PEG / tube feeding',
      tip: 'Staff trained to manage PEG and nasogastric tube feeds.',
      isConfirmed: f => isYes(f.medical_peg),
    },
    {
      key: 'wound',
      label: 'Advanced wound care',
      tip: 'Pressure-injury management beyond basic dressings.',
      isConfirmed: f => isYes(f.medical_wound),
    },
    {
      key: 'dementia_secure',
      label: 'Dementia secure unit',
      tip: 'Locked or controlled-access ward with trained staff.',
      isConfirmed: f => isYes(f.medical_dementia_unit),
    },
    {
      key: 'palliative',
      label: 'Palliative care offered',
      tip: 'Symptom management and end-of-life support. Not hospice-level guarantee.',
      isConfirmed: f => isYes(f.care_palliative),
    },
    {
      key: 'rehab',
      label: 'Rehabilitation support',
      tip: 'On-site or scheduled physiotherapy and post-hospital recovery.',
      isConfirmed: f => isYes(f.care_rehab) || isYes(f.medical_physio),
    },
  ];

  // Group B — Service / logistics badges
  const SERVICE_BADGES = [
    {
      key: 'halal',
      label: 'Halal-certified kitchen',
      tip: 'Confirmed halal food preparation.',
      isConfirmed: f => isYes(f.halal),
    },
  ];

  // Hybrid need-based search — required badges (all must be Confirmed)
  const NEED_BADGE_SETS = {
    'post-stroke':       ['rehab'],
    'advanced-dementia': ['dementia_secure'],
    'peg':               ['peg'],
    'palliative':        ['palliative'],
  };

  function escapeHtml(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, c => ({
      '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
    }[c]));
  }

  // ── Trust label (MOH Licensed / JKM Registered / Unverified) ──────────
  // Reads jkm_data_source column (e.g. "MOH NH 2026", "JKM 2026", "JKM 2026; MOH NH 2026").
  // Cards: MOH and JKM both shown. Profile: all three states rendered.
  function trustLabel(f, opts) {
    const isProfile = !!(opts && opts.showJkm);
    const src = (f.jkm_data_source || '').toLowerCase();
    const isMOH = src.includes('moh');
    const isJKM = src.includes('jkm');
    if (isMOH) {
      return '<span class="trust-pill trust-moh" title="Licensed under MOH (Private Healthcare Facilities Act 586 / Act 802)">⭐ MOH Licensed</span>';
    }
    if (isJKM) {
      return '<span class="trust-pill trust-jkm" title="Registered with JKM under the Care Centres Act 506">JKM Registered</span>';
    }
    return isProfile
      ? '<span class="trust-pill trust-unverified" title="No licence evidence on file yet">Not in MOH / JKM registry</span>'
      : '';
  }

  // Compact card-summary: show up to N confirmed clinical badges (in card row).
  function cardCapabilitySummary(f, max) {
    max = max || 3;
    const confirmed = CLINICAL_BADGES.filter(b => b.isConfirmed(f));
    if (!confirmed.length) return '';
    const shown = confirmed.slice(0, max);
    const more = confirmed.length - shown.length;
    const pills = shown.map(b =>
      `<span class="cap-pill" title="${escapeHtml(b.tip)}">✓ ${escapeHtml(b.label)}</span>`
    ).join('');
    const morePill = more > 0 ? `<span class="cap-pill cap-more">+${more} more</span>` : '';
    return `<div class="card-caps">${pills}${morePill}</div>`;
  }

  // Full badge grid for profile pages
  function profileBadgeGrid(f) {
    const renderRow = (defs) => defs.map(b => {
      const ok = b.isConfirmed(f);
      const cls = ok ? 'cap-badge ok' : 'cap-badge muted';
      const icon = ok ? '✓' : '?';
      return `<div class="${cls}" title="${escapeHtml(b.tip)}"><span class="cap-icon">${icon}</span>${escapeHtml(b.label)}</div>`;
    }).join('');

    const confirmedServices = SERVICE_BADGES.filter(b => b.isConfirmed(f));
    const serviceBlock = confirmedServices.length ? `
      <div class="badge-block">
        <div class="badge-block-head">Service &amp; logistics</div>
        <div class="badge-grid">${confirmedServices.map(b => `<div class="cap-badge ok" title="${escapeHtml(b.tip)}"><span class="cap-icon">✓</span>${escapeHtml(b.label)}</div>`).join('')}</div>
      </div>` : '';

    return `
      <div class="badge-block">
        <div class="badge-block-head">Clinical capability</div>
        <div class="badge-grid">${renderRow(CLINICAL_BADGES)}</div>
      </div>
      ${serviceBlock}`;
  }

  // ── Hybrid need-based search ─────────────────────────────────────────
  // Returns 'confirmed' / 'possible' / 'no-match' for a (facility, need).
  // 'confirmed' = every required badge is Confirmed for this facility
  // 'possible'  = required badges are Unverified (no positive evidence yet,
  //               but no denial — facility may be suitable)
  // (We have no third state for "denied", so 'no-match' is reserved for
  //  filtering on dimensions not in the badge set, e.g. care_types.)
  function needMatchTier(f, need) {
    const required = NEED_BADGE_SETS[need];
    if (!required) return 'confirmed';
    const allBadges = [...CLINICAL_BADGES, ...SERVICE_BADGES];
    const lookup = {};
    allBadges.forEach(b => { lookup[b.key] = b; });
    const allConfirmed = required.every(k => lookup[k] && lookup[k].isConfirmed(f));
    return allConfirmed ? 'confirmed' : 'possible';
  }

  // Export
  // Stub — kept for backwards-compat with generated static pages until they are regenerated.
  function tierMarker() { return ''; }

  root.NHGBadges = {
    CLINICAL_BADGES,
    SERVICE_BADGES,
    NEED_BADGE_SETS,
    trustLabel,
    cardCapabilitySummary,
    profileBadgeGrid,
    tierMarker,
    needMatchTier,
  };
})(typeof window !== 'undefined' ? window : globalThis);
