/* ─────────────────────────────── flash helpers ────────────────────────── */
function getOrCreateFlashContainer () {
  // 1.  Use an already‑rendered container if it exists …
  let container = document.querySelector('.flash-container');
  if (container) return container;

  // 2.  Otherwise create one **and put it in the same spot**
  //     where the template normally renders it: just before
  //     the main ".container" dashboard wrapper.
  container = document.createElement('div');
  container.className = 'flash-container';
  container.style.maxWidth = '800px';
  container.style.margin  = '20px auto';

  // insert before the dashboard so the visual order stays identical
  const dashboard = document.querySelector('.container');
  if (dashboard && dashboard.parentNode) {
    dashboard.parentNode.insertBefore(container, dashboard);
  } else {
    // (fallback) append to body—shouldn’t normally happen
    document.body.appendChild(container);
  }
  return container;
}
function clearFlash (flash, container) {
  flash.remove();
  if (container.children.length === 0) {
    container.remove();
  }
}


function showFlash (category = 'info', message = '') {
  const container = getOrCreateFlashContainer();

  const flash = document.createElement('div');
  flash.className = `flash ${category}`;    // e.g. "flash success"
  flash.textContent = message;
  container.appendChild(flash);

  // auto‑dismiss after 3 s (same as server‑rendered flashes)
  setTimeout(() => clearFlash(flash, container), 3000);
}

/* ───────────────────── Socket.IO listener ───────────────────────────────
   Backend should emit something like:
   socketio.emit('flash', {'category': 'success', 'message': 'Print paused'})
*/
window.socket = window.socket || io('/', { transports: ['websocket'], auth: { role: 'view' } });  // make one if it doesn’t exist
window.addEventListener('beforeunload', () => window.socket && window.socket.disconnect());

window.socket.on('flash', ({ category, message }) => {
  console.log('💬 flash:', category, message);
  showFlash(category, message);
});
