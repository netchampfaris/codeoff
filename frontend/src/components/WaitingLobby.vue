<template>
  <div
    class="flex h-full flex-col items-center justify-center overflow-y-auto px-4 py-8 font-mono sm:px-6"
    style="background: #080808"
  >
    <div class="w-full max-w-5xl text-center">
      <div class="mb-1 text-sm uppercase tracking-widest text-green-700">
        // lobby
      </div>
      <h2
        class="mb-6 break-words font-bold tracking-tight text-green-300 sm:mb-8"
        :class="large ? 'text-2xl sm:text-4xl' : 'text-xl sm:text-2xl'"
      >
        {{ title }}
      </h2>
      <div
        v-if="predictionOpen"
        class="mx-auto mb-6 max-w-2xl border border-green-950 bg-zinc-950 px-4 py-4 sm:px-5"
      >
        <div
          class="text-lg font-bold uppercase tracking-wide text-green-200 sm:text-xl"
        >
          {{
            selectedPlayerName
              ? `you picked ${selectedPlayerName}`
              : isOrganizer
                ? 'crowd split'
                : 'pick a side'
          }}
        </div>
      </div>
      <div
        class="mb-8 flex w-full flex-col items-center justify-center"
        :class="
          large
            ? 'gap-5 sm:flex-row sm:items-stretch sm:gap-10'
            : 'gap-4 sm:flex-row sm:items-stretch sm:gap-8'
        "
      >
        <LobbyPlayerCard
          :player="player1"
          :large="large"
          :votes="votes1"
          :locked="predictionLocked"
          :is-picked="selectedPlayerId === player1?.id"
          :view-only="isOrganizer"
          :prediction-percent="showPredictionSplit ? leftSplit : ''"
          default-name="player_1"
          @vote="pick"
        />
        <div
          class="font-bold tracking-[0.3em] text-green-800"
          :class="large ? 'text-xl sm:text-4xl' : 'text-lg sm:text-2xl'"
        >
          vs
        </div>
        <LobbyPlayerCard
          :player="player2"
          :large="large"
          :votes="votes2"
          :locked="predictionLocked"
          :is-picked="selectedPlayerId === player2?.id"
          :view-only="isOrganizer"
          :prediction-percent="showPredictionSplit ? rightSplit : ''"
          default-name="player_2"
          @vote="pick"
        />
      </div>
      <div
        class="mx-auto mt-4 max-w-md text-sm uppercase tracking-widest sm:mt-6"
      >
        <template v-if="bothJoined">
          <span v-if="isOrganizer" class="text-green-400">
            <span class="animate-pulse">_</span> you can start the match now
          </span>
          <span v-else class="text-green-700">
            <span class="animate-pulse">_</span> waiting for organizer to start
          </span>
        </template>
        <span v-else class="text-green-800">
          <span class="animate-pulse text-green-400">_</span>
          waiting for both players to connect
        </span>
      </div>
      <!-- Organizer start button -->
      <div v-if="isOrganizer" class="mt-6 flex justify-center">
        <AppButton
          variant="primary"
          size="md"
          class="w-full max-w-xs justify-center"
          :disabled="!bothJoined"
          @click="emit('start')"
        >
          {{ bothJoined ? '[start match]' : '[waiting for players]' }}
        </AppButton>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import AppButton from '@/components/AppButton.vue'
import LobbyPlayerCard from '@/components/LobbyPlayerCard.vue'
import { getPredictionStats } from '@/data/predictions'

const props = defineProps<{
  title: string
  player1: { id?: string; name: string; joined: boolean } | null
  player2: { id?: string; name: string; joined: boolean } | null
  large?: boolean
  matchId?: string
  votes1?: number
  votes2?: number
  isOrganizer?: boolean
  selectedPlayerId?: string | null
  predictionPending?: boolean
}>()

const emit = defineEmits<{ pick: [playerId: string]; start: [] }>()

const bothJoined = computed(
  () => !!props.player1?.joined && !!props.player2?.joined,
)

const predictionOpen = computed(
  () =>
    !!props.matchId && props.votes1 !== undefined && props.votes2 !== undefined,
)

const predictionStats = computed(() =>
  getPredictionStats(props.votes1, props.votes2),
)

const selectedPlayerName = computed(() => {
  if (props.selectedPlayerId === props.player1?.id)
    return props.player1?.name || 'player_1'
  if (props.selectedPlayerId === props.player2?.id)
    return props.player2?.name || 'player_2'
  return ''
})

const leftSplit = computed(() =>
  predictionStats.value.total ? `${predictionStats.value.percent1}%` : '--',
)

const rightSplit = computed(() =>
  predictionStats.value.total ? `${predictionStats.value.percent2}%` : '--',
)

const predictionLocked = computed(
  () => !!props.selectedPlayerId || !!props.predictionPending || !!props.isOrganizer,
)

const showPredictionSplit = computed(() => !!props.selectedPlayerId || !!props.isOrganizer)

function pick(playerId: string) {
  if (predictionLocked.value || !props.matchId || !playerId) return
  emit('pick', playerId)
}
</script>
