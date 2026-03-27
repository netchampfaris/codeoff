<template>
  <div class="text-center">
    <div
      class="mx-auto mb-3 flex items-center justify-center border text-sm font-bold uppercase"
      :class="[
        large ? 'mb-4 h-16 w-32' : 'mb-3 h-12 w-24',
        player?.joined
          ? 'bg-green-950/20 border-green-400 text-green-400'
          : 'bg-zinc-900 border-green-900 text-green-800',
      ]"
    >
      {{ player?.joined ? '[ready]' : '[wait]' }}
    </div>
    <div
      class="font-mono uppercase tracking-wider text-green-300"
      :class="large ? 'text-lg' : 'text-sm'"
    >
      {{ player?.name || defaultName }}
    </div>
    <div
      class="mt-1"
      :class="[
        large ? 'text-sm' : 'text-xs',
        player?.joined ? 'text-green-400' : 'text-green-800',
      ]"
    >
      {{ player?.joined ? 'connected' : 'waiting...' }}
    </div>
    <div v-if="votes !== undefined" class="mt-3">
      <AppButton
        variant="ghost"
        :disabled="hasVoted"
        @click="emit('vote', player?.id || '')"
      >
        [vote] {{ votes }}
      </AppButton>
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
