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
}

async function fetchACStatus(){
  try{
    const resp = await fetch('/api/ac/status');
    if(!resp.ok){
      console.warn('AC status fetch failed:', resp.status);
      updateACIndicator(null);
      return;
    }
    const data = await resp.json();
    updateACIndicator(data && 'is_on' in data ? data.is_on : null);
  }catch(err){
    console.error('AC status error:', err);
    updateACIndicator(null);
  }
}

function updateACIndicator(isOn){
  const pill = document.getElementById('acStatusPill');
  if(!pill) return;
  pill.classList.remove('ac-on','ac-off','ac-unknown');
  if(isOn === true){
    pill.classList.add('ac-on');
    pill.textContent = 'ON';
  } else if(isOn === false){
    pill.classList.add('ac-off');
    pill.textContent = 'OFF';
  } else {
    pill.classList.add('ac-unknown');
    pill.textContent = 'Unknown';
  }
}

document.addEventListener('DOMContentLoaded', () => {
  const locations = Array.isArray(window.LOCATIONS) ? window.LOCATIONS : [];
  // LOCATIONS is a list of dicts: {location, temp, hum}
  renderItems(locations);
  initSIO();
  fetchACStatus();
});
