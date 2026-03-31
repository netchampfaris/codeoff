<template>
  <div class="flex h-full flex-col bg-zinc-950 font-mono text-green-200">
    <AppNavbar :show-audience-count="false" />
    <!-- Content area fills remaining height -->
    <div class="relative flex flex-1 flex-col overflow-hidden">
      <div v-if="loading" class="flex h-full items-center justify-center">
        <div class="text-green-800">loading match...</div>
      </div>
      <div v-else-if="error" class="flex h-full items-center justify-center">
        <div class="text-red-400">{{ error }}</div>
      </div>
      <!-- Waiting lobby when match is Ready -->
      <WaitingLobby
        v-else-if="state && state.status === 'Ready'"
        :title="state.problem?.title || 'Match Lobby'"
        :player1="state.player_1"
        :player2="state.player_2"
        :is-organizer="state.is_organizer"
        @start="startMatch"
      />
      <div v-else-if="state" class="flex h-full flex-col">
        <!-- Top bar -->
        <div
          class="flex items-center justify-between border-b border-zinc-800 px-4 py-2"
        >
          <div class="flex items-center gap-3">
            <span class="text-xs uppercase tracking-widest text-green-700">
              round {{ state.round_number }} · match
              {{ state.bracket_position }}
            </span>
            <span
              v-if="myPlayerName"
              class="text-xs uppercase tracking-widest text-green-800"
              >// {{ myPlayerName }}</span
            >
            <span
              v-if="state.status === 'Finished' && winnerName"
              class="border border-green-400 bg-green-950/40 px-2 py-0.5 text-xs font-bold uppercase tracking-wider text-green-400"
            >
              {{ winnerName }} [winner]
            </span>
          </div>
          <div class="flex items-center gap-3">
            <span
              v-if="bestScore"
              class="border border-zinc-800 bg-zinc-900 px-2.5 py-1 font-mono text-sm"
              :class="
                bestScore.passed_tests === bestScore.total_tests
                  ? 'text-green-400'
                  : 'text-yellow-400'
              "
            >
              best: {{ bestScore.passed_tests }}/{{ bestScore.total_tests }}
            </span>
            <div
              v-if="state.status === 'Live'"
              class="font-mono text-3xl font-bold tabular-nums"
              :class="remaining < 60 ? 'text-red-400' : 'text-green-400'"
            >
              {{ formatted }}
            </div>
            <AppButton
              v-if="state.status === 'Live'"
              variant="ghost"
              size="sm"
              :disabled="runningTests || remaining === 0"
              @click="runTests"
            >
              {{ runningTests ? '[running...]' : '[run tests]' }}
            </AppButton>
            <AppButton
              v-if="state.status === 'Live'"
              variant="primary"
              size="sm"
              :disabled="submitting || remaining === 0"
              @click="submitCode"
            >
              {{
                remaining === 0
                  ? '[time up]'
                  : submitting
                    ? '[submitting...]'
                    : '[submit]'
              }}
            </AppButton>
            <span v-if="submitError" class="text-xs text-red-400">{{
              submitError
            }}</span>
          </div>
        </div>

        <!-- Main content -->
        <div ref="mainEl" class="flex flex-1 overflow-hidden">
          <!-- Left: Problem statement -->
          <div
            :style="{ width: problemPanelWidth + 'px' }"
            class="flex-shrink-0 overflow-hidden"
          >
            <ProblemPanel v-if="state.problem" :problem="state.problem" />
          </div>

          <!-- Horizontal drag handle -->
          <div
            class="group relative z-10 w-1 flex-shrink-0 cursor-col-resize bg-zinc-800 transition-colors hover:bg-green-700 active:bg-green-500"
            @mousedown.prevent="startDragH"
          >
            <div class="absolute inset-y-0 -left-1 -right-1" />
          </div>

          <!-- Right: Code editor + test results -->
          <div class="relative flex flex-1 flex-col overflow-hidden">
            <div
              class="relative overflow-hidden"
              :style="{ height: `calc(100% - ${bottomPanelHeight}px - 1px)` }"
            >
              <CodeEditor
                v-model="code"
                @cursor-change="onCursorChange"
                @mod-s="runTests"
                :readonly="state.status !== 'Live'"
                placeholder="Write your solution here..."
              />
              <div
                v-if="state.status !== 'Live'"
                class="absolute inset-0 flex items-center justify-center bg-black/70"
              >
                <div
                  class="border border-zinc-800 bg-zinc-900 px-10 py-8 text-center font-mono"
                >
                  <div
                    v-if="state.status === 'Finished'"
                    class="text-2xl font-bold tracking-tight"
                    :class="isWinner ? 'text-green-400' : 'text-red-400'"
                  >
                    {{
                      isWinner
                        ? 'you win!'
                        : winnerName
                          ? winnerName + ' wins'
                          : 'match over'
                    }}
                  </div>
                  <div
                    v-else-if="state.status === 'Review'"
                    class="text-2xl font-bold text-orange-400"
                  >
                    match under review
                  </div>
                  <div
                    v-if="state.winning_reason"
                    class="mt-2 text-sm text-green-700"
                  >
                    {{ state.winning_reason }}
                  </div>
                </div>
              </div>
            </div>

            <!-- Vertical drag handle -->
            <div
              class="z-10 h-1 flex-shrink-0 cursor-row-resize bg-zinc-800 transition-colors hover:bg-green-700 active:bg-green-500"
              @mousedown.prevent="startDragV"
            />

            <div
              :style="{ height: bottomPanelHeight + 'px' }"
              class="flex-shrink-0 overflow-y-auto"
            >
              <TestResultsPanel
                :test-results="testResults"
                :submissions="mySubmissions"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useCall } from 'frappe-ui'
import {
  useMatchState,
  useMatchTimer,
  usePostDeadlineRefresh,
} from '@/data/match'
import { useLobbyPoll } from '@/data/useLobbyPoll'
import { useMatchPlayers } from '@/data/useMatchPlayers'
import { useCodeDraft } from '@/data/useCodeDraft'
import { useResizablePanels } from '@/data/useResizablePanels'
import AppNavbar from '@/components/AppNavbar.vue'
import AppButton from '@/components/AppButton.vue'
import CodeEditor from '@/components/CodeEditor.vue'
import WaitingLobby from '@/components/WaitingLobby.vue'
import ProblemPanel from '@/components/ProblemPanel.vue'
import TestResultsPanel from '@/components/TestResultsPanel.vue'
import { session } from '@/data/session'

const props = defineProps<{
  matchId: string
}>()

const { state, loading, error, reload } = useMatchState(props.matchId)
const { remaining, formatted } = useMatchTimer(state)
usePostDeadlineRefresh(state, remaining, reload)

const testResults = ref<any>(null)
const runningTests = ref(false)
const submitting = ref(false)
const submitError = ref<string | null>(null)

// --- Organizer start match ---
const startMatchCall = useCall({
  url: '/api/v2/method/codeoff.api.contest.start_match_now',
  immediate: false,
  onSuccess() {
    reload()
  },
})

function startMatch() {
  startMatchCall.submit({ match_id: props.matchId })
}

// --- Resizable panels ---
const { problemPanelWidth, bottomPanelHeight, startDragH, startDragV } =
  useResizablePanels()

// --- Lobby polling ---
useLobbyPoll(
  computed(() => state.value?.status),
  reload,
)

// --- Player identity ---
function findMyPlayerId(): string | null {
  if (!state.value) return null
  const user = session.user as string | null
  if (!user) return null
  if (state.value.player_1?.user === user) return state.value.player_1.id
  if (state.value.player_2?.user === user) return state.value.player_2.id
  return null
}

// --- Code draft ---
const { code, onCursorChange } = useCodeDraft(
  props.matchId,
  state,
  findMyPlayerId,
)

// --- Match players ---
const { winnerName, player1Submissions } = useMatchPlayers(state)

const mySubmissions = computed(() => {
  if (!state.value) return []
  const myId = findMyPlayerId()
  return (state.value.submissions || []).filter((s) => s.player === myId)
})

const bestScore = computed(() => {
  const judged = mySubmissions.value.filter((s) => s.total_tests > 0)
  if (!judged.length) return null
  return judged.reduce(
    (best, s) => (s.passed_tests > best.passed_tests ? s : best),
    judged[0],
  )
})

const isWinner = computed(() => {
  if (!state.value?.winner) return false
  const user = session.user as string | null
  return !!user && state.value.winner === user
})

const myPlayerName = computed(() => {
  if (!state.value) return null
  const user = session.user as string | null
  if (!user) return null
  if (state.value.player_1?.user === user) return state.value.player_1.name
  if (state.value.player_2?.user === user) return state.value.player_2.name
  return null
})

// --- Join match ---
let joined = false
const joinMatch = useCall({
  url: '/api/v2/method/codeoff.api.contest.join_match',
  immediate: false,
  onSuccess() {
    reload()
  },
})

watch(state, (s) => {
  if (s && !joined && (s.status === 'Ready' || s.status === 'Live')) {
    joined = true
    joinMatch.submit({ match_id: props.matchId })
  }
})

// --- Run sample tests ---
const runSampleTests = useCall({
  url: '/api/v2/method/codeoff.api.contest.run_sample_tests',
  immediate: false,
  onSuccess(data: any) {
    testResults.value = data
    runningTests.value = false
  },
  onError() {
    runningTests.value = false
  },
})

function runTests() {
  if (
    runningTests.value ||
    state.value?.status !== 'Live' ||
    remaining.value === 0
  ) {
    return
  }

  runningTests.value = true
  testResults.value = null
  runSampleTests.submit({ match_id: props.matchId, source_code: code.value })
}

// --- Submit code ---
const submitCodeCall = useCall({
  url: '/api/v2/method/codeoff.api.contest.submit_code',
  immediate: false,
  onSuccess() {
    submitting.value = false
    submitError.value = null
    reload()
  },
  onError(err: any) {
    submitting.value = false
    submitError.value =
      err?.messages?.[0]?.message || err?.message || 'Submission failed'
  },
})

function submitCode() {
  submitting.value = true
  submitCodeCall.submit({ match_id: props.matchId, source_code: code.value })
}
</script>
