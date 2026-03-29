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
        <span
          class="text-xs font-semibold uppercase tracking-widest text-green-500"
          >codeoff</span
        >
      </router-link>
      <span v-if="title" class="text-xs text-green-800">/ {{ title }}</span>
    </div>

    <!-- Right: optional extra actions + user identity -->
    <div class="flex items-center gap-3">
      <span
        v-if="showAudienceCount"
        class="border border-zinc-800 bg-zinc-950 px-2 py-1 text-[10px] font-semibold uppercase tracking-widest"
        :class="audienceAvailable ? 'text-green-500' : 'text-green-800'"
      >
        live audience {{ audienceLabel }}
      </span>
      <slot name="actions" />
      <span class="text-xs text-green-700">$ {{ sessionUser || 'guest' }}</span>
      <AppButton
        v-if="sessionUser"
        variant="inline"
        class="text-green-800 hover:text-green-600"
        @click="session.logout.submit()"
      >
        [logout]
      </AppButton>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { session, sessionUser } from '@/data/session'
import { useAudienceCount } from '@/data/audience'
import AppButton from '@/components/AppButton.vue'

const props = withDefaults(
  defineProps<{
    title?: string
    showAudienceCount?: boolean
  }>(),
  {
    showAudienceCount: true,
  },
)

const { audienceTotal, audienceAvailable } = useAudienceCount()

const audienceLabel = computed(() => {
  if (audienceTotal.value == null) return '--'
  return String(audienceTotal.value)
})
</script>
