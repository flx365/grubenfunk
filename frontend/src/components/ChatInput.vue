<template>
  <div class="message-container">
    <input
      v-model="text"
      type="text"
      placeholder="Nachricht eingeben..."
      class="input"
    />
    <button @click="sendMessage" class="btn">
      Senden
    </button>

    <p v-if="response">{{ response }}</p>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const text = ref("")
const response = ref(null)

async function sendMessage() {
  if (!text.value) return

  const res = await fetch("http://localhost:8000/message", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      text: text.value
    })
  })

  const data = await res.json()
  response.value = "Server Antwort: " + JSON.stringify(data)
  text.value = ""  // Eingabefeld leeren nach dem Senden
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
