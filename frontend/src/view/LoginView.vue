<script setup>

</script>

<template>
  <div class="login-page">
    <div class="card">
      <h2>Anmelden</h2>

      <div class="input-group username-group">
        <label for="username">Username</label>
        <input
          id="username"
          type="text"
          placeholder="Username"
        />
      </div>

      <div class="input-group password-group">
        <label for="password">Password</label>
        <input
          id="password"
          type="password"
          placeholder="Password"
        />
      </div>

      <button type="button" class="btn btn-primary w-100">Anmelden</button>

      <div class="footer">
        Noch kein Konto?
        <router-link to="/register" class="link">Jetzt registrieren</router-link>
      </div>
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

.password-group {
  position: relative;
}

.link {
  text-decoration: none;
  color: #4a5cff;
}

.btn {
  border-radius: 0;
}

.footer {
  text-align: center;
  margin-top: 18px;
  font-size: 14px;
}

.footer .link {
  margin-left: 4px;
}
</style>