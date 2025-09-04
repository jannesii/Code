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

function createTile(id, name, temp=null, hum=null){
  const tile = document.createElement('div');
  tile.className = 'tile';
  tile.id = id;
  tile.innerHTML = `
    <div class="loc"></div>
    <div class="row"><span class="label">Lämpötila</span> <span class="value temp">-</span></div>
    <div class="row"><span class="label">Kosteus</span>    <span class="value hum">-</span></div>
  `;
  tile.querySelector('.loc').textContent = name || '—';
  tile.querySelector('.temp').textContent = fmtTemp(temp);
  tile.querySelector('.hum').textContent  = fmtHum(hum);

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

  return { name, temp, hum };
}

function renderItems(locations){
  const grid = document.getElementById('locationsGrid');
  if(!grid) return;

  const locs = Array.isArray(locations) ? locations : [];
  grid.innerHTML = '';

  locs.forEach(loc => {
    const { name, temp, hum } = extractNameTempHum(loc);
    const id = 'loc-' + slugify(name || 'default');
    const tile = createTile(id, name, temp, hum);
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

  if (tempEl) tempEl.textContent = fmtTemp(temp);
  if (humEl)  humEl.textContent  = fmtHum(hum);
}

function initSIO(){
  socket.on('esp32_temphum', data => {
    console.log('📡 Received esp32_temphum:', data);
    updateTile(data);
  });
}

document.addEventListener('DOMContentLoaded', () => {
  const locations = Array.isArray(window.LOCATIONS) ? window.LOCATIONS : [];
  // LOCATIONS is a list of dicts: {location, temp, hum}
  renderItems(locations);
  initSIO();
});
