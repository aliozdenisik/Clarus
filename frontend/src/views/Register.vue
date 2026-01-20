<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "../stores/auth";

const router = useRouter();
const authStore = useAuthStore();

const name = ref("");
const email = ref("");
const password = ref("");
const acceptTerms = ref(false);
const isLoading = ref(false);
const error = ref("");

async function handleRegister() {
  if (!acceptTerms.value) {
    error.value = "Kullanım koşullarını kabul etmeniz gerekiyor.";
    return;
  }

  isLoading.value = true;
  error.value = "";

  try {
    await authStore.register(name.value, email.value, password.value);
    router.push("/search");
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
      class="w-full max-w-[440px] bg-white dark:bg-surface-dark shadow-lg border border-border-light dark:border-border-dark rounded-sm overflow-hidden p-8 sm:p-10"
      v-motion
      :initial="{ opacity: 0, scale: 0.95 }"
      :enter="{ opacity: 1, scale: 1, transition: { duration: 300 } }"
    >
      <div class="text-center mb-8">
        <h2 class="text-3xl font-bold tracking-tight mb-2">
          Hesabınızı Oluşturun
        </h2>
        <p class="text-text-secondary text-sm">
          Kutsal metinleri keşfetmeye ve öğrenmeye başlayın.
        </p>
      </div>

      <div
        v-if="error"
        class="mb-4 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded text-red-600 dark:text-red-400 text-sm"
      >
        {{ error }}
      </div>

      <form @submit.prevent="handleRegister" class="space-y-5">
        <div>
          <label class="block text-sm font-medium mb-1.5" for="name"
            >Ad Soyad</label
          >
          <input
            v-model="name"
            type="text"
            id="name"
            required
            class="block w-full rounded-sm border border-border-light dark:border-border-dark bg-white dark:bg-background-dark py-3 px-4 placeholder:text-text-secondary focus:border-primary focus:ring-1 focus:ring-primary transition-colors text-sm"
            placeholder="Adınız ve Soyadınız"
          />
        </div>

        <div>
          <label class="block text-sm font-medium mb-1.5" for="email"
            >E-posta Adresi</label
          >
          <input
            v-model="email"
            type="email"
            id="email"
            required
            class="block w-full rounded-sm border border-border-light dark:border-border-dark bg-white dark:bg-background-dark py-3 px-4 placeholder:text-text-secondary focus:border-primary focus:ring-1 focus:ring-primary transition-colors text-sm"
            placeholder="isim@ornek.com"
          />
        </div>

        <div>
          <label class="block text-sm font-medium mb-1.5" for="password"
            >Şifre</label
          >
          <input
            v-model="password"
            type="password"
            id="password"
            required
            minlength="8"
            class="block w-full rounded-sm border border-border-light dark:border-border-dark bg-white dark:bg-background-dark py-3 px-4 placeholder:text-text-secondary focus:border-primary focus:ring-1 focus:ring-primary transition-colors text-sm"
            placeholder="••••••••"
          />
          <p class="mt-1 text-xs text-text-secondary">
            En az 8 karakter olmalıdır.
          </p>
        </div>

        <div class="flex items-start gap-2">
          <input
            v-model="acceptTerms"
            type="checkbox"
            id="terms"
            class="mt-1 rounded border-border-light text-primary focus:ring-primary"
          />
          <label for="terms" class="text-sm text-text-secondary">
            <a href="#" class="text-primary hover:underline"
              >Kullanım Koşullarını</a
            >
            ve
            <a href="#" class="text-primary hover:underline"
              >Gizlilik Politikasını</a
            >
            okudum ve kabul ediyorum.
          </label>
        </div>

        <button
          type="submit"
          :disabled="isLoading"
          class="w-full flex justify-center py-3 px-4 rounded-sm text-sm font-semibold text-white bg-primary hover:bg-primary-hover hover:-translate-y-0.5 active:translate-y-0 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary transition-all duration-200 disabled:opacity-50"
        >
          {{ isLoading ? "Kaydediliyor..." : "Kayıt Ol" }}
        </button>
      </form>

      <p class="mt-8 text-center text-sm text-text-secondary">
        Zaten hesabınız var mı?
        <router-link
          to="/login"
          class="font-semibold text-primary hover:text-primary-hover hover:underline transition-all"
          >Giriş Yap</router-link
        >
      </p>
    </div>
  </main>
</template>
