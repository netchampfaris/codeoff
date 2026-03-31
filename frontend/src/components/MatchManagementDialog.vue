<template>
	<div
		v-if="modelValue && match"
		class="fixed inset-0 z-[70] flex items-center justify-center bg-black/70 px-4"
		@click.self="close"
	>
		<div
			class="w-full max-w-2xl border border-zinc-800 bg-zinc-950 font-mono text-green-200 shadow-2xl"
		>
			<div class="flex items-start justify-between gap-4 border-b border-zinc-800 px-5 py-4">
				<div>
					<div class="text-[11px] uppercase tracking-[0.3em] text-green-700">
						organizer controls
					</div>
					<div class="mt-1 text-lg font-bold text-green-300">
						{{ match.problem?.title || match.match_id }}
					</div>
					<div
						class="mt-2 flex flex-wrap gap-x-4 gap-y-1 text-xs uppercase tracking-widest text-green-700"
					>
						<span>status {{ match.status }}</span>
						<span v-if="match.deadline">deadline {{ deadlineLabel }}</span>
						<span v-if="match.winner">winner {{ winnerLabel }}</span>
					</div>
				</div>
				<AppButton
					variant="inline"
					class="text-green-700 hover:text-green-400"
					:disabled="busy"
					@click="close"
				>
					[close]
				</AppButton>
			</div>

			<div class="space-y-6 px-5 py-5">
				<div
					v-if="feedback"
					class="border px-3 py-2 text-xs uppercase tracking-wide"
					:class="
						feedbackTone === 'error'
							? 'border-red-900 bg-red-950/30 text-red-300'
							: 'border-green-900 bg-green-950/20 text-green-300'
					"
				>
					{{ feedback }}
				</div>

				<section v-if="match.status === 'Ready'" class="space-y-3">
					<div class="text-sm font-bold uppercase tracking-widest text-green-500">
						ready match
					</div>
					<div class="flex flex-wrap gap-3">
						<AppButton
							variant="primary"
							size="sm"
							:disabled="busy"
							@click="startMatch"
						>
							{{ actionLabel('start') || '[start match]' }}
						</AppButton>
						<AppButton variant="ghost" size="sm" :disabled="busy" @click="resetMatch">
							{{ actionLabel('reset') || '[reset match]' }}
						</AppButton>
					</div>
				</section>

				<section v-if="match.status === 'Live'" class="space-y-3">
					<div class="text-sm font-bold uppercase tracking-widest text-green-500">
						live match
					</div>
					<div class="flex flex-wrap gap-3">
						<AppButton
							v-for="quickAdd in quickAdds"
							:key="quickAdd.seconds"
							variant="ghost"
							size="sm"
							:disabled="busy"
							@click="addTime(quickAdd.seconds)"
						>
							{{ actionLabel(`add-${quickAdd.seconds}`) || quickAdd.label }}
						</AppButton>
						<AppButton variant="primary" size="sm" :disabled="busy" @click="judgeNow">
							{{ actionLabel('judge') || '[judge now]' }}
						</AppButton>
						<AppButton variant="ghost" size="sm" :disabled="busy" @click="resetMatch">
							{{ actionLabel('reset') || '[reset match]' }}
						</AppButton>
					</div>
				</section>

				<section
					v-if="match.status === 'Live' || match.status === 'Review'"
					class="space-y-3"
				>
					<div class="text-sm font-bold uppercase tracking-widest text-green-500">
						set winner
					</div>
					<div class="grid gap-3 sm:grid-cols-2">
						<AppButton
							v-for="player in players"
							:key="player.id"
							variant="ghost"
							size="sm"
							:disabled="busy"
							class="justify-center"
							@click="forceFinish(player.id)"
						>
							{{
								actionLabel(`winner-${player.id}`) ||
								`[set winner: ${player.name}]`
							}}
						</AppButton>
					</div>
				</section>

				<section v-if="match.status === 'Review'" class="space-y-3">
					<div class="text-sm font-bold uppercase tracking-widest text-green-500">
						review actions
					</div>
					<div class="flex flex-wrap gap-3">
						<AppButton
							variant="primary"
							size="sm"
							:disabled="busy"
							@click="createRematch"
						>
							{{ actionLabel('rematch') || '[create rematch]' }}
						</AppButton>
						<AppButton variant="ghost" size="sm" :disabled="busy" @click="resetMatch">
							{{ actionLabel('reset') || '[reset match]' }}
						</AppButton>
					</div>
				</section>

				<section
					v-if="match.status === 'Finished' || match.status === 'Cancelled'"
					class="space-y-3"
				>
					<div class="text-sm font-bold uppercase tracking-widest text-green-500">
						post-match
					</div>
					<div class="flex flex-wrap gap-3">
						<AppButton variant="ghost" size="sm" :disabled="busy" @click="resetMatch">
							{{ actionLabel('reset') || '[reset match]' }}
						</AppButton>
					</div>
				</section>
			</div>
		</div>
	</div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useCall } from 'frappe-ui'
import type { MatchState } from '@/data/match'
import AppButton from '@/components/AppButton.vue'

const props = defineProps<{
	modelValue: boolean
	match: MatchState | null
}>()

const emit = defineEmits<{
	'update:modelValue': [value: boolean]
	refreshed: []
}>()

const pendingAction = ref<string | null>(null)
const feedback = ref('')
const feedbackTone = ref<'success' | 'error'>('success')

const quickAdds = [
	{ label: '[+1 min]', seconds: 60 },
	{ label: '[+2 min]', seconds: 120 },
	{ label: '[+5 min]', seconds: 300 },
]

const players = computed(() =>
	props.match
		? [
				{
					id: props.match.player_1.id,
					name: props.match.player_1.name || 'player_1',
				},
				{
					id: props.match.player_2.id,
					name: props.match.player_2.name || 'player_2',
				},
			].filter((player) => !!player.id)
		: [],
)

const deadlineLabel = computed(() => {
	if (!props.match?.deadline) return '--'
	return new Date(props.match.deadline).toLocaleTimeString([], {
		hour: '2-digit',
		minute: '2-digit',
		second: '2-digit',
	})
})

const winnerLabel = computed(() => {
	if (!props.match?.winner) return '--'
	return (
		players.value.find((player) => player.id === props.match?.winner)?.name ||
		props.match.winner
	)
})

const busy = computed(() => pendingAction.value !== null)

function close() {
	if (busy.value) return
	emit('update:modelValue', false)
}

function setFeedback(message: string, tone: 'success' | 'error' = 'success') {
	feedback.value = message
	feedbackTone.value = tone
}

function actionLabel(action: string) {
	return pendingAction.value === action ? '[working...]' : ''
}

function beginAction(action: string) {
	pendingAction.value = action
	feedback.value = ''
}

function endAction(message?: string) {
	pendingAction.value = null
	if (message) {
		setFeedback(message)
	}
	emit('refreshed')
}

function failAction(err: any) {
	pendingAction.value = null
	setFeedback(err?.messages?.[0]?.message || err?.message || 'Match action failed', 'error')
}

const startMatchCall = useCall({
	url: '/api/v2/method/codeoff.api.contest.start_match_now',
	immediate: false,
	onSuccess() {
		endAction('Match started')
	},
	onError: failAction,
})

const addTimeCall = useCall({
	url: '/api/v2/method/codeoff.api.contest.organizer_add_match_time',
	immediate: false,
	onSuccess() {
		endAction('Match time updated')
	},
	onError: failAction,
})

const judgeNowCall = useCall({
	url: '/api/v2/method/codeoff.api.contest.organizer_resolve_match',
	immediate: false,
	onSuccess(data: any) {
		endAction(data?.status === 'Review' ? 'Match moved to review' : 'Match resolved')
	},
	onError: failAction,
})

const forceFinishCall = useCall({
	url: '/api/v2/method/codeoff.api.contest.organizer_force_finish_match',
	immediate: false,
	onSuccess() {
		endAction('Winner updated')
	},
	onError: failAction,
})

const resetMatchCall = useCall({
	url: '/api/v2/method/codeoff.api.contest.organizer_reset_match',
	immediate: false,
	onSuccess() {
		endAction('Match reset')
	},
	onError: failAction,
})

const createRematchCall = useCall({
	url: '/api/v2/method/codeoff.api.contest.organizer_create_rematch',
	immediate: false,
	onSuccess(data: any) {
		endAction(
			data?.rematch_match_id
				? `Rematch created: ${data.rematch_match_id}`
				: 'Rematch created',
		)
	},
	onError: failAction,
})

function startMatch() {
	if (!props.match) return
	beginAction('start')
	startMatchCall.submit({ match_id: props.match.match_id })
}

function addTime(seconds: number) {
	if (!props.match) return
	beginAction(`add-${seconds}`)
	addTimeCall.submit({ match_id: props.match.match_id, seconds })
}

function judgeNow() {
	if (!props.match) return
	beginAction('judge')
	judgeNowCall.submit({ match_id: props.match.match_id })
}

function forceFinish(winnerPlayer: string) {
	if (!props.match) return
	beginAction(`winner-${winnerPlayer}`)
	forceFinishCall.submit({
		match_id: props.match.match_id,
		winner_player: winnerPlayer,
	})
}

function resetMatch() {
	if (!props.match) return
	beginAction('reset')
	resetMatchCall.submit({ match_id: props.match.match_id })
}

function createRematch() {
	if (!props.match) return
	beginAction('rematch')
	createRematchCall.submit({ match_id: props.match.match_id })
}
</script>
