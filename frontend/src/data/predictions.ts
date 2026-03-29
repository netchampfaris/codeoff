const PREDICTION_KEY_PREFIX = 'codeoff_prediction_'
const LEGACY_VOTE_KEY_PREFIX = 'codeoff_voted_'

export function getStoredPrediction(matchId: string | null | undefined) {
  if (!matchId) return null
  return (
    localStorage.getItem(`${PREDICTION_KEY_PREFIX}${matchId}`) ||
    localStorage.getItem(`${LEGACY_VOTE_KEY_PREFIX}${matchId}`)
  )
}

export function setStoredPrediction(matchId: string, playerId: string) {
  localStorage.setItem(`${PREDICTION_KEY_PREFIX}${matchId}`, playerId)
  localStorage.removeItem(`${LEGACY_VOTE_KEY_PREFIX}${matchId}`)
}

export function getPredictionStats(
  votes1?: number | null,
  votes2?: number | null,
) {
  const left = votes1 || 0
  const right = votes2 || 0
  const total = left + right

  if (!total) {
    return {
      total: 0,
      percent1: 0,
      percent2: 0,
    }
  }

  const percent1 = Math.round((left / total) * 100)

  return {
    total,
    percent1,
    percent2: 100 - percent1,
  }
}
