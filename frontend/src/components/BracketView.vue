<template>
  <div class="flex flex-1 flex-col overflow-hidden">
    <!-- Header -->
    <div
      class="flex items-center justify-between border-b border-gray-800 px-8 py-6"
    >
      <div>
        <h1 class="text-3xl font-bold text-white">
          {{ data.tournament_name }}
        </h1>
        <div class="mt-2 text-base text-gray-400">
          Round {{ data.current_round || 1 }} of {{ data.total_rounds }}
        </div>
      </div>
      <Badge
        :theme="data.status === 'In Progress' ? 'green' : 'gray'"
        variant="subtle"
        size="lg"
      >
        {{ data.status }}
      </Badge>
    </div>

    <!-- Bracket visualization -->
    <div
      class="flex flex-1 items-center justify-center overflow-x-auto px-8 py-10"
    >
      <div class="flex items-center gap-12">
        <div
          v-for="round in sortedRounds"
          :key="round.number"
          class="flex flex-col items-center gap-4"
        >
          <div
            class="mb-3 text-sm font-semibold uppercase tracking-wider text-gray-400"
          >
            {{ getRoundLabel(round.number) }}
          </div>
          <div
            class="flex flex-col justify-around"
            :style="{ gap: `${roundGap(round.number)}px` }"
          >
            <BracketMatchCard
              v-for="m in round.matches"
              :key="m.name"
              :match="m"
              @spectate="$emit('spectate', $event)"
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import BracketMatchCard from './BracketMatchCard.vue'

const props = defineProps<{
  data: {
    tournament_name: string
    tournament_id: string
    status: string
    current_round: number | null
    total_rounds: number
    rounds: Record<string, any[]>
  }
}>()

defineEmits<{
  spectate: [matchId: string]
}>()

const sortedRounds = computed(() => {
  return Object.keys(props.data.rounds)
    .map(Number)
    .sort((a, b) => a - b)
    .map((n) => ({ number: n, matches: props.data.rounds[n] }))
})

function getRoundLabel(round: number): string {
  const total = props.data.total_rounds
  if (round === total) return 'Final'
  if (round === total - 1) return 'Semi-Finals'
  if (round === total - 2) return 'Quarter-Finals'
  return `Round ${round}`
}

function roundGap(round: number): number {
  return 24 + (round - 1) * 96
}
</script>
