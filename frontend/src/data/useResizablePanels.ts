import { ref } from 'vue'

/**
 * Resizable split panels with drag handles.
 * Returns panel size refs and mousedown handlers for horizontal + vertical handles.
 */
export function useResizablePanels(
  options: {
    problemMin?: number
    problemMax?: number
    problemDefault?: number
    bottomMin?: number
    bottomMax?: number
    bottomDefault?: number
  } = {},
) {
  const {
    problemMin = 240,
    problemMax = 700,
    problemDefault = 400,
    bottomMin = 80,
    bottomMax = 500,
    bottomDefault = 220,
  } = options

  const problemPanelWidth = ref(problemDefault)
  const bottomPanelHeight = ref(bottomDefault)

  function startDragH(e: MouseEvent) {
    const startX = e.clientX
    const startW = problemPanelWidth.value
    function onMove(ev: MouseEvent) {
      problemPanelWidth.value = Math.min(
        problemMax,
        Math.max(problemMin, startW + (ev.clientX - startX)),
      )
    }
    function onUp() {
      window.removeEventListener('mousemove', onMove)
      window.removeEventListener('mouseup', onUp)
    }
    window.addEventListener('mousemove', onMove)
    window.addEventListener('mouseup', onUp)
  }

  function startDragV(e: MouseEvent) {
    const startY = e.clientY
    const startH = bottomPanelHeight.value
    function onMove(ev: MouseEvent) {
      bottomPanelHeight.value = Math.min(
        bottomMax,
        Math.max(bottomMin, startH + (startY - ev.clientY)),
      )
    }
    function onUp() {
      window.removeEventListener('mousemove', onMove)
      window.removeEventListener('mouseup', onUp)
    }
    window.addEventListener('mousemove', onMove)
    window.addEventListener('mouseup', onUp)
  }

  return { problemPanelWidth, bottomPanelHeight, startDragH, startDragV }
}
