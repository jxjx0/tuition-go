<script setup lang="ts">
import Navbar from './components/Navbar.vue'
import Footer from './components/Footer.vue'
</script>

<template>
  <div class="min-h-screen flex flex-col" style="background-color:#F5F7FA;color:#1B3A5C;font-family:'Geist','Geist Fallback',-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif">
    <Navbar />
    <main class="flex-1">
      <router-view />
    </main>
    <Footer />
  </div>
</template>
