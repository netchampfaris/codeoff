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
    :votes1="state.votes_1"
    :votes2="state.votes_2"
    :match-id="props.matchId"
    :is-organizer="state.is_organizer"
    large
    @vote="handleVote"
    @start="startMatch"
  />
  <div
    v-else-if="state"
    class="relative flex h-[100dvh] flex-col bg-term-bg font-mono text-green-200"
  >
    <!-- ══ Mobile layout (hidden md+) ══════════════════════════════ -->
    <div class="flex flex-1 flex-col overflow-hidden md:hidden">
      <!-- Mobile header -->
      <div
        class="flex shrink-0 items-center justify-between border-b border-term-border bg-term-surface px-4 py-2"
      >
        <div>
          <div class="text-xs uppercase tracking-widest text-green-700">
            r{{ state.round_number }} · m{{ state.bracket_position }}
          </div>
          <div
            class="text-sm font-bold uppercase tracking-wide text-term-green"
          >
            {{ state.problem?.title || state.match_id }}
          </div>
        </div>
        <div class="flex items-center gap-3">
          <div
            class="font-mono text-2xl font-bold tabular-nums"
            :class="
              state.status !== 'Live'
                ? 'text-green-800'
                : remaining < 60
                  ? 'text-red-400'
                  : 'text-term-green'
            "
          >
            {{
              state.status === 'Live' ? formatted : state.status.toUpperCase()
            }}
          </div>
          <button
            class="border border-green-900 px-2 py-1 text-xs font-bold uppercase tracking-widest text-green-700"
            @click="$router.push({ name: 'SpectateHome' })"
          >
            [home]
          </button>
        </div>
      </div>

      <!-- Player 1 panel (top half) -->
      <div
        class="flex flex-1 flex-col overflow-hidden border-b border-term-border"
      >
        <!-- Player 1 info bar -->
        <div
          class="flex shrink-0 items-center justify-between bg-term-surface px-3 py-1.5"
        >
          <div class="flex items-center gap-2">
            <span
              class="text-xs font-bold uppercase tracking-wide text-green-300"
              >{{ state.player_1?.name }}</span
            >
            <span class="text-xs font-bold text-green-600"
              >▲ {{ state.votes_1 }}</span
            >
            <span
              v-if="
                state.status === 'Finished' &&
                state.winner === state.player_1?.id
              "
              class="border border-term-green px-1.5 text-xs font-black uppercase tracking-widest text-term-green"
              >winner</span
            >
          </div>
          <div class="flex items-center gap-2">
            <button
              v-for="emoji in EMOJIS"
              :key="'m1-' + emoji"
              class="text-xl active:scale-95"
              @click="sendReaction(emoji, state.player_1?.id)"
            >
              {{ emoji }}
            </button>
            <div class="flex gap-0.5">
              <div
                v-for="i in state.problem?.total_test_cases || 0"
                :key="i"
                class="h-3 w-3 border transition-colors duration-300"
                :class="
                  bestScore1 && i <= bestScore1.passed_tests
                    ? 'border-term-green bg-term-green'
                    : 'border-green-900'
                "
              />
            </div>
          </div>
        </div>
        <!-- Code -->
        <div class="flex-1 overflow-hidden">
          <PlayerPanel
            :player-name="state.player_1?.name || 'Player 1'"
            :code="player1Code"
            :submissions="player1Submissions"
            side="left"
          />
        </div>
      </div>

      <!-- Player 2 panel (bottom half) -->
      <div class="flex flex-1 flex-col overflow-hidden">
        <!-- Player 2 info bar -->
        <div
          class="flex shrink-0 items-center justify-between bg-term-surface px-3 py-1.5"
        >
          <div class="flex items-center gap-2">
            <span
              class="text-xs font-bold uppercase tracking-wide text-green-300"
              >{{ state.player_2?.name }}</span
            >
            <span class="text-xs font-bold text-green-600"
              >▲ {{ state.votes_2 }}</span
            >
            <span
              v-if="
                state.status === 'Finished' &&
                state.winner === state.player_2?.id
              "
              class="border border-term-green px-1.5 text-xs font-black uppercase tracking-widest text-term-green"
              >winner</span
            >
          </div>
          <div class="flex items-center gap-2">
            <button
              v-for="emoji in EMOJIS"
              :key="'m2-' + emoji"
              class="text-xl active:scale-95"
              @click="sendReaction(emoji, state.player_2?.id)"
            >
              {{ emoji }}
            </button>
            <div class="flex gap-0.5">
              <div
                v-for="i in state.problem?.total_test_cases || 0"
                :key="i"
                class="h-3 w-3 border transition-colors duration-300"
                :class="
                  bestScore2 && i <= bestScore2.passed_tests
                    ? 'border-term-green bg-term-green'
                    : 'border-green-900'
                "
              />
            </div>
          </div>
        </div>
        <!-- Code -->
        <div class="flex-1 overflow-hidden">
          <PlayerPanel
            :player-name="state.player_2?.name || 'Player 2'"
            :code="player2Code"
            :submissions="player2Submissions"
          />
        </div>
      </div>
    </div>

    <!-- ══ Desktop layout (hidden mobile) ══════════════════════════ -->
    <div class="hidden flex-1 flex-col overflow-hidden pb-16 md:flex">
      <!-- Top bar: player | timer | player -->
      <div
        class="grid grid-cols-3 border-b border-term-border bg-term-surface px-6 py-3"
      >
        <!-- Player 1 -->
        <div class="flex items-start">
          <div>
            <div class="text-xs uppercase tracking-widest text-green-700">
              ← player 1
            </div>
            <div class="text-3xl font-bold tracking-tight text-green-300">
              {{ state.player_1?.name || 'Player 1' }}
            </div>
            <div class="mt-0.5 text-sm font-bold text-green-600">
              ▲ {{ state.votes_1 }}
            </div>
            <div class="mt-2 flex items-center gap-3">
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
            class="font-mono text-7xl font-bold leading-none tracking-tight"
            :class="
              state.status !== 'Live'
                ? 'text-green-800'
                : remaining < 60
                  ? 'text-red-400'
                  : 'text-term-green'
            "
          >
            {{
              state.status === 'Live' ? formatted : state.status.toUpperCase()
            }}
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
            @click="$router.push({ name: 'SpectateHome' })"
          >
            [home]
          </button>
        </div>

        <!-- Player 2 -->
        <div class="flex items-start justify-end">
          <div class="text-right">
            <div class="text-xs uppercase tracking-widest text-green-700">
              player 2 →
            </div>
            <div class="text-3xl font-bold tracking-tight text-green-300">
              {{ state.player_2?.name || 'Player 2' }}
            </div>
            <div class="mt-0.5 text-sm font-bold text-green-600">
              ▲ {{ state.votes_2 }}
            </div>
            <div class="mt-2 flex items-center justify-end gap-3">
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
              <div
                class="mt-1 border border-term-border bg-term-bg p-2 text-xs"
              >
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

    <!-- Floating emoji overlay (desktop only) -->
    <div
      class="pointer-events-none fixed inset-0 z-40 hidden overflow-hidden md:block"
    >
      <div
        v-for="f in floaters"
        :key="f.id"
        class="floater absolute bottom-14 text-3xl"
        :style="{ left: f.x + '%' }"
      >
        {{ f.emoji }}
      </div>
    </div>

    <!-- Dev login-as panel (both mobile and desktop, flag-gated) -->
    <div
      v-if="state.enable_dev_login && players.data?.length"
      class="fixed right-2 top-2 z-[60] flex items-center gap-2 rounded border border-green-900 bg-term-surface/95 px-2 py-1 backdrop-blur-sm"
    >
      <span class="text-xs text-green-800">login as:</span>
      <select
        class="border border-term-border bg-term-bg px-2 py-0.5 text-xs text-green-300 outline-none focus:border-term-green"
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

    <!-- Reaction bar: desktop only (mobile uses inline buttons in player info bars) -->
    <div
      class="fixed bottom-0 left-0 right-0 z-50 hidden items-stretch border-t border-term-border bg-term-surface/90 backdrop-blur-sm md:flex"
    >
      <div
        class="flex flex-1 items-center justify-center gap-3 border-r border-term-border py-2"
      >
        <span class="mr-1 text-xs uppercase tracking-widest text-green-800">{{
          state.player_1?.name
        }}</span>
        <button
          v-for="emoji in EMOJIS"
          :key="'p1-' + emoji"
          class="cursor-pointer text-2xl transition-transform hover:scale-125 active:scale-95"
          @click="sendReaction(emoji, state.player_1?.id)"
        >
          {{ emoji }}
        </button>
      </div>
      <div class="flex flex-1 items-center justify-center gap-3 py-2">
        <button
          v-for="emoji in EMOJIS"
          :key="'p2-' + emoji"
          class="cursor-pointer text-2xl transition-transform hover:scale-125 active:scale-95"
          @click="sendReaction(emoji, state.player_2?.id)"
        >
          {{ emoji }}
        </button>
        <span class="ml-1 text-xs uppercase tracking-widest text-green-800">{{
          state.player_2?.name
        }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useCall } from 'frappe-ui'
import { useMatchState, useMatchTimer } from '@/data/match'
import { useLobbyPoll } from '@/data/useLobbyPoll'
import { useMatchPlayers } from '@/data/useMatchPlayers'
import { getSocket } from '@/data/socket'
import { sessionUser } from '@/data/session'
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

// ── Organizer start ─────────────────────────────────────────────────────────
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

// ── Voting ──────────────────────────────────────────────────────────────────
const voteCall = useCall({
  url: '/api/v2/method/codeoff.api.contest.vote_for_player',
  immediate: false,
})

function handleVote(playerId: string) {
  voteCall.submit({ match_id: props.matchId, player_id: playerId })
}

// ── Dev login-as ────────────────────────────────────────────────────────────
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

// ── Reactions ────────────────────────────────────────────────────────────────
const EMOJIS = ['🔥', '💀', '👀', '🎉', '😬']

interface Floater {
  id: string
  emoji: string
  x: number
}

const floaters = ref<Floater[]>([])
const reactionThrottle: Record<string, string> = {}

const reactionCall = useCall({
  url: '/api/v2/method/codeoff.api.contest.send_reaction',
  immediate: false,
})

function playerSideX(playerId: string | null | undefined): number {
  if (!state.value) return Math.random() * 80 + 10
  if (playerId === state.value.player_1?.id) return Math.random() * 40 + 5
  if (playerId === state.value.player_2?.id) return Math.random() * 40 + 55
  return Math.random() * 80 + 10
}

function addFloater(emoji: string, id: string, playerId?: string | null) {
  floaters.value.push({ id, emoji, x: playerSideX(playerId) })
  setTimeout(() => {
    floaters.value = floaters.value.filter((f) => f.id !== id)
  }, 2500)
}

// IDs of floaters we spawned locally — skip their socket echo
const localFloaterIds = new Set<string>()

function sendReaction(emoji: string, playerId?: string | null) {
  const key = `${emoji}-${playerId}`
  const now = Date.now()
  if (now - parseInt(reactionThrottle[key] || '0') < 1000) return
  reactionThrottle[key] = String(now)
  // Spawn immediate local floater and pass its ID to the server so the echo can be skipped
  const localId = `local-${now}-${Math.random()}`
  localFloaterIds.add(localId)
  addFloater(emoji, localId, playerId)
  // Clean up the ID if the server never echoes back (e.g. network error)
  setTimeout(() => localFloaterIds.delete(localId), 3000)
  reactionCall.submit({
    match_id: props.matchId,
    emoji,
    player_id: playerId,
    client_id: localId,
  })
}

function handleReactionEvent(data: any) {
  if (data.event_type === 'reaction') {
    // Skip echo for floaters we already showed locally (matched via client_id)
    if (data.client_id && localFloaterIds.has(data.client_id)) {
      localFloaterIds.delete(data.client_id)
      return
    }
    addFloater(data.emoji, data.id, data.player_id)
  }
}

onMounted(() => {
  getSocket().on(`codeoff_match_${props.matchId}`, handleReactionEvent)
})

onUnmounted(() => {
  getSocket().off(`codeoff_match_${props.matchId}`, handleReactionEvent)
})
</script>

<style scoped>
@keyframes float-up {
  0% {
    transform: translateY(0) scale(1);
    opacity: 1;
  }
  70% {
    opacity: 0.9;
  }
  100% {
    transform: translateY(-50vh) scale(1.3);
    opacity: 0;
  }
}

.floater {
  animation: float-up 2.2s ease-out forwards;
}
</style>
