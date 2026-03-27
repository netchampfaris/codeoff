<template>
  <div class="border-zinc-800 bg-zinc-900 flex flex-col border-t font-mono">
    <!-- Tab bar -->
    <div class="border-zinc-800 flex border-b">
      <AppButton
        variant="tab"
        :active="activeTab === 'tests'"
        @click="activeTab = 'tests'"
      >
        console
        <span v-if="testResults" class="ml-1 text-green-700">
          {{ testResults.passed_tests }}/{{ testResults.total_tests }}
        </span>
      </AppButton>
      <AppButton
        variant="tab"
        :active="activeTab === 'submissions'"
        @click="activeTab = 'submissions'"
      >
        submissions
        <span v-if="submissions.length" class="ml-1 text-green-700">{{
          submissions.length
        }}</span>
      </AppButton>
    </div>

    <!-- Test results tab -->
    <div v-if="activeTab === 'tests'" class="overflow-auto p-3">
      <div v-if="testResults">
        <div
          v-if="testResults.stdout"
          class="border-zinc-800 bg-zinc-950 mb-3 border p-2"
        >
          <div
            class="mb-1 text-xs font-bold uppercase tracking-wider text-green-700"
          >
            $ stdout
          </div>
          <pre class="whitespace-pre-wrap text-sm text-green-300">{{
            testResults.stdout
          }}</pre>
        </div>
        <div class="flex flex-col gap-1">
          <template v-for="(result, i) in testResults.details" :key="i">
            <div
              class="border-zinc-800 flex items-start gap-3 border-b py-1.5 text-sm last:border-0"
            >
              <span
                class="w-14 shrink-0 font-bold"
                :class="result.passed ? 'text-green-400' : 'text-red-400'"
                >{{ result.passed ? '[ok]' : '[fail]' }}</span
              >
              <span class="shrink-0 text-green-700">test {{ i + 1 }}</span>
              <span
                v-if="!result.passed && result.actual !== undefined"
                class="text-xs text-red-300"
              >
                exp:
                <code class="text-green-400">{{ result.expected }}</code>
                &nbsp;·&nbsp; got:
                <code class="text-red-300">{{ result.actual }}</code>
              </span>
              <span v-if="result.error" class="text-xs text-red-400">{{
                result.error
              }}</span>
            </div>
            <pre
              v-if="result.traceback && !result.passed"
              class="mb-1 ml-14 whitespace-pre-wrap text-xs text-red-300/80"
              >{{ result.traceback }}</pre
            >
          </template>
        </div>
        <pre
          v-if="testResults.error"
          class="bg-red-950/20 mt-2 whitespace-pre-wrap border border-red-900 p-2 text-sm text-red-400"
          >{{ testResults.error }}</pre
        >
      </div>
      <div v-else class="py-4 text-center text-xs text-green-800">
        run tests to see results
      </div>
    </div>

    <!-- Submissions tab -->
    <div v-if="activeTab === 'submissions'" class="overflow-auto p-3">
      <div v-if="submissions.length" class="flex flex-col gap-1.5">
        <div
          v-for="sub in submissions"
          :key="sub.name"
          class="border-zinc-800 bg-zinc-900 flex items-center justify-between border p-2 text-sm"
        >
          <div class="flex items-center gap-3">
            <span
              class="font-bold"
              :class="
                sub.verdict === 'Accepted'
                  ? 'text-green-400'
                  : !sub.verdict
                    ? 'text-green-600'
                    : 'text-red-400'
              "
            >
              [{{
                sub.verdict === 'Accepted'
                  ? 'AC'
                  : sub.verdict === 'Wrong Answer'
                    ? 'WA'
                    : sub.verdict
                      ? sub.verdict.substring(0, 3).toUpperCase()
                      : sub.status
              }}]
            </span>
            <span v-if="sub.total_tests" class="text-xs text-green-700">
              {{ sub.passed_tests }}/{{ sub.total_tests }} tests
            </span>
          </div>
          <span class="text-xs text-green-800">{{
            formatTime(sub.submitted_at)
          }}</span>
        </div>
      </div>
      <div v-else class="py-4 text-center text-xs text-green-800">
        no submissions yet
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import AppButton from '@/components/AppButton.vue'

const props = defineProps<{
  testResults: {
    passed_tests: number
    total_tests: number
    details: Array<{
      passed: boolean
      actual?: any
      expected?: any
      error?: string
      traceback?: string
    }>
    error?: string
    stdout?: string
  } | null
  submissions: Array<{
    name: string
    verdict: string | null
    status: string
    passed_tests: number
    total_tests: number
    submitted_at: string
  }>
}>()

const activeTab = ref<'tests' | 'submissions'>('tests')

// Switch to tests tab when new results arrive
watch(
  () => props.testResults,
  (v) => {
    if (v) activeTab.value = 'tests'
  },
)

// Switch to submissions tab when a new submission appears
let prevCount = 0
watch(
  () => props.submissions.length,
  (n) => {
    if (n > prevCount) {
      prevCount = n
      activeTab.value = 'submissions'
    }
  },
  { immediate: true },
)

function formatTime(dt: string) {
  if (!dt) return ''
  return new Date(dt).toLocaleTimeString()
}
</script>
