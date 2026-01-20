<script setup>
import { computed } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "../stores/auth";

const router = useRouter();
const authStore = useAuthStore();

const isAuthenticated = computed(() => authStore.isAuthenticated);
const user = computed(() => authStore.user);

function logout() {
  authStore.logout();
  router.push("/login");
}
</script>

<template>
  <header
    class="sticky top-0 z-50 flex items-center justify-between border-b border-border-light dark:border-border-dark bg-white/90 dark:bg-background-dark/90 backdrop-blur-md px-6 py-4 lg:px-10"
  >
    <!-- Logo -->
    <router-link to="/" class="flex items-center gap-3 cursor-pointer">
      <div class="flex items-center justify-center text-primary">
        <span class="material-symbols-outlined text-3xl">menu_book</span>
      </div>
      <h2 class="text-xl font-bold tracking-tight">Holly Search</h2>
    </router-link>

    <!-- Navigation -->
    <div class="flex items-center gap-6">
      <template v-if="isAuthenticated">
        <router-link
          to="/search"
          class="hidden md:flex items-center gap-2 text-text-secondary hover:text-primary transition-colors text-sm font-medium"
        >
          <span class="material-symbols-outlined text-xl">search</span>
          <span>Arama</span>
        </router-link>

        <router-link
          to="/compare"
          class="hidden md:flex items-center gap-2 text-text-secondary hover:text-primary transition-colors text-sm font-medium"
        >
          <span class="material-symbols-outlined text-xl">compare</span>
          <span>Karşılaştır</span>
        </router-link>

        <div
          class="h-6 w-px bg-border-light dark:bg-border-dark hidden md:block"
        ></div>

        <div class="flex items-center gap-3">
          <span class="text-sm text-text-secondary hidden md:block">{{
            user?.name
          }}</span>
          <button
            @click="logout"
            class="flex items-center gap-2 text-text-secondary hover:text-red-500 transition-colors text-sm"
          >
            <span class="material-symbols-outlined text-xl">logout</span>
          </button>
        </div>
      </template>

      <template v-else>
        <router-link
          to="/login"
          class="text-sm font-medium text-text-secondary hover:text-primary transition-colors"
        >
          Giriş Yap
        </router-link>
        <router-link
          to="/register"
          class="flex items-center justify-center rounded bg-primary px-4 py-2 text-sm font-bold text-white transition-all hover:bg-primary-hover hover:-translate-y-0.5"
        >
          Kayıt Ol
        </router-link>
      </template>
    </div>
  </header>
</template>
