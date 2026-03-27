<template>
  <component :is="tag" v-bind="$attrs" :class="computedClasses">
    <slot />
  </component>
</template>

<script setup lang="ts">
import { computed } from 'vue'

/**
 * Variants:
 *   primary — filled green (submit, start match)
 *   ghost    — green-900 border; set :active for toggled-on state
 *   tab      — borderless with underline when :active (tab switcher)
 *   inline   — typography only; pass color via class prop
 *
 * Sizes (ignored by tab, inline):  xs (default) | sm | md
 */
const props = withDefaults(
  defineProps<{
    variant?: 'primary' | 'ghost' | 'tab' | 'inline'
    size?: 'xs' | 'sm' | 'md'
    active?: boolean
    tag?: string
  }>(),
  {
    variant: 'outline',
    size: 'xs',
    tag: 'button',
  },
)

const computedClasses = computed(() => {
  const classes: string[] = [
    'font-bold uppercase tracking-widest transition-colors',
  ]

  if (props.variant === 'inline') {
    classes.push('text-xs')
    return classes.join(' ')
  }

  if (props.variant === 'primary' || props.variant === 'ghost') {
    classes.push('disabled:cursor-not-allowed disabled:opacity-40')
  }

  // Padding / text size
  if (props.variant === 'tab') {
    classes.push('px-4 py-2 text-xs')
  } else {
    const sizes: Record<string, string> = {
      xs: 'px-3 py-1 text-xs',
      sm: 'px-4 py-1.5 text-xs',
      md: 'px-6 py-2 text-sm',
    }
    classes.push(sizes[props.size])
  }

  // Color
  switch (props.variant) {
    case 'primary':
      classes.push(
        'bg-green-950/30 hover:bg-green-950/60 border border-green-400 text-green-400',
      )
      break
    case 'ghost':
      classes.push(
        props.active
          ? 'border border-green-400 text-green-400'
          : 'border border-green-900 text-green-700 hover:border-green-600 hover:text-green-400',
      )
      break
    case 'tab':
      classes.push(
        props.active
          ? 'border-b-2 border-green-400 text-green-400'
          : 'text-green-800 hover:text-green-500',
      )
      break
    // 'inline': caller supplies color via class attribute
  }

  return classes.join(' ')
})
</script>
