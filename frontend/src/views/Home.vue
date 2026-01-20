<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";

const router = useRouter();
const query = ref("");
const searchMode = ref("semantic");

const quickChips = [
  { icon: "schedule", label: "Zaman Kavramı" },
  { icon: "group", label: "Peygamberler" },
  { icon: "volunteer_activism", label: "Sadaka" },
  { icon: "restaurant", label: "Helal/Haram" },
];

function handleSearch() {
  if (query.value.trim()) {
    router.push({
      name: "Results",
      query: { q: query.value, mode: searchMode.value },
    });
  }
}

function searchChip(label) {
  query.value = label;
  handleSearch();
}
</script>

<template>
  <main
    class="flex flex-1 flex-col items-center justify-center px-4 py-12 sm:px-6 lg:px-8"
  >
    <div
      class="flex w-full max-w-[800px] flex-col items-center gap-10"
      v-motion
      :initial="{ opacity: 0, y: 20 }"
      :enter="{ opacity: 1, y: 0, transition: { duration: 500 } }"
    >
      <!-- Hero -->
      <div class="flex flex-col items-center gap-4 text-center">
        <div
          class="mb-2 flex h-16 w-16 items-center justify-center rounded-full bg-primary/10 text-primary"
        >
          <span
            class="material-symbols-outlined text-4xl"
            style="font-variation-settings: &quot;FILL&quot; 1"
            >auto_awesome</span
          >
        </div>
        <h1
          class="text-4xl font-black leading-tight tracking-tight sm:text-5xl lg:text-6xl"
        >
          Metinlerin bilgeliğini keşfet
        </h1>
        <p class="text-lg font-normal text-text-secondary sm:text-xl">
          Kuran, İncil ve Tevrat'ta sabır, yaratılış veya hukuk hakkında
          sorgula.
        </p>
      </div>

      <!-- Search -->
      <div class="w-full flex flex-col gap-4">
        <!-- Mode Toggle -->
        <div class="flex justify-center">
          <div class="inline-flex rounded bg-gray-200 dark:bg-surface-dark p-1">
            <label
              class="group relative flex cursor-pointer items-center justify-center rounded px-4 py-1.5 text-sm font-medium transition-all"
              :class="
                searchMode === 'semantic'
                  ? 'bg-white dark:bg-border-dark text-primary shadow-sm'
                  : 'text-text-secondary'
              "
            >
              <span class="mr-2 material-symbols-outlined text-lg"
                >psychology</span
              >
              <span>Semantik</span>
              <input
                type="radio"
                v-model="searchMode"
                value="semantic"
                class="invisible absolute w-0"
              />
            </label>
            <label
              class="group relative flex cursor-pointer items-center justify-center rounded px-4 py-1.5 text-sm font-medium transition-all"
              :class="
                searchMode === 'keyword'
                  ? 'bg-white dark:bg-border-dark text-primary shadow-sm'
                  : 'text-text-secondary'
              "
            >
              <span class="mr-2 material-symbols-outlined text-lg"
                >find_in_page</span
              >
              <span>Anahtar Kelime</span>
              <input
                type="radio"
                v-model="searchMode"
                value="keyword"
                class="invisible absolute w-0"
              />
            </label>
          </div>
        </div>

        <!-- Search Input -->
        <form
          @submit.prevent="handleSearch"
          class="relative flex w-full shadow-sm"
        >
          <div
            class="flex w-full items-stretch rounded border border-border-light dark:border-border-dark bg-white dark:bg-surface-dark transition-colors focus-within:border-primary focus-within:ring-1 focus-within:ring-primary h-16"
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
              placeholder="Affetme hakkında metin ne diyor?"
            />
            <div class="flex items-center justify-center pr-2">
              <button
                type="submit"
                class="flex min-w-[100px] cursor-pointer items-center justify-center gap-2 rounded bg-primary px-5 py-2.5 text-sm font-bold text-white transition-all hover:bg-primary-hover hover:-translate-y-0.5 active:translate-y-0"
              >
                <span>Ara</span>
              </button>
            </div>
          </div>
        </form>

        <!-- Quick Chips -->
        <div class="mt-2 flex flex-wrap justify-center gap-3">
          <button
            v-for="chip in quickChips"
            :key="chip.label"
            @click="searchChip(chip.label)"
            class="flex items-center gap-2 rounded border border-border-light dark:border-border-dark bg-white dark:bg-surface-dark px-4 py-2 text-sm font-medium text-text-secondary transition-all hover:border-primary hover:text-primary hover:-translate-y-0.5"
          >
            <span class="material-symbols-outlined text-lg">{{
              chip.icon
            }}</span>
            {{ chip.label }}
          </button>
        </div>
      </div>
    </div>
  </main>
</template>
