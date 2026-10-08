<template>
  <div
    v-if="client"
    class="detail"
  >
    <div class="page-head">
      <h1>{{ client.name }}</h1>
      <NuxtLink
        to="/"
        class="btn btn-ghost"
      >← Back</NuxtLink>
    </div>

    <div class="card">
      <dl class="fields">
        <dt>Email</dt>
        <dd>{{ client.email }}</dd>
        <dt>Phone</dt>
        <dd>{{ client.phone || '—' }}</dd>
        <dt>Address</dt>
        <dd>{{ client.address || '—' }}</dd>
        <dt>Notes</dt>
        <dd>{{ client.notes || '—' }}</dd>
        <dt>Status</dt>
        <dd>
          <span
            class="badge"
            :class="client.is_active ? 'badge-ok' : 'badge-off'"
          >
            {{ client.is_active ? 'Active' : 'Inactive' }}
          </span>
        </dd>
        <dt>Created</dt>
        <dd>{{ new Date(client.created_at).toLocaleDateString() }}</dd>
      </dl>

      <button
        class="btn btn-primary"
        @click="editing = true"
      >
        Edit
      </button>
    </div>

    <ClientForm
      v-if="editing"
      :client="client"
      @close="editing = false"
      @saved="onSaved"
    />
  </div>
  <div
    v-else-if="error"
    class="card error"
  >
    {{ error }}
  </div>
  <div
    v-else
    class="card"
  >
    Loading…
  </div>
</template>

<script setup lang="ts">
import type { Client } from '~/composables/useAuth'

definePageMeta({ middleware: 'auth' })

const route = useRoute()
const api = useApi()
const client = ref<Client | null>(null)
const error = ref('')
const editing = ref(false)

async function load() {
  error.value = ''
  try {
    client.value = await api.get<Client>(`/api/v1/clients/${route.params.id}`)
  }
  catch (e) {
    error.value = (e as Error).message
  }
}

function onSaved() {
  editing.value = false
  load()
}

onMounted(load)
</script>
