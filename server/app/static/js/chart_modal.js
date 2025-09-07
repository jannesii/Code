// charts_dual_modal.js
// Renders Temperature + Humidity charts side-by-side in the single modal shown in your HTML.

(() => {
  // — Elements —
  const modal          = document.getElementById('chartModal');
  const closeBtn       = document.getElementById('closeModal');
  const prevBtn        = document.getElementById('prevDay');
  const nextBtn        = document.getElementById('nextDay');
  const dateEl         = document.getElementById('currentDate');
  const titleEl        = document.getElementById('chartTitle');

  const titleTempEl    = document.getElementById('chartTitleTemp');
  const titleHumEl     = document.getElementById('chartTitleHum');
  const avgTempEl      = document.getElementById('avgTemp');
  const avgHumEl       = document.getElementById('avgHum');

  const ctxTemp        = document.getElementById('chartCanvasTemp').getContext('2d');
  const ctxHum         = document.getElementById('chartCanvasHum').getContext('2d');

  // — State —
  let currentDate      = new Date();
  let currentLocation  = null;
  let chartTemp        = null;
  let chartHum         = null;
  // Averaging window in minutes. Set to 0 or 1 for raw values.
  const DEFAULT_AVG_MINUTES = 0; // change default to 10 if you always want 10‑min bins
  let averagingMinutes = Number(window?.CHART_AVG_MINUTES ?? DEFAULT_AVG_MINUTES) || 0;

  // — Utils —
  function formatDateISO(d) {
    // Use local date (no TZ shift) -> YYYY-MM-DD
    const y = d.getFullYear();
    const m = String(d.getMonth() + 1).padStart(2, '0');
    const day = String(d.getDate()).padStart(2, '0');
    return `${y}-${m}-${day}`;
  }
  function addDays(d, delta) {
    const nd = new Date(d);
    nd.setDate(nd.getDate() + delta);
    return nd;
  }
  function ensureVisibleThen(fn) {
    // Allow layout to settle so canvases have size
    requestAnimationFrame(() => requestAnimationFrame(fn));
  }

  // Group points into N‑minute bins and compute averages per bin
  function aggregateByMinutes(rows, minutes) {
    const m = Number(minutes);
    if (!m || m <= 1) {
      // No aggregation: return as-is
      const labels = rows.map(d => String(d.timestamp).slice(11, 16));
      const temps  = rows.map(d => Number(d.temperature)).filter(Number.isFinite);
      const hums   = rows.map(d => Number(d.humidity)).filter(Number.isFinite);
      const rawTemps = rows.map(d => Number(d.temperature));
      const rawHums  = rows.map(d => Number(d.humidity));
      return { labels, temps: rawTemps, hums: rawHums };
    }
    const buckets = new Map(); // key: binStartMin (0..1439) → {sumT,nT,sumH,nH}
    for (const r of rows) {
      const ts = new Date(r.timestamp);
      if (isNaN(ts)) continue;
      const hodMin = ts.getHours() * 60 + ts.getMinutes();
      const binStart = Math.floor(hodMin / m) * m; // integer minutes from midnight
      let b = buckets.get(binStart);
      if (!b) { b = { sumT: 0, nT: 0, sumH: 0, nH: 0 }; buckets.set(binStart, b); }
      const t = Number(r.temperature);
      const h = Number(r.humidity);
      if (Number.isFinite(t)) { b.sumT += t; b.nT += 1; }
      if (Number.isFinite(h)) { b.sumH += h; b.nH += 1; }
    }
    const keys = [...buckets.keys()].sort((a, b) => a - b);
    const labels = [];
    const temps  = [];
    const hums   = [];
    for (const k of keys) {
      const hh = Math.floor(k / 60).toString().padStart(2, '0');
      const mm = (k % 60).toString().padStart(2, '0');
      labels.push(`${hh}:${mm}`);
      const b = buckets.get(k);
      temps.push(b.nT ? b.sumT / b.nT : null);
      hums.push(b.nH ? b.sumH / b.nH : null);
    }
    return { labels, temps, hums };
  }

  function openModal()  { modal.style.display = 'flex'; }
  function closeModal() { modal.style.display = 'none'; }

  // — Data fetch + render both charts —
  function fetchAndRenderBoth(location) {
    if (!location) return;

    const dateStr = formatDateISO(currentDate);
    dateEl.textContent   = dateStr;
    titleEl.textContent  = `Lämpötila & Kosteus – ${location}`;
    titleTempEl.textContent = 'Lämpötila';
    titleHumEl.textContent  = 'Kosteus';

    const url = `/api/esp32_temphum?date=${encodeURIComponent(dateStr)}&location=${encodeURIComponent(location)}`;

    fetch(url, { method: 'GET', headers: { 'Accept': 'application/json' } })
      .then(r => r.json())
      .then(data => {
        // Expected shape: [{ temperature:Number, humidity:Number, timestamp:ISO }, ...]
        const { labels, temps, hums } = aggregateByMinutes(data, averagingMinutes);

        // Overall daily averages (raw from returned series after aggregation)
        const finiteT = temps.filter(Number.isFinite);
        const finiteH = hums.filter(Number.isFinite);
        const avgT = finiteT.length ? finiteT.reduce((a,b)=>a+b,0) / finiteT.length : NaN;
        const avgH = finiteH.length ? finiteH.reduce((a,b)=>a+b,0) / finiteH.length : NaN;

        avgTempEl.textContent = temps.length ? `Lämpötila: ${avgT.toFixed(1)}°C` : 'Lämpötila: –';
        avgHumEl.textContent  = hums.length  ? `Kosteus: ${avgH.toFixed(1)}%`    : 'Kosteus: –';

        // Create/update Temperature chart
        if (!chartTemp) {
          chartTemp = new Chart(ctxTemp, {
            type: 'line',
            data: {
              labels,
              datasets: [{
                label: '°C',
                data: temps,
                fill: false,
                pointRadius: 0,
                pointHoverRadius: 3,
                borderWidth: 2
              }]
            },
            options: {
              responsive: true,
              maintainAspectRatio: false,
              spanGaps: true,
              interaction: { mode: 'nearest', intersect: false },
              plugins: {
                // Built-in Chart.js decimation plugin: preserves peaks better than simple averaging
                decimation: {
                  enabled: true,
                  algorithm: 'min-max', // or 'lttb'
                  samples: 300,        // target samples to keep on screen
                  threshold: 600       // only decimate when data length > threshold
                }
              },
              scales: {
                x: { display: true, title: { display: true, text: 'Aika' } },
                y: { beginAtZero: false }
              }
            }
          });
        } else {
          chartTemp.data.labels = labels;
          chartTemp.data.datasets[0].data = temps;
          chartTemp.update();
        }

        // Create/update Humidity chart
        if (!chartHum) {
          chartHum = new Chart(ctxHum, {
            type: 'line',
            data: {
              labels,
              datasets: [{
                label: '%',
                data: hums,
                fill: false,
                pointRadius: 0,
                pointHoverRadius: 3,
                borderWidth: 2
              }]
            },
            options: {
              responsive: true,
              maintainAspectRatio: false,
              spanGaps: true,
              interaction: { mode: 'nearest', intersect: false },
              plugins: {
                decimation: {
                  enabled: true,
                  algorithm: 'min-max',
                  samples: 300,
                  threshold: 600
                }
              },
              scales: {
                x: { display: true, title: { display: true, text: 'Aika' } },
                y: { beginAtZero: false }
              }
            }
          });
        } else {
          chartHum.data.labels = labels;
          chartHum.data.datasets[0].data = hums;
          chartHum.update();
        }

        // Make sure both charts size correctly after becoming visible
        chartTemp.resize();
        chartHum.resize();
      })
      .catch(err => {
        console.error('❗ Error fetching/rendering data:', err);
        avgTempEl.textContent = 'Lämpötila: –';
        avgHumEl.textContent  = 'Kosteus: –';
      });
  }

  function openAndRender(location) {
    openModal();
    ensureVisibleThen(() => fetchAndRenderBoth(location));
  }

  // — Wire up modal controls —
  closeBtn.addEventListener('click', closeModal);
  window.addEventListener('click', (e) => {
    if (e.target === modal) closeModal();
  });

  prevBtn.addEventListener('click', () => {
    currentDate = addDays(currentDate, -1);
    openAndRender(currentLocation);
  });
  nextBtn.addEventListener('click', () => {
    currentDate = addDays(currentDate, 1);
    openAndRender(currentLocation);
  });

  // — Tile click → open modal with that location —
  // Assumes tiles like: <div class="tile"><div class="loc">Parveke</div>...</div>
  document.addEventListener('click', (e) => {
    const tile = e.target.closest('.tile');
    if (!tile) return;
    const nameEl = tile.querySelector('.loc');
    if (!nameEl) return;

    currentLocation = nameEl.textContent.trim();
    currentDate     = new Date(); // reset to today (optional)
    openAndRender(currentLocation);
  });

  // Optional: expose a function if you want to call it manually elsewhere
  window.openChartsForLocation = function(name, dateOpt) {
    currentLocation = name;
    if (dateOpt instanceof Date) currentDate = dateOpt;
    openAndRender(currentLocation);
  };

  // Optional: allow runtime control of averaging window
  window.setChartAvgMinutes = function(mins) {
    const n = parseInt(mins, 10);
    averagingMinutes = Number.isFinite(n) && n >= 0 ? n : 0;
    if (currentLocation) ensureVisibleThen(() => fetchAndRenderBoth(currentLocation));
  };
})();
