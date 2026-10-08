<template>
  <table class="table">
    <thead>
      <tr>
        <th>Name</th>
        <th>Email</th>
        <th>Phone</th>
        <th>Status</th>
        <th class="actions">
          Actions
        </th>
      </tr>
    </thead>
    <tbody>
      <tr v-if="loading">
        <td
          colspan="5"
          class="empty"
        >
          Loading…
        </td>
      </tr>
      <tr v-else-if="clients.length === 0">
        <td
          colspan="5"
          class="empty"
        >
          No clients found
        </td>
      </tr>
      <tr
        v-for="client in clients"
        :key="client.id"
        data-testid="client-row"
      >
        <td>
          <NuxtLink
            :to="`/clients/${client.id}`"
            class="link"
          >{{ client.name }}</NuxtLink>
        </td>
        <td>{{ client.email }}</td>
        <td>{{ client.phone || '—' }}</td>
        <td>
          <span
            class="badge"
            :class="client.is_active ? 'badge-ok' : 'badge-off'"
          >
            {{ client.is_active ? 'Active' : 'Inactive' }}
          </span>
        </td>
        <td class="actions">
          <button
            class="btn btn-ghost"
            data-testid="edit"
            @click="$emit('edit', client)"
          >
            Edit
          </button>
          <button
            class="btn btn-danger"
            data-testid="delete"
            @click="$emit('delete', client)"
          >
            Delete
          </button>
        </td>
      </tr>
    </tbody>
  </table>
</template>

<script setup lang="ts">
import type { Client } from '~/composables/useAuth'

defineProps<{
  clients: Client[]
  loading: boolean
}>()

defineEmits<{
  edit: [client: Client]
  delete: [client: Client]
}>()
</script>
