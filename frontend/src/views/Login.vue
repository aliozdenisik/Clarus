<script setup>
import { ref } from "vue";
import { useRouter, useRoute } from "vue-router";
import { useAuthStore } from "../stores/auth";

const router = useRouter();
const route = useRoute();
const authStore = useAuthStore();

const email = ref("");
const password = ref("");
const isLoading = ref(false);
const error = ref("");

async function handleLogin() {
  isLoading.value = true;
  error.value = "";

  try {
    await authStore.login(email.value, password.value);
    const redirect = route.query.redirect || "/search";
    router.push(redirect);
  } catch (err) {
    error.value = err.message;
  } finally {
    isLoading.value = false;
  }
}
</script>

<template>
  <main class="flex-grow flex items-center justify-center p-4 sm:p-6 lg:p-8">
    <div
      class="w-full max-w-[440px] bg-white dark:bg-surface-dark shadow-lg border border-border-light dark:border-border-dark rounded-sm overflow-hidden p-8 sm:p-10 transition-all duration-300 hover:shadow-xl"
      v-motion
      :initial="{ opacity: 0, scale: 0.95 }"
      :enter="{ opacity: 1, scale: 1, transition: { duration: 300 } }"
    >
      <!-- Header -->
      <div class="text-center mb-8">
        <h2 class="text-3xl font-bold tracking-tight mb-2">Giriş Yap</h2>
        <p class="text-text-secondary text-sm">
          Holly Search'ün derinliklerine hoş geldiniz.
        </p>
      </div>

      <!-- Error -->
      <div
        v-if="error"
        class="mb-4 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded text-red-600 dark:text-red-400 text-sm"
      >
        {{ error }}
      </div>

      <!-- Form -->
      <form @submit.prevent="handleLogin" class="space-y-5">
        <div>
          <label class="block text-sm font-medium mb-1.5" for="email"
            >E-posta</label
          >
          <input
            v-model="email"
            type="email"
            id="email"
            required
            class="block w-full rounded-sm border border-border-light dark:border-border-dark bg-white dark:bg-background-dark py-3 px-4 placeholder:text-text-secondary focus:border-primary focus:ring-1 focus:ring-primary transition-colors text-sm"
            placeholder="ad@domain.com"
          />
        </div>

        <div>
          <div class="flex items-center justify-between mb-1.5">
            <label class="block text-sm font-medium" for="password"
              >Şifre</label
            >
            <a
              href="#"
              class="text-xs font-medium text-primary hover:text-primary-hover transition-colors"
              >Şifremi Unuttum?</a
            >
          </div>
          <input
            v-model="password"
            type="password"
            id="password"
            required
            class="block w-full rounded-sm border border-border-light dark:border-border-dark bg-white dark:bg-background-dark py-3 px-4 placeholder:text-text-secondary focus:border-primary focus:ring-1 focus:ring-primary transition-colors text-sm"
            placeholder="••••••••"
          />
        </div>

        <button
          type="submit"
          :disabled="isLoading"
          class="w-full flex justify-center py-3 px-4 rounded-sm text-sm font-semibold text-white bg-primary hover:bg-primary-hover hover:-translate-y-0.5 active:translate-y-0 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {{ isLoading ? "Giriş yapılıyor..." : "GİRİŞ YAP" }}
        </button>
      </form>

      <!-- Divider -->
      <div class="relative mt-8 mb-6">
        <div class="absolute inset-0 flex items-center">
          <div
            class="w-full border-t border-border-light dark:border-border-dark"
          ></div>
        </div>
        <div class="relative flex justify-center text-sm">
          <span class="px-2 bg-white dark:bg-surface-dark text-text-secondary"
            >veya şununla devam et</span
          >
        </div>
      </div>

      <!-- Social Login -->
      <div class="grid grid-cols-2 gap-3">
        <button
          type="button"
          class="flex items-center justify-center w-full px-4 py-2.5 border border-border-light dark:border-border-dark rounded-sm bg-white dark:bg-background-dark text-sm font-medium hover:bg-gray-50 dark:hover:bg-gray-800 transition-all"
        >
          <svg class="h-5 w-5 mr-2" viewBox="0 0 24 24">
            <path
              d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
              fill="#4285F4"
            />
            <path
              d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
              fill="#34A853"
            />
            <path
              d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
              fill="#FBBC05"
            />
            <path
              d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
              fill="#EA4335"
            />
          </svg>
          Google
        </button>
        <button
          type="button"
          class="flex items-center justify-center w-full px-4 py-2.5 border border-border-light dark:border-border-dark rounded-sm bg-white dark:bg-background-dark text-sm font-medium hover:bg-gray-50 dark:hover:bg-gray-800 transition-all"
        >
          <svg class="h-5 w-5 mr-2" fill="currentColor" viewBox="0 0 24 24">
            <path
              d="M17.05 20.28c-.98.95-2.05.88-3.08.35-1.09-.46-2.09-.48-3.24 0-1.44.62-2.2.44-3.06-.35C2.79 15.25 3.51 7.59 9.05 7.31c1.35.07 2.29.74 3.08.8 1.18-.24 2.31-.93 3.57-.84 1.51.12 2.65.77 3.4 1.86-3.04 1.83-2.52 6.09.56 7.31-.24.75-.54 1.72-1.06 2.67-.52.93-1.07 1.86-1.55 1.17zm-4.32-15.3c.3.93-.8 2.08-1.74 2.06-1.12.08-2.31-1.07-2.06-2.37.05-1.11 1.56-2.06 2.45-1.89.84.05 1.16 1.48 1.35 2.2z"
            />
          </svg>
          Apple
        </button>
      </div>

      <!-- Footer -->
      <p class="mt-8 text-center text-sm text-text-secondary">
        Hesabın yok mu?
        <router-link
          to="/register"
          class="font-semibold text-primary hover:text-primary-hover hover:underline transition-all"
          >Kayıt Ol</router-link
        >
      </p>
    </div>
  </main>
</template>
