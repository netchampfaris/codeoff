<template>
  <div v-if="testResults" class="overflow-auto border-t border-gray-800 p-3">
    <h3 class="mb-2 text-sm font-semibold text-gray-300">
      Test Results
      <span class="ml-1 font-normal text-gray-500">
        ({{ testResults.passed_tests }}/{{ testResults.total_tests }})
      </span>
    </h3>
    <div class="flex flex-wrap gap-2">
      <div
        v-for="(result, i) in testResults.details"
        :key="i"
        class="rounded border px-2.5 py-1.5 text-sm"
        :class="
          result.passed
            ? 'bg-green-950 border-green-800'
            : 'bg-red-950 border-red-800'
        "
      >
        <div class="flex items-center gap-1.5">
          <LucideCheck
            v-if="result.passed"
            class="h-3.5 w-3.5 text-green-400"
          />
          <LucideX v-else class="h-3.5 w-3.5 text-red-400" />
          <span>Test {{ i + 1 }}</span>
        </div>
        <div
          v-if="!result.passed && result.actual !== undefined"
          class="mt-1 text-xs"
        >
          <div>
            Expected: <code>{{ result.expected }}</code>
          </div>
          <div>
            Got: <code>{{ result.actual }}</code>
          </div>
        </div>
        <div v-if="result.error" class="mt-1 text-xs text-red-400">
          {{ result.error }}
        </div>
      </div>
    </div>
    <div
      v-if="testResults.error"
      class="bg-red-950 mt-2 rounded border border-red-800 p-2 text-sm text-red-400"
    >
      {{ testResults.error }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { LucideCheck, LucideX } from 'lucide-vue-next'

defineProps<{
  testResults: {
    passed_tests: number
    total_tests: number
    details: Array<{
      passed: boolean
      actual?: any
      expected?: any
      error?: string
    }>
    error?: string
  } | null
}>()
</script>
