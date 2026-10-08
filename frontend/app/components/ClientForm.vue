<template>
  <div
    class="modal-backdrop"
    data-testid="client-form"
    @click.self="$emit('close')"
  >
    <div class="card modal">
      <div class="page-head">
        <h2>{{ client ? 'Edit client' : 'New client' }}</h2>
        <button
          class="btn btn-ghost"
          data-testid="close"
          @click="$emit('close')"
        >
          ✕
        </button>
      </div>

      <form @submit.prevent="onSubmit">
        <label for="c-name">Name</label>
        <input
          id="c-name"
          v-model="form.name"
          required
          maxlength="120"
        >

        <label for="c-email">Email</label>
        <input
          id="c-email"
          v-model="form.email"
          type="email"
          required
          :disabled="!!client"
        >

        <label for="c-phone">Phone</label>
        <input
          id="c-phone"
          v-model="form.phone"
          maxlength="30"
        >

        <label for="c-address">Address</label>
        <input
          id="c-address"
          v-model="form.address"
          maxlength="255"
        >

        <label for="c-notes">Notes</label>
        <textarea
          id="c-notes"
          v-model="form.notes"
          rows="3"
        />

        <label
          v-if="client"
          class="checkbox"
        >
          <input
            v-model="form.is_active"
            type="checkbox"
          > Active
        </label>

        <p
          v-if="error"
          class="error"
          data-testid="form-error"
        >
          {{ error }}
        </p>

        <button
          class="btn btn-primary"
          type="submit"
          :disabled="saving"
        >
          {{ saving ? 'Saving…' : 'Save' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Client } from '~/composables/useAuth'

const props = defineProps<{ client?: Client | null }>()
const emit = defineEmits<{ close: [], saved: [] }>()

const api = useApi()
const error = ref('')
const saving = ref(false)

const form = reactive({
  name: props.client?.name ?? '',
  email: props.client?.email ?? '',
  phone: props.client?.phone ?? '',
  address: props.client?.address ?? '',
  notes: props.client?.notes ?? '',
  is_active: props.client?.is_active ?? true,
})

async function onSubmit() {
  error.value = ''
  saving.value = true
  try {
    const payload = {
      name: form.name,
      phone: form.phone || null,
      address: form.address || null,
      notes: form.notes || null,
    }
    if (props.client) {
      await api.put(`/api/v1/clients/${props.client.id}`, {
        ...payload,
        is_active: form.is_active,
      })
    }
    else {
      await api.post('/api/v1/clients', { ...payload, email: form.email })
    }
    emit('saved')
  }
  catch (e) {
    error.value = (e as Error).message
  }
  finally {
    saving.value = false
  }
}
</script>
