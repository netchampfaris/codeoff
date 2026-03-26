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
                ? 'bg-green-950/20 border-term-green text-term-green'
                : 'border-green-900 bg-term-surface text-green-800',
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
              player1?.joined ? 'text-term-green' : 'text-green-800',
            ]"
          >
            {{ player1?.joined ? 'connected' : 'waiting...' }}
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
                ? 'bg-green-950/20 border-term-green text-term-green'
                : 'border-green-900 bg-term-surface text-green-800',
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
              player2?.joined ? 'text-term-green' : 'text-green-800',
            ]"
          >
            {{ player2?.joined ? 'connected' : 'waiting...' }}
          </div>
        </div>
      </div>
      <div class="text-sm uppercase tracking-widest text-green-800">
        <span class="animate-pulse text-term-green">_</span>
        waiting for both players to connect
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
