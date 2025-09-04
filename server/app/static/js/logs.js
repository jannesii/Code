// logs.js
// Simple auto-refresh and filter (expand as needed)
document.addEventListener('DOMContentLoaded', function() {
  // Auto-refresh every 30s
  setInterval(function() {
    window.location.reload();
  }, 30000);

  // Toolbar filter
  const buttons = document.querySelectorAll('.filter-btn');
  function applyFilter(filter) {
    document.querySelectorAll('.log-row').forEach(function(row) {
      if (filter === 'all') {
        row.style.display = '';
      } else {
        row.style.display = row.classList.contains(filter) ? '' : 'none';
      }
    });
    buttons.forEach(b => b.classList.toggle('active', b.dataset.filter === filter));
  }
  buttons.forEach(btn => btn.addEventListener('click', () => applyFilter(btn.dataset.filter)));

  // Still allow clicking the type badge to filter
  document.querySelectorAll('.log-type .badge').forEach(function(badge) {
    badge.addEventListener('click', function() {
      const type = Array.from(badge.classList).find(c => ['info','warning','error'].includes(c));
      if (type) applyFilter(type);
    });
  });

  // Timestamp formatting
  document.querySelectorAll('.log-timestamp').forEach(function(tsElem) {
    const iso = tsElem.dataset.raw || tsElem.textContent;
    if (!iso) return;
    try {
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
