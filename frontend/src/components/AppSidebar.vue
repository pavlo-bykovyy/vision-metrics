<template>
  <aside class="w-72 bg-[#0F172A] text-slate-400 flex flex-col border-r border-slate-800 h-screen sticky top-0">
    <div class="h-20 flex items-center px-8 shrink-0">
      <div class="w-8 h-8 bg-blue-500 rounded-lg flex items-center justify-center mr-3 shadow-lg shadow-blue-500/30">
        <span class="text-white font-bold text-lg">V</span>
      </div>
      <span class="text-white font-bold tracking-wider uppercase text-sm text-white">VisionMetrics</span>
    </div>

    <nav class="flex-1 px-4 py-6 space-y-8 overflow-y-auto">

      <div class="space-y-1">
        <router-link to="/" class="nav-link">
          <span class="mr-3">📊</span> Dashboard
        </router-link>
      </div>

      <!-- CV Section -->
      <div>
        <p class="px-4 text-[10px] font-black text-slate-500 uppercase tracking-[0.2em] mb-4">CV</p>
        <div class="space-y-1">
          <router-link to="/models" class="nav-link">
            <span class="mr-3">🧠</span> AI Models
          </router-link>
          <router-link to="/evaluations" class="nav-link">
            <span class="mr-3">📈</span> Evaluations
          </router-link>
        </div>
      </div>

      <!-- Datasets Section -->
      <div>
        <p class="px-4 text-[10px] font-black text-slate-500 uppercase tracking-[0.2em] mb-4">Datasets</p>
        <div class="space-y-1">
          <router-link to="/datasets" class="nav-link">
            <span class="mr-3">📂</span> Datasets
          </router-link>
        </div>
      </div>

      <!-- Base Section -->
      <div>
        <p class="px-4 text-[10px] font-black text-slate-500 uppercase tracking-[0.2em] mb-4">Base</p>
        <div class="space-y-1">
          <router-link to="/base-model-tasks" class="nav-link">
            <span class="mr-3">📦</span> Test Base Model
          </router-link>
        </div>
      </div>

      <!-- LoRA Section -->
      <div>
        <p class="px-4 text-[10px] font-black text-slate-500 uppercase tracking-[0.2em] mb-4">LoRA</p>
        <div class="space-y-1">
          <router-link to="/lora-adapters" class="nav-link">
            <span class="mr-3">🔌</span> LoRA Adapters
          </router-link>
          <router-link to="/test-lora" class="nav-link">
            <span class="mr-3">💬</span> Test LoRA
          </router-link>
          <router-link to="/lora-tasks" class="nav-link">
            <span class="mr-3">📋</span> LoRA Tasks
          </router-link>
          <router-link to="/active-models" class="nav-link">
            <span class="mr-3">🚀</span> LoRA Active Models
          </router-link>
        </div>
      </div>

      <!-- Judges Section -->
      <div>
        <p class="px-4 text-[10px] font-black text-slate-500 uppercase tracking-[0.2em] mb-4">Judges</p>
        <div class="space-y-1">
          <router-link to="/judges" class="nav-link">
            <span class="mr-3">🧑‍⚖️</span> Judges
          </router-link>
          <router-link to="/judge-tasks" class="nav-link">
            <span class="mr-3">📋</span> Judge Tasks
          </router-link>
        </div>
      </div>

      <!-- API Section -->
      <div>
        <p class="px-4 text-[10px] font-black text-slate-500 uppercase tracking-[0.2em] mb-4">API</p>
        <div class="space-y-1">
          <router-link to="/api-docs" class="nav-link">
            <span class="mr-3">📖</span> API Docs
          </router-link>
        </div>
      </div>

<!--      <div>-->
<!--        <p class="px-4 text-[10px] font-black text-slate-500 uppercase tracking-[0.2em] mb-4">Management</p>-->
<!--        <div class="space-y-1">-->
<!--          <router-link to="/users" class="nav-link">-->
<!--            <span class="mr-3">👥</span> Users-->
<!--          </router-link>-->
<!--          <router-link to="/settings" class="nav-link">-->
<!--            <span class="mr-3">⚙️</span> Settings-->
<!--          </router-link>-->
<!--        </div>-->
<!--      </div>-->
    </nav>

    <div class="p-4 border-t border-slate-800 shrink-0 mt-auto">
      <button
          @click="handleLogout"
          class="w-full flex items-center px-4 py-3 rounded-xl text-slate-400 hover:bg-red-500/10 hover:text-red-500 transition-all duration-200 font-medium text-sm group"
      >
        <svg
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            stroke-width="2"
            stroke="currentColor"
            class="w-5 h-5 mr-3 transition-transform group-hover:-translate-x-1"
        >
          <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 9V5.25A2.25 2.25 0 0013.5 3h-6a2.25 2.25 0 00-2.25 2.25v13.5A2.25 2.25 0 007.5 21h6a2.25 2.25 0 002.25-2.25V15M12 9l-3 3m0 0l3 3m-3-3h12.75" />
        </svg>
        Logout
      </button>
    </div>
  </aside>
</template>

<script setup>
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()

const handleLogout = () => {
  localStorage.removeItem('token')

  delete axios.defaults.headers.common['Authorization']

  router.push('/login')
}
</script>

<style scoped>
@reference "@/assets/main.css";

.nav-link {
  @apply flex items-center px-4 py-2.5 rounded-xl transition-all duration-200 hover:bg-slate-800 hover:text-white font-medium text-sm;
}

.router-link-exact-active {
  @apply bg-blue-600 text-white shadow-lg shadow-blue-500/20;
}
</style>