import { computed } from 'vue'
import type { Ref } from 'vue'
import type { MatchState } from './match'

type Submission = MatchState['submissions'][number]

/**
 * Derived player data: winner name, per-player submissions and best scores.
 */
export function useMatchPlayers(state: Ref<MatchState | null>) {
  const winnerName = computed(() => {
    if (!state.value?.winner) return ''
    if (state.value.player_1?.id === state.value.winner)
      return state.value.player_1.name
    if (state.value.player_2?.id === state.value.winner)
      return state.value.player_2.name
    return state.value.winner
  })

  const player1Submissions = computed<Submission[]>(() => {
    if (!state.value) return []
    return (state.value.submissions || []).filter(
      (s) => s.player === state.value!.player_1?.id,
    )
  })

  const player2Submissions = computed<Submission[]>(() => {
    if (!state.value) return []
    return (state.value.submissions || []).filter(
      (s) => s.player === state.value!.player_2?.id,
    )
  })

  function bestScore(submissions: Submission[]) {
    const judged = submissions.filter((s) => s.total_tests > 0)
    if (!judged.length) return null
    return judged.reduce(
      (best, s) => (s.passed_tests > best.passed_tests ? s : best),
      judged[0],
    )
  }

  const bestScore1 = computed(() => bestScore(player1Submissions.value))
  const bestScore2 = computed(() => bestScore(player2Submissions.value))

  return {
    winnerName,
    player1Submissions,
    player2Submissions,
    bestScore1,
    bestScore2,
  }
}
