import { computed } from 'vue'

export function useBracketRounds(
  rounds: () => Record<string, any[]>,
  totalRounds: () => number,
) {
  const sortedRounds = computed(() => {
    return Object.keys(rounds())
      .map(Number)
      .sort((a, b) => a - b)
      .map((n) => ({ number: n, matches: rounds()[n] }))
  })

  function getRoundLabel(round: number): string {
    const total = totalRounds()
    if (round === total) return 'Final'
    if (round === total - 1) return 'Semi-Finals'
    if (round === total - 2) return 'Quarter-Finals'
    return `Round ${round}`
  }

  function roundGap(round: number): number {
    return 24 + (round - 1) * 96
  }

  return { sortedRounds, getRoundLabel, roundGap }
}
