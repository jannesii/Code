// static/js/dashboard.js

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

    socket.on('image2v', data => {
      console.log('📷 Received image2v event, data:', data);
      document.querySelector('.image-tile img').src = 'data:image/jpeg;base64,' + data.image;
      console.log('🖼️ Image tile updated');
    });

    socket.on('status2v', data => {
      console.log('ℹ️ Received status2v event, data:', data);
      document.getElementById('status').innerText = data.status;
      console.log('🏷️ Status text set to:', data.status);
    });

    socket.on('temphum2v', data => {
      console.log('🌡️ Received temphum2v event, data:', data);
      document.getElementById('temperature').innerText = data.temperature + '°C';
      document.getElementById('humidity').innerText    = data.humidity + '%';
      console.log('🌡️ Temperature/Humidity updated:', data.temperature, data.humidity);
    });
  
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
