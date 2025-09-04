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
})

socket.on('server_shutdown', () => {
    console.log('🔒 Server is shutting down...');
    socket.disconnect();
});