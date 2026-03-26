<template>
  <div class="w-80 overflow-hidden border font-mono" :class="borderClass">
    <!-- Player 1 -->
    <div
      class="flex items-center justify-between border-b border-term-border px-3 py-2.5"
      :class="playerBgClass(match.player_1)"
    >
      <span class="truncate text-base" :class="playerTextClass(match.player_1)">
        {{ match.player_1_name || 'tbd' }}
      </span>
      <span
        v-if="match.winner === match.player_1"
        class="text-base font-bold text-term-green"
        >[W]</span
      >
    </div>
    <!-- Player 2 -->
    <div
      class="flex items-center justify-between px-3 py-2.5"
      :class="playerBgClass(match.player_2)"
    >
      <span class="truncate text-base" :class="playerTextClass(match.player_2)">
        {{ match.player_2_name || 'tbd' }}
      </span>
      <span
        v-if="match.winner === match.player_2"
        class="text-base font-bold text-term-green"
        >[W]</span
      >
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
          class="inline-block h-1.5 w-1.5 animate-pulse rounded-full bg-term-green"
        />
        {{ match.status }}
      </span>
      <button
        v-if="match.status === 'Live' || match.status === 'Ready'"
        class="text-xs font-bold uppercase tracking-wider text-term-green hover:text-green-300"
        @click="$emit('spectate', match.name)"
      >
        [spectate]
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  match: {
    name: string
    status: string
    player_1: string | null
    player_2: string | null
    player_1_name: string | null
    player_2_name: string | null
    winner: string | null
  }
}>()

defineEmits<{
  spectate: [matchId: string]
}>()

const borderClass = computed(() => {
  if (props.match.status === 'Live') return 'border-term-green'
  if (props.match.status === 'Ready') return 'border-green-700'
  if (props.match.status === 'Finished') return 'border-term-border'
  return 'border-term-border'
})

const statusClass = computed(() => {
  if (props.match.status === 'Live')
    return 'border-green-900 bg-green-950/20 text-term-green'
  if (props.match.status === 'Ready')
    return 'border-green-900 bg-green-950/10 text-green-600'
  if (props.match.status === 'Finished')
    return 'border-term-border bg-term-surface text-green-800'
  return 'border-term-border bg-term-surface text-green-900'
})

function playerBgClass(playerId: string | null): string {
  if (props.match.winner && props.match.winner === playerId)
    return 'bg-green-950/30'
  return 'bg-term-surface'
}

function playerTextClass(playerId: string | null): string {
  if (!playerId) return 'text-green-900 italic'
  if (props.match.winner && props.match.winner !== playerId)
    return 'text-green-900 line-through'
  return 'text-green-200'
}
</script>
