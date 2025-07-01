// static/js/3d.js

// Initial load
console.log('📦 Dashboard script loaded');

// Wait for DOM to be ready
document.addEventListener('DOMContentLoaded', () => {
    console.log('📑 DOMContentLoaded fired');
  
    // — Socket.IO setup using cookie auth —
    console.log('🛠️ Initializing Socket.IO with session cookie');
    const socket = io('/', {
      transports: ['websocket']
    });

    window.addEventListener('beforeunload', () => {
      socket.disconnect();
    });    

    socket.on('connect_error', err => {
      console.error('Connection error:', err);
    });

    socket.on('connect', () => {
      console.log('✅ Yhdistetty palvelimeen');
    });

    socket.on('image', data => {
      fetch('/api/previewJpg')
        .then(response => response.blob())
        .then(imageBlob => {
          const imageObjectURL = URL.createObjectURL(imageBlob);
          document.querySelector('.image-tile img').src = imageObjectURL;
          console.log('🖼️ Image tile updated');
        })
        .catch(error => {
          console.error('Error fetching image:', error);
        });
      /* console.log('📷 Received image event, data:', data);
      document.querySelector('.image-tile img').src = '/api/previewJpg' //'data:image/jpeg;base64,' + data.image;
      console.log('🖼️ Image tile updated'); */
    });

    // ─── Printer elements ─────────────────────────────────────────
    const bedTempEl      = document.getElementById('bedTemp');
    const nozzleTempEl   = document.getElementById('nozzleTemp');
    const nozzleTypeEl   = document.getElementById('nozzleType');
    const nozzleDiamEl   = document.getElementById('nozzleDiam');
    const printerStatEl  = document.getElementById('printerStatus');
    const gcodeStatEl    = document.getElementById('gcodeStatus');
    const printerStatTile= document.getElementById('printerStatusTile');
    //  ─ progress‑bar DOM elements ─
    const fileNameEl      = document.getElementById('fileName');
    const progPercentEl   = document.getElementById('progressPercent');
    const progBarEl       = document.getElementById('progressBar');
    const layerInfoEl     = document.getElementById('layerInfo');
    const remainingTimeEl = document.getElementById('remainingTime');
    const printSpeedEl    = document.getElementById('printSpeed');
    // ── Timelapse status ──
    const timelapseStatusEl = document.getElementById('timelapseStatus');

    function formatTime(sec){
      const h = Math.floor(sec/3600).toString().padStart(2,'0');
      const m = Math.floor(sec%3600/60).toString().padStart(2,'0');
      const s = Math.floor(sec%60).toString().padStart(2,'0');
      return `${h}:${m}:${s}`;
    }

    socket.on('status2v', data => {
      console.log('ℹ️ Received status2v event:', data);

      if ('bed_temperature'    in data) bedTempEl.textContent    = data.bed_temperature.toFixed(1) + ' °C';
      if ('nozzle_temperature' in data) nozzleTempEl.textContent = data.nozzle_temperature.toFixed(1) + ' °C';
      if ('nozzle_type'        in data) nozzleTypeEl.textContent = data.nozzle_type;
      if ('nozzle_diameter'    in data) nozzleDiamEl.textContent = data.nozzle_diameter + ' mm';
      if ('status'             in data){
        printerStatEl.textContent = data.status;
        printerStatTile.dataset.state = data.status;   // colour via CSS
      }
      if ('gcode_status'       in data){
        gcodeStatEl.textContent  = data.gcode_status;
      }

      // ── progress‑bar update (guard against partially‑filled packets) ──
      if ('percentage' in data){
        progBarEl.style.width   = data.percentage + '%';
        progPercentEl.textContent = data.percentage + ' %';
      }

      if ('file_name' in data) fileNameEl.textContent = data.file_name;

      if ('current_layer' in data && 'total_layers' in data){
        layerInfoEl.textContent = `Layer ${data.current_layer} / ${data.total_layers}`;
      }

      if ('remaining_time' in data){
        remainingTimeEl.textContent = formatTime(data.remaining_time);
      }

      if ('print_speed' in data){
        printSpeedEl.textContent = data.print_speed + ' mm/s';
      }
      // ── Timelapse status ──
      if ('timelapse_status' in data) {
        const isActive = data.timelapse_status === true      // boolean true
                      || data.timelapse_status === 'True';   // string "True" (just in case)

        timelapseStatusEl.innerHTML = isActive
          ? '<button class="control-btn-status start-btn">Active</button>'
          : '<button class="control-btn-status stop-btn">Inactive</button>';
      }
    });

    socket.on('temphum2v', data => {
      console.log('🌡️ Received temphum2v event, data:', data);
      document.getElementById('temperature').innerText = data.temperature + '°C';
      document.getElementById('humidity').innerText    = data.humidity + '%';
      console.log('🌡️ Temperature/Humidity updated:', data.temperature, data.humidity);
    });
    
    // ── printer control buttons ─
    document.querySelectorAll('.control-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        var body = {};
        const action = btn.dataset.action;
        body.action = action;  // unified action name
        if (action == 'run_gcode') {
          const gcodeInput = document.getElementById('gcodeInput').value.trim();
          body.gcode = gcodeInput;
        } 
        console.log(`🔘 "${action}" button clicked`);
        socket.emit('printerAction', body); 
      });
    });
    // ─── G‑code autocomplete ──────────────────────────────────────
    const gcodeInput  = document.getElementById('gcodeInput');
    const suggestBox  = document.getElementById('gcodeSuggest');
    let   gcodeCache  = [];

    // one fetch at startup
    fetch('/api/gcode')
      .then(r => r.json())
      .then(data => { gcodeCache = data.gcode_list || []; })
      .catch(err => console.error('⚠️ Could not load /api/gcode:', err));

    /* helpers ----------------------------------------------------- */
    function closeSuggest(){ suggestBox.style.display='none'; }
    function showSuggest(items){
      suggestBox.innerHTML = items
        .map(cmd => `<li class="autocomplete-item">${cmd}</li>`).join('');
      suggestBox.style.display = items.length ? 'block' : 'none';
    }

    /* replace the partial word before caret with full command */
    function insertCmd(cmd){
      const {selectionStart:pos, value:txt} = gcodeInput;
      const before = txt.slice(0,pos);
      const after  = txt.slice(pos);
      const chunks = before.split(/\n/);          // last line only
      chunks[chunks.length-1] = cmd;              // replace partial
      gcodeInput.value = chunks.join('\n') + after;
      gcodeInput.focus();
      closeSuggest();
    }

    /* main listener ---------------------------------------------- */
    gcodeInput.addEventListener('input', () => {
      const {selectionStart:pos, value:txt} = gcodeInput;
      const before = txt.slice(0,pos);
      const last   = before.split(/\n/).pop().trim().toUpperCase();

      if(!last){ closeSuggest(); return; }

      const hits = gcodeCache
                    .filter(c => c.toUpperCase().startsWith(last))
                    .slice(0,10);                // top‑10 only
      showSuggest(hits);
    });

    /* click‑to‑choose */
    suggestBox.addEventListener('click', e => {
      if(e.target.classList.contains('autocomplete-item')){
        insertCmd(e.target.textContent);
      }
    });

    /* basic up/down/enter navigation */
    gcodeInput.addEventListener('keydown', e => {
      const active = suggestBox.querySelector('.active');
      let next;
      if(e.key==='ArrowDown'){
        next = active ? active.nextSibling : suggestBox.firstChild;
      }else if(e.key==='ArrowUp'){
        next = active ? active.previousSibling : suggestBox.lastChild;
      }else if(e.key==='Enter' && active){
        e.preventDefault();
        insertCmd(active.textContent);
        return;
      }else{
        return; // let other keys through
      }
      if(active) active.classList.remove('active');
      if(next){ next.classList.add('active'); }
    });

    /* hide list when focus leaves */
    gcodeInput.addEventListener('blur', () => setTimeout(closeSuggest,150));


    // — Chart.js modal logic —
    const modal       = document.getElementById('chartModal');
    const titleEl     = document.getElementById('chartTitle');
    const dateEl      = document.getElementById('currentDate');
    const prevBtn     = document.getElementById('prevDay');
    const nextBtn     = document.getElementById('nextDay');
    const closeBtn    = document.getElementById('closeModal');
    const avgTempEl   = document.getElementById('avgTemp');
    const avgHumEl    = document.getElementById('avgHum');
    const ctx         = document.getElementById('chartCanvas').getContext('2d');
    let currentDate   = new Date();
    let currentField  = 'temperature';
    let chartInstance = null;
  
    function formatDate(d) {
      const iso = d.toISOString().split('T')[0];
      console.log('🗓️ formatDate:', iso);
      return iso;
    }

    function openModal() {
      console.log('🔍 Opening chart modal');
      modal.style.display = 'flex';
    }
    function closeModal() {
      console.log('❌ Closing chart modal');
      modal.style.display = 'none';
    }
  
    function fetchAndRender(field) {
      const dateStr = formatDate(currentDate);
      console.log('🚀 fetchAndRender, field:', field, 'date:', dateStr);

      dateEl.textContent = dateStr;
      titleEl.textContent = field==='temperature'
        ? `Lämpötila (${dateStr})`
        : `Kosteus (${dateStr})`;
      console.log('🏷️ Modal title set:', titleEl.textContent);
  
      console.log('🔗 Fetching /api/temphum?date=' + dateStr);
      fetch(`/api/temphum?date=${dateStr}`)
        .then(r => {
          console.log('📥 Fetch response status:', r.status);
          return r.json();
        })
        .then(data => {
          console.log('📊 Data received for chart:', data);

          const labels = data.map(d => d.timestamp.slice(11,19));
          const values = data.map(d => d[field]);
  
          // compute averages
          const temps = data.map(d => d.temperature);
          const hums  = data.map(d => d.humidity);
          const avgT = temps.length ? (temps.reduce((a,b)=>a+b,0)/temps.length) : NaN;
          const avgH = hums.length  ? (hums.reduce((a,b)=>a+b,0)/hums.length)  : NaN;

          console.log(`📈 Computed avgT=${avgT.toFixed(1)}, avgH=${avgH.toFixed(1)}`);
  
          avgTempEl.textContent = temps.length
            ? `Lämpötila: ${avgT.toFixed(1)}°C`
            : 'Lämpötila: –';
          avgHumEl.textContent  = hums.length
            ? `Kosteus: ${avgH.toFixed(1)}%`
            : 'Kosteus: –';
          console.log('🏷️ Avg elements updated');

          if (!chartInstance) {
            console.log('📊 Initializing new Chart.js instance');
            chartInstance = new Chart(ctx, {
              type: 'line',
              data: {
                labels,
                datasets: [{
                  label: field==='temperature' ? '°C' : '%',
                  data: values,
                  fill: false,
                }]
              },
              options: {
                scales: {
                  x: { display: true, title: { display: true, text: 'Aika' } },
                  y: { beginAtZero: true }
                }
              }
            });
          } else {
            console.log('🔄 Updating existing Chart.js instance');
            chartInstance.data.labels                    = labels;
            chartInstance.data.datasets[0].data         = values;
            chartInstance.data.datasets[0].label        = field==='temperature' ? '°C' : '%';
            chartInstance.update();
          }
        })
        .catch(err => console.error('❗ Error fetching/rendering data:', err));
    }
  
    // Tile click handlers
    document.getElementById('tempTile').addEventListener('click', () => {
      console.log('🎯 tempTile clicked');
      currentField = 'temperature';
      currentDate  = new Date();
      openModal();
      fetchAndRender(currentField);
    });
    document.getElementById('humTile').addEventListener('click', () => {
      console.log('🎯 humTile clicked');
      currentField = 'humidity';
      currentDate  = new Date();
      openModal();
      fetchAndRender(currentField);
    });
  
    // Prev/Next day
    prevBtn.addEventListener('click', () => {
      console.log('⬅️ prevDay clicked, before:', currentDate.toISOString());
      currentDate.setDate(currentDate.getDate() - 1);
      console.log('⬅️ new currentDate:', currentDate.toISOString());
      fetchAndRender(currentField);
    });
    nextBtn.addEventListener('click', () => {
      console.log('➡️ nextDay clicked, before:', currentDate.toISOString());
      currentDate.setDate(currentDate.getDate() + 1);
      console.log('➡️ new currentDate:', currentDate.toISOString());
      fetchAndRender(currentField);
    });
  
    // Close modal
    closeBtn.addEventListener('click', closeModal);
    window.addEventListener('click', e => {
      console.log('🌐 Window click event:', e.target);
      if (e.target === modal) {
        closeModal();
      }
    });
});
