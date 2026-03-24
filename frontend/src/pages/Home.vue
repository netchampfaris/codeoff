<template>
  <div class="bg-gray-950 flex h-full flex-col text-gray-200">
    <div v-if="loading" class="flex flex-1 items-center justify-center">
      <div class="text-gray-500">Loading...</div>
    </div>

    <!-- Player view: show their match -->
    <div
      v-else-if="match?.match_id"
      class="flex flex-1 items-center justify-center"
    >
      <div class="text-center">
        <div class="mb-2 text-sm text-gray-400">Your match is</div>
        <div class="mb-4 text-lg font-semibold text-white">
          {{ match.status === 'Live' ? 'Live now!' : 'Coming up' }}
        </div>
        <div class="mb-6 text-sm text-gray-500">{{ match.match_id }}</div>
        <Button
          variant="solid"
          size="lg"
          @click="
            $router.push({
              name: 'MatchWorkspace',
              params: { matchId: match.match_id },
            })
          "
        >
          {{ match.status === 'Live' ? 'Go to Match' : 'Open Workspace' }}
        </Button>
      </div>
    </div>

    <!-- Organizer / non-player view: tournament bracket -->
    <div
      v-else-if="match?.status === 'not_a_player'"
      class="flex flex-1 flex-col overflow-hidden"
    >
      <div
        v-if="bracket.loading"
        class="flex flex-1 items-center justify-center"
      >
        <div class="text-sm text-gray-500">Loading bracket...</div>
      </div>
      <BracketView
        v-else-if="bracket.data"
        :data="bracket.data"
        @spectate="
          $router.push({ name: 'Spectate', params: { matchId: $event } })
        "
      />
      <div v-else class="flex flex-1 items-center justify-center">
        <div class="text-sm text-gray-500">No tournament found.</div>
      </div>
    </div>

    <!-- No match found for player -->
    <div v-else class="flex flex-1 items-center justify-center">
      <div class="text-center">
        <div class="mb-2 text-lg font-semibold text-white">No Active Match</div>
        <div class="text-sm text-gray-500">
          You don't have any upcoming matches right now. Check back later.
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useCall } from 'frappe-ui'
import { useMyMatch } from '@/data/match'
import BracketView from '@/components/BracketView.vue'

const { match, loading } = useMyMatch()

const bracket = useCall({
  url: '/api/v2/method/codeoff.api.contest.get_tournament_bracket',
  immediate: true,
})
</script>
