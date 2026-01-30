<template>
  <div class="message-container">
    <input
      v-model="text"
      @keyup.enter="sendMessage"
      placeholder="Nachricht eingeben..."
      class="input"
    />
    <button @click="sendMessage" class="btn">
      Senden
    </button>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps(['roomId', 'userId', 'userName'])
const text = ref("")

async function sendMessage() {
  if (!text.value.trim() || !props.roomId || !props.userId) return

  // HTTP POST an Backend
  await fetch("http://127.0.0.1:8000/message", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      text: text.value,
      room_id: props.roomId,
      user_id: props.userId,
      username: props.userName
    })
  })
  text.value = ""
}
</script>

<style scoped>
.message-container {
  display: flex;
  gap: 10px;
  margin-top: 20px;
}

.input {
  padding: 8px;
  flex: 1;
  border-radius: 4px;
  border: 1px solid #ccc;
}

.btn {
  padding: 8px 14px;
  background: #42b983;
  border: none;
  color: white;
  border-radius: 4px;
  cursor: pointer;
}
</style>
