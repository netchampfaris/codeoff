import { reactive, ref, onMounted, onUnmounted, computed } from 'vue'
import { useCall } from 'frappe-ui'
import { getSocket } from './socket'

interface Player {
  id: string
  name: string
  user: string
  joined: boolean
}

interface Draft {
  source_code: string
  cursor_line: number
  cursor_column: number
  updated_at: string
}

interface MatchState {
  match_id: string
  status: string
  start_time: string | null
  deadline: string | null
  player_1: Player
  player_2: Player
  winner: string | null
  winning_reason: string | null
  drafts: Record<string, Draft>
  problem: {
    name: string
    title: string
    statement: string
    constraints_text: string
    function_name: string
    function_signature: string
    starter_code: string
    sample_test_cases: Array<{ input: string; expected_output: string }>
  } | null
  submissions: Array<{
    name: string
    player: string
    status: string
    verdict: string | null
    passed_tests: number
    total_tests: number
    score: number
    submitted_at: string
  }>
}

export function useMatchState(matchId: string) {
  const state = ref<MatchState | null>(null)
  const loading = ref(true)
  const error = ref<string | null>(null)

  const fetchState = useCall({
    url: '/api/v2/method/codeoff.api.contest.get_match_state',
    immediate: false,
    onSuccess(data: MatchState) {
      state.value = data
      loading.value = false
    },
    onError(err: any) {
      error.value = err?.message || 'Failed to load match'
      loading.value = false
    },
  })

  function load() {
    loading.value = true
    fetchState.submit({ match_id: matchId })
  }

  function reload() {
    fetchState.submit({ match_id: matchId })
  }

  function handleEvent(data: any) {
    if (!state.value) return

    switch (data.event_type) {
      case 'match_started':
        state.value.status = data.status
        state.value.start_time = data.start_time
        state.value.deadline = data.deadline
        break

      case 'player_joined':
        if (data.slot === 'player_1') state.value.player_1.joined = true
        if (data.slot === 'player_2') state.value.player_2.joined = true
        break

      case 'draft_updated':
        state.value.drafts[data.player_id] = {
          source_code: data.source_code,
          cursor_line: data.cursor_line,
          cursor_column: data.cursor_column,
          updated_at: data.updated_at,
        }
        break

      case 'submission_received':
        state.value.submissions.push({
          name: data.submission_id,
          player: data.player_id,
          status: data.status,
          verdict: null,
          passed_tests: 0,
          total_tests: 0,
          score: 0,
          submitted_at: data.submitted_at,
        })
        break

      case 'verdict_updated':
        const sub = state.value.submissions.find(
          (s) => s.name === data.submission_id,
        )
        if (sub) {
          sub.status = 'Completed'
          sub.verdict = data.verdict
          sub.passed_tests = data.passed_tests
          sub.total_tests = data.total_tests
          sub.score = data.score
        }
        break

      case 'match_finished':
        state.value.status = data.status
        state.value.winner = data.winner_id
        state.value.winning_reason = data.winning_reason
        break

      case 'match_review_required':
        state.value.status = data.status
        break
    }
  }

  onMounted(() => {
    load()
    getSocket().on(`codeoff_match_${matchId}`, handleEvent)
  })

  onUnmounted(() => {
    getSocket().off(`codeoff_match_${matchId}`, handleEvent)
  })

  return { state, loading, error, reload }
}

export function useMyMatch() {
  const match = ref<{
    match_id: string | null
    status: string
    tournament?: string
  } | null>(null)
  const loading = ref(true)

  const fetch = useCall({
    url: '/api/v2/method/codeoff.api.contest.get_my_match',
    immediate: false,
    onSuccess(data: any) {
      match.value = data
      loading.value = false
    },
    onError() {
      loading.value = false
    },
  })

  onMounted(() => {
    fetch.submit({})
  })

  return { match, loading, reload: () => fetch.submit({}) }
}

export function useMatchTimer(
  state: ReturnType<typeof useMatchState>['state'],
) {
  const remaining = ref(0)
  let timer: ReturnType<typeof setInterval> | null = null

  function update() {
    if (!state.value?.deadline) {
      remaining.value = 0
      return
    }
    const deadlineMs = new Date(state.value.deadline).getTime()
    const now = Date.now()
    remaining.value = Math.max(0, Math.floor((deadlineMs - now) / 1000))
  }

  onMounted(() => {
    update()
    timer = setInterval(update, 1000)
  })

  onUnmounted(() => {
    if (timer) clearInterval(timer)
  })

  const formatted = computed(() => {
    const mins = Math.floor(remaining.value / 60)
    const secs = remaining.value % 60
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  })

  return { remaining, formatted }
}
