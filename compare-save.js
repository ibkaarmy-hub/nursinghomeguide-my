/* ── Compare & Save — NursingHomeGuide.my ─────────────────────────────── */
(function () {
  const SAVED_KEY   = 'nh_saved_facilities'; // string[]
  const COMPARE_KEY = 'nh_compare_list';      // {slug, name}[]
  const MAX_COMPARE = 3;

  /* ── localStorage helpers ─────────────────────────────────────────────── */
  function getSaved()    { try { return JSON.parse(localStorage.getItem(SAVED_KEY)   || '[]'); } catch { return []; } }
  function setSaved(a)   { localStorage.setItem(SAVED_KEY, JSON.stringify(a)); }
  function getCompare()  { try { return JSON.parse(localStorage.getItem(COMPARE_KEY) || '[]'); } catch { return []; } }
  function setCompare(a) { localStorage.setItem(COMPARE_KEY, JSON.stringify(a)); }

  /* ── Toast ────────────────────────────────────────────────────────────── */
  let toastTimer;
  function showToast(msg) {
    let t = document.getElementById('nhg-toast');
    if (!t) {
      t = document.createElement('div');
      t.id = 'nhg-toast';
      Object.assign(t.style, {
        position: 'fixed', left: '50%', transform: 'translateX(-50%)',
        background: '#1e293b', color: 'white', padding: '10px 18px',
        borderRadius: '8px', fontSize: '.88rem', fontWeight: '500',
        zIndex: '500', pointerEvents: 'none', whiteSpace: 'nowrap',
        transition: 'opacity .25s', opacity: '0',
      });
      document.body.appendChild(t);
    }
    /* position above compare bar or mobile CTA bar */
    t.style.bottom = getCompare().length ? '70px' : '20px';
    t.textContent = msg;
    t.style.opacity = '1';
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => { t.style.opacity = '0'; }, 2800);
  }

  /* ── Save feature ─────────────────────────────────────────────────────── */
  function isSaved(slug) { return getSaved().includes(slug); }

  function toggleSave(slug) {
    const arr = getSaved();
    const idx = arr.indexOf(slug);
    if (idx >= 0) {
      arr.splice(idx, 1);
      setSaved(arr);
      updateSaveBtn(slug);
      showToast('Removed from saved');
    } else {
      arr.push(slug);
      setSaved(arr);
      updateSaveBtn(slug);
      showToast('Saved! (' + arr.length + ' saved total)');
    }
    window.dispatchEvent(new Event('nhg-saved-changed'));
  }

  function updateSaveBtn(slug) {
    const btn = document.getElementById('nhg-save-btn');
    if (!btn) return;
    const saved = isSaved(slug);
    btn.textContent = saved ? '💙 Saved' : '❤️ Save this facility';
    btn.style.background    = saved ? '#eff6ff' : '#f1f5f9';
    btn.style.color         = saved ? '#1d4ed8' : 'var(--text,#0f172a)';
    btn.style.borderColor   = saved ? '#bfdbfe' : 'var(--border,#e2e8f0)';
    btn.style.fontWeight    = '500';
  }

  /* ── Compare feature ──────────────────────────────────────────────────── */
  function isInCompare(slug) { return getCompare().some(x => x.slug === slug); }

  function toggleCompare(slug, name) {
    const arr = getCompare();
    const idx = arr.findIndex(x => x.slug === slug);
    if (idx >= 0) {
      arr.splice(idx, 1);
      setCompare(arr);
    } else {
      if (arr.length >= MAX_COMPARE) {
        showToast('Remove one facility first to add another');
        return;
      }
      arr.push({ slug, name });
      setCompare(arr);
    }
    updateCompareBtn(slug);
    renderCompareBar();
  }

  function updateCompareBtn(slug) {
    const btn = document.getElementById('nhg-compare-btn');
    if (!btn) return;
    const inList = isInCompare(slug);
    btn.textContent = inList ? '⚖️ In compare list ✓' : '⚖️ Add to Compare (up to 3)';
    btn.style.background    = inList ? '#fef3c7' : '#fef9c3';
    btn.style.borderColor   = inList ? '#fcd34d' : '#fde047';
    btn.style.color         = inList ? '#78350f' : '#78350f';
  }

  /* ── Compare bar ──────────────────────────────────────────────────────── */
  function renderCompareBar() {
    const arr = getCompare();
    let bar = document.getElementById('nhg-compare-bar');

    if (!arr.length) {
      if (bar) bar.style.display = 'none';
      document.body.classList.remove('nhg-compare-open');
      return;
    }

    if (!bar) {
      injectCompareStyles();
      bar = document.createElement('div');
      bar.id = 'nhg-compare-bar';
      document.body.appendChild(bar);
    }

    bar.style.display = 'flex';
    document.body.classList.add('nhg-compare-open');

    const chips = arr.map(x =>
      `<span class="nhg-chip">
        <span class="nhg-chip-name">${escHtml(x.name)}</span>
        <button class="nhg-chip-remove" onclick="NHGCompareSave.removeFromCompare('${esc(x.slug)}','${esc(x.name)}')" aria-label="Remove">×</button>
      </span>`
    ).join('');

    bar.innerHTML =
      `<span class="nhg-bar-label">Compare (${arr.length}/3):</span>
       <div class="nhg-chips">${chips}</div>
       <div class="nhg-bar-actions">
         <a class="nhg-compare-now" href="/compare.html">Compare now →</a>
         <button class="nhg-bar-clear" onclick="NHGCompareSave.clearCompare()">Clear</button>
       </div>`;
  }

  function escHtml(s) {
    return String(s || '').replace(/[&<>"']/g, c =>
      ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  }
  function esc(s) {
    return String(s || '').replace(/\\/g, '\\\\').replace(/'/g, "\\'");
  }

  function injectCompareStyles() {
    if (document.getElementById('nhg-compare-styles')) return;
    const s = document.createElement('style');
    s.id = 'nhg-compare-styles';
    s.textContent = `
      #nhg-compare-bar {
        position: fixed; bottom: 0; left: 0; right: 0; z-index: 200;
        background: white; border-top: 2px solid #2563eb;
        padding: 10px 16px; gap: 10px; align-items: center; flex-wrap: wrap;
        box-shadow: 0 -4px 16px rgba(0,0,0,.12); display: none;
      }
      .nhg-bar-label { font-size: .82rem; color: #64748b; font-weight: 700; white-space: nowrap; flex-shrink: 0; }
      .nhg-chips { display: flex; gap: 6px; flex-wrap: wrap; flex: 1; }
      .nhg-chip { display: inline-flex; align-items: center; gap: 5px; background: #eff6ff; color: #1d4ed8; padding: 4px 6px 4px 12px; border-radius: 999px; font-size: .82rem; font-weight: 500; }
      .nhg-chip-name { max-width: 180px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
      .nhg-chip-remove { background: none; border: none; cursor: pointer; color: #64748b; font-size: 1.1rem; line-height: 1; padding: 0 4px; }
      .nhg-chip-remove:hover { color: #ef4444; }
      .nhg-bar-actions { display: flex; gap: 8px; align-items: center; margin-left: auto; }
      .nhg-compare-now { background: #2563eb; color: white; padding: 8px 16px; border-radius: 8px; font-weight: 600; font-size: .88rem; text-decoration: none; white-space: nowrap; }
      .nhg-compare-now:hover { opacity: .9; text-decoration: none; }
      .nhg-bar-clear { background: #f1f5f9; border: 1px solid #e2e8f0; border-radius: 8px; padding: 8px 12px; cursor: pointer; font-size: .82rem; color: #64748b; white-space: nowrap; }
      .nhg-bar-clear:hover { background: #e2e8f0; }
      body.nhg-compare-open { padding-bottom: 62px; }
      @media (max-width: 600px) {
        #nhg-compare-bar { bottom: 70px; flex-wrap: nowrap; overflow-x: auto; }
        .nhg-chips { flex-wrap: nowrap; }
        body.nhg-compare-open { padding-bottom: 140px; }
      }
    `;
    document.head.appendChild(s);
  }

  function removeFromCompare(slug) {
    const arr = getCompare().filter(x => x.slug !== slug);
    setCompare(arr);
    const curSlug = window.__CURRENT_FACILITY && window.__CURRENT_FACILITY.slug;
    if (curSlug) updateCompareBtn(curSlug);
    renderCompareBar();
  }

  function clearCompare() {
    setCompare([]);
    const curSlug = window.__CURRENT_FACILITY && window.__CURRENT_FACILITY.slug;
    if (curSlug) updateCompareBtn(curSlug);
    renderCompareBar();
  }

  /* ── Init (called after render() in facility pages) ───────────────────── */
  function init(slug, name) {
    window.__CURRENT_FACILITY = { slug, name };

    const saveBtn = document.getElementById('nhg-save-btn');
    if (saveBtn) {
      saveBtn.onclick = () => toggleSave(slug);
      updateSaveBtn(slug);
    }

    const compareBtn = document.getElementById('nhg-compare-btn');
    if (compareBtn) {
      compareBtn.onclick = () => toggleCompare(slug, name);
      updateCompareBtn(slug);
    }

    renderCompareBar();
  }

  /* ── Public API ───────────────────────────────────────────────────────── */
  window.NHGCompareSave = {
    init,
    toggleSave,
    toggleCompare,
    removeFromCompare,
    clearCompare,
    getSaved,
    getCompare,
    isSaved,
    isInCompare,
  };
})();
