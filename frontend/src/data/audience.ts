import { ref, watch, onMounted, onUnmounted } from 'vue'
import { useCall } from 'frappe-ui'
import { useRoute } from 'vue-router'
import { getSocket } from './socket'

const AUDIENCE_CHANNEL = 'codeoff_audience'
const AUDIENCE_HEARTBEAT_MS = 20_000
const AUDIENCE_VIEWER_KEY = 'codeoff_audience_viewer_token'

const audienceTotal = ref<number | null>(null)
const audienceAvailable = ref(false)

export function useAudienceCount() {
  return { audienceTotal, audienceAvailable }
}

export function useAudiencePresence() {
  const route = useRoute()
  let heartbeatTimer: ReturnType<typeof setInterval> | null = null
  let active = false

  const heartbeatCall = useCall({
    url: '/api/v2/method/codeoff.api.contest.heartbeat_audience',
    immediate: false,
    onSuccess(data: { audience_total: number }) {
      audienceTotal.value = data.audience_total
      audienceAvailable.value = true
    },
    onError() {
      audienceAvailable.value = false
    },
  })

  const leaveCall = useCall({
    url: '/api/v2/method/codeoff.api.contest.leave_audience',
    immediate: false,
  })

  function getViewerToken() {
    let token = sessionStorage.getItem(AUDIENCE_VIEWER_KEY)
    if (!token) {
      token = `aud-${crypto.randomUUID()}`
      sessionStorage.setItem(AUDIENCE_VIEWER_KEY, token)
    }
    return token
  }

  function isEligibleRoute() {
    return route.name !== 'MatchWorkspace'
  }

  function applyAudienceEvent(data: any) {
    if (data?.event_type !== 'audience_count_updated') return
    audienceTotal.value = data.audience_total
    audienceAvailable.value = true
  }

  function sendHeartbeat() {
    heartbeatCall.submit({ viewer_token: getViewerToken() })
  }

  function startPresence() {
    if (active || !isEligibleRoute()) return
    active = true
    sendHeartbeat()
    heartbeatTimer = setInterval(sendHeartbeat, AUDIENCE_HEARTBEAT_MS)
  }

  function stopPresence() {
    if (!active) return
    active = false
    if (heartbeatTimer) {
      clearInterval(heartbeatTimer)
      heartbeatTimer = null
    }
    leaveCall.submit({ viewer_token: getViewerToken() })
  }

  onMounted(() => {
    getSocket().on(AUDIENCE_CHANNEL, applyAudienceEvent)
  })

  watch(
    () => route.name,
    () => {
      if (isEligibleRoute()) {
        startPresence()
      } else {
        stopPresence()
      }
    },
    { immediate: true },
  )

  onUnmounted(() => {
    stopPresence()
    getSocket().off(AUDIENCE_CHANNEL, applyAudienceEvent)
  })
}