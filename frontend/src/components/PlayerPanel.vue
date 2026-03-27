<template>
  <div class="flex flex-1 flex-col font-mono" :class="borderClass">
    <div class="flex-1 overflow-hidden">
      <CodeEditor
        :model-value="code"
        readonly
        fontSize="18px"
        placeholder="# waiting for player to start coding..."
      />
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
  return props.side === 'left' ? 'border-r border-zinc-800' : ''
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
