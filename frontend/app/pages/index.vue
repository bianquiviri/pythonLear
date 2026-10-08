<template>
  <div>
    <div class="page-head">
      <h1>Clients</h1>
      <button
        class="btn btn-primary"
        data-testid="new-client"
        @click="showForm = true"
      >
        + New client
      </button>
    </div>

    <div class="toolbar">
      <input
        v-model="search"
        class="search"
        type="search"
        placeholder="Search by name, email or phone…"
        data-testid="search"
        @input="onSearch"
      >
      <span
        v-if="meta"
        class="count"
      >{{ meta.total }} clients</span>
    </div>

    <ClientTable
      :clients="clients"
      :loading="loading"
      @edit="openEdit"
      @delete="onDelete"
    />

    <div
      v-if="meta && meta.pages > 1"
      class="pager"
    >
      <button
        class="btn btn-ghost"
        :disabled="meta.page <= 1"
        @click="goTo(meta.page - 1)"
      >
        ← Prev
      </button>
      <span>Page {{ meta.page }} of {{ meta.pages }}</span>
      <button
        class="btn btn-ghost"
        :disabled="meta.page >= meta.pages"
        @click="goTo(meta.page + 1)"
      >
        Next →
      </button>
    </div>

    <ClientForm
      v-if="showForm"
      :client="editing"
      @close="showForm = false"
      @saved="onSaved"
    />
  </div>
</template>

<script setup lang="ts">
import type { Client, PageMeta } from '~/composables/useAuth'

definePageMeta({ middleware: 'auth' })

const api = useApi()
const clients = ref<Client[]>([])
const meta = ref<PageMeta | null>(null)
const search = ref('')
const page = ref(1)
const loading = ref(false)
const showForm = ref(false)
const editing = ref<Client | null>(null)
let searchTimer: ReturnType<typeof setTimeout> | undefined

async function load() {
  loading.value = true
  try {
    const query = new URLSearchParams({ page: String(page.value), per_page: '10' })
    if (search.value)
      query.set('search', search.value)
    const res = await api.get<{ items: Client[], meta: PageMeta }>(`/api/v1/clients?${query}`)
    clients.value = res.items
    meta.value = res.meta
  }
  finally {
    loading.value = false
  }
}

function onSearch() {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    page.value = 1
    load()
  }, 300)
}

function goTo(p: number) {
  page.value = p
  load()
}

function openEdit(client: Client) {
  editing.value = client
  showForm.value = true
}

async function onSaved() {
  showForm.value = false
  editing.value = null
  await load()
}

async function onDelete(client: Client) {
  if (!confirm(`Delete client "${client.name}"?`))
    return
  await api.remove(`/api/v1/clients/${client.id}`)
  await load()
}

onMounted(load)
</script>
