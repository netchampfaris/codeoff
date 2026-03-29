<template>
  <div class="flex min-h-screen flex-col bg-zinc-950 font-mono text-green-200">
    <AppNavbar title="spectate">
      <template #actions>
        <DevLoginDropdown />
      </template>
    </AppNavbar>

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
          class="group w-full rounded-none border border-zinc-800 bg-zinc-900 p-4 text-left font-mono transition-colors hover:border-green-600 hover:bg-green-950/30"
          @click="
            $router.push({ name: 'Spectate', params: { matchId: m.name } })
          "
        >
          <div class="mb-2 flex items-center justify-between">
            <span
              class="text-xs font-bold uppercase tracking-widest"
              :class="m.status === 'Live' ? 'text-green-400' : 'text-green-700'"
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
            v-if="m.status === 'Ready'"
            class="mt-3 border-t border-green-950 pt-3 text-xs uppercase tracking-widest"
          >
            <div class="text-green-600">crowd pick open</div>
            <div
              class="mt-2 grid grid-cols-[minmax(0,1fr)_auto_minmax(0,1fr)] items-end gap-3"
            >
              <div class="text-left">
                <div
                  class="text-[9px] uppercase tracking-[0.3em] text-green-700"
                >
                  {{ m.player_1_name || 'player 1' }}
                </div>
                <div class="mt-1 font-mono text-2xl font-bold text-green-300">
                  {{ predictionLeftPercent(m) }}
                </div>
              </div>
              <div
                class="pb-1 text-[10px] uppercase tracking-[0.3em] text-green-900"
              >
                vs
              </div>
              <div class="text-right">
                <div
                  class="text-[9px] uppercase tracking-[0.3em] text-green-700"
                >
                  {{ m.player_2_name || 'player 2' }}
                </div>
                <div class="mt-1 font-mono text-2xl font-bold text-green-300">
                  {{ predictionRightPercent(m) }}
                </div>
              </div>
            </div>
            <div class="mt-1 text-green-900">
              {{ predictionCountLabel(m) }}
            </div>
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
import { getPredictionStats, getStoredPrediction } from '@/data/predictions'
import AppNavbar from '@/components/AppNavbar.vue'
import DevLoginDropdown from '@/components/DevLoginDropdown.vue'

interface LiveMatch {
  name: string
  status: 'Live' | 'Ready'
  is_organizer: boolean
  round_number: number
  bracket_position: number
  player_1: string | null
  player_2: string | null
  player_1_name: string | null
  player_2_name: string | null
  problem: string | null
  problem_title: string | null
  votes_1: number
  votes_2: number
}

const matches = ref<LiveMatch[]>([])
const loading = ref(true)

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

function predictionLeftPercent(match: LiveMatch) {
  if (!match.is_organizer && !getStoredPrediction(match.name)) return '--'
  const stats = getPredictionStats(match.votes_1, match.votes_2)
  return stats.total ? `${stats.percent1}%` : '--'
}

function predictionRightPercent(match: LiveMatch) {
  if (!match.is_organizer && !getStoredPrediction(match.name)) return '--'
  const stats = getPredictionStats(match.votes_1, match.votes_2)
  return stats.total ? `${stats.percent2}%` : '--'
}

function predictionCountLabel(match: LiveMatch) {
  if (!match.is_organizer && !getStoredPrediction(match.name)) {
    return 'pick to reveal crowd split'
  }
  const total = getPredictionStats(match.votes_1, match.votes_2).total
  return `${total} pick${total === 1 ? '' : 's'}`
}

onMounted(() => {
  fetch.submit()
  pollTimer = setInterval(() => fetch.submit(), 5000)
})

onUnmounted(() => {
  if (pollTimer) clearInterval(pollTimer)
})
</script>
