<template>
  <nav
    class="flex h-full w-52 flex-shrink-0 flex-col border-r border-zinc-800 bg-zinc-900 font-mono"
  >
    <div class="flex items-center gap-2 border-b border-zinc-800 px-4 py-3">
      <span class="text-xl font-bold tracking-tight text-green-400">&gt;_</span>
      <h1
        class="text-base font-semibold uppercase tracking-widest text-green-300"
      >
        codeoff
      </h1>
    </div>
    <div class="flex-1 space-y-px px-2 py-2">
      <router-link
        v-for="link in navigation"
        :key="link.name"
        :to="link.route"
        class="flex items-center gap-2 px-2 py-2 text-sm uppercase tracking-wider transition-colors"
        :class="[
          isActive(link.activeRegex)
            ? 'border-l-2 border-green-400 bg-zinc-900 pl-[6px] text-green-400'
            : 'border-l-2 border-transparent text-green-700 hover:bg-zinc-900 hover:text-green-400',
        ]"
      >
        <span v-if="isActive(link.activeRegex)" class="text-green-400">›</span>
        <span v-else class="text-green-800">›</span>
        {{ link.name }}
      </router-link>
    </div>
    <div class="border-t border-zinc-800 px-3 py-3">
      <div class="flex items-center justify-between">
        <span class="truncate text-sm text-green-700">
          <span class="text-green-600">$</span> {{ session.user }}
        </span>
        <Button
          variant="ghost"
          size="sm"
          class="rounded-none"
          @click="session.logout.submit()"
        >
          <LucideLogOut class="h-4 w-4 text-green-700" />
        </Button>
      </div>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { useRoute } from 'vue-router'
import { session } from '@/data/session'

const route = useRoute()

const navigation = [
  {
    name: 'Home',
    route: { name: 'Home' },
    icon: 'LucideHome',
    activeRegex: /Home/,
  },
]

function isActive(regex: RegExp) {
  return route.name ? regex.test(route.name.toString()) : false
}
</script>
