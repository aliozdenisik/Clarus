<script setup>
import { ref } from "vue";
import { useStreaming } from "../composables/useStreaming";

const { text, isStreaming, status, error, startStream, stopStream } = useStreaming();
const topic = ref("");

function handleCompare() {
  if (topic.value.trim()) {
    startStream(`/api/stream/compare?topic=${encodeURIComponent(topic.value)}`);
  }
}

// Export as Markdown
function exportMarkdown() {
  const markdown = `# Karşılaştırmalı Analiz: ${topic.value}\n\n${text.value.replace(/\\n/g, '\n')}\n\n---\n*Holly Search ile oluşturuldu*`;
  const blob = new Blob([markdown], { type: 'text/markdown' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `karsilastirma-${topic.value.toLowerCase().replace(/\s+/g, '-')}.md`;
  a.click();
  URL.revokeObjectURL(url);
}

// Copy to clipboard
async function copyToClipboard() {
  try {
    await navigator.clipboard.writeText(text.value.replace(/\\n/g, '\n'));
    alert('Panoya kopyalandı!');
  } catch (err) {
    alert('Kopyalama başarısız oldu');
  }
}

// Share (Web Share API)
async function shareResult() {
  if (navigator.share) {
    try {
      await navigator.share({
        title: `Karşılaştırmalı Analiz: ${topic.value}`,
        text: text.value.replace(/\\n/g, '\n').substring(0, 500) + '...',
        url: window.location.href
      });
    } catch (err) {
      // User cancelled share
    }
  } else {
    copyToClipboard();
  }
}
</script>

<template>
  <main class="flex-1 w-full px-4 md:px-6 py-8">
    <div class="max-w-[1200px] mx-auto">
      <h1 class="text-3xl font-bold mb-2">Karşılaştırmalı Analiz</h1>
      <p class="text-text-secondary mb-8">
        Bir konuyu Kuran, İncil ve Tevrat perspektifinden karşılaştırın.
      </p>

      <!-- Search -->
      <div class="flex gap-3 mb-8">
        <input
          v-model="topic"
          type="text"
          class="flex-1 rounded-lg border border-border-light dark:border-border-dark bg-white dark:bg-surface-dark px-4 py-3 text-base placeholder:text-text-secondary focus:border-primary focus:ring-1 focus:ring-primary"
          placeholder="Karşılaştırmak istediğiniz konuyu yazın... (örn: Yaratılış)"
          @keyup.enter="handleCompare"
        />
        <button
          @click="handleCompare"
          :disabled="isStreaming"
          class="flex items-center gap-2 rounded-lg bg-primary px-6 py-3 text-sm font-bold text-white transition-all hover:bg-primary-hover disabled:opacity-50"
        >
          <span class="material-symbols-outlined">compare</span>
          Karşılaştır
        </button>
      </div>

      <!-- Loading - Modern Skeleton -->
      <div
        v-if="isStreaming && !text"
        class="bg-white dark:bg-surface-dark rounded-xl border border-border-light dark:border-border-dark p-6 md:p-8"
      >
        <div class="flex items-center gap-3 mb-6">
          <div class="ai-thinking">
            <span class="dot"></span>
            <span class="dot"></span>
            <span class="dot"></span>
          </div>
          <span class="text-primary font-medium">Metinler karşılaştırılıyor...</span>
        </div>
        <!-- Multi-column skeleton for compare -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div class="space-y-3">
            <div class="skeleton-line w-1/3 h-5"></div>
            <div class="skeleton-line w-full"></div>
            <div class="skeleton-line w-11/12"></div>
            <div class="skeleton-line w-4/5"></div>
          </div>
          <div class="space-y-3">
            <div class="skeleton-line w-1/3 h-5"></div>
            <div class="skeleton-line w-full"></div>
            <div class="skeleton-line w-10/12"></div>
            <div class="skeleton-line w-3/4"></div>
          </div>
        </div>
      </div>

      <!-- Error -->
      <div
        v-if="error"
        class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 mb-8"
      >
        <p class="text-red-600 dark:text-red-400">{{ error }}</p>
      </div>

      <!-- Results -->
      <div
        v-if="text"
        class="bg-white dark:bg-surface-dark rounded-xl border border-border-light dark:border-border-dark p-6 md:p-8"
      >
        <div class="prose dark:prose-invert max-w-none">
          <div
            v-html="
              text
                .replace(/\\n/g, '<br>')
                .replace(
                  /## /g,
                  '<h3 class=&quot;text-lg font-bold text-primary mt-6 mb-2&quot;>',
                )
            "
          ></div>
          <span v-if="isStreaming" class="animate-blink">█</span>
        </div>

        <div
          v-if="isStreaming"
          class="mt-6 pt-4 border-t border-border-light dark:border-border-dark"
        >
          <button
            @click="stopStream"
            class="flex items-center gap-1 px-3 py-1.5 text-sm text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 rounded transition-colors"
          >
            <span class="material-symbols-outlined text-lg">stop</span>
            Durdur
          </button>
        </div>

        <!-- Export Actions -->
        <div
          v-if="text && !isStreaming"
          class="mt-6 pt-4 border-t border-border-light dark:border-border-dark flex flex-wrap gap-2"
        >
          <button
            @click="exportMarkdown"
            class="flex items-center gap-1 px-3 py-1.5 text-sm bg-primary/10 text-primary hover:bg-primary/20 rounded transition-colors"
          >
            <span class="material-symbols-outlined text-lg">download</span>
            İndir (.md)
          </button>
          <button
            @click="copyToClipboard"
            class="flex items-center gap-1 px-3 py-1.5 text-sm bg-gray-100 dark:bg-gray-800 text-text-secondary hover:bg-gray-200 dark:hover:bg-gray-700 rounded transition-colors"
          >
            <span class="material-symbols-outlined text-lg">content_copy</span>
            Kopyala
          </button>
          <button
            @click="shareResult"
            class="flex items-center gap-1 px-3 py-1.5 text-sm bg-gray-100 dark:bg-gray-800 text-text-secondary hover:bg-gray-200 dark:hover:bg-gray-700 rounded transition-colors"
          >
            <span class="material-symbols-outlined text-lg">share</span>
            Paylaş
          </button>
        </div>
      </div>
    </div>
  </main>
</template>
