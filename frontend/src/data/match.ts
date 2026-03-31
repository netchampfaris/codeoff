import { ref, onMounted, onUnmounted, computed, watch, type Ref } from 'vue'
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

export interface MatchState {
  match_id: string
  status: string
  is_organizer: boolean
  enable_dev_login: boolean
  round_number: number | null
  bracket_position: number | null
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
    total_test_cases: number
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
  votes_1: number
  votes_2: number
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

    if (data.event_type === 'draft_updated') {
      // Lightweight patch — these fire on every keystroke
      state.value.drafts[data.player_id] = {
        source_code: data.source_code,
        cursor_line: data.cursor_line,
        cursor_column: data.cursor_column,
        updated_at: data.updated_at,
      }
      return
    }

    if (data.event_type === 'vote_update') {
      state.value.votes_1 = data.votes_1
      state.value.votes_2 = data.votes_2
      return
    }

    // Full state replacement for all other events
    if (data.event_type === 'match_state') {
      // Preserve drafts from the current state since realtime state
      // may not have the latest keystrokes
      const currentDrafts = state.value.drafts
      state.value = { ...data, drafts: { ...data.drafts, ...currentDrafts } }
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

export function usePostDeadlineRefresh(
  state: ReturnType<typeof useMatchState>['state'],
  remaining: Ref<number>,
  reload: () => void,
) {
  let refreshTimer: ReturnType<typeof setInterval> | null = null

  function stopRefreshTimer() {
    if (refreshTimer) {
      clearInterval(refreshTimer)
      refreshTimer = null
    }
  }

  watch(
    () => [state.value?.status, remaining.value] as const,
    ([status, secondsLeft]) => {
      if (status !== 'Live' || secondsLeft > 0) {
        stopRefreshTimer()
        return
      }

      if (refreshTimer) return

      reload()
      refreshTimer = setInterval(() => {
        if (state.value?.status !== 'Live') {
          stopRefreshTimer()
          return
        }
        reload()
      }, 2000)
    },
    { immediate: true },
  )

  onUnmounted(stopRefreshTimer)
}
