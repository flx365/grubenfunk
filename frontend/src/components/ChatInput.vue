<template>
  <div class="message-container">
    <textarea
      ref="textareaRef"
      v-model="text"
      @input="autoResize"
      @keydown.enter.exact.prevent="sendMessage"
      @keydown.enter.shift.stop
      placeholder="Nachricht eingeben..."
      class="input"
      rows="1"
    ></textarea>
    <button @click="sendMessage" class="btn">
      Senden
    </button>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted } from 'vue'

const props = defineProps(['roomId', 'userId', 'userName'])
const text = ref("")
const textareaRef = ref(null)

// Passt die Höhe des Textfelds dynamisch an den Inhalt an
const autoResize = () => {
  const el = textareaRef.value
  if (!el) return

  // Höhe kurz auf 'auto' setzen, um die echte scrollHeight zu berechnen (falls Text gelöscht wurde)
  el.style.height = 'auto'
  const maxHeight = 200
  el.style.height = Math.min(el.scrollHeight, maxHeight) + 'px'

  // Scrollbar nur anzeigen, wenn Max-Höhe erreicht ist
  el.style.overflowY = el.scrollHeight > maxHeight ? 'auto' : 'hidden'
}

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

  // Eingabefeld leeren und Größe zurücksetzen
  text.value = ""
  await nextTick()
  autoResize()
}

// Initiale Größenberechnung beim Laden
onMounted(() => {
    autoResize()
})
</script>

<style scoped>
.message-container {
  display: flex;
  gap: 10px;
  margin-top: 20px;
  align-items: flex-end;
}

.input {
  padding: 8px 10px;
  flex: 1;
  border-radius: 6px;
  border: 1px solid #ccc;
  resize: none;
  line-height: 1.35;
  font-family: inherit;
  min-height: 40px;
  max-height: 200px;
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
