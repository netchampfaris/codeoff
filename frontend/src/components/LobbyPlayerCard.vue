<template>
  <div
    class="border-zinc-900 bg-zinc-950/50 w-full max-w-sm border px-5 py-5 text-center sm:px-6 sm:py-6"
  >
    <div
      class="font-mono uppercase tracking-wide text-green-200"
      :class="large ? 'text-2xl sm:text-3xl' : 'text-lg sm:text-xl'"
    >
      {{ player?.name || defaultName }}
    </div>
    <div
      class="mt-2"
      :class="[
        large ? 'text-sm' : 'text-xs',
        player?.joined ? 'text-green-500' : 'text-green-700',
      ]"
    >
      {{ player?.joined ? 'connected' : 'waiting...' }}
    </div>
    <div
      v-if="votes !== undefined"
      class="mt-5 border-t border-green-950 pt-4 text-left"
    >
      <div class="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <div class="text-[10px] uppercase tracking-[0.3em] text-green-800">
            votes
          </div>
          <div class="mt-1 font-mono text-2xl font-bold text-green-300">
            {{ votes }}
          </div>
        </div>
        <AppButton
          variant="ghost"
          class="w-full justify-center sm:w-auto sm:min-w-28"
          :disabled="hasVoted"
          @click="emit('vote', player?.id || '')"
        >
          {{ hasVoted ? '[voted]' : '[vote]' }}
        </AppButton>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import AppButton from '@/components/AppButton.vue'

defineProps<{
  player: { id?: string; name: string; joined: boolean } | null
  large?: boolean
  votes?: number
  hasVoted: boolean
  defaultName?: string
}>()

const emit = defineEmits<{ vote: [playerId: string] }>()
</script>
