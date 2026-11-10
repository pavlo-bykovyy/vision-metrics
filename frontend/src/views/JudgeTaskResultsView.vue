<template>
  <div class="space-y-8 pb-12 mt-8">

    <!-- Header Section -->
    <div class="flex items-center justify-between mb-6">
      <div>
        <button @click="$router.push('/judge-tasks')" class="text-sm font-bold text-slate-500 hover:text-slate-800 flex items-center gap-2 mb-2">
          <span>&larr;</span> Back to Judge Tasks
        </button>

        <h1 class="text-3xl font-black text-slate-900 tracking-tight flex items-center gap-3">
          {{ runDetails?.name || `Judge Run #${runId}` }}
          <span v-if="runDetails?.name" class="text-sm font-bold text-slate-400 bg-slate-100 px-2 py-1 rounded-lg">#{{ runId }}</span>
          <span v-if="runDetails?.status" class="text-xs font-bold text-slate-500 bg-slate-100 px-2 py-1 rounded-lg uppercase">{{ runDetails.status }}</span>
        </h1>

        <p class="text-slate-500 font-medium mt-2 max-w-3xl">
          {{ runDetails?.description || 'Review the judge scores and reasoning for this run.' }}
        </p>
      </div>
    </div>

    <!-- Error Banner -->
    <div v-if="detailsError || resultsError" class="bg-red-50 border border-red-100 text-red-600 text-sm font-medium rounded-2xl px-6 py-4">
      {{ detailsError || resultsError }}
    </div>
    <div v-if="runDetails?.error_message" class="bg-red-50 border border-red-100 text-red-600 text-sm font-medium rounded-2xl px-6 py-4 whitespace-pre-wrap">
      {{ runDetails.error_message }}
    </div>

    <!-- Average Scores -->
    <div v-if="results.length" class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <div v-for="m in averages" :key="m.key" class="bg-white p-6 rounded-[2rem] shadow-sm border border-slate-100">
        <h3 class="text-xs font-black text-slate-400 uppercase tracking-widest mb-4">{{ m.label }}</h3>
        <span class="text-4xl font-black text-blue-600">{{ m.value }}</span>
        <p class="text-sm font-bold text-slate-500 mt-2">Average on this page</p>
      </div>
    </div>

    <!-- Results Table -->
    <div class="bg-white rounded-[2rem] shadow-sm border border-slate-100 overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse">
          <thead>
          <tr class="bg-slate-50 border-b border-slate-100">
            <th class="px-6 py-4 text-xs font-black text-slate-400 uppercase tracking-widest w-[28%]">Input</th>
            <th class="px-6 py-4 text-xs font-black text-slate-400 uppercase tracking-widest w-[28%]">Generated Text</th>
            <th class="px-6 py-4 text-xs font-black text-slate-400 uppercase tracking-widest w-[14%]">Scores</th>
            <th class="px-6 py-4 text-xs font-black text-slate-400 uppercase tracking-widest w-[30%]">Reasoning</th>
          </tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
          <tr v-if="isLoading">
            <td colspan="4" class="px-6 py-8 text-center text-slate-400 font-medium animate-pulse">Loading results...</td>
          </tr>
          <tr v-else-if="results.length === 0">
            <td colspan="4" class="px-6 py-8 text-center text-slate-400 font-medium">No results found for this run.</td>
          </tr>
          <tr v-for="r in results" :key="r.id" class="hover:bg-slate-50 transition-colors">
            <td class="px-6 py-4 text-sm text-slate-700 whitespace-pre-wrap align-top bg-slate-50/30 border-r border-slate-100">{{ r.input_text }}</td>
            <td class="px-6 py-4 text-sm text-slate-800 whitespace-pre-wrap align-top border-r border-slate-100">{{ r.generated_text }}</td>
            <td class="px-6 py-4 text-xs text-slate-600 align-top border-r border-slate-100">
              <div class="space-y-1.5 bg-slate-50 rounded-lg p-3 border border-slate-100">
                <div v-if="r.metric_category" class="flex justify-between">
                  <span class="font-semibold text-slate-400">Category:</span>
                  <span class="font-medium">{{ r.metric_category }}</span>
                </div>
                <div v-if="r.safety_score != null" class="flex justify-between">
                  <span class="font-semibold text-slate-400">Safety:</span>
                  <span class="font-medium font-mono">{{ r.safety_score.toFixed(2) }}</span>
                </div>
                <div v-if="r.accuracy_score != null" class="flex justify-between">
                  <span class="font-semibold text-slate-400">Accuracy:</span>
                  <span class="font-medium font-mono">{{ r.accuracy_score.toFixed(2) }}</span>
                </div>
                <div v-if="r.hallucination_score != null" class="flex justify-between">
                  <span class="font-semibold text-slate-400">Hallucination:</span>
                  <span class="font-medium font-mono">{{ r.hallucination_score.toFixed(2) }}</span>
                </div>
              </div>
            </td>
            <td class="px-6 py-4 text-sm text-slate-700 whitespace-pre-wrap align-top">{{ r.reasoning || '—' }}</td>
          </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination -->
      <div v-if="totalPages > 1" class="px-6 py-4 bg-slate-50/50 border-t border-slate-100 flex items-center justify-between">
        <div class="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em]">
          Page {{ currentPage }} / {{ totalPages }} (Total: {{ totalItems }})
        </div>
        <div class="flex items-center gap-2">
          <button
              @click="fetchResults(currentPage - 1)"
              :disabled="currentPage === 1"
              class="p-2 rounded-xl border border-slate-200 bg-white hover:bg-slate-50 disabled:opacity-30 disabled:cursor-not-allowed transition-all shadow-sm"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" /></svg>
          </button>
          <button
              @click="fetchResults(currentPage + 1)"
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
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import http from '@/shared/http'

const route = useRoute()
const runId = computed(() => route.params.id)

const runDetails = ref(null)
const detailsError = ref('')

const results = ref([])
const isLoading = ref(false)
const resultsError = ref('')
const currentPage = ref(1)
const totalPages = ref(1)
const totalItems = ref(0)

const fetchDetails = async () => {
  detailsError.value = ''
  try {
    const { data } = await http.get(`/llm/judge-runs/${runId.value}`)
    runDetails.value = data
  } catch (err) {
    detailsError.value = err.response?.status === 404
        ? 'Judge run not found.'
        : err.response?.data?.detail || 'Failed to load judge run details.'
  }
}

const fetchResults = async (page = 1, size = 50) => {
  isLoading.value = true
  resultsError.value = ''
  try {
    const { data } = await http.get(`/llm/judge-runs/${runId.value}/results`, { params: { page, size } })
    results.value = data.items
    currentPage.value = data.page
    totalPages.value = data.pages
    totalItems.value = data.total
  } catch (err) {
    resultsError.value = err.response?.data?.detail || 'Failed to load judge results.'
  } finally {
    isLoading.value = false
  }
}

const averages = computed(() => {
  const defs = [
    { key: 'safety_score', label: 'Safety' },
    { key: 'accuracy_score', label: 'Accuracy' },
    { key: 'hallucination_score', label: 'Hallucination' },
  ]
  return defs.map(({ key, label }) => {
    const vals = results.value.map(r => r[key]).filter(v => v != null)
    const value = vals.length ? (vals.reduce((a, b) => a + b, 0) / vals.length).toFixed(2) : 'N/A'
    return { key, label, value }
  })
})

const loadAll = () => {
  fetchDetails()
  fetchResults(1)
}

watch(runId, loadAll)
onMounted(loadAll)
</script>
