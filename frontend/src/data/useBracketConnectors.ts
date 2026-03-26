import { ref, onMounted, onUpdated, nextTick } from 'vue'
import type { ComputedRef } from 'vue'

export function useBracketConnectors(
  containerRef: ReturnType<typeof ref<HTMLElement | undefined>>,
  sortedRounds: ComputedRef<{ number: number; matches: any[] }[]>,
) {
  const matchRefs: Record<string, HTMLElement> = {}
  const connectors = ref<string[]>([])
  const svgWidth = ref(0)
  const svgHeight = ref(0)

  function setMatchRef(name: string, el: any) {
    if (el?.$el) el = el.$el
    if (el) matchRefs[name] = el
  }

  function computeConnectors() {
    const container = containerRef.value?.querySelector(
      '.relative',
    ) as HTMLElement
    if (!container) return

    const containerRect = container.getBoundingClientRect()
    const newWidth = container.scrollWidth
    const newHeight = container.scrollHeight

    const paths: string[] = []
    const rounds = sortedRounds.value

    for (let ri = 0; ri < rounds.length - 1; ri++) {
      const currentMatches = rounds[ri].matches
      const nextMatches = rounds[ri + 1].matches

      for (let mi = 0; mi < currentMatches.length; mi++) {
        const matchEl = matchRefs[currentMatches[mi].name]
        const nextMatchEl = matchRefs[nextMatches[Math.floor(mi / 2)]?.name]
        if (!matchEl || !nextMatchEl) continue

        const srcRect = matchEl.getBoundingClientRect()
        const dstRect = nextMatchEl.getBoundingClientRect()

        const x1 = srcRect.right - containerRect.left
        const y1 = srcRect.top + srcRect.height / 2 - containerRect.top
        const x2 = dstRect.left - containerRect.left
        const y2 = dstRect.top + dstRect.height / 2 - containerRect.top
        const midX = (x1 + x2) / 2

        paths.push(`M ${x1} ${y1} H ${midX} V ${y2} H ${x2}`)
      }
    }

    const pathsStr = paths.join('|')
    if (
      pathsStr !== connectors.value.join('|') ||
      newWidth !== svgWidth.value ||
      newHeight !== svgHeight.value
    ) {
      svgWidth.value = newWidth
      svgHeight.value = newHeight
      connectors.value = paths
    }
  }

  onMounted(() => nextTick(computeConnectors))
  onUpdated(() => nextTick(computeConnectors))

  return { connectors, svgWidth, svgHeight, setMatchRef }
}
