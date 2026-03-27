<template>
  <div
    class="flex h-10 shrink-0 items-center justify-between border-b border-zinc-800 bg-zinc-900 px-4"
  >
    <!-- Left: brand + page title -->
    <div class="flex items-center gap-2">
      <router-link
        to="/"
        class="flex items-center gap-2 transition-opacity hover:opacity-70"
      >
        <span class="font-bold text-green-400">&gt;_</span>
        <span class="text-xs font-semibold uppercase tracking-widest text-green-500"
          >codeoff</span
        >
      </router-link>
      <span v-if="title" class="text-xs text-green-800">/ {{ title }}</span>
    </div>

    <!-- Right: optional extra actions + user identity -->
    <div class="flex items-center gap-3">
      <slot name="actions" />
      <span class="text-xs text-green-700">$ {{ sessionUser || 'guest' }}</span>
      <button
        v-if="sessionUser"
        class="text-xs font-bold uppercase tracking-widest text-green-800 transition-colors hover:text-green-600"
        @click="session.logout.submit()"
      >
        [logout]
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { session, sessionUser } from '@/data/session'

defineProps<{
  title?: string
}>()
</script>
