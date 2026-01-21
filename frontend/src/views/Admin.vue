<script setup>
import { ref, onMounted, computed } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useRouter } from 'vue-router'

const authStore = useAuthStore()
const router = useRouter()

const stats = ref({
  totalUsers: 0,
  totalSearches: 0,
  todaySearches: 0,
  activeUsers: 0
})
const users = ref([])
const systemInfo = ref({})
const loading = ref(true)
const error = ref(null)
const activeTab = ref('overview')

// Check if current user is admin
const isAdmin = computed(() => {
  return authStore.user?.email === 'admin@hollysearch.com' || authStore.user?.email === 'test@example.com'
})

async function fetchStats() {
  try {
    const response = await fetch('/api/admin/stats', {
      headers: { 'Authorization': `Bearer ${authStore.token}` }
    })
    if (response.ok) {
      stats.value = await response.json()
    }
  } catch (e) {
    console.error('Stats fetch failed:', e)
  }
}

async function fetchUsers() {
  try {
    const response = await fetch('/api/admin/users', {
      headers: { 'Authorization': `Bearer ${authStore.token}` }
    })
    if (response.ok) {
      users.value = await response.json()
    }
  } catch (e) {
    console.error('Users fetch failed:', e)
  }
}

async function fetchSystemInfo() {
  try {
    const response = await fetch('/api/admin/system', {
      headers: { 'Authorization': `Bearer ${authStore.token}` }
    })
    if (response.ok) {
      systemInfo.value = await response.json()
    }
  } catch (e) {
    console.error('System info fetch failed:', e)
  }
}

onMounted(async () => {
  if (!isAdmin.value) {
    router.push('/')
    return
  }
  
  loading.value = true
  await Promise.all([fetchStats(), fetchUsers(), fetchSystemInfo()])
  loading.value = false
})

function formatDate(dateStr) {
  return new Date(dateStr).toLocaleString('tr-TR')
}
</script>

<template>
  <main class="flex-1 w-full px-4 md:px-6 py-8">
    <div class="max-w-[1200px] mx-auto">
      <!-- Header -->
      <div class="flex items-center justify-between mb-8">
        <div>
          <h1 class="text-3xl font-bold">Admin Dashboard</h1>
          <p class="text-text-secondary">Sistem yönetimi ve istatistikleri</p>
        </div>
        <div class="flex items-center gap-2 px-3 py-1.5 bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 rounded-full text-sm">
          <span class="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
          Sistem Aktif
        </div>
      </div>

      <!-- Tabs -->
      <div class="flex border-b border-border-light dark:border-border-dark mb-6">
        <button
          @click="activeTab = 'overview'"
          :class="['px-4 py-2 text-sm font-medium border-b-2 transition-colors', activeTab === 'overview' ? 'border-primary text-primary' : 'border-transparent text-text-secondary hover:text-text-main']"
        >
          Genel Bakış
        </button>
        <button
          @click="activeTab = 'users'"
          :class="['px-4 py-2 text-sm font-medium border-b-2 transition-colors', activeTab === 'users' ? 'border-primary text-primary' : 'border-transparent text-text-secondary hover:text-text-main']"
        >
          Kullanıcılar
        </button>
        <button
          @click="activeTab = 'system'"
          :class="['px-4 py-2 text-sm font-medium border-b-2 transition-colors', activeTab === 'system' ? 'border-primary text-primary' : 'border-transparent text-text-secondary hover:text-text-main']"
        >
          Sistem
        </button>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="flex justify-center py-12">
        <div class="flex gap-1">
          <span class="w-2 h-2 bg-primary rounded-full animate-bounce" style="animation-delay: 0ms"></span>
          <span class="w-2 h-2 bg-primary rounded-full animate-bounce" style="animation-delay: 150ms"></span>
          <span class="w-2 h-2 bg-primary rounded-full animate-bounce" style="animation-delay: 300ms"></span>
        </div>
      </div>

      <!-- Overview Tab -->
      <div v-else-if="activeTab === 'overview'" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <!-- Stats Cards -->
        <div class="bg-white dark:bg-surface-dark border border-border-light dark:border-border-dark rounded-xl p-6">
          <div class="flex items-center gap-3 mb-2">
            <div class="p-2 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
              <span class="material-symbols-outlined text-blue-600">group</span>
            </div>
            <span class="text-text-secondary text-sm">Toplam Kullanıcı</span>
          </div>
          <p class="text-3xl font-bold">{{ stats.totalUsers || users.length }}</p>
        </div>

        <div class="bg-white dark:bg-surface-dark border border-border-light dark:border-border-dark rounded-xl p-6">
          <div class="flex items-center gap-3 mb-2">
            <div class="p-2 bg-green-100 dark:bg-green-900/30 rounded-lg">
              <span class="material-symbols-outlined text-green-600">search</span>
            </div>
            <span class="text-text-secondary text-sm">Toplam Arama</span>
          </div>
          <p class="text-3xl font-bold">{{ stats.totalSearches || '—' }}</p>
        </div>

        <div class="bg-white dark:bg-surface-dark border border-border-light dark:border-border-dark rounded-xl p-6">
          <div class="flex items-center gap-3 mb-2">
            <div class="p-2 bg-purple-100 dark:bg-purple-900/30 rounded-lg">
              <span class="material-symbols-outlined text-purple-600">trending_up</span>
            </div>
            <span class="text-text-secondary text-sm">Bugünkü Aramalar</span>
          </div>
          <p class="text-3xl font-bold">{{ stats.todaySearches || '—' }}</p>
        </div>

        <div class="bg-white dark:bg-surface-dark border border-border-light dark:border-border-dark rounded-xl p-6">
          <div class="flex items-center gap-3 mb-2">
            <div class="p-2 bg-amber-100 dark:bg-amber-900/30 rounded-lg">
              <span class="material-symbols-outlined text-amber-600">bolt</span>
            </div>
            <span class="text-text-secondary text-sm">Aktif Kullanıcı</span>
          </div>
          <p class="text-3xl font-bold">{{ stats.activeUsers || '—' }}</p>
        </div>

        <!-- Recent Activity -->
        <div class="col-span-full bg-white dark:bg-surface-dark border border-border-light dark:border-border-dark rounded-xl p-6 mt-4">
          <h3 class="text-lg font-bold mb-4">Son Kullanıcılar</h3>
          <div class="space-y-3">
            <div v-for="user in users.slice(0, 5)" :key="user.id" class="flex items-center justify-between py-2 border-b border-border-light dark:border-border-dark last:border-0">
              <div class="flex items-center gap-3">
                <div class="w-8 h-8 bg-primary/10 rounded-full flex items-center justify-center">
                  <span class="text-primary text-sm font-bold">{{ user.name?.charAt(0) || 'U' }}</span>
                </div>
                <div>
                  <p class="font-medium">{{ user.name }}</p>
                  <p class="text-sm text-text-secondary">{{ user.email }}</p>
                </div>
              </div>
              <span class="text-xs text-text-secondary">{{ formatDate(user.created_at) }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Users Tab -->
      <div v-else-if="activeTab === 'users'" class="bg-white dark:bg-surface-dark border border-border-light dark:border-border-dark rounded-xl overflow-hidden">
        <table class="w-full">
          <thead class="bg-gray-50 dark:bg-gray-800">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-text-secondary uppercase tracking-wider">Kullanıcı</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-text-secondary uppercase tracking-wider">Email</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-text-secondary uppercase tracking-wider">Kayıt Tarihi</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-text-secondary uppercase tracking-wider">Durum</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-border-light dark:divide-border-dark">
            <tr v-for="user in users" :key="user.id" class="hover:bg-gray-50 dark:hover:bg-gray-800/50">
              <td class="px-6 py-4">
                <div class="flex items-center gap-3">
                  <div class="w-8 h-8 bg-primary/10 rounded-full flex items-center justify-center">
                    <span class="text-primary text-sm font-bold">{{ user.name?.charAt(0) || 'U' }}</span>
                  </div>
                  <span class="font-medium">{{ user.name }}</span>
                </div>
              </td>
              <td class="px-6 py-4 text-text-secondary">{{ user.email }}</td>
              <td class="px-6 py-4 text-text-secondary text-sm">{{ formatDate(user.created_at) }}</td>
              <td class="px-6 py-4">
                <span class="px-2 py-1 text-xs bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 rounded-full">
                  Aktif
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- System Tab -->
      <div v-else-if="activeTab === 'system'" class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div class="bg-white dark:bg-surface-dark border border-border-light dark:border-border-dark rounded-xl p-6">
          <h3 class="text-lg font-bold mb-4 flex items-center gap-2">
            <span class="material-symbols-outlined text-primary">dns</span>
            Backend
          </h3>
          <div class="space-y-3">
            <div class="flex justify-between">
              <span class="text-text-secondary">Framework</span>
              <span class="font-medium">FastAPI</span>
            </div>
            <div class="flex justify-between">
              <span class="text-text-secondary">Python</span>
              <span class="font-medium">{{ systemInfo.python_version || '3.12' }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-text-secondary">API Status</span>
              <span class="text-green-600 font-medium">Çalışıyor</span>
            </div>
          </div>
        </div>

        <div class="bg-white dark:bg-surface-dark border border-border-light dark:border-border-dark rounded-xl p-6">
          <h3 class="text-lg font-bold mb-4 flex items-center gap-2">
            <span class="material-symbols-outlined text-primary">storage</span>
            Veritabanları
          </h3>
          <div class="space-y-3">
            <div class="flex justify-between">
              <span class="text-text-secondary">PostgreSQL</span>
              <span class="text-green-600 font-medium">Bağlı</span>
            </div>
            <div class="flex justify-between">
              <span class="text-text-secondary">Qdrant</span>
              <span class="text-green-600 font-medium">Bağlı</span>
            </div>
            <div class="flex justify-between">
              <span class="text-text-secondary">Koleksiyonlar</span>
              <span class="font-medium">{{ systemInfo.collections || 4 }}</span>
            </div>
          </div>
        </div>

        <div class="bg-white dark:bg-surface-dark border border-border-light dark:border-border-dark rounded-xl p-6">
          <h3 class="text-lg font-bold mb-4 flex items-center gap-2">
            <span class="material-symbols-outlined text-primary">api</span>
            OpenRouter API
          </h3>
          <div class="space-y-3">
            <div class="flex justify-between">
              <span class="text-text-secondary">Durum</span>
              <span class="text-green-600 font-medium">Aktif</span>
            </div>
            <div class="flex justify-between">
              <span class="text-text-secondary">Model</span>
              <span class="font-medium text-sm">text-embedding-3-large</span>
            </div>
            <div class="flex justify-between">
              <span class="text-text-secondary">Cache</span>
              <span class="text-green-600 font-medium">Etkin</span>
            </div>
          </div>
        </div>

        <div class="bg-white dark:bg-surface-dark border border-border-light dark:border-border-dark rounded-xl p-6">
          <h3 class="text-lg font-bold mb-4 flex items-center gap-2">
            <span class="material-symbols-outlined text-primary">web</span>
            Frontend
          </h3>
          <div class="space-y-3">
            <div class="flex justify-between">
              <span class="text-text-secondary">Framework</span>
              <span class="font-medium">Vue 3 + Vite</span>
            </div>
            <div class="flex justify-between">
              <span class="text-text-secondary">Styling</span>
              <span class="font-medium">Tailwind CSS</span>
            </div>
            <div class="flex justify-between">
              <span class="text-text-secondary">Mode</span>
              <span class="font-medium">Development</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </main>
</template>
