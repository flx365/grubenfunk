<script setup>
import ChatInput from '../components/ChatInput.vue'
import {onMounted, ref} from 'vue';
import router from "@/router/index.js";

const API_BASE_URL = 'http://127.0.0.1:8000';

const rooms = ref([]);
const messages = ref([]);
const selectedRoomId = ref(null);
const currentUser = ref(null);

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

// Logout
const handleLogout = () => {
  localStorage.removeItem("chat_user");
  currentUser.value = null;
  router.push('/login');
};

onMounted(() => {
  const storedUser = localStorage.getItem("chat_user");
  if (storedUser) {
    currentUser.value = JSON.parse(storedUser);
  } else {
    router.push('/login');
  }

  loadRooms();
});
</script>

<template>
  <div class="main-container">

    <div class="sidebar">
      <h3>Räume</h3>
      <ul>
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
}

.sidebar {
  width: 200px;
  border-right: 1px solid black;
  padding: 10px;
}

.chat-area {
  flex: 1;
  padding: 10px;
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
