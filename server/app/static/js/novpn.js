document.addEventListener('DOMContentLoaded', () => {
  const table = document.querySelector('.nv-table');
  if (!table) return;

  // CSRF token from cookie
  const getCookie = (name) => {
    const m = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
    return m ? m.pop() : '';
  };
  const csrf = getCookie('csrf_token');

  const showStatus = (row, text, ok=true) => {
    const spans = row.querySelectorAll('.nv-status');
    spans.forEach(s => {
      s.textContent = text;
      s.classList.toggle('nv-success', ok);
      s.classList.toggle('nv-error', !ok);
      setTimeout(() => { s.textContent = ''; }, 2000);
    });
  };

  table.addEventListener('change', async (e) => {
    const el = e.target;
    if (!(el instanceof HTMLInputElement)) return;
    if (!el.classList.contains('nv-toggle')) return;
    const row = el.closest('tr');
    const mac = row?.getAttribute('data-mac');
    const field = el.getAttribute('data-field');
    if (!mac || !field) return;
    const value = !!el.checked;

    try {
      const res = await fetch('/api/novpn/update', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrf,
        },
        body: JSON.stringify({ mac, [field]: value }),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok || !data.ok) {
        // revert UI
        el.checked = !value;
        showStatus(row, data.message || 'Tallennus epäonnistui', false);
        return;
      }
      showStatus(row, 'Tallennettu', true);
    } catch (err) {
      el.checked = !value;
      showStatus(row, 'Virhe yhteydessä', false);
    }
  });
});

