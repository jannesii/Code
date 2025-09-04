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
        const labels = data.map(d => String(d.timestamp).slice(11,19));

        const temps  = data.map(d => Number(d.temperature)).filter(Number.isFinite);
        const hums   = data.map(d => Number(d.humidity)).filter(Number.isFinite);

        const avgT = temps.length ? temps.reduce((a,b)=>a+b,0) / temps.length : NaN;
        const avgH = hums.length  ? hums.reduce((a,b)=>a+b,0)  / hums.length  : NaN;

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
                pointRadius: 2,
                borderWidth: 2
              }]
            },
            options: {
              responsive: true,
              maintainAspectRatio: false,
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
                pointRadius: 2,
                borderWidth: 2
              }]
            },
            options: {
              responsive: true,
              maintainAspectRatio: false,
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
})();
