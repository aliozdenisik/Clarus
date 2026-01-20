<script setup>
import { RouterView } from "vue-router";
import AppHeader from "./components/AppHeader.vue";
</script>

<template>
  <div
    class="min-h-screen bg-background-light dark:bg-background-dark text-text-main dark:text-white font-display"
  >
    <AppHeader />
    <RouterView />
  </div>
</template>
