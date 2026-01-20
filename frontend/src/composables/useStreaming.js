import { ref, onUnmounted } from 'vue'
import { useAuthStore } from '../stores/auth'

/**
 * Composable for SSE streaming with token-by-token display
 */
export function useStreaming() {
  const authStore = useAuthStore()
  const text = ref('')
  const isStreaming = ref(false)
  const status = ref('idle') // idle, connecting, streaming, done, error
  const error = ref(null)
  const citations = ref([])
  const metadata = ref({})
  
  let abortController = null
  
  async function startStream(url) {
    // Reset state
    text.value = ''
    isStreaming.value = true
    status.value = 'connecting'
    error.value = null
    citations.value = []
    metadata.value = {}
    
    abortController = new AbortController()
    
    try {
      const response = await fetch(url, {
        headers: {
          'Authorization': `Bearer ${authStore.token}`,
        },
        signal: abortController.signal,
      })
      
      if (!response.ok) {
        throw new Error('Stream bağlantısı başarısız')
      }
      
      status.value = 'streaming'
      
      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      
      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        
        const chunk = decoder.decode(value, { stream: true })
        const lines = chunk.split('\n')
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6))
              
              if (data.status) {
                status.value = data.status
              }
              
              if (data.token) {
                text.value += data.token
              }
              
              if (data.citations) {
                citations.value = data.citations
              }
              
              if (data.confidence !== undefined) {
                metadata.value.confidence = data.confidence
              }
              
              if (data.latency !== undefined) {
                metadata.value.latency = data.latency
              }
              
              if (data.done) {
                status.value = 'done'
                isStreaming.value = false
              }
              
              if (data.error) {
                error.value = data.error
                status.value = 'error'
                isStreaming.value = false
              }
            } catch (e) {
              // Ignore JSON parse errors for incomplete chunks
            }
          }
        }
      }
      
      if (isStreaming.value) {
        status.value = 'done'
        isStreaming.value = false
      }
      
    } catch (err) {
      if (err.name !== 'AbortError') {
        error.value = err.message
        status.value = 'error'
      }
      isStreaming.value = false
    }
  }
  
  function stopStream() {
    if (abortController) {
      abortController.abort()
      abortController = null
    }
    isStreaming.value = false
    status.value = 'idle'
  }
  
  function reset() {
    stopStream()
    text.value = ''
    error.value = null
    citations.value = []
    metadata.value = {}
  }
  
  onUnmounted(() => {
    stopStream()
  })
  
  return {
    text,
    isStreaming,
    status,
    error,
    citations,
    metadata,
    startStream,
    stopStream,
    reset,
  }
}
