<template>
  <template v-if="bracket.data?.enable_dev_login && players.data?.length">
    <span class="text-xs text-green-800">login as:</span>
    <select
      class="border-zinc-800 bg-zinc-950 border px-2 py-0.5 text-xs text-green-300 outline-none focus:border-green-400"
      :value="sessionUser || ''"
      @change="loginAs(($event.target as HTMLSelectElement).value)"
    >
      <option value="" disabled class="bg-zinc-900 text-green-700">
        {{ sessionUser || 'guest' }}
      </option>
      <option
        v-for="p in players.data"
        :key="p.name"
        :value="p.user"
        class="bg-zinc-900"
      >
        {{ p.player_name || p.user }}
      </option>
    </select>
    <span v-if="loggingIn" class="animate-pulse text-xs text-green-700"
      >...</span
    >
  </template>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { sessionUser } from '@/data/session'
import { useTournament } from '@/data/useTournament'

const { bracket, players } = useTournament()
const loggingIn = ref(false)

async function loginAs(email: string) {
  if (!email || email === sessionUser.value) return
  loggingIn.value = true
  try {
    await window.fetch('/api/method/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ usr: email, pwd: '123' }),
    })
    window.location.reload()
  } catch {
    loggingIn.value = false
  }
}
</script>
