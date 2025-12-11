<script setup>
import ChatInput from '../components/ChatInput.vue'
import { ref, onMounted } from 'vue';

//TODO: .env Datei erstellen
//TODO: echte URL und API-Key eintragen
const API_BASE_URL = '...';
const API_KEY = '...';

const rooms = ref([]);
const messages = ref([]);
const selectedRoomId = ref(null);

// Räume laden
const loadRooms = () => {
  var req = new XMLHttpRequest();
  req.onreadystatechange = function () {
    if (req.readyState == 4 && req.status == 200) {
      var data = JSON.parse(req.responseText);
      rooms.value = data;
    }
  }
  req.open("GET", API_BASE_URL + "/rooms");
  req.setRequestHeader("Content-Type", "application/json");
  req.setRequestHeader("api-key", API_KEY);
  req.send();
};

// Nachrichten aus Räume laden
const selectRoom = (roomId) => {
  selectedRoomId.value = roomId;
  messages.value = [];

  var req = new XMLHttpRequest();
  req.onreadystatechange = function () {
    if (req.readyState == 4 && req.status == 200) {
      var data = JSON.parse(req.responseText);
      messages.value = data;
    }
  }
  req.open("GET", API_BASE_URL + "/messages?RoomID=" + roomId);
  req.setRequestHeader("Content-Type", "application/json");
  req.setRequestHeader("api-key", API_KEY);
  req.send();
};

onMounted(() => {
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
</style>
