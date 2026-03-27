<template>
  <div class="w-80 overflow-hidden border font-mono" :class="borderClass">
    <!-- Player 1 -->
    <div
      class="border-zinc-800 flex items-center justify-between border-b px-3 py-2.5"
      :class="playerBgClass(match.player_1)"
    >
      <span class="truncate text-base" :class="playerTextClass(match.player_1)">
        {{ match.player_1_name || 'tbd' }}
      </span>
      <div class="flex items-center gap-2">
        <span
          v-if="showScores && match.best_score_player_1 > 0"
          class="text-xs tabular-nums text-green-600"
          >{{ match.best_score_player_1 }}</span
        >
        <span
          v-if="match.winner === match.player_1"
          class="text-base font-bold text-green-400"
          >[W]</span
        >
      </div>
    </div>
    <!-- Player 2 -->
    <div
      class="flex items-center justify-between px-3 py-2.5"
      :class="playerBgClass(match.player_2)"
    >
      <span class="truncate text-base" :class="playerTextClass(match.player_2)">
        {{ match.player_2_name || 'tbd' }}
      </span>
      <div class="flex items-center gap-2">
        <span
          v-if="showScores && match.best_score_player_2 > 0"
          class="text-xs tabular-nums text-green-600"
          >{{ match.best_score_player_2 }}</span
        >
        <span
          v-if="match.winner === match.player_2"
          class="text-base font-bold text-green-400"
          >[W]</span
        >
      </div>
    </div>
    <!-- Status bar -->
    <div
      class="flex items-center justify-between border-t px-3 py-1.5"
      :class="statusClass"
    >
      <span
        class="flex items-center gap-1.5 text-xs font-bold uppercase tracking-widest"
      >
        <span
          v-if="match.status === 'Live'"
          class="inline-block h-1.5 w-1.5 animate-pulse rounded-full bg-green-400"
        />
        {{ match.status }}
        <span
          v-if="match.status === 'Live' && remaining > 0"
          class="font-mono tabular-nums"
          >{{ timerFormatted }}</span
        >
      </span>
      <div class="flex items-center gap-2">
        <AppButton
          v-if="isOrganizer && match.status === 'Draft'"
          variant="inline"
          class="text-green-700 hover:text-green-400"
          @click="$emit('makeReady', match.name)"
        >
          [make ready]
        </AppButton>
        <AppButton
          v-if="match.status === 'Live' || match.status === 'Ready'"
          variant="inline"
          class="text-green-400 hover:text-green-300"
          @click="$emit('spectate', match.name)"
        >
          [spectate]
        </AppButton>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import AppButton from '@/components/AppButton.vue'

const props = defineProps<{
  match: {
    name: string
    status: string
    player_1: string | null
    player_2: string | null
    player_1_name: string | null
    player_2_name: string | null
    winner: string | null
    deadline: string | null
    best_score_player_1: number
    best_score_player_2: number
  }
  isOrganizer?: boolean
}>()

defineEmits<{
  spectate: [matchId: string]
  makeReady: [matchId: string]
}>()

const borderClass = computed(() => {
  if (props.match.status === 'Live') return 'border-green-400'
  if (props.match.status === 'Ready') return 'border-green-700'
  if (props.match.status === 'Finished') return 'border-zinc-800'
  return 'border-zinc-800'
})

const statusClass = computed(() => {
  if (props.match.status === 'Live')
    return 'border-green-900 bg-green-950/20 text-green-400'
  if (props.match.status === 'Ready')
    return 'border-green-900 bg-green-950/10 text-green-600'
  if (props.match.status === 'Finished')
    return 'border-zinc-800 bg-zinc-900 text-green-800'
  return 'border-zinc-800 bg-zinc-900 text-green-900'
})

const remaining = ref(0)
let timerId: ReturnType<typeof setInterval> | null = null

function updateTimer() {
  if (!props.match.deadline || props.match.status !== 'Live') {
    remaining.value = 0
    return
  }
  const deadlineMs = new Date(props.match.deadline).getTime()
  remaining.value = Math.max(0, Math.floor((deadlineMs - Date.now()) / 1000))
}

onMounted(() => {
  updateTimer()
  timerId = setInterval(updateTimer, 1000)
})

onUnmounted(() => {
  if (timerId) clearInterval(timerId)
})

const timerFormatted = computed(() => {
  const m = Math.floor(remaining.value / 60)
  const s = remaining.value % 60
  return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`
})

const showScores = computed(
  () => props.match.status === 'Live' || props.match.status === 'Finished',
)

function playerBgClass(playerId: string | null): string {
  if (props.match.winner && props.match.winner === playerId)
    return 'bg-green-950/30'
  return 'bg-zinc-900'
}

function playerTextClass(playerId: string | null): string {
  if (!playerId) return 'text-green-900 italic'
  if (props.match.winner && props.match.winner !== playerId)
    return 'text-green-900 line-through'
  return 'text-green-200'
}
</script>
