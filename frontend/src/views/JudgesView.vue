<template>
  <div class="w-full px-4 md:px-8 space-y-8 pb-20">
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <h1 class="text-3xl font-black text-slate-900 tracking-tight">Judges Management</h1>
        <p class="text-slate-500 font-medium mt-1">Manage LLM models used as automated judges for evaluation.</p>
      </div>

      <button
          @click="$router.push('/judges/create')"
          class="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2.5 rounded-xl shadow-lg shadow-blue-600/20 transition-all font-bold flex items-center text-sm"
      >
        <span class="mr-2">+</span>
        Add Judge
      </button>
    </div>

    <div class="bg-white rounded-[2.5rem] shadow-xl shadow-slate-200/50 border border-slate-100 overflow-hidden relative">
      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse">
          <thead>
          <tr class="bg-slate-50 text-slate-500 text-sm border-b border-slate-100">
            <th class="p-4 pl-8 font-semibold w-24">ID</th>
            <th class="p-4 font-semibold">Model Name</th>
            <th class="p-4 font-semibold">Created At</th>
            <th class="p-4 pr-8 font-semibold text-right">Actions</th>
          </tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
          <tr v-if="isLoading" class="text-center">
            <td colspan="4" class="py-12 text-slate-400 font-medium animate-pulse">Loading judges...</td>
          </tr>
          <tr v-else-if="judges.length === 0" class="text-center">
            <td colspan="4" class="py-12">
              <div class="text-4xl mb-3 opacity-50">⚖️</div>
              <h3 class="text-lg font-bold text-slate-700">No judges found</h3>
              <p class="text-slate-500 mt-1">Click "Add Judge" to register a new LLM evaluation model.</p>
            </td>
          </tr>
          <tr
              v-for="judge in judges"
              :key="judge.id"
              class="hover:bg-slate-50/50 transition-colors text-sm"
          >
            <td class="p-4 pl-8 font-mono font-bold text-slate-400">#{{ judge.id }}</td>
            <td class="p-4 font-bold text-slate-800">{{ judge.model_name }}</td>
            <td class="p-4 text-slate-600 font-medium">{{ formatDate(judge.created_at) }}</td>
            <td class="p-4 pr-8 text-right space-x-2">
              <button
                  @click="$router.push(`/judges/${judge.id}/edit`)"
                  class="px-3 py-1.5 text-xs font-bold text-blue-600 bg-blue-50 hover:bg-blue-100 rounded-lg transition-colors"
              >
                Edit
              </button>
              <button
                  @click="deleteJudge(judge)"
                  class="px-3 py-1.5 text-xs font-bold text-red-600 bg-red-50 hover:bg-red-100 rounded-lg transition-colors"
              >
                Delete
              </button>
            </td>
          </tr>
          </tbody>
        </table>
      </div>

      <div v-if="totalPages > 1" class="px-8 py-4 bg-slate-50/50 border-t border-slate-100 flex items-center justify-between">
        <div class="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em]">
          Page {{ currentPage }} / {{ totalPages }}
        </div>
        <div class="flex items-center gap-2">
          <button
              @click="fetchJudges(currentPage - 1)"
              :disabled="currentPage === 1"
              class="p-2 rounded-xl border border-slate-200 bg-white hover:bg-slate-50 disabled:opacity-30 disabled:cursor-not-allowed transition-all shadow-sm"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" /></svg>
          </button>

          <div class="flex items-center gap-1">
            <button
                v-for="p in visiblePages" :key="p"
                @click="fetchJudges(p)"
                class="w-8 h-8 rounded-lg text-[11px] font-black transition-all"
                :class="p === currentPage ? 'bg-blue-600 text-white shadow-lg shadow-blue-500/30' : 'bg-white border border-slate-100 text-slate-500 hover:bg-slate-50'"
            >
              {{ p }}
            </button>
          </div>

          <button
              @click="fetchJudges(currentPage + 1)"
              :disabled="currentPage === totalPages"
              class="p-2 rounded-xl border border-slate-200 bg-white hover:bg-slate-50 disabled:opacity-30 disabled:cursor-not-allowed transition-all shadow-sm"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" /></svg>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || ''

const judges = ref([])
const isLoading = ref(false)
const currentPage = ref(1)
const totalPages = ref(1)
const pageSize = 10

const getHeaders = () => {
  const token = localStorage.getItem('token')
  return token ? { 'Authorization': `Bearer ${token}` } : {}
}

const formatDate = (isoString) => {
  if (!isoString) return '—'
  const date = new Date(isoString)
  return date.toLocaleString('en-GB', {
    day: '2-digit', month: 'short', year: 'numeric',
    hour: '2-digit', minute: '2-digit'
  })
}

const visiblePages = computed(() => {
  const pages = []
  for (let i = 1; i <= totalPages.value; i++) {
    pages.push(i)
  }
  return pages
})

const fetchJudges = async (page = 1) => {
  isLoading.value = true
  try {
    const response = await axios.get(`${API_URL}/llm/judges/`, {
      params: { page, size: pageSize },
      headers: getHeaders()
    })
    judges.value = response.data.items
    currentPage.value = response.data.page
    totalPages.value = response.data.pages
  } catch (error) {
    console.error(error)
  } finally {
    isLoading.value = false
  }
}

const deleteJudge = async (judge) => {
  if (!confirm(`Are you sure you want to delete the judge "${judge.model_name}"?`)) return

  try {
    const response = await axios.delete(`${API_URL}/llm/judges/${judge.id}`, { headers: getHeaders() })

    if (response.status === 204 || response.data?.deleted === true) {
      judges.value = judges.value.filter(j => j.id !== judge.id)

      if (judges.value.length === 0 && currentPage.value > 1) {
        await fetchJudges(currentPage.value - 1)
      } else {
        await fetchJudges(currentPage.value)
      }
    } else {
      await fetchJudges(currentPage.value)
    }
  } catch (error) {
    alert(error.response?.data?.detail || "Failed to delete judge.")
  }
}

onMounted(() => {
  fetchJudges()
})
</script>