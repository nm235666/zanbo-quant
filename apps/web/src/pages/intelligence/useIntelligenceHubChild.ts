import { computed } from 'vue'
import { useRoute } from 'vue-router'

export function useIntelligenceHubChild() {
  const route = useRoute()
  return computed(() =>
    route.matched.some((record) => (record.meta as { intelligenceHubChild?: boolean }).intelligenceHubChild === true),
  )
}
