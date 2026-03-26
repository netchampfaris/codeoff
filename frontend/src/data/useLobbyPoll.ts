import { ref, watch, onUnmounted } from 'vue'
import type { Ref } from 'vue'

/**
 * Polls reload() every 2 seconds while match status is "Ready" (lobby).
 * Cleans up the interval when status changes or component unmounts.
 */
export function useLobbyPoll(
  status: Ref<string | undefined>,
  reload: () => void,
) {
  let poll: ReturnType<typeof setInterval> | null = null

  watch(
    status,
    (s) => {
      if (s === 'Ready' && !poll) {
        poll = setInterval(reload, 2000)
      } else if (s !== 'Ready' && poll) {
        clearInterval(poll)
        poll = null
      }
    },
    { immediate: true },
  )

  onUnmounted(() => {
    if (poll) clearInterval(poll)
  })
}
