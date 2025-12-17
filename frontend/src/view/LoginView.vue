<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const username = ref('')
const loading = ref(false)
const error = ref(null)


const handleLogin = async () => {
  //Leere Eingabe verhindern
  if (!username.value.trim()) {
    error.value = "Bitte einen Namen eingeben.";
    return;
  }

  loading.value = true;
  error.value = null;

  try {
    // User im Backend anlegen (POST an Python)
    const response = await fetch("http://localhost:8000/user", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        username: username.value
      })
    });
    const data = await response.json();
    // Prüfen ob wir eine ID zurückbekommen haben
    if (data.ID) {
      // User Daten speichern für die ChatView
      const userObject = {
        id: data.ID,
        name: username.value
      };
      localStorage.setItem("chat_user", JSON.stringify(userObject));
      // Weiterleitung zum Chat
      await router.push('/chat');
    } else {
      console.error("Server Antwort:", data);
      error.value = "Fehler: Konnte User nicht anlegen.";
    }
  } catch (e) {
    console.error(e);
    error.value = "Verbindung zum Server fehlgeschlagen.";
  } finally {
    loading.value = false;
  }
};
</script>

<template>
  <div class="login-page">
    <div class="card">
      <h2>Willkommen</h2>

      <div class="input-group username-group">
        <label for="username">Username</label>
        <input
          id="username"
          v-model="username"
          @keyup.enter="handleLogin"
          type="text"
          placeholder="Username"
          :disabled="loading"
        />
      </div>

      <button type="button"
              class="btn btn-primary w-100"
              @click="handleLogin">
        Chat betreten</button>
    </div>
  </div>
</template>

<style scoped>
.login-page {
  font-family: Arial, sans-serif;
  background: #f2f4f8;
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
}

.card {
  background: #ffffff;
  width: 360px;
  padding: 40px 32px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

h2 {
  text-align: center;
  margin-bottom: 8px;
  font-size: 28px;
}

.input-group {
  margin-bottom: 18px;
}

.input-group label {
  display: block;
  margin-bottom: 6px;
  font-size: 14px;
  color: #555;
}

.input-group input {
  width: 100%;
  padding: 12px;
  font-size: 15px;
  border: 1px solid #dcdcdc;
  border-radius: 0px;
  outline: none;
}

.input-group input:focus {
  border-color: #5b6bff;
}

.btn {
  border-radius: 0;
}

</style>