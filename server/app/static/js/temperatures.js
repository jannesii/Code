console.log('🧊 temperatures.js loaded');

function slugify(s){
  return String(s || '').toLowerCase().replace(/[^a-z0-9]+/g,'-').replace(/(^-|-$)/g,'');
}

function fmtTemp(v){
  const n = Number(v);
  return Number.isFinite(n) ? `${n.toFixed(1)} °C` : '-';
}
function fmtHum(v){
  const n = Number(v);
  return Number.isFinite(n) ? `${n.toFixed(0)} %` : '-';
}

function fmtTime(ts){
  // Returns a readable local timestamp without a label
  if (!ts) return '—';
  try {
    const d = ts instanceof Date ? ts : new Date(ts);
    // Prefer a concise local string; include date + time
    return d.toLocaleString(undefined, {
      year: 'numeric', month: '2-digit', day: '2-digit',
      hour: '2-digit', minute: '2-digit', second: '2-digit'
    });
  } catch {
    return '—';
  }
}

function createTile(id, name, temp=null, hum=null, ts=null){
  const tile = document.createElement('div');
  tile.className = 'tile';
  tile.id = id;
  tile.innerHTML = `
    <div class="loc"></div>
    <div class="row"><span class="label">Lämpötila</span> <span class="value temp">-</span></div>
    <div class="row"><span class="label">Kosteus</span>    <span class="value hum">-</span></div>
    <div class="timestamp">—</div>
  `;
  tile.querySelector('.loc').textContent = name || '—';
  tile.querySelector('.temp').textContent = fmtTemp(temp);
  tile.querySelector('.hum').textContent  = fmtHum(hum);
  const tsEl = tile.querySelector('.timestamp');
  if (tsEl) tsEl.textContent = fmtTime(ts);

  // Click handler opens charts for this location
  tile.addEventListener('click', () => {
    console.log(`🖱️ Tile clicked: ${name} (id=${id})`);
    if (typeof openAndRender === 'function') {
      openAndRender(name);
    }
  });

  return tile;
}

function extractNameTempHum(entry){
  // Supports both initial payload {location, temp, hum}
  // and live events {location, temperature}/{temperature_c}, {humidity}/{humidity_pct}
  if (entry == null) return { name: '—', temp: null, hum: null };

  if (typeof entry === 'string') {
    return { name: entry.trim(), temp: null, hum: null };
  }

  const name = String(entry.location || '—').trim();

  const temp = (
    entry.temperature
  );

  const hum = (
    entry.humidity
  );

  // Optional timestamp if present in payload
  const ts = (entry.timestamp || null);

  return { name, temp, hum, ts };
}

function renderItems(locations){
  const grid = document.getElementById('locationsGrid');
  if(!grid) return;

  const locs = Array.isArray(locations) ? locations : [];
  grid.innerHTML = '';

  locs.forEach(loc => {
    const { name, temp, hum, ts } = extractNameTempHum(loc);
    const id = 'loc-' + slugify(name || 'default');
    const tile = createTile(id, name, temp, hum, ts);
    grid.appendChild(tile);
  });
}

function ensureTile(name){
  const id = 'loc-' + slugify(name || 'default');
  let tile = document.getElementById(id);
  if (!tile) {
    const grid = document.getElementById('locationsGrid');
    if (!grid) return null;
    tile = createTile(id, name);
    grid.appendChild(tile);
  } else {
    tile.querySelector('.loc').textContent = name || '—';
  }
  return tile;
}

function updateTile(data){
  const { name, temp, hum } = extractNameTempHum(data);
  if (!name) return;

  const tile = ensureTile(name);
  if (!tile) return;

  const tempEl = tile.querySelector('.temp');
  const humEl  = tile.querySelector('.hum');
  const tsEl   = tile.querySelector('.timestamp');

  if (tempEl) tempEl.textContent = fmtTemp(temp);
  if (humEl)  humEl.textContent  = fmtHum(hum);
  // Update timestamp to "now" on each update
  if (tsEl)   tsEl.textContent   = fmtTime(new Date());
}

function initSIO(){
  socket.on('esp32_temphum', data => {
    console.log('📡 Received esp32_temphum:', data);
    updateTile(data);
  });
  socket.on('ac_status', data => {
    console.log('📡 Received ac_status:', data);
    if (!data) return;
    updateACIndicator(data.is_on);
  });
  socket.on('ac_state', data => {
    console.log('📡 Received ac_state:', data);
    if (!data) return;
    if (data.mode) setSelectValue('acMode', data.mode);
    if (data.fan_speed) setSelectValue('acFan', data.fan_speed);
  });
  socket.on('thermostat_status', data => {
    console.log('📡 Received thermostat_status:', data);
    if (!data) return;
    updateThermoIndicator(!!data.enabled);
  });
  socket.on('sleep_status', data => {
    console.log('📡 Received sleep_status:', data);
    if (!data) return;
    setSleepUI(data);
  });
  socket.on('thermo_config', data => {
    console.log('📡 Received thermo_config:', data);
    if (!data) return;
    setThermoConfigUI(data);
  });
}

async function fetchACStatus(){
  try{
    const resp = await fetch('/api/ac/status');
    if(!resp.ok){
      console.warn('AC status fetch failed:', resp.status);
      updateACIndicator(null);
      updateThermoIndicator(null);
      return;
    }
    const data = await resp.json();
    updateACIndicator(data && 'is_on' in data ? data.is_on : null);
    updateThermoIndicator(data && 'thermostat_enabled' in data ? data.thermostat_enabled : null);
    if (data && data.mode) setSelectValue('acMode', data.mode);
    if (data && data.fan_speed) setSelectValue('acFan', data.fan_speed);
    setSleepUI(data);
    setThermoConfigUI(data);
  }catch(err){
    console.error('AC status error:', err);
    updateACIndicator(null);
    updateThermoIndicator(null);
  }
}

function updateACIndicator(isOn){
  const pill = document.getElementById('acStatusPill');
  const btn  = document.getElementById('btnAcPowerToggle');
  if(!pill) return;
  pill.classList.remove('ac-on','ac-off','ac-unknown');
  if(isOn === true){
    pill.classList.add('ac-on');
    pill.textContent = 'ON';
    if (btn) btn.textContent = 'Turn AC Off';
  } else if(isOn === false){
    pill.classList.add('ac-off');
    pill.textContent = 'OFF';
    if (btn) btn.textContent = 'Turn AC On';
  } else {
    pill.classList.add('ac-unknown');
    pill.textContent = 'Unknown';
    if (btn) btn.textContent = 'Toggle AC';
  }
}

function updateThermoIndicator(enabled){
  const pill = document.getElementById('thermoStatusPill');
  const btn  = document.getElementById('btnThermoToggle');
  if(pill){
    pill.classList.remove('ac-on','ac-off','ac-unknown');
    if(enabled === true){
      pill.classList.add('ac-on');
      pill.textContent = 'Thermostat ON';
    } else if(enabled === false){
      pill.classList.add('ac-off');
      pill.textContent = 'Thermostat OFF';
    } else {
      pill.classList.add('ac-unknown');
      pill.textContent = 'Thermostat —';
    }
  }
  if(btn){
    btn.textContent = (enabled === true) ? 'Disable Thermostat' : 'Enable Thermostat';
  }
}

document.addEventListener('DOMContentLoaded', () => {
  const locations = Array.isArray(window.LOCATIONS) ? window.LOCATIONS : [];
  // LOCATIONS is a list of dicts: {location, temp, hum}
  renderItems(locations);
  initSIO();
  fetchACStatus();

  // Wire control buttons
  const btnAc = document.getElementById('btnAcPowerToggle');
  const btnTh = document.getElementById('btnThermoToggle');
  if(btnAc){
    btnAc.addEventListener('click', () => {
      const pill = document.getElementById('acStatusPill');
      const isOn = pill && pill.classList.contains('ac-on');
      socket.emit('ac_control', { action: isOn ? 'power_off' : 'power_on' });
    });
  }
  if(btnTh){
    btnTh.addEventListener('click', () => {
      const pill = document.getElementById('thermoStatusPill');
      const enabled = pill && pill.classList.contains('ac-on');
      socket.emit('ac_control', { action: enabled ? 'thermostat_disable' : 'thermostat_enable' });
    });
  }

  // Wire selects
  const selMode = document.getElementById('acMode');
  const selFan  = document.getElementById('acFan');
  if (selMode){
    selMode.addEventListener('change', () => {
      const val = selMode.value;
      // Only allow cold/wet/wind
      if(['cold','wet','wind'].includes(val)){
        socket.emit('ac_control', { action: 'set_mode', value: val });
      }
    });
  }
  if (selFan){
    selFan.addEventListener('change', () => {
      const val = selFan.value;
      // Only allow low/high
      if(['low','high'].includes(val)){
        socket.emit('ac_control', { action: 'set_fan_speed', value: val });
      }
    });
  }

  const sleepEnabled = document.getElementById('sleepEnabled');
  const sleepPill    = document.getElementById('sleepStatusPill');
  const btnSleepToggle = document.getElementById('btnSleepToggle');
  const sleepStart   = document.getElementById('sleepStart');
  const sleepStop    = document.getElementById('sleepStop');
  const btnSleepSave = document.getElementById('btnSleepSave');
  if (btnSleepToggle){
    btnSleepToggle.addEventListener('click', () => {
      const enabled = sleepPill && sleepPill.classList.contains('ac-on');
      socket.emit('ac_control', { action: 'set_sleep_enabled', value: !enabled });
    });
  }
  if (btnSleepSave && sleepStart && sleepStop){
    btnSleepSave.addEventListener('click', () => {
      const start = asTimeValue((sleepStart.value || '').trim());
      const stop  = asTimeValue((sleepStop.value || '').trim());
      socket.emit('ac_control', { action: 'set_sleep_times', start, stop });
    });
  }

  const sp = document.getElementById('setpointC');
  const hy = document.getElementById('hysteresis');
  const btnThermoSave = document.getElementById('btnThermoSave');
  if (btnThermoSave && sp && hy){
    btnThermoSave.addEventListener('click', () => {
      const setpoint = parseFloat(sp.value);
      const hyst = parseFloat(hy.value);
      if (!Number.isNaN(setpoint)){
        socket.emit('ac_control', { action: 'set_setpoint', value: setpoint });
      }
      if (!Number.isNaN(hyst)){
        socket.emit('ac_control', { action: 'set_hysteresis', value: hyst });
      }
    });
  }
});

function setSelectValue(id, value){
  const el = document.getElementById(id);
  if(!el) return;
  const val = String(value || '').toLowerCase();
  for (const opt of el.options){
    if (opt.value === val){ el.value = val; return; }
  }
}

function setSleepUI(data){
  if (!data) return;
  const sleepEnabled = document.getElementById('sleepEnabled');
  const pill = document.getElementById('sleepStatusPill');
  const btn  = document.getElementById('btnSleepToggle');
  const sleepStart   = document.getElementById('sleepStart');
  const sleepStop    = document.getElementById('sleepStop');
  if ('sleep_enabled' in data){
    const en = !!data.sleep_enabled;
    if (pill){
      pill.classList.remove('ac-on','ac-off','ac-unknown');
      if (en){ pill.classList.add('ac-on'); pill.textContent = 'Sleep ON'; }
      else    { pill.classList.add('ac-off'); pill.textContent = 'Sleep OFF'; }
    }
    if (btn){ btn.textContent = en ? 'Disable Sleep' : 'Enable Sleep'; }
    if (sleepEnabled){ sleepEnabled.checked = en; }
  }
  if (data.sleep_start && sleepStart){ sleepStart.value = asTimeValue(data.sleep_start); }
  if (data.sleep_stop  && sleepStop ){ sleepStop.value  = asTimeValue(data.sleep_stop); }
}

function asTimeValue(s){
  // Accept HH:MM, optional seconds; normalize to HH:MM
  if (!s) return '';
  try{
    const m = String(s).match(/^(\d{1,2}):(\d{2})/);
    if (!m) return '';
    const hh = String(m[1]).padStart(2,'0');
    const mm = String(m[2]).padStart(2,'0');
    return `${hh}:${mm}`;
  }catch{ return ''; }
}

function setThermoConfigUI(data){
  const sp = document.getElementById('setpointC');
  const hy = document.getElementById('hysteresis');
  if ('setpoint_c' in data && sp){
    const v = parseFloat(data.setpoint_c);
    if (!Number.isNaN(v)) sp.value = v.toFixed(1);
  }
  if ('deadband_c' in data && hy){
    const v = parseFloat(data.deadband_c);
    if (!Number.isNaN(v)) hy.value = v.toFixed(1);
  }
}
