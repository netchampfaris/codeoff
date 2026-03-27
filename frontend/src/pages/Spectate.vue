<template>
  <div class="bg-zinc-950 flex h-[100dvh] flex-col font-mono text-green-200">
    <AppNavbar
      :title="
        state
          ? `spectate / round ${state.round_number} . match ${state.bracket_position}`
          : 'spectate'
      "
    >
      <template #actions>
        <DevLoginDropdown />
      </template>
    </AppNavbar>

    <!-- Content area fills remaining height -->
    <div class="relative flex flex-1 flex-col overflow-hidden">
      <div v-if="loading" class="flex h-full items-center justify-center">
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
      <div v-else-if="state" class="relative flex h-full flex-col">
        <!-- ══ Mobile layout (hidden md+) ══════════════════════════════ -->
        <div class="flex flex-1 flex-col overflow-hidden md:hidden">
          <!-- Mobile header -->
          <div
            class="border-zinc-800 bg-zinc-900 flex shrink-0 items-center justify-between border-b px-4 py-2"
          >
            <div>
              <div class="text-xs uppercase tracking-widest text-green-700">
                r{{ state.round_number }} · m{{ state.bracket_position }}
              </div>
              <div
                class="text-sm font-bold uppercase tracking-wide text-green-400"
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
                      : 'text-green-400'
                "
              >
                {{
                  state.status === 'Live'
                    ? formatted
                    : state.status.toUpperCase()
                }}
              </div>
              <AppButton
                variant="ghost"
                @click="$router.push({ name: 'SpectateHome' })"
              >
                [home]
              </AppButton>
            </div>
          </div>

          <!-- Player 1 panel (top half) -->
          <div
            class="border-zinc-800 flex flex-1 flex-col overflow-hidden border-b"
          >
            <!-- Player 1 info bar -->
            <div
              class="bg-zinc-900 flex shrink-0 items-center justify-between px-3 py-1.5"
            >
              <div class="flex items-center gap-2">
                <span
                  class="text-xs font-bold uppercase tracking-wide text-green-300"
                  >{{ state.player_1?.name }}</span
                >
                <span class="text-xs font-bold text-green-600"
                  >▲ {{ state.votes_1 }}</span
                >
                <MatchVerdict
                  :status="state.status"
                  :winner="state.winner"
                  :player-id="state.player_1?.id"
                />
              </div>
              <div class="flex items-center gap-2">
                <EmojiButtonBar
                  :player-id="state.player_1?.id"
                  :active-emoji="activeEmoji"
                  @react="sendReaction"
                />
                <TestCaseDots
                  :total="state.problem?.total_test_cases || 0"
                  :passed="bestScore1?.passed_tests || 0"
                />
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
              class="bg-zinc-900 flex shrink-0 items-center justify-between px-3 py-1.5"
            >
              <div class="flex items-center gap-2">
                <span
                  class="text-xs font-bold uppercase tracking-wide text-green-300"
                  >{{ state.player_2?.name }}</span
                >
                <span class="text-xs font-bold text-green-600"
                  >▲ {{ state.votes_2 }}</span
                >
                <MatchVerdict
                  :status="state.status"
                  :winner="state.winner"
                  :player-id="state.player_2?.id"
                />
              </div>
              <div class="flex items-center gap-2">
                <EmojiButtonBar
                  :player-id="state.player_2?.id"
                  :active-emoji="activeEmoji"
                  @react="sendReaction"
                />
                <TestCaseDots
                  :total="state.problem?.total_test_cases || 0"
                  :passed="bestScore2?.passed_tests || 0"
                />
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
            class="border-zinc-800 bg-zinc-900 grid grid-cols-3 border-b px-6 py-3"
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
                  <TestCaseDots
                    :total="state.problem?.total_test_cases || 0"
                    :passed="bestScore1?.passed_tests || 0"
                    large
                  />
                  <MatchVerdict
                    :status="state.status"
                    :winner="state.winner"
                    :player-id="state.player_1?.id"
                    large
                  />
                </div>
              </div>
            </div>

            <!-- Center: round + timer -->
            <div class="flex flex-col items-center justify-center">
              <div class="flex items-center">
                <AppButton
                  variant="inline"
                  :active="showProblem"
                  class="!text-xl text-green-600 hover:text-green-400"
                  @click="showProblem = !showProblem"
                >
                  [{{ state.problem?.title || state.match_id }}]
                </AppButton>
              </div>
              <div
                class="mb-1 text-base font-bold uppercase tracking-widest text-green-400"
              >
                round {{ state.round_number }} · match
                {{ state.bracket_position }}
              </div>
              <div
                class="font-mono text-7xl font-bold leading-none tracking-tight"
                :class="
                  state.status !== 'Live'
                    ? 'text-green-800'
                    : remaining < 60
                      ? 'text-red-400'
                      : 'text-green-400'
                "
              >
                {{
                  state.status === 'Live'
                    ? formatted
                    : state.status.toUpperCase()
                }}
              </div>
              <div
                v-if="state.status === 'Finished' && !state.winner"
                class="mt-2 text-2xl font-black uppercase tracking-widest text-yellow-500"
              >
                — draw —
              </div>
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
                  <MatchVerdict
                    :status="state.status"
                    :winner="state.winner"
                    :player-id="state.player_2?.id"
                    large
                  />
                  <TestCaseDots
                    :total="state.problem?.total_test_cases || 0"
                    :passed="bestScore2?.passed_tests || 0"
                    large
                  />
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
            class="flex-shrink-0 border-t-2 border-green-400"
            :style="{ height: bottomPanelHeight + 'px' }"
          >
            <!-- Drag handle -->
            <div
              class="group flex h-1.5 w-full cursor-row-resize items-center justify-center bg-green-400 transition-colors hover:bg-green-300"
              @mousedown.prevent="startDragV"
            />
            <div class="flex h-full flex-row overflow-hidden">
              <!-- Statement -->
              <div class="border-zinc-800 flex-1 overflow-auto border-r">
                <ProblemPanel :problem="state.problem" />
              </div>
              <!-- Examples column -->
              <div
                v-if="state.problem.sample_test_cases?.length"
                class="bg-zinc-900 w-80 overflow-auto p-4"
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
                    class="border-zinc-800 bg-zinc-950 border p-2 text-xs text-green-300"
                  >
                    <div class="mb-1 text-green-700">$ input:</div>
                    <code class="block whitespace-pre text-green-400">{{
                      tc.input
                    }}</code>
                  </div>
                  <div
                    class="border-zinc-800 bg-zinc-950 mt-1 border p-2 text-xs"
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
            class="floater absolute bottom-14 text-4xl"
            :style="{ left: f.x + '%' }"
          >
            <span class="floater-emoji" :class="f.dir">{{ f.emoji }}</span>
          </div>
        </div>

        <!-- Dev login-as panel removed — now in AppNavbar #actions slot -->

        <!-- Reaction bar: desktop only (mobile uses inline buttons in player info bars) -->
        <div
          class="border-zinc-800 bg-zinc-900/90 fixed bottom-0 left-0 right-0 z-50 hidden items-stretch border-t backdrop-blur-sm md:flex"
        >
          <div
            class="border-zinc-800 flex flex-1 items-center justify-center gap-3 border-r py-2"
          >
            <span
              class="mr-1 text-xs uppercase tracking-widest text-green-800"
              >{{ state.player_1?.name }}</span
            >
            <EmojiButtonBar
              :player-id="state.player_1?.id"
              :active-emoji="activeEmoji"
              large
              @react="sendReaction"
            />
          </div>
          <div class="flex flex-1 items-center justify-center gap-3 py-2">
            <EmojiButtonBar
              :player-id="state.player_2?.id"
              :active-emoji="activeEmoji"
              large
              @react="sendReaction"
            />
            <span
              class="ml-1 text-xs uppercase tracking-widest text-green-800"
              >{{ state.player_2?.name }}</span
            >
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useCall } from 'frappe-ui'
import { useMatchState, useMatchTimer } from '@/data/match'
import { useLobbyPoll } from '@/data/useLobbyPoll'
import { useMatchPlayers } from '@/data/useMatchPlayers'
import { getSocket } from '@/data/socket'
import AppNavbar from '@/components/AppNavbar.vue'
import AppButton from '@/components/AppButton.vue'
import WaitingLobby from '@/components/WaitingLobby.vue'
import PlayerPanel from '@/components/PlayerPanel.vue'
import ProblemPanel from '@/components/ProblemPanel.vue'
import DevLoginDropdown from '@/components/DevLoginDropdown.vue'
import TestCaseDots from '@/components/TestCaseDots.vue'
import EmojiButtonBar from '@/components/EmojiButtonBar.vue'
import MatchVerdict from '@/components/MatchVerdict.vue'
import { useResizablePanels } from '@/data/useResizablePanels'

const props = defineProps<{
  matchId: string
}>()

const { state, loading, reload } = useMatchState(props.matchId)
const { remaining, formatted } = useMatchTimer(state)

// Poll for status change after timer expires (server processes asynchronously)
watch(remaining, (r) => {
  if (r === 0 && state.value?.status === 'Live') {
    const t = setInterval(() => {
      if (!state.value || state.value.status !== 'Live') {
        clearInterval(t)
        return
      }
      reload()
    }, 2000)
    onUnmounted(() => clearInterval(t))
  }
})

const showProblem = ref(false)
const { bottomPanelHeight, startDragV } = useResizablePanels({
  bottomMin: 120,
  bottomMax: 700,
  bottomDefault: Math.round(window.innerHeight * 0.38),
})

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

// ── Reactions ────────────────────────────────────────────────────────────────

interface Floater {
  id: string
  emoji: string
  x: number
  dir: 'left' | 'right'
}

const floaters = ref<Floater[]>([])
const reactionThrottle: Record<string, string> = {}

// key: `${emoji}-${playerId}` — briefly true after firing for button burst animation
const activeEmoji = ref<Record<string, boolean>>({})

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
  const dir = Math.random() < 0.5 ? 'left' : 'right'
  floaters.value.push({ id, emoji, x: playerSideX(playerId), dir })
  setTimeout(() => {
    floaters.value = floaters.value.filter((f) => f.id !== id)
  }, 2800)
}

// IDs of floaters we spawned locally — skip their socket echo
const localFloaterIds = new Set<string>()

function sendReaction(emoji: string, playerId?: string | null) {
  const key = `${emoji}-${playerId}`
  const now = Date.now()
  if (now - parseInt(reactionThrottle[key] || '0') < 1000) return
  reactionThrottle[key] = String(now)

  // Burst animation on the button
  activeEmoji.value[key] = true
  setTimeout(() => {
    delete activeEmoji.value[key]
  }, 350)

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
/* ── Floating emoji overlay ─────────────────────────────────────────────── */
@keyframes float-up {
  0% {
    transform: translateY(0);
    opacity: 0;
  }
  8% {
    opacity: 1;
  }
  80% {
    opacity: 0.9;
  }
  100% {
    transform: translateY(-58vh);
    opacity: 0;
  }
}

/* Inner: horizontal sway + rotation — gives a curved bubble path */
@keyframes sway-right {
  0% {
    transform: translateX(0) rotate(-4deg) scale(1.25);
  }
  30% {
    transform: translateX(18px) rotate(5deg);
  }
  65% {
    transform: translateX(7px) rotate(-2deg);
  }
  100% {
    transform: translateX(14px) rotate(4deg) scale(0.85);
  }
}
@keyframes sway-left {
  0% {
    transform: translateX(0) rotate(4deg) scale(1.25);
  }
  30% {
    transform: translateX(-18px) rotate(-5deg);
  }
  65% {
    transform: translateX(-7px) rotate(2deg);
  }
  100% {
    transform: translateX(-14px) rotate(-4deg) scale(0.85);
  }
}

.floater {
  animation: float-up 2.8s cubic-bezier(0.25, 0.8, 0.4, 1) forwards;
}

.floater-emoji {
  display: inline-block;
  animation: sway-right 2.8s ease-in-out forwards;
}
.floater-emoji.left {
  animation-name: sway-left;
}
</style>
