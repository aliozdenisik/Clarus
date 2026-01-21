<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";

const router = useRouter();
const query = ref("");
const searchMode = ref("semantic");
const source = ref("all");

const sources = [
  { value: "all", label: "Tümü", icon: "library_books" },
  { value: "ot", label: "Eski Ahit", icon: "history_edu" },
  { value: "nt", label: "Yeni Ahit", icon: "menu_book" },
  { value: "apocrypha", label: "Apokrif", icon: "auto_stories" },
  { value: "quran", label: "Kuran", icon: "book" },
];

function handleSearch() {
  if (query.value.trim()) {
    router.push({
      name: "Results",
      query: { q: query.value, mode: searchMode.value, source: source.value },
    });
  }
}
</script>

<template>
  <main class="flex-1 flex justify-center w-full px-4 md:px-6 py-8">
    <div class="w-full max-w-[900px]">
      <h1 class="text-3xl font-bold mb-8">Kutsal Metinlerde Ara</h1>

      <!-- Search Form -->
      <form @submit.prevent="handleSearch" class="space-y-6">
        <!-- Source Selection -->
        <div class="flex gap-3">
          <button
            v-for="s in sources"
            :key="s.value"
            type="button"
            @click="source = s.value"
            class="flex items-center gap-2 px-4 py-2 rounded border transition-all"
            :class="
              source === s.value
                ? 'border-primary bg-primary/10 text-primary'
                : 'border-border-light dark:border-border-dark text-text-secondary hover:border-primary'
            "
          >
            <span class="material-symbols-outlined text-lg">{{ s.icon }}</span>
            {{ s.label }}
          </button>
        </div>

        <!-- Search Input -->
        <div
          class="flex w-full items-stretch rounded-lg border border-border-light dark:border-border-dark bg-white dark:bg-surface-dark transition-colors focus-within:border-primary focus-within:ring-1 focus-within:ring-primary h-14"
        >
          <div
            class="flex items-center justify-center pl-4 text-text-secondary"
          >
            <span class="material-symbols-outlined text-2xl">search</span>
          </div>
          <input
            v-model="query"
            type="text"
            class="flex w-full min-w-0 flex-1 resize-none bg-transparent px-4 py-2 text-base font-normal placeholder:text-text-secondary focus:outline-none"
            placeholder="Sormak istediğiniz konuyu yazın..."
          />
          <div class="flex items-center justify-center pr-2">
            <button
              type="submit"
              class="flex items-center gap-2 rounded bg-primary px-5 py-2.5 text-sm font-bold text-white transition-all hover:bg-primary-hover"
            >
              <span class="material-symbols-outlined text-lg">send</span>
              Ara
            </button>
          </div>
        </div>

        <!-- Mode Toggle -->
        <div class="flex items-center gap-4">
          <span class="text-sm text-text-secondary">Arama modu:</span>
          <div class="inline-flex rounded bg-gray-100 dark:bg-surface-dark p-1">
            <label
              class="cursor-pointer flex items-center px-3 py-1.5 rounded text-sm font-medium transition-all"
              :class="
                searchMode === 'semantic'
                  ? 'bg-white dark:bg-border-dark text-primary shadow-sm'
                  : 'text-text-secondary'
              "
            >
              <input
                type="radio"
                v-model="searchMode"
                value="semantic"
                class="sr-only"
              />
              Semantik
            </label>
            <label
              class="cursor-pointer flex items-center px-3 py-1.5 rounded text-sm font-medium transition-all"
              :class="
                searchMode === 'keyword'
                  ? 'bg-white dark:bg-border-dark text-primary shadow-sm'
                  : 'text-text-secondary'
              "
            >
              <input
                type="radio"
                v-model="searchMode"
                value="keyword"
                class="sr-only"
              />
              Anahtar Kelime
            </label>
          </div>
        </div>
      </form>
    </div>
  </main>
</template>
