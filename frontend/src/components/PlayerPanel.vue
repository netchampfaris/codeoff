<template>
  <div class="flex flex-1 flex-col" :class="borderClass">
    <div
      class="flex items-center justify-between border-b border-gray-800 px-4 py-2.5"
    >
      <span class="text-base font-semibold text-white">{{ playerName }}</span>
      <div class="flex items-center gap-3">
        <span
          v-if="bestScore"
          class="rounded bg-gray-800 px-2.5 py-1 font-mono text-sm"
          :class="
            bestScore.passed_tests === bestScore.total_tests
              ? 'text-green-400'
              : 'text-yellow-400'
          "
        >
          Best: {{ bestScore.passed_tests }}/{{ bestScore.total_tests }}
        </span>
      </div>
    </div>
    <div class="flex-1 overflow-hidden">
      <CodeEditor :model-value="code" readonly fontSize="18px" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import CodeEditor from './CodeEditor.vue'

const props = defineProps<{
  playerName: string
  code: string
  submissions: Array<{
    name: string
    verdict: string | null
    passed_tests: number
    total_tests: number
  }>
  side?: 'left' | 'right'
}>()

const borderClass = computed(() => {
  return props.side === 'left' ? 'border-r border-gray-800' : ''
})

const bestScore = computed(() => {
  const judged = props.submissions.filter((s) => s.total_tests > 0)
  if (!judged.length) return null
  return judged.reduce(
    (best, s) => (s.passed_tests > best.passed_tests ? s : best),
    judged[0],
  )
})
</script>
