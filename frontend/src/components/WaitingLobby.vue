<template>
  <div
    class="bg-gray-950 flex h-full flex-col items-center justify-center text-gray-200"
  >
    <div class="text-center">
      <h2
        class="mb-6 text-2xl font-semibold text-white"
        :class="large && 'text-3xl'"
      >
        {{ title }}
      </h2>
      <div
        class="mb-8 flex items-center justify-center"
        :class="large ? 'gap-12' : 'gap-8'"
      >
        <div class="text-center">
          <div
            class="mx-auto mb-2 flex items-center justify-center rounded-full"
            :class="[
              large ? 'mb-3 h-20 w-20 text-3xl' : 'mb-2 h-16 w-16 text-2xl',
              player1?.joined
                ? 'bg-green-900 text-green-400'
                : 'bg-gray-800 text-gray-500',
            ]"
          >
            {{ player1?.joined ? '✓' : '?' }}
          </div>
          <div
            class="font-medium text-white"
            :class="large ? 'text-lg font-semibold' : 'text-sm'"
          >
            {{ player1?.name || 'Player 1' }}
          </div>
          <div
            class="mt-1"
            :class="[
              large ? 'text-sm' : 'text-xs',
              player1?.joined ? 'text-green-400' : 'text-gray-500',
            ]"
          >
            {{ player1?.joined ? 'Ready' : 'Waiting...' }}
          </div>
        </div>
        <div
          class="font-bold text-gray-600"
          :class="large ? 'text-4xl' : 'text-2xl'"
        >
          vs
        </div>
        <div class="text-center">
          <div
            class="mx-auto mb-2 flex items-center justify-center rounded-full"
            :class="[
              large ? 'mb-3 h-20 w-20 text-3xl' : 'mb-2 h-16 w-16 text-2xl',
              player2?.joined
                ? 'bg-green-900 text-green-400'
                : 'bg-gray-800 text-gray-500',
            ]"
          >
            {{ player2?.joined ? '✓' : '?' }}
          </div>
          <div
            class="font-medium text-white"
            :class="large ? 'text-lg font-semibold' : 'text-sm'"
          >
            {{ player2?.name || 'Player 2' }}
          </div>
          <div
            class="mt-1"
            :class="[
              large ? 'text-sm' : 'text-xs',
              player2?.joined ? 'text-green-400' : 'text-gray-500',
            ]"
          >
            {{ player2?.joined ? 'Ready' : 'Waiting...' }}
          </div>
        </div>
      </div>
      <div class="text-sm text-gray-500">
        Match will start when both players join
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  title: string
  player1: { name: string; joined: boolean } | null
  player2: { name: string; joined: boolean } | null
  large?: boolean
}>()
</script>
