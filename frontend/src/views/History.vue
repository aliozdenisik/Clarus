<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()
const history = ref([])
const loading = ref(true)
const error = ref(null)

async function fetchHistory() {
  loading.value = true
  error.value = null
  
  try {
    const response = await fetch('/api/search/history', {
      headers: {
        'Authorization': `Bearer ${authStore.token}`
      }
    })
    
    if (!response.ok) {
      throw new Error('Geçmiş yüklenemedi')
    }
    
    const data = await response.json()
    history.value = Array.isArray(data) ? data : (data.history || [])
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchHistory()
})
</script>

<template>
  <main class="flex-1 w-full px-4 md:px-6 py-8">
    <div class="max-w-[800px] mx-auto">
      <h1 class="text-3xl font-bold mb-2">Arama Geçmişi</h1>
      <p class="text-text-secondary mb-8">
        Son aramalarınız burada listelenir.
      </p>

      <!-- Loading -->
      <div v-if="loading" class="flex justify-center py-12">
        <div class="flex gap-1">
          <span class="w-2 h-2 bg-primary rounded-full animate-bounce" style="animation-delay: 0ms"></span>
          <span class="w-2 h-2 bg-primary rounded-full animate-bounce" style="animation-delay: 150ms"></span>
          <span class="w-2 h-2 bg-primary rounded-full animate-bounce" style="animation-delay: 300ms"></span>
        </div>
      </div>

      <!-- Error -->
      <div v-else-if="error" class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
        <p class="text-red-600 dark:text-red-400">{{ error }}</p>
      </div>

      <!-- Empty State -->
      <div v-else-if="history.length === 0" class="text-center py-12">
        <span class="material-symbols-outlined text-5xl text-text-secondary mb-4">history</span>
        <p class="text-text-secondary">Henüz arama yapmadınız.</p>
      </div>

      <!-- History List -->
      <div v-else class="space-y-3">
        <div
          v-for="item in history"
          :key="item.id"
          class="flex items-center justify-between bg-white dark:bg-surface-dark border border-border-light dark:border-border-dark rounded-lg p-4 hover:shadow-sm transition-shadow"
        >
          <div class="flex items-center gap-3">
            <span class="material-symbols-outlined text-primary">search</span>
            <div>
              <p class="font-medium">{{ item.query }}</p>
              <p class="text-sm text-text-secondary">
                {{ item.search_type }} · {{ new Date(item.created_at).toLocaleString('tr-TR') }}
              </p>
            </div>
          </div>
          <router-link
            :to="`/results?q=${encodeURIComponent(item.query)}&source=${item.search_type.includes('quran') ? 'quran' : 'bible'}`"
            class="text-primary hover:underline text-sm"
          >
            Tekrarla
          </router-link>
        </div>
      </div>
    </div>
  </main>
</template>
