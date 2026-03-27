<template>
  <div
    class="flex h-full flex-col items-center justify-center font-mono"
    style="background: #080808"
  >
    <div class="text-center">
      <div class="mb-1 text-sm uppercase tracking-widest text-green-700">
        // lobby
      </div>
      <h2
        class="mb-8 font-bold tracking-tight text-green-300"
        :class="large ? 'text-4xl' : 'text-2xl'"
      >
        {{ title }}
      </h2>
      <div
        class="mb-10 flex items-center justify-center"
        :class="large ? 'gap-16' : 'gap-10'"
      >
        <div class="text-center">
          <div
            class="mx-auto mb-3 flex items-center justify-center border text-sm font-bold uppercase"
            :class="[
              large ? 'mb-4 h-16 w-32' : 'mb-3 h-12 w-24',
              player1?.joined
                ? 'bg-green-950/20 border-green-400 text-green-400'
                : 'bg-zinc-900 border-green-900 text-green-800',
            ]"
          >
            {{ player1?.joined ? '[ready]' : '[wait]' }}
          </div>
          <div
            class="font-mono uppercase tracking-wider text-green-300"
            :class="large ? 'text-lg' : 'text-sm'"
          >
            {{ player1?.name || 'player_1' }}
          </div>
          <div
            class="mt-1"
            :class="[
              large ? 'text-sm' : 'text-xs',
              player1?.joined ? 'text-green-400' : 'text-green-800',
            ]"
          >
            {{ player1?.joined ? 'connected' : 'waiting...' }}
          </div>
          <div v-if="votes1 !== undefined" class="mt-3">
            <AppButton
              variant="ghost"
              :disabled="hasVoted"
              @click="vote(player1?.id || '')"
            >
              [vote] {{ votes1 }}
            </AppButton>
          </div>
        </div>
        <div
          class="font-bold tracking-widest text-green-800"
          :class="large ? 'text-4xl' : 'text-2xl'"
        >
          vs
        </div>
        <div class="text-center">
          <div
            class="mx-auto mb-3 flex items-center justify-center border text-sm font-bold uppercase"
            :class="[
              large ? 'mb-4 h-16 w-32' : 'mb-3 h-12 w-24',
              player2?.joined
                ? 'bg-green-950/20 border-green-400 text-green-400'
                : 'bg-zinc-900 border-green-900 text-green-800',
            ]"
          >
            {{ player2?.joined ? '[ready]' : '[wait]' }}
          </div>
          <div
            class="font-mono uppercase tracking-wider text-green-300"
            :class="large ? 'text-lg' : 'text-sm'"
          >
            {{ player2?.name || 'player_2' }}
          </div>
          <div
            class="mt-1"
            :class="[
              large ? 'text-sm' : 'text-xs',
              player2?.joined ? 'text-green-400' : 'text-green-800',
            ]"
          >
            {{ player2?.joined ? 'connected' : 'waiting...' }}
          </div>
          <div v-if="votes2 !== undefined" class="mt-3">
            <AppButton
              variant="ghost"
              :disabled="hasVoted"
              @click="vote(player2?.id || '')"
            >
              [vote] {{ votes2 }}
            </AppButton>
          </div>
        </div>
      </div>
      <div class="mt-6 text-sm uppercase tracking-widest">
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
      <div v-if="isOrganizer" class="mt-6">
        <AppButton
          variant="primary"
          size="md"
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
