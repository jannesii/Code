// — Socket.IO setup using cookie auth —
console.log('🛠️ Initializing Socket.IO with session cookie');
// Expose a single shared socket instance on window
window.socket = io('/', {
    transports: ['websocket'],
    auth: { role: 'view' }
});

window.addEventListener('beforeunload', () => {
    window.socket && window.socket.disconnect();
});    

window.socket.on('connect_error', err => {
    console.error('Connection error:', err);
});

window.socket.on('connect', () => {
    console.log('✅ Yhdistetty palvelimeen');
})

window.socket.on('server_shutdown', () => {
    console.log('🔒 Server is shutting down...');
    window.socket && window.socket.disconnect();
});
