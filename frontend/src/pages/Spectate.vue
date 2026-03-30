<template>
  <div class="flex h-[100dvh] flex-col bg-zinc-950 font-mono text-green-200">
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
        :selected-player-id="selectedPlayerId"
        :prediction-pending="predictionPending"
        large
        @pick="handlePredictionPick"
        @start="startMatch"
      />
      <div v-else-if="state" class="relative flex h-full min-h-0 flex-col">
        <div
          class="pointer-events-none absolute inset-x-0 top-2 z-50 flex flex-col gap-2 px-3 md:top-3 md:px-6"
        >
          <transition name="banner-fade">
            <div
              v-if="activeBanner"
              class="momentum-banner mx-auto w-full max-w-xl border px-4 py-2"
              :class="activeBanner.tone"
            >
              <div
                class="text-current/70 text-[10px] uppercase tracking-[0.35em]"
              >
                {{ activeBanner.label }}
              </div>
              <div
                class="text-sm font-bold uppercase tracking-wide text-current md:text-base"
              >
                {{ activeBanner.message }}
              </div>
            </div>
          </transition>

          <div class="flex items-start justify-between gap-3">
            <transition name="banner-fade">
              <div
                v-if="leftSpike"
                class="reaction-spike-chip border px-3 py-1 text-left text-[10px] uppercase tracking-[0.3em]"
              >
                {{ leftSpike.message }}
              </div>
            </transition>
            <transition name="banner-fade">
              <div
                v-if="rightSpike"
                class="reaction-spike-chip border px-3 py-1 text-right text-[10px] uppercase tracking-[0.3em]"
              >
                {{ rightSpike.message }}
              </div>
            </transition>
          </div>
        </div>

        <!-- ══ Mobile layout (hidden md+) ══════════════════════════════ -->
        <div class="flex min-h-0 flex-1 flex-col overflow-hidden md:hidden">
          <!-- Mobile header -->
          <div
            class="flex shrink-0 items-center justify-between border-b border-zinc-800 bg-zinc-900 px-4 py-2"
          >
            <div>
              <div class="flex flex-wrap items-center gap-x-2 gap-y-1">
                <div
                  class="text-sm font-bold uppercase tracking-wide text-green-400"
                >
                  {{ state.problem?.title || state.match_id }}
                </div>
                <div
                  class="text-[10px] uppercase tracking-[0.3em] text-green-700"
                >
                  {{ mobileRoundMatchLabel }}
                </div>
              </div>
              <div
                v-if="predictionStatusLabel || headerHintLabel"
                class="mt-1 flex flex-wrap items-center gap-x-2 gap-y-1 text-[10px] uppercase tracking-widest"
              >
                <span v-if="predictionStatusLabel" class="text-green-700">{{
                  predictionStatusLabel
                }}</span>
                <span v-if="headerHintLabel" class="text-green-800">{{
                  headerHintLabel
                }}</span>
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
            class="flex min-h-0 flex-1 flex-col overflow-hidden border-b border-zinc-800"
            :class="{ 'panel-spike': isSpikeActive(state.player_1?.id) }"
          >
            <!-- Player 1 info bar -->
            <div
              class="flex shrink-0 items-center justify-between bg-zinc-900 px-3 py-1.5"
            >
              <div class="flex items-center gap-2">
                <span
                  class="text-xs font-bold uppercase tracking-wide text-green-300"
                  >{{ state.player_1?.name }}</span
                >
                <span
                  v-if="showCrowdSplit"
                  class="text-[10px] uppercase tracking-[0.25em] text-green-800"
                >
                  {{ leftCrowdSplit }}
                </span>
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
            <div class="min-h-0 flex-1 overflow-hidden">
              <PlayerPanel
                :player-name="state.player_1?.name || 'Player 1'"
                :code="player1Code"
                :submissions="player1Submissions"
                side="left"
                :class="{ 'panel-spike': isSpikeActive(state.player_1?.id) }"
              />
            </div>
          </div>

          <!-- Player 2 panel (bottom half) -->
          <div
            class="flex min-h-0 flex-1 flex-col overflow-hidden"
            :class="{ 'panel-spike': isSpikeActive(state.player_2?.id) }"
          >
            <!-- Player 2 info bar -->
            <div
              class="flex shrink-0 items-center justify-between bg-zinc-900 px-3 py-1.5"
            >
              <div class="flex items-center gap-2">
                <span
                  class="text-xs font-bold uppercase tracking-wide text-green-300"
                  >{{ state.player_2?.name }}</span
                >
                <span
                  v-if="showCrowdSplit"
                  class="text-[10px] uppercase tracking-[0.25em] text-green-800"
                >
                  {{ rightCrowdSplit }}
                </span>
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
            <div class="min-h-0 flex-1 overflow-hidden">
              <PlayerPanel
                :player-name="state.player_2?.name || 'Player 2'"
                :code="player2Code"
                :submissions="player2Submissions"
                :class="{ 'panel-spike': isSpikeActive(state.player_2?.id) }"
              />
            </div>
          </div>
        </div>

        <!-- ══ Desktop layout (hidden mobile) ══════════════════════════ -->
        <div class="hidden flex-1 flex-col overflow-hidden pb-16 md:flex">
          <!-- Top bar: player | timer | player -->
          <div
            class="grid grid-cols-3 border-b border-zinc-800 bg-zinc-900 px-6 py-2"
          >
            <!-- Player 1 -->
            <div
              class="flex items-start"
              :class="{ 'panel-spike': isSpikeActive(state.player_1?.id) }"
            >
              <div>
                <div class="text-xs uppercase tracking-widest text-green-700">
                  ← player 1
                </div>
                <div class="flex items-baseline gap-3">
                  <div class="text-3xl font-bold tracking-tight text-green-300">
                    {{ state.player_1?.name || 'Player 1' }}
                  </div>
                  <div
                    v-if="showCrowdSplit"
                    class="text-xs uppercase tracking-[0.3em] text-green-800"
                  >
                    {{ leftCrowdSplit }}
                  </div>
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
              <div
                class="mb-1 flex flex-wrap items-center justify-center gap-x-3 gap-y-1 text-[11px] uppercase tracking-[0.3em]"
              >
                <AppButton
                  variant="inline"
                  :active="showProblem"
                  class="!text-sm text-green-600 hover:text-green-400"
                  @click="showProblem = !showProblem"
                >
                  [{{ state.problem?.title || state.match_id }}]
                </AppButton>
                <span v-if="predictionStatusLabel" class="text-green-500">
                  {{ predictionStatusLabel }}
                </span>
                <span v-if="headerHintLabel" class="text-green-800">
                  {{ headerHintLabel }}
                </span>
              </div>
              <div class="flex items-end justify-center gap-6">
                <div
                  class="font-mono text-6xl font-bold leading-none tracking-tight"
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
              </div>
              <div
                v-if="state.status === 'Finished' && !state.winner"
                class="mt-2 text-2xl font-black uppercase tracking-widest text-yellow-500"
              >
                — draw —
              </div>
            </div>

            <!-- Player 2 -->
            <div
              class="flex items-start justify-end"
              :class="{ 'panel-spike': isSpikeActive(state.player_2?.id) }"
            >
              <div class="text-right">
                <div class="text-xs uppercase tracking-widest text-green-700">
                  player 2 →
                </div>
                <div class="flex items-baseline justify-end gap-3">
                  <div
                    v-if="showCrowdSplit"
                    class="text-xs uppercase tracking-[0.3em] text-green-800"
                  >
                    {{ rightCrowdSplit }}
                  </div>
                  <div class="text-3xl font-bold tracking-tight text-green-300">
                    {{ state.player_2?.name || 'Player 2' }}
                  </div>
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
              :class="{ 'panel-spike': isSpikeActive(state.player_1?.id) }"
            />
            <PlayerPanel
              :player-name="state.player_2?.name || 'Player 2'"
              :code="player2Code"
              :submissions="player2Submissions"
              :class="{ 'panel-spike': isSpikeActive(state.player_2?.id) }"
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
              <div class="flex-1 overflow-auto border-r border-zinc-800">
                <ProblemPanel :problem="state.problem" />
              </div>
              <!-- Examples column -->
              <div
                v-if="state.problem.sample_test_cases?.length"
                class="w-80 overflow-auto bg-zinc-900 p-4"
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
                    class="border border-zinc-800 bg-zinc-950 p-2 text-xs text-green-300"
                  >
                    <div class="mb-1 text-green-700">$ input:</div>
                    <code class="block whitespace-pre text-green-400">{{
                      tc.input
                    }}</code>
                  </div>
                  <div
                    class="mt-1 border border-zinc-800 bg-zinc-950 p-2 text-xs"
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
          class="fixed bottom-0 left-0 right-0 z-50 hidden items-stretch border-t border-zinc-800 bg-zinc-900/90 backdrop-blur-sm md:flex"
        >
          <div
            class="flex flex-1 items-center justify-center gap-3 border-r border-zinc-800 py-2"
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
import {
  getPredictionStats,
  getStoredPrediction,
  setStoredPrediction,
} from '@/data/predictions'
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
const selectedPlayerId = ref(getStoredPrediction(props.matchId))
const predictionPending = ref(false)
const pendingPredictionId = ref<string | null>(null)

const showProblem = ref(false)
const { bottomPanelHeight, startDragV } = useResizablePanels({
  bottomMin: 120,
  bottomMax: 700,
  bottomDefault: Math.round(window.innerHeight * 0.38),
})

useLobbyPoll(
  computed(() => state.value?.status),
  reload,
  ['Ready', 'Live'],
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
const startMatchCall: any = useCall({
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
const voteCall: any = useCall({
  url: '/api/v2/method/codeoff.api.contest.vote_for_player',
  immediate: false,
  onSuccess() {
    if (pendingPredictionId.value) {
      selectedPlayerId.value = pendingPredictionId.value
      setStoredPrediction(props.matchId, pendingPredictionId.value)
    }
    pendingPredictionId.value = null
    predictionPending.value = false
  },
  onError() {
    pendingPredictionId.value = null
    predictionPending.value = false
  },
})

function handlePredictionPick(playerId: string) {
  if (selectedPlayerId.value || predictionPending.value) return
  pendingPredictionId.value = playerId
  predictionPending.value = true
  voteCall.submit({ match_id: props.matchId, player_id: playerId })
}

const predictionStats = computed(() =>
  getPredictionStats(state.value?.votes_1, state.value?.votes_2),
)

const selectedPlayerName = computed(() => {
  if (!state.value || !selectedPlayerId.value) return ''
  if (selectedPlayerId.value === state.value.player_1?.id) {
    return state.value.player_1?.name || 'player_1'
  }
  if (selectedPlayerId.value === state.value.player_2?.id) {
    return state.value.player_2?.name || 'player_2'
  }
  return ''
})

const predictionStatusLabel = computed(() => {
  if (!state.value || !selectedPlayerId.value || !selectedPlayerName.value)
    return ''
  if (state.value.status === 'Live')
    return `your pick: ${selectedPlayerName.value}`
  if (state.value.status === 'Review')
    return `your pick: ${selectedPlayerName.value} · pending`
  if (state.value.status === 'Finished') {
    if (!state.value.winner)
      return `your pick: ${selectedPlayerName.value} · draw`
    return state.value.winner === selectedPlayerId.value
      ? `call hit: ${selectedPlayerName.value}`
      : `call missed: ${selectedPlayerName.value}`
  }
  return `your pick: ${selectedPlayerName.value}`
})

const hasCrowdSplit = computed(() => predictionStats.value.total > 0)

const showCrowdSplit = computed(
  () =>
    hasCrowdSplit.value &&
    (!!selectedPlayerId.value || !!state.value?.is_organizer),
)

const leftCrowdSplit = computed(() =>
  hasCrowdSplit.value ? `${predictionStats.value.percent1}%` : '',
)

const rightCrowdSplit = computed(() =>
  hasCrowdSplit.value ? `${predictionStats.value.percent2}%` : '',
)

const crowdTotalLabel = computed(() =>
  showCrowdSplit.value
    ? `${predictionStats.value.total} pick${predictionStats.value.total === 1 ? '' : 's'}`
    : '',
)

const mobileRoundMatchLabel = computed(() => {
  const base = `r${state.value?.round_number} · m${state.value?.bracket_position}`
  return crowdTotalLabel.value ? `${base} · ${crowdTotalLabel.value}` : base
})

const headerHintLabel = computed(() => {
  if (state.value?.status === 'Ready') {
    return state.value.is_organizer
      ? 'organizer view'
      : 'pick to reveal crowd split'
  }
  return ''
})

// ── Reactions ────────────────────────────────────────────────────────────────

interface Floater {
  id: string
  emoji: string
  x: number
  dir: 'left' | 'right'
}

interface MomentumBanner {
  id: string
  label: string
  message: string
  priority: number
  durationMs: number
  tone: 'success' | 'lead' | 'warning' | 'review'
}

interface ReactionSpike {
  id: string
  playerId: string
  message: string
}

const floaters = ref<Floater[]>([])
const reactionThrottle: Record<string, string> = {}
const activeBanner = ref<MomentumBanner | null>(null)
const queuedBanners = ref<MomentumBanner[]>([])
const activeSpikes = ref<ReactionSpike[]>([])
const reactionWindowByPlayer: Record<string, number[]> = {}
const spikeCooldownByPlayer: Record<string, number> = {}
const finalMinuteShown = ref(false)

const REACTION_SPIKE_WINDOW_MS = 3000
const REACTION_SPIKE_DURATION_MS = 2200
const REACTION_SPIKE_THRESHOLD = 8
const REACTION_SPIKE_COOLDOWN_MS = 4500

let bannerTimer: ReturnType<typeof setTimeout> | null = null

// key: `${emoji}-${playerId}` — briefly true after firing for button burst animation
const activeEmoji = ref<Record<string, boolean>>({})

const reactionCall: any = useCall({
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

function playerNameFor(playerId: string | null | undefined): string {
  if (!state.value || !playerId) return 'crowd'
  if (playerId === state.value.player_1?.id)
    return state.value.player_1?.name || 'player 1'
  if (playerId === state.value.player_2?.id)
    return state.value.player_2?.name || 'player 2'
  return 'crowd'
}

function showBanner(banner: MomentumBanner) {
  activeBanner.value = banner
  if (bannerTimer) clearTimeout(bannerTimer)
  bannerTimer = setTimeout(() => {
    activeBanner.value = null
    const nextBanner = queuedBanners.value.shift()
    if (nextBanner) showBanner(nextBanner)
  }, banner.durationMs)
}

function queueBanner(banner: MomentumBanner) {
  if (!activeBanner.value) {
    showBanner(banner)
    return
  }

  if (banner.priority > activeBanner.value.priority) {
    showBanner(banner)
    return
  }

  queuedBanners.value.push(banner)
  queuedBanners.value.sort((left, right) => right.priority - left.priority)
}

function pushMomentumBanner(
  label: string,
  message: string,
  tone: MomentumBanner['tone'],
  priority: number,
  durationMs = 2800,
) {
  queueBanner({
    id: `${Date.now()}-${Math.random()}`,
    label,
    message,
    tone,
    priority,
    durationMs,
  })
}

function triggerReactionSpike(playerId: string) {
  const spikeId = `${playerId}-${Date.now()}`
  activeSpikes.value = activeSpikes.value.filter(
    (spike) => spike.playerId !== playerId,
  )
  activeSpikes.value.push({
    id: spikeId,
    playerId,
    message: `crowd erupts for ${playerNameFor(playerId)}`,
  })

  setTimeout(() => {
    activeSpikes.value = activeSpikes.value.filter(
      (spike) => spike.id !== spikeId,
    )
  }, REACTION_SPIKE_DURATION_MS)
}

function noteReaction(playerId: string | null | undefined) {
  if (!playerId) return

  const now = Date.now()
  const recent = (reactionWindowByPlayer[playerId] || []).filter(
    (timestamp) => now - timestamp <= REACTION_SPIKE_WINDOW_MS,
  )
  recent.push(now)
  reactionWindowByPlayer[playerId] = recent

  if (
    recent.length >= REACTION_SPIKE_THRESHOLD &&
    now - (spikeCooldownByPlayer[playerId] || 0) > REACTION_SPIKE_COOLDOWN_MS
  ) {
    spikeCooldownByPlayer[playerId] = now
    triggerReactionSpike(playerId)
  }
}

function isSpikeActive(playerId: string | null | undefined) {
  return (
    !!playerId &&
    activeSpikes.value.some((spike) => spike.playerId === playerId)
  )
}

const leftSpike = computed(
  () =>
    activeSpikes.value.find(
      (spike) => spike.playerId === state.value?.player_1?.id,
    ) || null,
)

const rightSpike = computed(
  () =>
    activeSpikes.value.find(
      (spike) => spike.playerId === state.value?.player_2?.id,
    ) || null,
)

function leaderForScores(
  score1: number,
  score2: number,
  player1Id: string | null | undefined,
  player2Id: string | null | undefined,
) {
  if (score1 === score2) return null
  return score1 > score2 ? player1Id || null : player2Id || null
}

const momentumSnapshot = computed(() => {
  if (!state.value) return null

  const submissions = state.value.submissions || []
  const lastSubmission = submissions[submissions.length - 1]

  return {
    status: state.value.status,
    winner: state.value.winner,
    winningReason: state.value.winning_reason,
    player1Id: state.value.player_1?.id || null,
    player2Id: state.value.player_2?.id || null,
    score1: bestScore1.value?.passed_tests || 0,
    score2: bestScore2.value?.passed_tests || 0,
    submissionsCount: submissions.length,
    lastSubmissionPlayerId: lastSubmission?.player || null,
  }
})

watch(momentumSnapshot, (next, prev) => {
  if (!next || !prev) return

  if (
    next.winner &&
    next.winner !== prev.winner &&
    next.winningReason === 'First Accepted'
  ) {
    pushMomentumBanner(
      'solve landed',
      `${playerNameFor(next.winner)} lands the solve`,
      'success',
      100,
      3200,
    )
    return
  }

  if (next.status === 'Review' && prev.status !== 'Review') {
    pushMomentumBanner('review', 'match under review', 'review', 90, 3200)
    return
  }

  const scoresChanged =
    next.score1 !== prev.score1 || next.score2 !== prev.score2
  const previousLeader = leaderForScores(
    prev.score1,
    prev.score2,
    prev.player1Id,
    prev.player2Id,
  )
  const nextLeader = leaderForScores(
    next.score1,
    next.score2,
    next.player1Id,
    next.player2Id,
  )

  if (scoresChanged && nextLeader && nextLeader !== previousLeader) {
    pushMomentumBanner(
      previousLeader ? 'answer back' : 'lead change',
      previousLeader
        ? `${playerNameFor(nextLeader)} answers back`
        : `${playerNameFor(nextLeader)} takes the lead`,
      'lead',
      previousLeader ? 80 : 70,
    )
    return
  }

  if (
    prev.submissionsCount === 0 &&
    next.submissionsCount > 0 &&
    next.lastSubmissionPlayerId
  ) {
    pushMomentumBanner(
      'first blood',
      `${playerNameFor(next.lastSubmissionPlayerId)} lands first blood`,
      'warning',
      60,
    )
  }
})

watch(
  () => [state.value?.status, remaining.value] as const,
  ([status, secondsLeft], previous) => {
    if (status !== 'Live') {
      finalMinuteShown.value = false
      return
    }

    if (
      !finalMinuteShown.value &&
      secondsLeft <= 60 &&
      (!previous || previous[1] > 60)
    ) {
      finalMinuteShown.value = true
      pushMomentumBanner('time pressure', 'final minute', 'warning', 65, 2600)
    }
  },
)

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
  noteReaction(playerId)
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
    noteReaction(data.player_id)
  }
}

onMounted(() => {
  getSocket().on(`codeoff_match_${props.matchId}`, handleReactionEvent)
})

onUnmounted(() => {
  if (bannerTimer) clearTimeout(bannerTimer)
  getSocket().off(`codeoff_match_${props.matchId}`, handleReactionEvent)
})
</script>

<style scoped>
@keyframes banner-slide-in {
  0% {
    transform: translateY(-8px);
    opacity: 0;
  }
  100% {
    transform: translateY(0);
    opacity: 1;
  }
}

@keyframes panel-spike-pulse {
  0% {
    box-shadow:
      inset 0 0 0 0 rgba(74, 222, 128, 0),
      0 0 0 0 rgba(74, 222, 128, 0);
    background: rgba(34, 197, 94, 0);
  }
  30% {
    box-shadow:
      inset 0 0 0 1px rgba(74, 222, 128, 0.8),
      0 0 18px rgba(74, 222, 128, 0.18);
    background: rgba(34, 197, 94, 0.08);
  }
  100% {
    box-shadow:
      inset 0 0 0 0 rgba(74, 222, 128, 0),
      0 0 0 0 rgba(74, 222, 128, 0);
    background: rgba(34, 197, 94, 0);
  }
}

.banner-fade-enter-active,
.banner-fade-leave-active {
  transition:
    opacity 0.18s ease,
    transform 0.18s ease;
}

.banner-fade-enter-from,
.banner-fade-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}

.momentum-banner {
  animation: banner-slide-in 0.22s ease-out;
  backdrop-filter: blur(10px);
}

.momentum-banner.success {
  background: rgba(2, 44, 34, 0.94);
  border-color: rgba(74, 222, 128, 0.8);
  color: rgb(187 247 208);
}

.momentum-banner.lead {
  background: rgba(5, 46, 22, 0.94);
  border-color: rgba(34, 197, 94, 0.65);
  color: rgb(134 239 172);
}

.momentum-banner.warning {
  background: rgba(26, 26, 12, 0.94);
  border-color: rgba(250, 204, 21, 0.55);
  color: rgb(253 224 71);
}

.momentum-banner.review {
  background: rgba(39, 39, 42, 0.94);
  border-color: rgba(161, 161, 170, 0.65);
  color: rgb(228 228 231);
}

.reaction-spike-chip {
  background: rgba(5, 46, 22, 0.9);
  border-color: rgba(34, 197, 94, 0.45);
  color: rgb(134 239 172);
  backdrop-filter: blur(8px);
}

.panel-spike {
  animation: panel-spike-pulse 1.6s ease-out;
}

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
