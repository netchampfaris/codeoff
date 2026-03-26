<template>
  <div class="flex flex-1 flex-col overflow-hidden font-mono">
    <!-- Header -->
    <div
      class="flex items-center justify-between border-b border-term-border bg-term-surface px-8 py-5"
    >
      <div class="flex-1 text-center">
        <div class="mb-0.5 text-base uppercase tracking-widest text-green-700">
          // tournament
        </div>
        <h1 class="text-[2rem] font-bold tracking-tight text-green-300">
          {{ data.tournament_name }}
        </h1>
        <div class="mt-1 text-base text-green-700">
          round
          <span class="text-term-green">{{ data.current_round || 1 }}</span>
          <span class="text-green-800"> / </span>
          {{ data.total_rounds }}
        </div>
      </div>
    </div>

    <!-- Bracket visualization -->
    <div
      ref="bracketContainer"
      class="flex flex-1 items-center justify-center overflow-x-auto px-8 py-10"
    >
      <div class="relative flex items-center gap-16">
        <!-- Connector lines -->
        <svg
          v-if="connectors.length"
          class="pointer-events-none absolute inset-0"
          :style="{ width: svgWidth + 'px', height: svgHeight + 'px' }"
        >
          <path
            v-for="(c, i) in connectors"
            :key="i"
            :d="c"
            fill="none"
            stroke="rgb(22 101 52)"
            stroke-width="1.5"
          />
        </svg>
        <div
          v-for="round in sortedRounds"
          :key="round.number"
          class="flex flex-col items-center gap-4"
        >
          <div
            class="mb-3 text-base font-bold uppercase tracking-[0.2em] text-green-600"
          >
            [ {{ getRoundLabel(round.number) }} ]
          </div>
          <div
            class="flex flex-col justify-around"
            :style="{ gap: `${roundGap(round.number)}px` }"
          >
            <div
              v-for="m in round.matches"
              :key="m.name"
              :ref="(el: any) => setMatchRef(m.name, el)"
            >
              <BracketMatchCard
                :match="m"
                @spectate="$emit('spectate', $event)"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import BracketMatchCard from './BracketMatchCard.vue'
import { useBracketRounds } from '@/data/useBracketRounds'
import { useBracketConnectors } from '@/data/useBracketConnectors'

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

const bracketContainer = ref<HTMLElement>()

const { sortedRounds, getRoundLabel, roundGap } = useBracketRounds(
  () => props.data.rounds,
  () => props.data.total_rounds,
)

const { connectors, svgWidth, svgHeight, setMatchRef } = useBracketConnectors(
  bracketContainer,
  sortedRounds,
)
</script>
