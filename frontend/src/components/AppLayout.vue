<template>
  <div class="flex h-full bg-term-bg font-mono">
    <AppSidebar />
    <main class="flex-1 overflow-auto bg-term-bg">
      <slot />
    </main>
  </div>
</template>

<script setup lang="ts">
import AppSidebar from './AppSidebar.vue'
</script>
