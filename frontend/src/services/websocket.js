let socket = null;

const createWebSocket = (userId) => {
  // WebSocket Verbindung aufbauen
  socket = new WebSocket(`ws://127.0.0.1:8000/ws/${userId}`);
  // Event-Handler für WebSocket Ereignisse
  socket.onopen = () => {
    console.log("WebSocket Verbindung geöffnet");
  };
  socket.onclose = () => {
    console.log("WebSocket Verbindung geschlossen");
  };
  socket.onerror = (error) => {
    console.log("WebSocket Fehler:", error);
  };
};

// WebSocket trennen
const closeWebSocket = () => {
  if (socket) {
    socket.close();
    socket = null;
  }
};

export { createWebSocket, closeWebSocket };
