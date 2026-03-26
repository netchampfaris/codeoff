<template>
  <div
    v-if="loading"
    class="flex h-screen items-center justify-center bg-term-bg font-mono"
  >
    <div class="text-green-800">loading match...</div>
  </div>
  <WaitingLobby
    v-else-if="state && state.status === 'Ready'"
    :title="state.problem?.title || state.match_id"
    :player1="state.player_1"
    :player2="state.player_2"
    large
  />
  <div
    v-else-if="state"
    class="relative flex h-screen flex-col bg-term-bg font-mono text-green-200"
  >
    <!-- Top bar: player | timer | player -->
    <div
      class="grid grid-cols-3 border-b border-term-border bg-term-surface px-6 py-3"
    >
      <!-- Player 1 -->
      <div class="flex items-center">
        <div>
          <div class="text-xs uppercase tracking-widest text-green-700">
            ← player 1
          </div>
          <div class="flex items-center gap-3">
            <div class="text-3xl font-bold tracking-tight text-green-300">
              {{ state.player_1?.name || 'Player 1' }}
            </div>
            <div class="flex items-center gap-1">
              <div
                v-for="i in state.problem?.total_test_cases || 0"
                :key="i"
                class="h-6 w-6 border-2 transition-colors duration-300"
                :class="
                  bestScore1 && i <= bestScore1.passed_tests
                    ? 'border-term-green bg-term-green'
                    : 'border-green-900 bg-transparent'
                "
              />
            </div>
            <span
              v-if="
                state.status === 'Finished' &&
                state.winner === state.player_1?.id
              "
              class="border-4 border-term-green px-4 py-1 text-2xl font-black uppercase tracking-widest text-term-green"
            >
              winner
            </span>
          </div>
        </div>
      </div>

      <!-- Center: round + timer -->
      <div class="flex flex-col items-center justify-center">
        <div class="text-xl uppercase tracking-[0.25em] text-term-green">
          {{ state.problem?.title || state.match_id }}
        </div>
        <div
          class="mb-1 text-base font-bold uppercase tracking-widest text-green-400"
        >
          round {{ state.round_number }} · match {{ state.bracket_position }}
        </div>
        <div
          class="text-7xl font-mono font-bold leading-none tracking-tight"
          :class="
            state.status !== 'Live'
              ? 'text-green-800'
              : remaining < 60
                ? 'text-red-400'
                : 'text-term-green'
          "
        >
          {{ state.status === 'Live' ? formatted : state.status.toUpperCase() }}
        </div>
        <button
          class="mt-2 border px-3 py-1 text-xs font-bold uppercase tracking-widest transition-colors"
          :class="
            showProblem
              ? 'border-term-green text-term-green'
              : 'border-green-900 text-green-700 hover:border-green-600 hover:text-green-400'
          "
          @click="showProblem = !showProblem"
        >
          {{ showProblem ? '[hide problem]' : '[show problem]' }}
        </button>
        <button
          class="mt-1 border border-green-900 px-3 py-1 text-xs font-bold uppercase tracking-widest text-green-700 transition-colors hover:border-green-600 hover:text-green-400"
          @click="$router.push({ name: 'Home' })"
        >
          [home]
        </button>
      </div>

      <!-- Player 2 -->
      <div class="flex items-center justify-end">
        <div class="text-right">
          <div class="text-xs uppercase tracking-widest text-green-700">
            player 2 →
          </div>
          <div class="flex items-center justify-end gap-3">
            <span
              v-if="
                state.status === 'Finished' &&
                state.winner === state.player_2?.id
              "
              class="border-4 border-term-green px-4 py-1 text-2xl font-black uppercase tracking-widest text-term-green"
            >
              winner
            </span>
            <div class="flex items-center gap-1">
              <div
                v-for="i in state.problem?.total_test_cases || 0"
                :key="i"
                class="h-6 w-6 border-2 transition-colors duration-300"
                :class="
                  bestScore2 && i <= bestScore2.passed_tests
                    ? 'border-term-green bg-term-green'
                    : 'border-green-900 bg-transparent'
                "
              />
            </div>
            <div class="text-3xl font-bold tracking-tight text-green-300">
              {{ state.player_2?.name || 'Player 2' }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Editors -->
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

    <!-- Problem drawer -->
    <div
      v-if="showProblem && state.problem"
      class="h-[38%] flex-shrink-0 border-t-2 border-term-green"
    >
      <div class="flex h-full flex-row overflow-hidden">
        <!-- Statement -->
        <div class="flex-1 overflow-auto border-r border-term-border">
          <ProblemPanel :problem="state.problem" />
        </div>
        <!-- Examples column -->
        <div
          v-if="state.problem.sample_test_cases?.length"
          class="w-80 overflow-auto bg-term-surface p-4"
        >
          <div
            class="mb-3 text-xs font-bold uppercase tracking-widest text-green-600"
          >
            # examples
          </div>
          <div
            v-for="(tc, i) in state.problem.sample_test_cases"
            :key="i"
            class="mb-4"
          >
            <div
              class="mb-1 text-xs font-bold uppercase tracking-wider text-green-700"
            >
              example {{ i + 1 }}
            </div>
            <div
              class="border border-term-border bg-term-bg p-2 text-xs text-green-300"
            >
              <div class="mb-1 text-green-700">$ input:</div>
              <code class="block whitespace-pre text-term-green">{{
                tc.input
              }}</code>
            </div>
            <div class="mt-1 border border-term-border bg-term-bg p-2 text-xs">
              <div class="mb-1 text-green-700">$ expected:</div>
              <code class="block whitespace-pre text-green-300">{{
                tc.expected_output
              }}</code>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useMatchState, useMatchTimer } from '@/data/match'
import { useLobbyPoll } from '@/data/useLobbyPoll'
import { useMatchPlayers } from '@/data/useMatchPlayers'
import WaitingLobby from '@/components/WaitingLobby.vue'
import PlayerPanel from '@/components/PlayerPanel.vue'
import ProblemPanel from '@/components/ProblemPanel.vue'

const props = defineProps<{
  matchId: string
}>()

const { state, loading, reload } = useMatchState(props.matchId)
const { remaining, formatted } = useMatchTimer(state)

const showProblem = ref(false)

useLobbyPoll(
  computed(() => state.value?.status),
  reload,
)

const {
  winnerName,
  player1Submissions,
  player2Submissions,
  bestScore1,
  bestScore2,
} = useMatchPlayers(state)

const player1Code = computed(() => {
  if (!state.value?.player_1?.id) return ''
  return state.value.drafts[state.value.player_1.id]?.source_code || ''
})

const player2Code = computed(() => {
  if (!state.value?.player_2?.id) return ''
  return state.value.drafts[state.value.player_2.id]?.source_code || ''
})
</script>
