<template>
  <div class="card login-card">
    <h1>Sign in</h1>
    <form
      data-testid="login-form"
      @submit.prevent="onSubmit"
    >
      <label for="email">Email</label>
      <input
        id="email"
        v-model="email"
        type="email"
        required
        autocomplete="username"
      >

      <label for="password">Password</label>
      <input
        id="password"
        v-model="password"
        type="password"
        required
        autocomplete="current-password"
      >

      <p
        v-if="error"
        class="error"
        data-testid="login-error"
      >
        {{ error }}
      </p>

      <button
        class="btn btn-primary"
        type="submit"
        :disabled="loading"
      >
        {{ loading ? 'Signing in…' : 'Sign in' }}
      </button>
    </form>
    <p class="hint">
      Demo: check the seeded admin credentials in <code>.env</code>
    </p>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: 'auth' })

const { login } = useAuth()
const email = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

async function onSubmit() {
  error.value = ''
  loading.value = true
  try {
    await login(email.value, password.value)
    await navigateTo('/')
  }
  catch (e) {
    const apiError = e as { status?: number, message?: string }
    error.value = apiError.status === 401 ? 'Invalid email or password' : (apiError.message ?? 'Login failed')
  }
  finally {
    loading.value = false
  }
}
</script>
