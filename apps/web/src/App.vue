<template>
  <RouterView v-slot="{ Component }">
    <Transition name="page" mode="out-in">
      <component :is="Component" />
    </Transition>
  </RouterView>
  <AppToastContainer />
</template>

<script setup lang="ts">
import { RouterView } from 'vue-router'
import { useRealtimeBus } from './shared/realtime/useRealtimeBus'
import AppToastContainer from './shared/ui/AppToastContainer.vue'

useRealtimeBus()
</script>
