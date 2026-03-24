<template>
  <div class="flex h-full flex-col">
    <!-- Scrollable problem statement -->
    <div class="flex-1 overflow-auto p-4">
      <h2 class="mb-3 text-lg font-semibold text-white">{{ problem.title }}</h2>
      <div
        class="prose prose-sm prose-invert max-w-none text-gray-300"
        v-html="statementHtml"
      />

      <div v-if="problem.constraints_text" class="mt-4">
        <h3 class="mb-1 text-sm font-semibold text-gray-300">Constraints</h3>
        <div class="whitespace-pre-wrap text-sm text-gray-400">
          {{ problem.constraints_text }}
        </div>
      </div>

      <div v-if="problem.sample_test_cases?.length" class="mt-4">
        <h3 class="mb-2 text-sm font-semibold text-gray-300">
          Sample Test Cases
        </h3>
        <div
          v-for="(tc, i) in problem.sample_test_cases"
          :key="i"
          class="mb-3 rounded border border-gray-700 bg-gray-900 p-3 text-sm"
        >
          <div>
            <span class="font-medium text-gray-400">Input:</span>
            <code class="ml-1 text-gray-200">{{ tc.input }}</code>
          </div>
          <div class="mt-1">
            <span class="font-medium text-gray-400">Expected:</span>
            <code class="ml-1 text-gray-200">{{ tc.expected_output }}</code>
          </div>
        </div>
      </div>

      <!-- Submission history -->
      <div v-if="submissions.length" class="mt-4">
        <h3 class="mb-2 text-sm font-semibold text-gray-300">Submissions</h3>
        <div
          v-for="sub in submissions"
          :key="sub.name"
          class="mb-2 flex items-center justify-between rounded border border-gray-700 bg-gray-900 p-2 text-sm"
        >
          <div class="flex items-center gap-2">
            <Badge
              :theme="
                sub.verdict === 'Accepted'
                  ? 'green'
                  : !sub.verdict
                    ? 'blue'
                    : 'red'
              "
              variant="subtle"
              size="sm"
            >
              {{ sub.verdict || sub.status }}
            </Badge>
            <span v-if="sub.total_tests" class="text-gray-400">
              {{ sub.passed_tests }}/{{ sub.total_tests }}
            </span>
          </div>
          <span class="text-xs text-gray-500">{{
            formatTime(sub.submitted_at)
          }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { marked } from 'marked'

const props = defineProps<{
  problem: {
    title: string
    statement: string
    constraints_text?: string
    sample_test_cases?: Array<{ input: string; expected_output: string }>
  }
  submissions: Array<{
    name: string
    verdict: string | null
    status: string
    passed_tests: number
    total_tests: number
    submitted_at: string
  }>
}>()

const statementHtml = computed(() => {
  return marked.parse(props.problem.statement || '', { async: false }) as string
})

function formatTime(dt: string) {
  if (!dt) return ''
  return new Date(dt).toLocaleTimeString()
}
</script>
