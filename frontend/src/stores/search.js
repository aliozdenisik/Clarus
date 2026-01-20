import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useAuthStore } from './auth'

const API_URL = '/api'

export const useSearchStore = defineStore('search', () => {
  const query = ref('')
  const results = ref([])
  const isLoading = ref(false)
  const isStreaming = ref(false)
  const streamedText = ref('')
  const error = ref(null)
  const history = ref([])
  
  const authStore = useAuthStore()
  
  function getHeaders() {
    return {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${authStore.token}`,
    }
  }
  
  async function search(searchQuery, source = 'quran') {
    query.value = searchQuery
    isLoading.value = true
    error.value = null
    
    try {
      const response = await fetch(`${API_URL}/search/${source}`, {
        method: 'POST',
        headers: getHeaders(),
        body: JSON.stringify({ query: searchQuery, top_k: 10 }),
      })
      
      if (!response.ok) {
        const err = await response.json()
        throw new Error(err.detail || 'Arama başarısız')
      }
      
      const data = await response.json()
      results.value = data.results
      return data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      isLoading.value = false
    }
  }
  
  async function streamSearch(searchQuery, source = 'quran', onToken) {
    query.value = searchQuery
    isStreaming.value = true
    streamedText.value = ''
    error.value = null
    
    const url = `${API_URL}/stream/search?q=${encodeURIComponent(searchQuery)}&source=${source}`
    
    try {
      const eventSource = new EventSource(url, {
        // Note: EventSource doesn't support custom headers
        // We need to pass token as query param or use fetch
      })
      
      // Using fetch for SSE with auth
      const response = await fetch(url, {
        headers: { 'Authorization': `Bearer ${authStore.token}` },
      })
      
      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      
      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        
        const text = decoder.decode(value)
        const lines = text.split('\n')
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = JSON.parse(line.slice(6))
            
            if (data.token) {
              streamedText.value += data.token
              if (onToken) onToken(data.token)
            }
            
            if (data.done) {
              isStreaming.value = false
            }
            
            if (data.error) {
              error.value = data.error
              isStreaming.value = false
            }
          }
        }
      }
    } catch (err) {
      error.value = err.message
      isStreaming.value = false
    }
  }
  
  async function fetchHistory() {
    try {
      const response = await fetch(`${API_URL}/search/history?limit=20`, {
        headers: getHeaders(),
      })
      
      if (response.ok) {
        history.value = await response.json()
      }
    } catch (err) {
      console.error('Failed to fetch history:', err)
    }
  }
  
  function clearResults() {
    results.value = []
    streamedText.value = ''
    error.value = null
  }
  
  return {
    query,
    results,
    isLoading,
    isStreaming,
    streamedText,
    error,
    history,
    search,
    streamSearch,
    fetchHistory,
    clearResults,
  }
})
