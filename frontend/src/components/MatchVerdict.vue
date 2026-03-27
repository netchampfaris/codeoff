<template>
  <span
    v-if="status === 'Finished' && winner === playerId"
    class="font-black uppercase tracking-widest text-green-400"
    :class="
      large
        ? 'border-4 border-green-400 px-4 py-1 text-2xl'
        : 'border border-green-400 px-1.5 text-xs'
    "
    >winner</span
  >
  <span
    v-else-if="status === 'Finished' && !winner"
    class="font-black uppercase tracking-widest text-yellow-500"
    :class="
      large
        ? 'border-4 border-yellow-600 px-4 py-1 text-2xl'
        : 'border border-yellow-600 px-1.5 text-xs'
    "
    >draw</span
  >
</template>

<script setup lang="ts">
defineProps<{
  status: string
  winner: string | null | undefined
  playerId: string | null | undefined
  large?: boolean
}>()
</script>
