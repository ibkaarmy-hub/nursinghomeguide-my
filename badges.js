/* Capability badges — Phase C
 *
 * Two-state model per _research/regulatory-framework.md §3:
 *   Confirmed (positive evidence)  /  Unverified (greyed)
 *
 * The card shows trust label + (if any) confirmed-capability summary.
 * The profile shows the full Group A + Group B grid plus the tier marker.
 *
 * Reads `_effective_*` fields populated by applyVerificationStaleness() in data.js.
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
      key: 'rn_24_7',
      label: 'RN 24/7',
      tip: 'Registered nurse confirmed on duty around the clock.',
      isConfirmed: f => isYes(f.rn_24_7),
    },
    {
      key: 'peg',
      label: 'PEG / tube feeding',
      tip: 'Staff trained to manage PEG and nasogastric tube feeds.',
      isConfirmed: f => isYes(f.medical_peg),
    },
    {
      key: 'tracheostomy',
      label: 'Tracheostomy care',
      tip: 'Staff trained to suction and manage tracheostomies.',
      isConfirmed: f => isYes(f.medical_tracheostomy),
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
      key: 'sg_transfer',
      label: 'SG transfer ready',
      tip: 'Accepts Singaporean residents — admission workflow + currency handling.',
      isConfirmed: f => isYes(f.sg_transfer_ready),
    },
    {
      key: 'halal',
      label: 'Halal-certified kitchen',
      tip: 'Confirmed halal food preparation.',
      isConfirmed: f => isYes(f.halal),
    },
    {
      key: 'wheelchair',
      label: 'Wheelchair accessible',
      tip: 'Confirmed wheelchair-friendly throughout.',
      isConfirmed: f => isYes(f.wheelchair),
    },
  ];

  // Hybrid need-based search — required badges (all must be Confirmed)
  const NEED_BADGE_SETS = {
    'post-stroke':       ['rn_24_7', 'rehab'],
    'advanced-dementia': ['rn_24_7', 'dementia_secure'],
    'peg':               ['rn_24_7', 'peg'],
    'palliative':        ['rn_24_7', 'palliative'],
    'tracheostomy':      ['rn_24_7', 'tracheostomy'],
  };

  function escapeHtml(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, c => ({
      '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
    }[c]));
  }

  // ── Trust label (MOH Licensed / Unverified listing / JKM Registered) ─
  // Cards: MOH Licensed only. JKM is the silent ~96% default; "Unverified
  // listing" would shout on every card while verification is in progress.
  // Both render on the profile detail view.
  function trustLabel(f, opts) {
    const isProfile = !!(opts && opts.showJkm);
    const cat = (f._effective_license_category || f.license_category || 'Unverified').trim();
    if (cat === 'MOH Licensed') {
      return '<span class="trust-pill trust-moh" title="Confirmed under MOH Act 586 / Act 802">⭐ MOH Licensed</span>';
    }
    if (cat === 'JKM Registered') {
      return isProfile
        ? '<span class="trust-pill trust-jkm" title="Pusat Jagaan registered under Act 506">JKM Registered</span>'
        : '';
    }
    return isProfile
      ? '<span class="trust-pill trust-unverified" title="No licence evidence on file yet">Unverified listing</span>'
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

    const docFreq = (f.doctor_visit_frequency || '').trim();
    const docPill = docFreq && docFreq.toLowerCase() !== 'unverified'
      ? `<span class="doc-pill ok" title="Doctor visit frequency on record.">Doctor: ${escapeHtml(docFreq)}</span>`
      : `<span class="doc-pill muted" title="Doctor visit frequency not yet confirmed.">Doctor: Unverified</span>`;

    return `
      <div class="badge-block">
        <div class="badge-block-head">Clinical capability</div>
        <div class="badge-grid">${renderRow(CLINICAL_BADGES)}</div>
      </div>
      <div class="badge-block">
        <div class="badge-block-head">Service &amp; logistics</div>
        <div class="badge-grid">${renderRow(SERVICE_BADGES)}</div>
      </div>
      <div class="badge-tags">${docPill}</div>`;
  }

  // Last-updated marker — profile only.
  function tierMarker(f) {
    const date = (f.last_verified_on || f.last_updated || '').trim();
    if (!date) return '';
    const expired = f._licence_expired
      ? ` <span class="tier-warn">Licence expired — re-verifying.</span>`
      : '';
    return `<div class="tier-marker">Last updated: ${escapeHtml(date)}${expired}</div>`;
  }

  // ── Hybrid need-based search ─────────────────────────────────────────
  // Returns 'confirmed' / 'possible' / 'no-match' for a (facility, need).
  // 'confirmed' = every required badge is Confirmed for this facility
  // 'possible'  = required badges are Unverified (no positive evidence yet,
  //               but no denial — facility may be suitable)
  // (We have no third state for "denied", so 'no-match' is reserved for
  //  filtering on dimensions not in the badge set, e.g. care_category.)
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
