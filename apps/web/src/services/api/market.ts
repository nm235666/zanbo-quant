import { http } from '../http'

export async function fetchMarketConclusion() {
  const { data } = await http.get('/api/market/conclusion')
  return data
}
