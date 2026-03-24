<template>
  <div
    v-if="loading"
    class="bg-gray-950 flex h-screen items-center justify-center"
  >
    <div class="text-gray-400">Loading match...</div>
  </div>
  <WaitingLobby
    v-else-if="state && state.status === 'Ready'"
    :title="state.problem?.title || state.match_id"
    :player1="state.player_1"
    :player2="state.player_2"
    large
  />
  <div v-else-if="state" class="bg-gray-950 flex h-screen flex-col text-white">
    <!-- Top bar -->
    <div
      class="flex items-center justify-between border-b border-gray-800 px-6 py-3"
    >
      <div class="flex items-center gap-4">
        <span class="text-lg font-semibold text-white">
          {{ state.problem?.title || state.match_id }}
        </span>
        <Badge
          :theme="state.status === 'Live' ? 'green' : 'gray'"
          variant="subtle"
          size="sm"
        >
          {{ state.status }}
        </Badge>
      </div>
      <div
        v-if="state.status === 'Live'"
        class="font-mono text-3xl font-bold"
        :class="remaining < 60 ? 'text-red-400' : 'text-white'"
      >
        {{ formatted }}
      </div>
    </div>

    <!-- Players + editors -->
    <div class="flex flex-1 overflow-hidden">
      <PlayerPanel
        :player-name="state.player_1?.name || 'Player 1'"
        :code="player1Code"
        :submissions="player1Submissions"
        side="left"
      />
      <PlayerPanel
        :player-name="state.player_2?.name || 'Player 2'"
        :code="player2Code"
        :submissions="player2Submissions"
      />
    </div>

    <!-- Winner banner -->
    <div
      v-if="state.status === 'Finished' || state.status === 'Review'"
      class="border-t border-gray-800 px-6 py-4 text-center"
    >
      <template v-if="state.status === 'Finished'">
        <span class="text-2xl font-bold text-green-400">
          {{ winnerName }} wins!
        </span>
        <span class="ml-3 text-sm text-gray-400">
          {{ state.winning_reason }}
        </span>
      </template>
      <template v-else>
        <span class="text-xl font-semibold text-orange-400">
          Match under review
        </span>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, watch, onUnmounted } from 'vue'
import { useMatchState, useMatchTimer } from '@/data/match'
import WaitingLobby from '@/components/WaitingLobby.vue'
import PlayerPanel from '@/components/PlayerPanel.vue'

const props = defineProps<{
  matchId: string
}>()

const { state, loading, reload } = useMatchState(props.matchId)
const { remaining, formatted } = useMatchTimer(state)

// Poll for state updates while on lobby screen
let lobbyPoll: ReturnType<typeof setInterval> | null = null
watch(
  () => state.value?.status,
  (status) => {
    if (status === 'Ready' && !lobbyPoll) {
      lobbyPoll = setInterval(reload, 2000)
    } else if (status !== 'Ready' && lobbyPoll) {
      clearInterval(lobbyPoll)
      lobbyPoll = null
    }
  },
  { immediate: true },
)
onUnmounted(() => {
  if (lobbyPoll) clearInterval(lobbyPoll)
})

const player1Code = computed(() => {
  if (!state.value?.player_1?.id) return ''
  return state.value.drafts[state.value.player_1.id]?.source_code || ''
})

const player2Code = computed(() => {
  if (!state.value?.player_2?.id) return ''
  return state.value.drafts[state.value.player_2.id]?.source_code || ''
})

const player1Submissions = computed(() => {
  if (!state.value) return []
  return (state.value.submissions || []).filter(
    (s) => s.player === state.value!.player_1?.id,
  )
})

const player2Submissions = computed(() => {
  if (!state.value) return []
  return (state.value.submissions || []).filter(
    (s) => s.player === state.value!.player_2?.id,
  )
})

const winnerName = computed(() => {
  if (!state.value?.winner) return ''
  if (state.value.player_1.id === state.value.winner)
    return state.value.player_1.name
  if (state.value.player_2.id === state.value.winner)
    return state.value.player_2.name
  return state.value.winner
})
</script>
