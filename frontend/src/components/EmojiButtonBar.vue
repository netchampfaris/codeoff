<template>
  <button
    v-for="emoji in EMOJIS"
    :key="emoji"
    class="emoji-btn rounded-none"
    :class="[
      large ? 'cursor-pointer text-2xl' : 'px-1 text-xl',
      { fired: activeEmoji[`${emoji}-${playerId}`] },
    ]"
    @click="emit('react', emoji, playerId)"
  >
    {{ emoji }}
  </button>
</template>

<script setup lang="ts">
const EMOJIS = ['🔥', '💀', '👀', '🎉', '😬']

defineProps<{
  playerId: string | null | undefined
  activeEmoji: Record<string, boolean>
  large?: boolean
}>()

const emit = defineEmits<{
  react: [emoji: string, playerId: string | null | undefined]
}>()
</script>

<style scoped>
@keyframes emoji-burst {
  0% {
    transform: scale(1);
  }
  25% {
    transform: scale(0.7) rotate(-8deg);
  }
  60% {
    transform: scale(1.5) rotate(6deg);
  }
  80% {
    transform: scale(1.2) rotate(-3deg);
  }
  100% {
    transform: scale(1) rotate(0deg);
  }
}

.emoji-btn {
  transition:
    transform 0.1s ease,
    filter 0.1s ease;
  will-change: transform;
  user-select: none;
}
.emoji-btn:hover {
  transform: scale(1.3);
  filter: drop-shadow(0 0 4px rgba(74, 222, 128, 0.5));
}
.emoji-btn:active {
  transform: scale(0.85);
}
.emoji-btn.fired {
  animation: emoji-burst 0.35s cubic-bezier(0.36, 0.07, 0.19, 0.97) forwards;
}
</style>
