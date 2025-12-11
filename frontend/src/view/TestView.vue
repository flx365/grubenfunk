<script setup>
import { useRouter } from 'vue-router'
import {ref, onMounted} from "vue";

const router = useRouter()
const goToChat = () => {
  router.push('/chat')
}

const backendResponse = ref(null)

onMounted(async () => {
  try {
    const response = await fetch('http://localhost:8000/')
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
  <div class="container mt-4"> <div class="mb-4">
      <button @click="goToChat" class="btn btn-primary">
        Zum Chat gehen
      </button>
    </div>
  </div>
</template>

<style scoped>

</style>