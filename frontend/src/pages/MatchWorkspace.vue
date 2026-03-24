<template>
  <div
    v-if="loading"
    class="bg-gray-950 flex h-full items-center justify-center"
  >
    <div class="text-gray-500">Loading match...</div>
  </div>
  <div
    v-else-if="error"
    class="bg-gray-950 flex h-full items-center justify-center"
  >
    <div class="text-red-400">{{ error }}</div>
  </div>
  <!-- Waiting lobby when match is Ready -->
  <WaitingLobby
    v-else-if="state && state.status === 'Ready'"
    :title="state.problem?.title || 'Match Lobby'"
    :player1="state.player_1"
    :player2="state.player_2"
  />
  <div v-else-if="state" class="bg-gray-950 flex h-full flex-col text-gray-200">
    <!-- Top bar -->
    <div
      class="flex items-center justify-between border-b border-gray-800 px-4 py-2"
    >
      <div class="flex items-center gap-3">
        <span class="text-sm font-medium text-gray-200">
          {{ state.problem?.title || state.match_id }}
        </span>
        <Badge :theme="statusTheme" variant="subtle" size="sm">
          {{ state.status }}
        </Badge>
      </div>
      <div class="flex items-center gap-3">
        <span
          v-if="bestScore"
          class="rounded bg-gray-800 px-2.5 py-1 font-mono text-sm"
          :class="
            bestScore.passed_tests === bestScore.total_tests
              ? 'text-green-400'
              : 'text-yellow-400'
          "
        >
          Best: {{ bestScore.passed_tests }}/{{ bestScore.total_tests }}
        </span>
        <div
          v-if="state.status === 'Live'"
          class="font-mono text-lg font-semibold"
          :class="remaining < 60 ? 'text-red-400' : 'text-white'"
        >
          {{ formatted }}
        </div>
        <Button
          v-if="state.status === 'Live'"
          variant="subtle"
          size="sm"
          :loading="runningTests"
          @click="runTests"
        >
          Run Tests
        </Button>
        <Button
          v-if="state.status === 'Live'"
          variant="solid"
          size="sm"
          :loading="submitting"
          @click="submitCode"
        >
          Submit
        </Button>
      </div>
    </div>

    <!-- Main content -->
    <div class="flex flex-1 overflow-hidden">
      <!-- Left: Problem statement -->
      <div
        class="w-[400px] flex-shrink-0 overflow-hidden border-r border-gray-800"
      >
        <ProblemPanel
          v-if="state.problem"
          :problem="state.problem"
          :submissions="mySubmissions"
        />
      </div>

      <!-- Right: Code editor + test results -->
      <div class="relative flex flex-1 flex-col overflow-hidden">
        <div class="relative flex-1 overflow-hidden">
          <CodeEditor
            v-model="code"
            @cursor-change="onCursorChange"
            :readonly="state.status !== 'Live'"
            placeholder="Write your solution here..."
          />
          <div
            v-if="state.status !== 'Live'"
            class="absolute inset-0 flex items-center justify-center bg-black/60"
          >
            <div class="rounded-lg bg-gray-900 px-8 py-6 text-center">
              <div
                v-if="state.status === 'Finished'"
                class="text-lg font-semibold text-green-400"
              >
                Match Over — {{ winnerName }} wins!
              </div>
              <div
                v-else-if="state.status === 'Review'"
                class="text-lg font-semibold text-orange-400"
              >
                Match Over — Under Review
              </div>
              <div
                v-if="state.winning_reason"
                class="mt-1 text-sm text-gray-400"
              >
                {{ state.winning_reason }}
              </div>
            </div>
          </div>
        </div>
        <TestResultsPanel :test-results="testResults" />
      </div>
    </div>

    <!-- Winner banner -->
    <div
      v-if="state.status === 'Finished' || state.status === 'Review'"
      class="border-t border-gray-800 px-4 py-3 text-center"
    >
      <template v-if="state.status === 'Finished'">
        <span class="text-lg font-semibold text-green-400">
          {{ winnerName }} wins!
        </span>
        <span class="ml-2 text-sm text-gray-400">
          {{ state.winning_reason }}
        </span>
      </template>
      <template v-else>
        <span class="text-lg font-semibold text-orange-400">
          Match under review
        </span>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useCall } from 'frappe-ui'
import { useMatchState, useMatchTimer } from '@/data/match'
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

const STORAGE_KEY = `codeoff_code_${props.matchId}`
const code = ref(localStorage.getItem(STORAGE_KEY) || '')
const testResults = ref<any>(null)
const runningTests = ref(false)
const submitting = ref(false)

// Join match when player opens the page (once)
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

// Throttled draft update
let draftTimeout: ReturnType<typeof setTimeout> | null = null
const updateDraft = useCall({
  url: '/api/v2/method/codeoff.api.contest.update_draft',
  immediate: false,
})

function onCursorChange(line: number, column: number) {
  scheduleDraftUpdate(line, column)
}

let lastCursor = { line: 0, column: 0 }
function scheduleDraftUpdate(line: number, column: number) {
  lastCursor = { line, column }
  if (draftTimeout) clearTimeout(draftTimeout)
  draftTimeout = setTimeout(() => {
    updateDraft.submit({
      match_id: props.matchId,
      source_code: code.value,
      cursor_line: lastCursor.line,
      cursor_column: lastCursor.column,
    })
  }, 400)
}

watch(code, () => {
  localStorage.setItem(STORAGE_KEY, code.value)
  scheduleDraftUpdate(lastCursor.line, lastCursor.column)
})

// Initialize code from localStorage, server draft, or starter code
watch(
  state,
  (s) => {
    if (!s || code.value) return
    const playerId = findMyPlayerId()
    if (playerId && s.drafts[playerId]) {
      code.value = s.drafts[playerId].source_code
    } else if (s.problem?.starter_code) {
      code.value = s.problem.starter_code
    }
  },
  { immediate: true },
)

function findMyPlayerId(): string | null {
  if (!state.value) return null
  const user = session.user.value
  if (!user) return null
  if (state.value.player_1?.user === user) return state.value.player_1.id
  if (state.value.player_2?.user === user) return state.value.player_2.id
  return null
}

// Run sample tests
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
  runningTests.value = true
  testResults.value = null
  runSampleTests.submit({
    match_id: props.matchId,
    source_code: code.value,
  })
}

// Submit code
const submitCodeCall = useCall({
  url: '/api/v2/method/codeoff.api.contest.submit_code',
  immediate: false,
  onSuccess() {
    submitting.value = false
  },
  onError() {
    submitting.value = false
  },
})

function submitCode() {
  submitting.value = true
  submitCodeCall.submit({
    match_id: props.matchId,
    source_code: code.value,
  })
}

const mySubmissions = computed(() => {
  if (!state.value) return []
  return state.value.submissions || []
})

const bestScore = computed(() => {
  const judged = mySubmissions.value.filter((s) => s.total_tests > 0)
  if (!judged.length) return null
  return judged.reduce(
    (best, s) => (s.passed_tests > best.passed_tests ? s : best),
    judged[0],
  )
})

const statusTheme = computed(() => {
  switch (state.value?.status) {
    case 'Live':
      return 'green'
    case 'Finished':
      return 'blue'
    case 'Review':
      return 'orange'
    default:
      return 'gray'
  }
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
