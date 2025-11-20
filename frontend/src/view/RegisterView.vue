<script setup>
</script>


<template>
  <div class="register-page">
    <h2>Registrieren</h2>
    <router-link to="/login" class="link">Zurück zum Login</router-link>
  </div>
</template>

<style scoped>
.register-page {
  font-family: Arial, sans-serif;
  background: #f2f4f8;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

h2 {
  text-align: center;
  margin-bottom: 8px;
  font-size: 28px;
}

.link {
  text-decoration: none;
  color: #4a5cff;
  margin-top: 20px;
}
</style>