<script setup>
import { ref } from "vue";
import { useStreaming } from "../composables/useStreaming";

const { text, isStreaming, status, startStream, stopStream } = useStreaming();
const topic = ref("");

function handleCompare() {
  if (topic.value.trim()) {
    startStream(`/api/stream/compare?topic=${encodeURIComponent(topic.value)}`);
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

      <!-- Loading -->
      <div
        v-if="status === 'analyzing'"
        class="flex items-center justify-center py-12"
      >
        <div class="flex items-center gap-3 text-text-secondary">
          <div class="flex gap-1">
            <span
              class="w-2 h-2 bg-primary rounded-full animate-bounce"
              style="animation-delay: 0ms"
            ></span>
            <span
              class="w-2 h-2 bg-primary rounded-full animate-bounce"
              style="animation-delay: 150ms"
            ></span>
            <span
              class="w-2 h-2 bg-primary rounded-full animate-bounce"
              style="animation-delay: 300ms"
            ></span>
          </div>
          <span>Metinler analiz ediliyor...</span>
        </div>
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
      </div>
    </div>
  </main>
</template>
