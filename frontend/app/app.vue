<template>
  <div class="layout">
    <header class="topbar">
      <NuxtLink
        to="/"
        class="brand"
      >Clients SPA</NuxtLink>
      <nav
        v-if="user"
        class="nav"
      >
        <span class="user">{{ user.email }} ({{ user.role }})</span>
        <button
          class="btn btn-ghost"
          data-testid="logout"
          @click="logout"
        >
          Log out
        </button>
      </nav>
    </header>
    <main class="main">
      <NuxtPage />
    </main>
  </div>
</template>

<script setup lang="ts">
const { user, logout } = useAuth()
</script>
