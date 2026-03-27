<template>
  <div class="bg-zinc-950 flex h-full flex-col font-mono text-green-200">
    <AppNavbar title="home">
      <template #actions>
        <DevLoginDropdown />
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
import { onMounted, onUnmounted } from 'vue'
import { useCall } from 'frappe-ui'
import { useMyMatch } from '@/data/match'
import { useTournament } from '@/data/useTournament'
import AppNavbar from '@/components/AppNavbar.vue'
import AppButton from '@/components/AppButton.vue'
import BracketView from '@/components/BracketView.vue'
import DevLoginDropdown from '@/components/DevLoginDropdown.vue'

const { match, loading, reload } = useMyMatch()
const { bracket } = useTournament()

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

// Auto-refresh bracket every 5 s so timers and scores stay live
let bracketTimer: ReturnType<typeof setInterval> | null = null
onMounted(() => {
  bracketTimer = setInterval(() => bracket.submit(), 5_000)
})
onUnmounted(() => {
  if (bracketTimer) clearInterval(bracketTimer)
})
</script>
