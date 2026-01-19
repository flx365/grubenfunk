<script setup>
import ChatInput from '../components/ChatInput.vue'
import {closeWebSocket, createWebSocket} from '../services/websocket.js';
import {onMounted, ref} from 'vue';
import router from "@/router/index.js";

const API_BASE_URL = 'http://127.0.0.1:8000';

const rooms = ref([]);
const messages = ref([]);
const selectedRoomId = ref(null);
const currentUser = ref(null);
const newRoomName = ref("");
const isSidebarOpen = ref(true);

// Räume laden (via Fetch API)
const loadRooms = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/rooms`);
    if (!response.ok) throw new Error('Netzwerk Fehler');
    rooms.value = await response.json();
  } catch (error) {
    console.error("Fehler beim Laden der Räume:", error);
  }
};

// Nachrichten aus Räume laden (via Fetch API)
const selectRoom = async (roomId) => {
  selectedRoomId.value = roomId;
  messages.value = [];
  try {
    const response = await fetch(`${API_BASE_URL}/messages?RoomID=${roomId}`);
    if (!response.ok) throw new Error('Netzwerk Fehler');
    messages.value = await response.json();
  } catch (error) {
    console.error("Fehler beim Laden der Nachrichten:", error);
  }
};

// Neuen Raum erstellen
const createRoom = async () => {
  // Sicherheitscheck
  if (!currentUser.value) return;

  try{
    const response = await fetch(`${API_BASE_URL}/rooms`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name: newRoomName.value,
        user_id: currentUser.value.id
      })
    })

    const data = await response.json();
    console.log("Raum erstellt:", data);
    // Eingabefeld wieder leeren für den nächsten Raum
    newRoomName.value = "";
    // Liste aktualisieren
    await loadRooms();
  }catch(error){
    console.error("Fehler beim Erstellen des Raums:", error);
  }
};

// Logout
const handleLogout = () => {
  localStorage.removeItem("chat_user");
  currentUser.value = null;
  closeWebSocket()
  router.push('/login');
};

const toggleSidebar = () => {
  isSidebarOpen.value = !isSidebarOpen.value;
};

onMounted(() => {
  const storedUser = localStorage.getItem("chat_user");
  if (storedUser) {
    currentUser.value = JSON.parse(storedUser);
    createWebSocket(currentUser.value.id);
  } else {
    router.push('/login');
  }

  loadRooms();
});
</script>

<template>
  <div class="main-container">

    <button
      class="sidebar-toggle"
      @click="toggleSidebar"
    >
      {{ isSidebarOpen ? '<' : '>' }}
    </button>

    <div class="sidebar" :class="{ closed: !isSidebarOpen }">
      <h3>Räume</h3>

      <div class="create-room-section">
        <input
          v-model="newRoomName"
          placeholder="Neuer Raum erstellen..."
          @keyup.enter="createRoom"
        />
        <button @click="createRoom">+</button>
      </div>
      <hr />

      <ul class="rooms-list">
        <li
          v-for="room in rooms"
          :key="room.ID"
          @click="selectRoom(room.ID)"
          class="room-item"
        >
          {{ room.Name }}
        </li>
      </ul>
    </div>

    <div class="chat-area">

      <div v-if="currentUser" class="user-info">
        <span>Account: </span>
        <span class="user-name">{{ currentUser.name }}</span>
        <span class="user-id">#{{ currentUser.id }}</span>
        <span> | </span>
        <button class="btn-logout" @click="handleLogout">
        Abmelden
      </button>
      </div>

      <h3>Chat</h3>

      <div v-if="!selectedRoomId">
        Links einen Raum anklicken.
      </div>

      <div v-else>
        <div
          v-for="msg in messages"
          :key="msg.ID"
          class="message-item"
        >
          <strong>{{ msg.Name }}:</strong> {{ msg.Text }}
        </div>
      </div>

      <div>
        <ChatInput/>
      </div>
    </div>

  </div>
</template>

<style scoped>
.main-container {
  display: flex;
  height: 100vh;
  position: relative;
}

.sidebar {
  width: 240px;
  min-width: 240px;
  border-right: 1px solid black;
  padding: 10px;
  transition: transform 0.25s ease, width 0.25s ease, padding 0.25s ease;
  background: #f8f9fa;
  display: flex;
  flex-direction: column;
}

.sidebar.closed {
  width: 0;
  min-width: 0;
  padding: 10px 0;
  overflow: hidden;
  transform: translateX(-100%);
  border-right: none;
}

.sidebar-toggle {
  position: absolute;
  top: 12px;
  left: 12px;
  z-index: 2;
  background: #343a40;
  color: #f8f9fa;
  border: none;
  border-radius: 4px;
  padding: 6px 8px;
  cursor: pointer;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
}

.sidebar-toggle:hover {
  background: #212529;
}

.create-room-section {
  display: flex;
  gap: 5px;
  margin-bottom: 10px;
}

.create-room-section input {
  flex: 1;
  padding: 4px;
  width: 100%;
}

.chat-area {
  flex: 1;
  padding: 10px;
  overflow-y: auto;
  margin-left: 40px;
}

.rooms-list {
  list-style: none;
  padding: 0;
  margin: 0;
  flex: 1;
  overflow-y: auto;
}

.room-item {
  cursor: pointer;
  margin-bottom: 5px;
  color: blue;
}

.message-item {
  margin-bottom: 10px;
  border-bottom: 1px solid #ccc;
}

.user-info {
  position: absolute;
  top: 15px;
  right: 20px;
  background-color: #e9ecef;
  padding: 5px 12px;
  color: #495057;
  border: 1px solid #dee2e6;
}

.user-name {
  font-weight: bold;
  margin-right: 5px;
}

.user-id {
  color: #888;
  font-size: 0.8rem;
}

.btn-logout {
  background: none;
  border: 1px;
  font-size: 0.75rem;
  cursor: pointer;
  text-decoration: underline;
}

.btn-logout:hover {
  background-color: #dc3545;
  color: black;
}

</style>
