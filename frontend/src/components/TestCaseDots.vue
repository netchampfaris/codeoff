<template>
  <div :class="large ? 'flex gap-1' : 'flex gap-0.5'">
    <div
      v-for="i in total"
      :key="i"
      class="transition-colors duration-300"
      :class="[
        large ? 'h-6 w-6 border-2' : 'h-3 w-3 border',
        i <= passed
          ? 'border-green-400 bg-green-400'
          : 'border-green-900 bg-transparent',
      ]"
    />
  </div>
</template>

<script setup lang="ts">
defineProps<{ total: number; passed: number; large?: boolean }>()
</script>
