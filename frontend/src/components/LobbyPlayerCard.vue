<template>
  <div
    class="w-full max-w-sm border px-5 py-5 text-center sm:px-6 sm:py-6"
    :class="[
      player?.joined ? 'border-green-500' : 'border-zinc-900',
      isPicked ? 'bg-green-950/20' : 'bg-zinc-950/50',
    ]"
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
    <div v-if="predictionPercent" class="mt-5 border-t border-green-950 pt-4">
      <div class="text-[10px] uppercase tracking-[0.3em] text-green-700">
        crowd split
      </div>
      <div class="mt-2 font-mono text-3xl font-bold text-green-300 sm:text-4xl">
        {{ predictionPercent }}
      </div>
    </div>
    <div v-if="votes !== undefined" class="mt-5 text-left">
      <div>
        <AppButton
          variant="ghost"
          class="w-full justify-center"
          :disabled="locked"
          @click="emit('vote', player?.id || '')"
        >
          {{ buttonLabel }}
        </AppButton>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import AppButton from '@/components/AppButton.vue'

const props = withDefaults(
  defineProps<{
    player: { id?: string; name: string; joined: boolean } | null
    large?: boolean
    votes?: number
    locked?: boolean
    isPicked?: boolean
    viewOnly?: boolean
    predictionPercent?: string
    defaultName?: string
  }>(),
  {
    locked: false,
    isPicked: false,
    viewOnly: false,
    predictionPercent: '',
  },
)

const buttonLabel = computed(() => {
  if (props.viewOnly) return '[view only]'
  if (props.isPicked) return '[picked]'
  if (props.locked) return '[locked]'
  return '[pick]'
})

const emit = defineEmits<{ vote: [playerId: string] }>()
</script>
