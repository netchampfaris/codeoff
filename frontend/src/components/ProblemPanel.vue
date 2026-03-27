<template>
  <div class="flex h-full flex-col bg-zinc-950 font-mono">
    <!-- Scrollable problem statement -->
    <div class="flex-1 overflow-auto p-4">
      <div class="mb-1 text-xs uppercase tracking-widest text-green-700">
        // problem
      </div>
      <h2
        class="mb-4 text-base font-bold uppercase tracking-wider text-green-400"
      >
        {{ problem.title }}
      </h2>
      <div
        class="prose prose-sm prose-invert max-w-none text-sm leading-relaxed text-green-200 [&_code]:font-mono [&_code]:text-green-400 [&_h3]:uppercase [&_h3]:tracking-wider [&_h3]:text-green-400 [&_strong]:text-green-300"
        v-html="statementHtml"
      />

      <div v-if="problem.constraints_text" class="mt-5">
        <h3
          class="mb-2 text-xs font-bold uppercase tracking-widest text-green-600"
        >
          # constraints
        </h3>
        <div
          class="whitespace-pre-wrap border border-zinc-800 bg-zinc-900 p-3 text-sm text-green-300"
        >
          {{ problem.constraints_text }}
        </div>
      </div>

      <div v-if="problem.sample_test_cases?.length" class="mt-5">
        <h3
          class="mb-3 text-xs font-bold uppercase tracking-widest text-green-600"
        >
          # sample cases
        </h3>
        <div
          v-for="(tc, i) in problem.sample_test_cases"
          :key="i"
          class="mb-3 border border-zinc-800 bg-zinc-900 p-3 text-sm"
        >
          <div class="mb-1">
            <span class="text-green-700">$ input:</span>
            <code class="ml-2 text-green-400">{{ tc.input }}</code>
          </div>
          <div>
            <span class="text-green-700">$ expected:</span>
            <code class="ml-2 text-green-300">{{ tc.expected_output }}</code>
          </div>
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
}>()

const statementHtml = computed(() => {
  return marked.parse(props.problem.statement || '', { async: false }) as string
})
</script>
