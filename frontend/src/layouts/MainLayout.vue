<template>
  <div class="flex h-screen bg-slate-50 overflow-hidden">

    <Sidebar />

    <div class="flex-1 flex flex-col h-screen overflow-hidden">

      <Header />

      <main class="flex-1 overflow-y-auto p-6 lg:p-8">
        <router-view />
      </main>

    </div>
  </div>
</template>

<script setup>
import Sidebar from '@/components/AppSidebar.vue'
import Header from '@/components/AppHeader.vue'
</script>