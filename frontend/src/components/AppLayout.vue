<template>
  <div class="flex h-full bg-zinc-950 font-mono">
    <AppSidebar />
    <main class="flex-1 overflow-auto bg-zinc-950">
      <slot />
    </main>
  </div>
</template>

<script setup lang="ts">
import AppSidebar from './AppSidebar.vue'
</script>
