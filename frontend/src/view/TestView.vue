<script setup>
import { ref, onMounted } from 'vue'

const backendResponse = ref(null)

onMounted(async () => {
  try {
    const response = await fetch('http://127.0.0.1:8000/')
    if (response.ok) {
      backendResponse.value = await response.json()
    } else {
      backendResponse.value = { error: 'Failed to fetch data from backend' }
    }
  } catch (error) {
    backendResponse.value = { error: 'Failed to connect to backend' }
  }
})
</script>

<template>
  <div v-if="backendResponse">
    <h2>Backend Response:</h2>
    <pre>{{ backendResponse }}</pre>
  </div>
</template>

<style scoped>

</style>