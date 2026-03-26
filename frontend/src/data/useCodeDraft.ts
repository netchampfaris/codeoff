import { ref, watch } from 'vue'
import { useCall } from 'frappe-ui'
import type { Ref } from 'vue'
import type { MatchState } from './match'

/**
 * Manages code state: localStorage persistence, draft sync with server,
 * and initialization from server draft or starter code.
 */
export function useCodeDraft(
  matchId: string,
  state: Ref<MatchState | null>,
  findMyPlayerId: () => string | null,
) {
  const STORAGE_KEY = `codeoff_code_${matchId}`
  const code = ref(localStorage.getItem(STORAGE_KEY) || '')

  let lastCursor = { line: 0, column: 0 }
  let draftTimeout: ReturnType<typeof setTimeout> | null = null

  const updateDraft = useCall({
    url: '/api/v2/method/codeoff.api.contest.update_draft',
    immediate: false,
  })

  function scheduleDraftUpdate(line: number, column: number) {
    lastCursor = { line, column }
    if (draftTimeout) clearTimeout(draftTimeout)
    draftTimeout = setTimeout(() => {
      updateDraft.submit({
        match_id: matchId,
        source_code: code.value,
        cursor_line: lastCursor.line,
        cursor_column: lastCursor.column,
      })
    }, 400)
  }

  function onCursorChange(line: number, column: number) {
    scheduleDraftUpdate(line, column)
  }

  watch(code, () => {
    localStorage.setItem(STORAGE_KEY, code.value)
    scheduleDraftUpdate(lastCursor.line, lastCursor.column)
  })

  // Initialize from server draft or starter code (only if local storage is empty)
  watch(
    state,
    (s) => {
      if (!s || code.value) return
      const playerId = findMyPlayerId()
      if (playerId && s.drafts[playerId]) {
        code.value = s.drafts[playerId].source_code
      } else if (s.problem?.starter_code) {
        code.value = s.problem.starter_code
      }
    },
    { immediate: true },
  )

  return { code, onCursorChange }
}
