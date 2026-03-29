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
        class="mb-8 flex w-full flex-col items-center justify-center"
        :class="large ? 'gap-5 sm:flex-row sm:items-stretch sm:gap-10' : 'gap-4 sm:flex-row sm:items-stretch sm:gap-8'"
      >
        <LobbyPlayerCard
          :player="player1"
          :large="large"
          :votes="votes1"
          :has-voted="hasVoted"
          default-name="player_1"
          @vote="vote"
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
          :has-voted="hasVoted"
          default-name="player_2"
          @vote="vote"
        />
      </div>
      <div class="mx-auto mt-4 max-w-md text-sm uppercase tracking-widest sm:mt-6">
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
import { ref, computed } from 'vue'
import AppButton from '@/components/AppButton.vue'
import LobbyPlayerCard from '@/components/LobbyPlayerCard.vue'

const props = defineProps<{
  title: string
  player1: { id?: string; name: string; joined: boolean } | null
  player2: { id?: string; name: string; joined: boolean } | null
  large?: boolean
  matchId?: string
  votes1?: number
  votes2?: number
  isOrganizer?: boolean
}>()

const emit = defineEmits<{ vote: [playerId: string]; start: [] }>()

const bothJoined = computed(
  () => !!props.player1?.joined && !!props.player2?.joined,
)

const hasVoted = ref(
  !!props.matchId && !!localStorage.getItem(`codeoff_voted_${props.matchId}`),
)

function vote(playerId: string) {
  if (hasVoted.value || !props.matchId || !playerId) return
  hasVoted.value = true
  localStorage.setItem(`codeoff_voted_${props.matchId}`, playerId)
  emit('vote', playerId)
}
</script>
