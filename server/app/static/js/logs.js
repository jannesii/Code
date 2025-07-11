// logs.js
// Simple auto-refresh and filter (expand as needed)
document.addEventListener('DOMContentLoaded', function() {
  // Auto-refresh every 30s
  setInterval(function() {
    window.location.reload();
  }, 30000);

  // Example: filter logs by type
  document.querySelectorAll('.log-type').forEach(function(typeElem) {
    typeElem.addEventListener('click', function() {
      const type = typeElem.textContent;
      document.querySelectorAll('.log-row').forEach(function(row) {
        row.style.display = row.classList.contains(type) ? '' : 'none';
      });
    });
  });

  document.querySelectorAll('.log-timestamp').forEach(function(tsElem) {
    const iso = tsElem.textContent;
    if (!iso) return;
    try {
      // Parse ISO string and format as local date/time
      const date = new Date(iso);
      if (!isNaN(date.getTime())) {
        tsElem.textContent = date.toLocaleString('fi-FI', {
          year: 'numeric', month: '2-digit', day: '2-digit',
          hour: '2-digit', minute: '2-digit', second: '2-digit'
        });
      }
    } catch (e) {}
  });
});
