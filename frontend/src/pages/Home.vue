<template>
  <div
    class="relative flex h-full flex-col bg-term-bg font-mono text-green-200"
  >
    <div v-if="loading" class="flex flex-1 items-center justify-center">
      <div class="text-green-800">loading...</div>
    </div>

    <!-- Player view: show their match -->
    <div
      v-else-if="match?.match_id"
      class="flex flex-1 items-center justify-center"
    >
      <div class="text-center">
        <div class="mb-1 text-sm uppercase tracking-widest text-green-700">
          // your match
        </div>
        <div
          class="mb-3 text-3xl font-bold tracking-tight"
          :class="
            match.status === 'Live' ? 'text-term-green' : 'text-green-300'
          "
        >
          {{ match.status === 'Live' ? 'live now' : 'coming up' }}
        </div>
        <div class="mb-6 text-sm text-green-700">{{ match.match_id }}</div>
        <button
          class="border px-6 py-2 text-sm font-bold uppercase tracking-widest transition-colors"
          :class="
            match.status === 'Live'
              ? 'bg-green-950/30 hover:bg-green-950/60 border-term-green text-term-green'
              : 'border-green-700 text-green-600 hover:border-green-400 hover:text-green-300'
          "
          @click="
            $router.push({
              name: 'MatchWorkspace',
              params: { matchId: match.match_id },
            })
          "
        >
          {{ match.status === 'Live' ? '[go to match]' : '[open workspace]' }}
        </button>
      </div>
    </div>

    <!-- Organizer / non-player view: tournament bracket -->
    <div
      v-else-if="match?.status === 'not_a_player'"
      class="flex flex-1 flex-col overflow-hidden"
    >
      <div
        v-if="bracket.loading"
        class="flex flex-1 items-center justify-center"
      >
        <div class="text-sm text-green-800">loading bracket...</div>
      </div>
      <BracketView
        v-else-if="bracket.data"
        :data="bracket.data"
        @spectate="
          $router.push({ name: 'Spectate', params: { matchId: $event } })
        "
      />
      <div v-else class="flex flex-1 items-center justify-center">
        <div class="text-sm text-green-800">no tournament found.</div>
      </div>
    </div>

    <!-- No match found for player -->
    <div v-else class="flex flex-1 items-center justify-center">
      <div class="text-center">
        <div class="mb-1 text-sm uppercase tracking-widest text-green-700">
          // status
        </div>
        <div class="mb-2 text-2xl font-bold text-green-800">
          no active match
        </div>
        <div class="text-sm text-green-900">
          no upcoming matches right now. check back later.
        </div>
      </div>
    </div>

    <!-- Login-as dropdown (dev/testing) -->
    <div
      v-if="players.data?.length"
      class="absolute bottom-4 right-4 flex items-center gap-2"
    >
      {{ sessionUser }}
      <span class="text-xs text-green-800">login as:</span>
      <select
        class="border border-term-border bg-term-surface px-2 py-1 text-xs text-green-300 outline-none focus:border-term-green"
        :value="sessionUser || ''"
        @change="loginAs(($event.target as HTMLSelectElement).value)"
      >
        <option value="" disabled class="bg-term-surface text-green-700">
          select player...
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
      <span v-if="loggingIn" class="animate-pulse text-xs text-green-700"
        >...</span
      >
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useCall } from 'frappe-ui'
import { useMyMatch } from '@/data/match'
import { sessionUser } from '@/data/session'
import BracketView from '@/components/BracketView.vue'

const { match, loading, reload } = useMyMatch()
const loggingIn = ref(false)

const bracket = useCall({
  url: '/api/v2/method/codeoff.api.contest.get_tournament_bracket',
  immediate: true,
})

const players = useCall({
  url: '/api/v2/method/codeoff.api.contest.get_all_players',
  immediate: true,
})

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
</script>
