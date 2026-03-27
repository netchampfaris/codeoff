import { useCall } from 'frappe-ui'

interface TournamentBracket {
  tournament_name: string
  tournament_id: string
  status: string
  current_round: number | null
  total_rounds: number
  is_organizer?: boolean
  enable_dev_login?: boolean
  rounds: Record<string, any[]>
}

interface Player {
  name: string
  user: string
  player_name?: string
}

// Module-level singletons — shared across all components, fetched once
const bracket = useCall<TournamentBracket>({
  url: '/api/v2/method/codeoff.api.contest.get_tournament_bracket',
  immediate: true,
})

const players = useCall<Player[]>({
  url: '/api/v2/method/codeoff.api.contest.get_all_players',
  immediate: true,
})

export function useTournament() {
  return { bracket, players }
}
