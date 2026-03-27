<template>
  <div class="flex min-h-screen flex-col bg-term-bg font-mono text-green-200">
    <!-- Header -->
    <div class="relative border-b border-term-border bg-term-surface px-8 py-4">
      <div class="text-xs uppercase tracking-widest text-green-700">
        // codeoff
      </div>
      <div class="text-2xl font-bold tracking-tight text-green-300">
        spectate
      </div>
      <!-- Dev login-as: only shown when enable_dev_login flag is set -->
      <div
        v-if="bracket.data?.enable_dev_login && players.data?.length"
        class="absolute right-4 top-1/2 flex -translate-y-1/2 items-center gap-2"
      >
        <span class="text-xs text-green-800">login as:</span>
        <select
          class="border border-term-border bg-term-bg px-2 py-1 text-xs text-green-300 outline-none focus:border-term-green"
          :value="sessionUser || ''"
          @change="loginAs(($event.target as HTMLSelectElement).value)"
        >
          <option value="" disabled class="bg-term-surface text-green-700">
            {{ sessionUser || 'guest' }}
          </option>
          <option
            v-for="p in players.data"
            :key="p.name"
            :value="p.user"
            class="bg-term-surface"
          >
            {{ p.player_name || p.user }}
          </option>
        </select>
        <span v-if="loggingIn" class="animate-pulse text-xs text-green-700">...</span>
      </div>
    </div>

    <!-- Loading -->
    <div
      v-if="loading"
      class="flex flex-1 items-center justify-center text-sm text-green-800"
    >
      <span class="animate-pulse">loading matches...</span>
    </div>

    <!-- Empty -->
    <div
      v-else-if="!matches.length"
      class="flex flex-1 items-center justify-center"
    >
      <div class="text-center">
        <div class="mb-2 text-4xl text-green-900">_</div>
        <div class="text-sm uppercase tracking-widest text-green-800">
          no live matches
        </div>
        <div class="mt-1 text-xs text-green-900">check back soon</div>
      </div>
    </div>

    <!-- Match list -->
    <div v-else class="mx-auto w-full max-w-2xl px-6 py-8">
      <div class="mb-6 text-xs uppercase tracking-widest text-green-700">
        {{ matches.length }} match{{ matches.length === 1 ? '' : 'es' }} in
        progress
      </div>
      <div class="flex flex-col gap-3">
        <button
          v-for="m in matches"
          :key="m.name"
          class="hover:bg-green-950/30 group w-full border border-term-border bg-term-surface p-4 text-left transition-colors hover:border-green-600"
          @click="
            $router.push({ name: 'Spectate', params: { matchId: m.name } })
          "
        >
          <div class="mb-2 flex items-center justify-between">
            <span
              class="text-xs font-bold uppercase tracking-widest"
              :class="
                m.status === 'Live' ? 'text-term-green' : 'text-green-700'
              "
            >
              {{ m.status === 'Live' ? '● LIVE' : '○ LOBBY' }}
            </span>
            <span class="text-xs text-green-800">
              R{{ m.round_number }} · M{{ m.bracket_position }}
            </span>
          </div>
          <div class="flex items-center gap-3">
            <span class="font-bold text-green-200">{{
              m.player_1_name || '???'
            }}</span>
            <span class="text-green-800">vs</span>
            <span class="font-bold text-green-200">{{
              m.player_2_name || '???'
            }}</span>
          </div>
          <div v-if="m.problem_title" class="mt-1 text-xs text-green-700">
            {{ m.problem_title }}
          </div>
          <div
            class="mt-2 text-xs uppercase tracking-widest text-green-900 transition-colors group-hover:text-green-600"
          >
            [watch →]
          </div>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useCall } from 'frappe-ui'
import { sessionUser } from '@/data/session'

interface LiveMatch {
  name: string
  status: 'Live' | 'Ready'
  round_number: number
  bracket_position: number
  player_1: string | null
  player_2: string | null
  player_1_name: string | null
  player_2_name: string | null
  problem: string | null
  problem_title: string | null
}

const matches = ref<LiveMatch[]>([])
const loading = ref(true)

// Dev login-as — fetched once on mount; flag checked before rendering
const bracket = useCall({
  url: '/api/v2/method/codeoff.api.contest.get_tournament_bracket',
  immediate: true,
})

const players = useCall({
  url: '/api/v2/method/codeoff.api.contest.get_all_players',
  immediate: true,
})

const loggingIn = ref(false)

async function loginAs(email: string) {
  if (!email || email === sessionUser.value) return
  loggingIn.value = true
  try {
    await fetch('/api/method/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ usr: email, pwd: '123' }),
    })
    window.location.reload()
  } catch {
    loggingIn.value = false
  }
}

const fetch = useCall({
  url: '/api/v2/method/codeoff.api.contest.get_live_matches',
  immediate: false,
  onSuccess(data: LiveMatch[]) {
    matches.value = data
    loading.value = false
  },
  onError() {
    loading.value = false
  },
})

let pollTimer: ReturnType<typeof setInterval> | null = null

onMounted(() => {
  fetch.submit({})
  pollTimer = setInterval(() => fetch.submit({}), 5000)
})

onUnmounted(() => {
  if (pollTimer) clearInterval(pollTimer)
})
</script>
