<template>
  <FrappeUIProvider>
    <router-view />
  </FrappeUIProvider>
</template>

<script setup lang="ts">
import { FrappeUIProvider } from 'frappe-ui'
import { useAudiencePresence } from '@/data/audience'

useAudiencePresence()
</script>
