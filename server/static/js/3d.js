// static/js/dashboard.js

// Wait for DOM to be ready
document.addEventListener('DOMContentLoaded', () => {
    // Read the API key we exposed on window
    const API_KEY = window.API_KEY;
    if (!API_KEY) {
      console.error('API key puuttuu!');
      return;
    }
  
    // — Socket.IO setup —
    const socket = io('/', {
      auth: { api_key: API_KEY },
      transports: ['websocket','polling']
    });
    socket.on('connect_error', err => console.error('Connection error:', err));
    socket.on('connect', () => console.log('✅ Yhdistetty palvelimeen'));
    socket.on('image2v', data => {
      console.log('Received image data.');
      document.querySelector('.image-tile img').src = 'data:image/jpeg;base64,' + data.image;
    });
    socket.on('status2v', data => {
      console.log('Received status data.');
      document.getElementById('status').innerText = data.status;
    });
    socket.on('temphum2v', data => {
      console.log('Received temperature/humidity data.');
      document.getElementById('temperature').innerText = data.temperature + '°C';
      document.getElementById('humidity').innerText = data.humidity + '%';
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
      return d.toISOString().split('T')[0];
    }
    function openModal() { modal.style.display = 'flex'; }
    function closeModal() { modal.style.display = 'none'; }
  
    function fetchAndRender(field) {
      const dateStr = formatDate(currentDate);
      dateEl.textContent = dateStr;
      titleEl.textContent = field==='temperature'
        ? `Lämpötila (${dateStr})`
        : `Kosteus (${dateStr})`;
  
      fetch(`/api/temphum?date=${dateStr}`)
        .then(r => r.json())
        .then(data => {
          const labels = data.map(d => d.timestamp.slice(11,19));
          const values = data.map(d => d[field]);
  
          // compute averages
          const temps = data.map(d => d.temperature);
          const hums  = data.map(d => d.humidity);
          const avgT = temps.length ? (temps.reduce((a,b)=>a+b,0)/temps.length) : NaN;
          const avgH = hums.length  ? (hums.reduce((a,b)=>a+b,0)/hums.length) : NaN;
  
          avgTempEl.textContent = temps.length
            ? `Lämpötila: ${avgT.toFixed(1)}°C`
            : 'Lämpötila: –';
          avgHumEl.textContent  = hums.length
            ? `Kosteus: ${avgH.toFixed(1)}%`
            : 'Kosteus: –';
  
          if (!chartInstance) {
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
            chartInstance.data.labels = labels;
            chartInstance.data.datasets[0].data = values;
            chartInstance.data.datasets[0].label = field==='temperature' ? '°C' : '%';
            chartInstance.update();
          }
        });
    }
  
    // Tile click handlers
    document.getElementById('tempTile').addEventListener('click', () => {
      currentField = 'temperature';
      currentDate  = new Date();
      openModal();
      fetchAndRender(currentField);
    });
    document.getElementById('humTile').addEventListener('click', () => {
      currentField = 'humidity';
      currentDate  = new Date();
      openModal();
      fetchAndRender(currentField);
    });
  
    // Prev/Next day
    prevBtn.addEventListener('click', () => {
      currentDate.setDate(currentDate.getDate() - 1);
      fetchAndRender(currentField);
    });
    nextBtn.addEventListener('click', () => {
      currentDate.setDate(currentDate.getDate() + 1);
      fetchAndRender(currentField);
    });
  
    // Close modal
    closeBtn.addEventListener('click', closeModal);
    window.addEventListener('click', e => {
      if (e.target === modal) closeModal();
    });
  });
  