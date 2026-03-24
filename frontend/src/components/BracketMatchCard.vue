<template>
  <div class="w-72 overflow-hidden rounded-xl border" :class="borderClass">
    <!-- Player 1 -->
    <div
      class="flex items-center justify-between border-b border-gray-800 px-4 py-3"
      :class="playerBgClass(match.player_1)"
    >
      <span
        class="truncate text-base font-medium"
        :class="playerTextClass(match.player_1)"
      >
        {{ match.player_1_name || 'TBD' }}
      </span>
      <span
        v-if="match.winner === match.player_1"
        class="text-sm font-semibold text-green-400"
        >W</span
      >
    </div>
    <!-- Player 2 -->
    <div
      class="flex items-center justify-between px-4 py-3"
      :class="playerBgClass(match.player_2)"
    >
      <span
        class="truncate text-base font-medium"
        :class="playerTextClass(match.player_2)"
      >
        {{ match.player_2_name || 'TBD' }}
      </span>
      <span
        v-if="match.winner === match.player_2"
        class="text-sm font-semibold text-green-400"
        >W</span
      >
    </div>
    <!-- Status bar -->
    <div
      class="flex items-center justify-between border-t px-4 py-2"
      :class="statusClass"
    >
      <span class="text-xs font-medium uppercase tracking-wider">{{
        match.status
      }}</span>
      <button
        v-if="match.status === 'Live' || match.status === 'Ready'"
        class="text-xs font-medium text-blue-400 hover:text-blue-300"
        @click="$emit('spectate', match.name)"
      >
        Spectate →
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
  if (props.match.status === 'Live') return 'border-green-600'
  if (props.match.status === 'Ready') return 'border-blue-700'
  if (props.match.status === 'Finished') return 'border-gray-700'
  return 'border-gray-800'
})

const statusClass = computed(() => {
  if (props.match.status === 'Live')
    return 'border-green-900 bg-green-950/30 text-green-400'
  if (props.match.status === 'Ready')
    return 'border-blue-900 bg-blue-950/30 text-blue-400'
  if (props.match.status === 'Finished')
    return 'border-gray-800 bg-gray-900 text-gray-500'
  return 'border-gray-800 bg-gray-900 text-gray-600'
})

function playerBgClass(playerId: string | null): string {
  if (props.match.winner && props.match.winner === playerId)
    return 'bg-green-950/50'
  return 'bg-gray-900'
}

function playerTextClass(playerId: string | null): string {
  if (!playerId) return 'text-gray-600 italic'
  if (props.match.winner && props.match.winner !== playerId)
    return 'text-gray-600 line-through'
  return 'text-gray-200'
}
</script>
