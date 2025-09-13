// Settings modal: opens Sleep or Thermostat settings in an overlay
(() => {
  const modal = document.getElementById('settingsModal');
  if (!modal) return;
  const dialog = modal.querySelector('.dialog');
  const backdrop = modal.querySelector('.backdrop');
  const titleEl = document.getElementById('settingsTitle');
  const closeBtn = document.getElementById('closeSettings');

  const sleepPanel = document.getElementById('sleepPanel');
  const thermoPanel = document.getElementById('thermoPanel');

  const btnOpenSleep = document.getElementById('openSleepSettings');
  const btnOpenThermo = document.getElementById('openThermoSettings');

  function setVisible(el, visible){ if (el) el.hidden = !visible; }
  function openModal(kind){
    if (!modal) return;
    modal.classList.add('is-open');
    setVisible(sleepPanel, kind === 'sleep');
    setVisible(thermoPanel, kind === 'thermo');
    if (titleEl) titleEl.textContent = kind === 'sleep' ? 'Sleep Settings' : 'Thermostat Settings';
    // Prefill by fetching latest status
    fetch('/api/ac/status').then(r => r.ok ? r.json() : null).then(data => {
      if (!data) return;
      try{
        // Sleep
        const pill = document.getElementById('sleepStatusPill');
        const btnToggle = document.getElementById('btnSleepToggle');
        if (btnToggle){ btnToggle.textContent = (data.sleep_enabled ? 'Disable Sleep' : 'Enable Sleep'); }
        const sleepStart = document.getElementById('sleepStart');
        const sleepStop  = document.getElementById('sleepStop');
        if (sleepStart && data.sleep_start) sleepStart.value = (String(data.sleep_start).slice(0,5));
        if (sleepStop  && data.sleep_stop ) sleepStop.value  = (String(data.sleep_stop ).slice(0,5));
        // Thermostat
        const sp  = document.getElementById('modalSetpointC');
        const hyP = document.getElementById('modalHysteresisPos');
        const hyN = document.getElementById('modalHysteresisNeg');
        if (sp  && 'setpoint_c'     in data){ const v = parseFloat(data.setpoint_c); if (!Number.isNaN(v)) sp.value  = v.toFixed(1); }
        if (hyP && 'pos_hysteresis' in data){ const v = parseFloat(data.pos_hysteresis); if (!Number.isNaN(v)) hyP.value = v.toFixed(1); }
        if (hyN && 'neg_hysteresis' in data){ const v = parseFloat(data.neg_hysteresis); if (!Number.isNaN(v)) hyN.value = v.toFixed(1); }
      }catch{}
    }).catch(()=>{});
  }
  function closeModal(){ modal.classList.remove('is-open'); }

  if (btnOpenSleep)  btnOpenSleep.addEventListener('click', () => openModal('sleep'));
  if (btnOpenThermo) btnOpenThermo.addEventListener('click', () => openModal('thermo'));
  if (closeBtn) closeBtn.addEventListener('click', closeModal);
  modal.addEventListener('click', (e) => { if (e.target === modal || e.target === backdrop) closeModal(); });
  dialog.addEventListener('click', (e) => e.stopPropagation());
})();

