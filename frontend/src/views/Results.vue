<script setup>
import { ref, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useStreaming } from "../composables/useStreaming";

const route = useRoute();
const router = useRouter();
const {
  text,
  isStreaming,
  status,
  error,
  citations,
  metadata,
  startStream,
  stopStream,
} = useStreaming();

const query = ref("");
const showCursor = ref(true);

onMounted(() => {
  query.value = route.query.q || "";
  if (query.value) {
    const source = route.query.source || "quran";
    startStream(
      `/api/stream/search?q=${encodeURIComponent(query.value)}&source=${source}`,
    );
  }
});

function handleNewSearch() {
  router.push("/");
}

function handleRegenerate() {
  const source = route.query.source || "quran";
  startStream(
    `/api/stream/search?q=${encodeURIComponent(query.value)}&source=${source}`,
  );
}

// Export as Markdown
function exportMarkdown() {
  const markdown = `# Arama: ${query.value}\n\n${text.value}\n\n---\n*Holly Search ile oluşturuldu*`;
  const blob = new Blob([markdown], { type: 'text/markdown' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `arama-${query.value.toLowerCase().replace(/\s+/g, '-')}.md`;
  a.click();
  URL.revokeObjectURL(url);
}

// Copy to clipboard
async function copyToClipboard() {
  try {
    await navigator.clipboard.writeText(text.value);
    alert('Panoya kopyalandı!');
  } catch (err) {
    alert('Kopyalama başarısız oldu');
  }
}
</script>

<template>
  <main class="flex-1 flex justify-center w-full px-4 md:px-0 py-8">
    <div class="flex flex-col w-full max-w-[800px] gap-8">
      <!-- Search Bar -->
      <div class="w-full">
        <div
          class="flex w-full items-stretch rounded-lg h-12 shadow-sm ring-1 ring-border-light dark:ring-border-dark bg-background-light dark:bg-surface-dark overflow-hidden"
        >
          <div
            class="text-text-secondary flex items-center justify-center pl-4 pr-2"
          >
            <span class="material-symbols-outlined">search</span>
          </div>
          <input
            v-model="query"
            readonly
            class="flex w-full flex-1 bg-transparent border-none text-text-main dark:text-white placeholder:text-text-secondary focus:ring-0 px-2 text-base"
          />
          <div class="flex items-center justify-center pr-2">
            <button
              @click="handleNewSearch"
              class="p-1 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-full transition-colors"
            >
              <span class="material-symbols-outlined text-text-secondary"
                >close</span
              >
            </button>
          </div>
        </div>
      </div>

      <!-- AI Response -->
      <div
        class="flex flex-col bg-background-light dark:bg-surface-dark rounded-xl p-6 md:p-8 border border-border-light dark:border-border-dark"
        v-motion
        :initial="{ opacity: 0, y: 10 }"
        :enter="{ opacity: 1, y: 0, transition: { duration: 400 } }"
      >
        <!-- Header -->
        <div class="flex items-center gap-3 mb-6">
          <div
            class="flex items-center justify-center size-8 rounded-full bg-primary/10 text-primary"
          >
            <span class="material-symbols-outlined text-lg">auto_awesome</span>
          </div>
          <h2 class="text-xl font-bold">Bütünleşik Yorum</h2>
        </div>

        <!-- Status - Modern Loading -->
        <div
          v-if="status === 'connecting' || status === 'searching'"
          class="mb-5"
        >
          <div class="flex items-center gap-3 mb-4">
            <div class="ai-thinking">
              <span class="dot"></span>
              <span class="dot"></span>
              <span class="dot"></span>
            </div>
            <span class="text-primary font-medium">Kutsal metinlerde aranıyor...</span>
          </div>
          <!-- Skeleton Lines -->
          <div class="space-y-3">
            <div class="skeleton-line w-full"></div>
            <div class="skeleton-line w-11/12"></div>
            <div class="skeleton-line w-4/5"></div>
            <div class="skeleton-line w-3/4"></div>
          </div>
        </div>

        <div
          v-if="status === 'generating'"
          class="mb-5"
        >
          <div class="flex items-center gap-3 mb-4">
            <span class="material-symbols-outlined text-emerald-500 animate-pulse text-2xl">auto_awesome</span>
            <span class="text-emerald-600 font-medium">Yanıt oluşturuluyor...</span>
          </div>
        </div>

        <!-- Content -->
        <div
          class="bg-white dark:bg-background-dark border border-border-light dark:border-border-dark rounded-lg p-6 shadow-sm"
        >
          <div class="prose dark:prose-invert max-w-none">
            <p class="whitespace-pre-wrap">
              {{ text }}
            </p>
          </div>

          <!-- Error -->
          <div
            v-if="error"
            class="mt-4 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded text-red-600 text-sm"
          >
            {{ error }}
          </div>
        </div>

        <!-- Controls -->
        <div
          class="mt-6 pt-4 border-t border-border-light dark:border-border-dark flex justify-between items-center"
        >
          <p class="text-text-secondary text-xs uppercase tracking-wide">
            Bu kısım yapay zeka tarafından oluşturulmuştur.
          </p>
          <div class="flex gap-2">
            <button
              v-if="isStreaming"
              @click="stopStream"
              class="flex items-center gap-1 px-3 py-1.5 text-sm text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 rounded transition-colors"
            >
              <span class="material-symbols-outlined text-lg">stop</span>
              Durdur
            </button>
            <button
              v-else
              @click="handleRegenerate"
              class="flex items-center gap-1 px-3 py-1.5 text-sm text-primary hover:bg-primary/10 rounded transition-colors"
            >
              <span class="material-symbols-outlined text-lg">refresh</span>
              Yeniden Oluştur
            </button>
            <button
              v-if="text && !isStreaming"
              @click="exportMarkdown"
              class="flex items-center gap-1 px-3 py-1.5 text-sm bg-primary/10 text-primary hover:bg-primary/20 rounded transition-colors"
            >
              <span class="material-symbols-outlined text-lg">download</span>
              İndir
            </button>
            <button
              v-if="text && !isStreaming"
              @click="copyToClipboard"
              class="flex items-center gap-1 px-3 py-1.5 text-sm bg-gray-100 dark:bg-gray-800 text-text-secondary hover:bg-gray-200 dark:hover:bg-gray-700 rounded transition-colors"
            >
              <span class="material-symbols-outlined text-lg">content_copy</span>
              Kopyala
            </button>
          </div>
        </div>
      </div>
    </div>
  </main>
</template>
