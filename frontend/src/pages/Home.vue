<template>
  <div class="bg-zinc-950 flex h-full flex-col font-mono text-green-200">
    <AppNavbar title="home">
      <template #actions>
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
    </AppNavbar>

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
          :class="match.status === 'Live' ? 'text-green-400' : 'text-green-300'"
        >
          {{ match.status === 'Live' ? 'live now' : 'coming up' }}
        </div>
        <div class="mb-6 text-sm text-green-700">{{ match.match_id }}</div>
        <AppButton
          :variant="match.status === 'Live' ? 'primary' : 'ghost'"
          size="md"
          @click="
            $router.push({
              name: 'MatchWorkspace',
              params: { matchId: match.match_id },
            })
          "
        >
          {{ match.status === 'Live' ? '[go to match]' : '[open workspace]' }}
        </AppButton>
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
        @makeReady="makeMatchReady($event)"
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
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'
import { useCall } from 'frappe-ui'
import { useMyMatch } from '@/data/match'
import { sessionUser } from '@/data/session'
import AppNavbar from '@/components/AppNavbar.vue'
import AppButton from '@/components/AppButton.vue'
import BracketView from '@/components/BracketView.vue'

const { match, loading, reload } = useMyMatch()
const loggingIn = ref(false)

const makeReadyCall = useCall({
  url: '/api/v2/method/codeoff.api.contest.make_match_ready',
  immediate: false,
  onSuccess() {
    bracket.submit()
  },
})

function makeMatchReady(matchId: string) {
  makeReadyCall.submit({ match_id: matchId })
}

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

// Auto-refresh bracket every 5 s so timers and scores stay live
let bracketTimer: ReturnType<typeof setInterval> | null = null
onMounted(() => {
  bracketTimer = setInterval(() => bracket.submit(), 5_000)
})
onUnmounted(() => {
  if (bracketTimer) clearInterval(bracketTimer)
})
</script>
