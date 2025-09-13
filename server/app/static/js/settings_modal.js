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
        const btnToggle = document.getElementById('btnSleepToggle');
        if (btnToggle){ btnToggle.textContent = (data.sleep_enabled ? 'Disable Sleep' : 'Enable Sleep'); }
        // Weekly schedule: parse JSON if string
        let schedule = data.sleep_schedule;
        try{ if (typeof schedule === 'string') schedule = JSON.parse(schedule); }catch{}
        const days = ['mon','tue','wed','thu','fri','sat','sun'];
        const fillAll = (s,e) => { days.forEach((d, i) => {
          const sEl = document.getElementById(`sleep_${d}_start`);
          const eEl = document.getElementById(`sleep_${d}_stop`);
          if (sEl) sEl.value = s || '';
          if (eEl) eEl.value = e || '';
        }); };
        if (schedule && typeof schedule === 'object'){
          days.forEach(d => {
            const row = schedule[d] || {};
            const sEl = document.getElementById(`sleep_${d}_start`);
            const eEl = document.getElementById(`sleep_${d}_stop`);
            if (sEl) sEl.value = (row.start || '').slice(0,5);
            if (eEl) eEl.value = (row.stop  || '').slice(0,5);
          });
        } else {
          // Fallback to global times
          const s = (data.sleep_start || '').slice(0,5);
          const e = (data.sleep_stop  || '').slice(0,5);
          fillAll(s, e);
        }
        // Thermostat
        const sp  = document.getElementById('modalSetpointC');
        const hyP = document.getElementById('modalHysteresisPos');
        const hyN = document.getElementById('modalHysteresisNeg');
        if (sp  && 'setpoint_c'     in data){ const v = parseFloat(data.setpoint_c); if (!Number.isNaN(v)) sp.value  = v.toFixed(1); }
        if (hyP && 'pos_hysteresis' in data){ const v = parseFloat(data.pos_hysteresis); if (!Number.isNaN(v)) hyP.value = v.toFixed(1); }
        if (hyN && 'neg_hysteresis' in data){ const v = parseFloat(data.neg_hysteresis); if (!Number.isNaN(v)) hyN.value = v.toFixed(1); }
        const minOn = document.getElementById('modalMinOnS');
        const minOff= document.getElementById('modalMinOffS');
        const pollS = document.getElementById('modalPollS');
        const smooth= document.getElementById('modalSmoothWindow');
        const stale = document.getElementById('modalMaxStaleS');
        if (minOn && 'min_on_s' in data) minOn.value = parseInt(data.min_on_s)||0;
        if (minOff&& 'min_off_s' in data) minOff.value= parseInt(data.min_off_s)||0;
        if (pollS && 'poll_interval_s' in data) pollS.value = parseInt(data.poll_interval_s)||15;
        if (smooth&& 'smooth_window' in data) smooth.value= parseInt(data.smooth_window)||1;
        if (stale) stale.value = (data.max_stale_s == null ? '' : parseInt(data.max_stale_s));
        // Populate location selection
        const cont = document.getElementById('ctrlLocContainer');
        if (cont){
          cont.innerHTML = '';
          const names = Array.isArray(window.LOCATIONS)
            ? [...new Set(window.LOCATIONS.map(x => String(x.location || x.name || '').trim()).filter(Boolean))]
            : [];
          let selected = [];
          try{
            let cl = data.control_locations;
            if (typeof cl === 'string') cl = JSON.parse(cl);
            if (Array.isArray(cl)) selected = cl.map(String);
          }catch{}
          if (!selected.length && names.length){ selected = [names[0]]; }

          const emitSelection = () => {
            const active = [...cont.querySelectorAll('.loc-btn.active')].map(b => b.dataset.loc);
            if (active.length === 0){ return; }
            if (window.socket){ window.socket.emit('ac_control', { action: 'set_control_locations', locations: active }); }
          };
          names.forEach(n => {
            const btn = document.createElement('button');
            btn.type = 'button';
            btn.className = 'loc-btn' + (selected.includes(n) ? ' active' : '');
            btn.textContent = n;
            btn.dataset.loc = n;
            btn.addEventListener('click', () => {
              const isActive = btn.classList.contains('active');
              if (isActive){
                // Prevent deactivating last one
                const actives = cont.querySelectorAll('.loc-btn.active');
                if (actives.length <= 1){ return; }
                btn.classList.remove('active');
              } else {
                btn.classList.add('active');
              }
              emitSelection();
            });
            cont.appendChild(btn);
          });
        }
      }catch{}
    }).catch(()=>{});
  }
  function closeModal(){ modal.classList.remove('is-open'); }

  if (btnOpenSleep)  btnOpenSleep.addEventListener('click', () => openModal('sleep'));
  if (btnOpenThermo) btnOpenThermo.addEventListener('click', () => openModal('thermo'));
  if (closeBtn) closeBtn.addEventListener('click', closeModal);
  modal.addEventListener('click', (e) => { if (e.target === modal || e.target === backdrop) closeModal(); });
  dialog.addEventListener('click', (e) => e.stopPropagation());

  // Auto-save sleep schedule on change
  const days = ['mon','tue','wed','thu','fri','sat','sun'];
  function buildSchedule(){
    const schedule = {};
    days.forEach(d => {
      const s = document.getElementById(`sleep_${d}_start`);
      const e = document.getElementById(`sleep_${d}_stop`);
      schedule[d] = { start: s && s.value ? s.value : null, stop: e && e.value ? e.value : null };
    });
    return schedule;
  }
  let _sleepDebounce = null;
  function emitSleepSchedule(){
    const schedule = buildSchedule();
    if (window.socket){ window.socket.emit('ac_control', { action: 'set_sleep_schedule', schedule }); }
  }
  function debounceEmitSleep(){
    if (_sleepDebounce) clearTimeout(_sleepDebounce);
    _sleepDebounce = setTimeout(emitSleepSchedule, 300);
  }
  days.forEach(d => {
    const s = document.getElementById(`sleep_${d}_start`);
    const e = document.getElementById(`sleep_${d}_stop`);
    if (s) { s.addEventListener('change', debounceEmitSleep); s.addEventListener('input', debounceEmitSleep); }
    if (e) { e.addEventListener('change', debounceEmitSleep); e.addEventListener('input', debounceEmitSleep); }
  });
  // Toggle sleep enabled/disabled
  const btnSleepToggle = document.getElementById('btnSleepToggle');
  if (btnSleepToggle){
    btnSleepToggle.addEventListener('click', () => {
      const enable = /enable/i.test(btnSleepToggle.textContent || '');
      if (window.socket){ window.socket.emit('ac_control', { action: 'set_sleep_enabled', value: enable }); }
      // Flip label immediately
      btnSleepToggle.textContent = enable ? 'Disable Sleep' : 'Enable Sleep';
    });
  }

  // Temporary sleep override: disable sleep for X minutes
  const disableInput = document.getElementById('sleepDisableMinutes');
  const disableBtn = document.getElementById('btnSleepDisableFor');
  if (disableBtn){
    disableBtn.addEventListener('click', () => {
      const raw = disableInput ? parseInt(disableInput.value, 10) : NaN;
      let minutes = Number.isFinite(raw) ? raw : 0;
      if (minutes < 5) minutes = 5;
      // snap to 5-minute steps
      minutes = Math.max(5, Math.round(minutes / 5) * 5);
      if (window.socket){ window.socket.emit('ac_control', { action: 'disable_sleep_for', minutes }); }
    });
  }

  // Auto-save thermostat settings on change
  const sp  = document.getElementById('modalSetpointC');
  const hyP = document.getElementById('modalHysteresisPos');
  const hyN = document.getElementById('modalHysteresisNeg');
  const minOn = document.getElementById('modalMinOnS');
  const minOff= document.getElementById('modalMinOffS');
  const pollS = document.getElementById('modalPollS');
  const smooth= document.getElementById('modalSmoothWindow');
  const stale = document.getElementById('modalMaxStaleS');
  function emitSetpoint(){
    if (!sp) return;
    const v = parseFloat(sp.value);
    if (Number.isFinite(v) && window.socket){ window.socket.emit('ac_control', { action: 'set_setpoint', value: v }); }
  }
  function emitHysteresis(){
    if (!hyP || !hyN) return;
    const pos = parseFloat(hyP.value);
    const neg = parseFloat(hyN.value);
    if (Number.isFinite(pos) && Number.isFinite(neg) && window.socket){
      window.socket.emit('ac_control', { action: 'set_hysteresis_split', pos, neg });
    }
  }
  let _spDebounce = null, _hyDebounce = null;
  function debounce(fn, key){
    return function(){
      if (key === 'sp'){ if (_spDebounce) clearTimeout(_spDebounce); _spDebounce = setTimeout(fn, 300); }
      else { if (_hyDebounce) clearTimeout(_hyDebounce); _hyDebounce = setTimeout(fn, 300); }
    };
  }
  if (sp){ sp.addEventListener('input', debounce(emitSetpoint, 'sp')); sp.addEventListener('change', emitSetpoint); }
  if (hyP){ hyP.addEventListener('input', debounce(emitHysteresis)); hyP.addEventListener('change', emitHysteresis); }
  if (hyN){ hyN.addEventListener('input', debounce(emitHysteresis)); hyN.addEventListener('change', emitHysteresis); }
  function emitSimple(action, el, parser){ if (!el) return; const raw = el.value; const v = parser(raw); if (window.socket && v !== undefined) window.socket.emit('ac_control', { action, value: v }); }
  if (minOn){ minOn.addEventListener('change', () => emitSimple('set_min_on_s', minOn, v=>parseInt(v))); }
  if (minOff){ minOff.addEventListener('change', () => emitSimple('set_min_off_s', minOff, v=>parseInt(v))); }
  if (pollS){ pollS.addEventListener('change', () => emitSimple('set_poll_interval_s', pollS, v=>parseInt(v))); }
  if (smooth){ smooth.addEventListener('change', () => emitSimple('set_smooth_window', smooth, v=>parseInt(v))); }
  if (stale){ stale.addEventListener('change', () => emitSimple('set_max_stale_s', stale, v=> (v===''? null : parseInt(v)) )); }
})();
