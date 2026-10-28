<template>
  <div class="space-y-8 pb-12 mt-8">

    <!-- Header Section -->
    <div class="flex items-center justify-between mb-6">
      <div>
        <button @click="$router.push('/lora-tasks')" class="text-sm font-bold text-slate-500 hover:text-slate-800 flex items-center gap-2 mb-2">
          <span>&larr;</span> Back to Tasks
        </button>

        <h1 class="text-3xl font-black text-slate-900 tracking-tight flex items-center gap-3">
          {{ taskDetails?.name || `Task #${taskId}` }}
          <span v-if="taskDetails?.name" class="text-sm font-bold text-slate-400 bg-slate-100 px-2 py-1 rounded-lg">#{{ taskId }}</span>
        </h1>

        <p class="text-slate-500 font-medium mt-2 max-w-3xl">
          {{ taskDetails?.description || 'Review the generated texts and performance metrics for this evaluation.' }}
        </p>
      </div>
    </div>

    <!-- Multi-Criteria Metrics Dashboard -->
    <div v-if="taskDetails?.metrics" class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">

      <!-- Predictive Quality Card -->
      <div class="bg-white p-6 rounded-[2rem] shadow-sm border border-slate-100 hover:shadow-md transition-shadow">
        <h3 class="text-xs font-black text-slate-400 uppercase tracking-widest mb-4 flex items-center gap-2">
          <span>🎯</span> Predictive Quality
        </h3>
        <div class="flex items-end gap-3">
          <span class="text-4xl font-black text-blue-600">{{ formatPercent(taskDetails.metrics.schema_validity_rate) }}</span>
        </div>
        <p class="text-sm font-bold text-slate-500 mt-2">Schema Validity Rate</p>
      </div>

      <!-- Operational Efficiency Card -->
      <div class="bg-white p-6 rounded-[2rem] shadow-sm border border-slate-100 hover:shadow-md transition-shadow">
        <h3 class="text-xs font-black text-slate-400 uppercase tracking-widest mb-4 flex items-center gap-2">
          <span>⚡</span> Operational Efficiency
        </h3>
        <div class="space-y-3">
          <div class="flex justify-between items-center border-b border-slate-50 pb-2">
            <span class="text-sm font-medium text-slate-500">Throughput (TPS)</span>
            <span class="font-bold text-slate-800 font-mono">{{ formatNumber(taskDetails.metrics.mean_tps) }} tok/s</span>
          </div>
          <div class="flex justify-between items-center border-b border-slate-50 pb-2">
            <span class="text-sm font-medium text-slate-500">VRAM Footprint</span>
            <span class="font-bold text-slate-800 font-mono">{{ formatNumber(taskDetails.metrics.mean_vram_mb, 0) }} MB</span>
          </div>
          <div class="flex justify-between items-center">
            <span class="text-sm font-medium text-slate-500">Avg Latency</span>
            <span class="font-bold text-slate-800 font-mono">{{ formatNumber(taskDetails.metrics.mean_latency_sec) }} s</span>
          </div>
        </div>
      </div>

      <!-- Calibration & Info Card -->
      <div class="bg-white p-6 rounded-[2rem] shadow-sm border border-slate-100 hover:shadow-md transition-shadow">
        <h3 class="text-xs font-black text-slate-400 uppercase tracking-widest mb-4 flex items-center gap-2">
          <span>⚖️</span> Calibration & Info
        </h3>
        <div class="space-y-3">
          <div class="flex justify-between items-center border-b border-slate-50 pb-2">
            <span class="text-sm font-medium text-slate-500">Mean Logprob</span>
            <span class="font-bold text-slate-800 font-mono">{{ formatNumber(taskDetails.metrics.mean_logprob, 4) }}</span>
          </div>
          <div class="flex justify-between items-center">
            <span class="text-sm font-medium text-slate-500">Total Samples</span>
            <span class="font-bold text-slate-800 font-mono">{{ taskDetails.metrics.total_samples || 'N/A' }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Per-Prompt Results Table -->
    <div class="bg-white rounded-[2rem] shadow-sm border border-slate-100 overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse">
          <thead>
          <tr class="bg-slate-50 border-b border-slate-100">
            <th class="px-6 py-4 text-xs font-black text-slate-400 uppercase tracking-widest w-[40%]">Question (Input Text)</th>
            <th class="px-6 py-4 text-xs font-black text-slate-400 uppercase tracking-widest w-[40%]">Answer (Generated Text)</th>
            <th class="px-6 py-4 text-xs font-black text-slate-400 uppercase tracking-widest w-[20%]">Metrics</th>
          </tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
          <tr v-if="isLoading">
            <td colspan="3" class="px-6 py-8 text-center text-slate-400 font-medium animate-pulse">Loading results...</td>
          </tr>
          <tr v-else-if="results.length === 0">
            <td colspan="3" class="px-6 py-8 text-center text-slate-400 font-medium">No results found for this task.</td>
          </tr>
          <tr v-for="result in results" :key="result.id" class="hover:bg-slate-50 transition-colors">
            <td class="px-6 py-4 text-sm text-slate-700 whitespace-pre-wrap align-top bg-slate-50/30 border-r border-slate-100">
              {{ result.input_text }}
            </td>
            <td class="px-6 py-4 text-sm text-slate-800 whitespace-pre-wrap align-top border-r border-slate-100">
              {{ result.generated_text }}
            </td>
            <td class="px-6 py-4 text-xs text-slate-600 align-top">
              <div class="space-y-1.5 bg-slate-50 rounded-lg p-3 border border-slate-100">
                <div v-if="result.latency_seconds != null" class="flex justify-between">
                  <span class="font-semibold text-slate-400">Latency:</span>
                  <span class="font-medium font-mono">{{ result.latency_seconds.toFixed(2) }}s</span>
                </div>
                <div v-if="result.prompt_tokens != null && result.completion_tokens != null" class="flex justify-between">
                  <span class="font-semibold text-slate-400">Tokens:</span>
                  <span class="font-medium font-mono" title="Prompt / Completion">{{ result.prompt_tokens }} / {{ result.completion_tokens }}</span>
                </div>
                <div v-if="result.peak_memory_mb != null" class="flex justify-between">
                  <span class="font-semibold text-slate-400">VRAM:</span>
                  <span class="font-medium font-mono">{{ result.peak_memory_mb.toFixed(0) }} MB</span>
                </div>
                <div v-if="result.avg_logprob != null" class="flex justify-between">
                  <span class="font-semibold text-slate-400">Logprob:</span>
                  <span class="font-medium font-mono">{{ result.avg_logprob.toFixed(3) }}</span>
                </div>
                <div v-if="result.latency_seconds == null && result.prompt_tokens == null" class="text-slate-400 italic text-center">
                  No metrics available
                </div>
              </div>
            </td>
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

    <!-- NEW: Raw JSON Data Box -->
    <div v-if="taskDetails" class="bg-white rounded-[2.5rem] shadow-xl shadow-slate-200/50 border border-slate-100 overflow-hidden mt-8">
      <div class="px-10 py-6 border-b border-slate-50 flex items-center justify-between bg-slate-50/30">
        <div>
          <h2 class="text-xl font-black text-slate-800 tracking-tight">Raw Evaluation Data</h2>
          <p class="text-sm text-slate-500 mt-1 font-medium">Full JSON response for this evaluation run.</p>
        </div>
        <button @click="copyToClipboard(JSON.stringify(taskDetails, null, 2))" class="flex items-center gap-2 px-4 py-2 text-sm font-bold text-slate-600 hover:text-blue-600 bg-white border border-slate-200 hover:border-blue-200 rounded-xl transition-colors shadow-sm" title="Copy JSON">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"></path></svg>
          Copy JSON
        </button>
      </div>
      <div class="p-6 bg-slate-50/50">
        <pre class="text-xs font-mono text-slate-700 overflow-x-auto whitespace-pre-wrap p-4 bg-white rounded-2xl border border-slate-100 shadow-inner">{{ JSON.stringify(taskDetails, null, 4) }}</pre>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'

const route = useRoute()
const taskId = route.params.id
const API_URL = import.meta.env.VITE_API_URL || ''

const results = ref([])
const isLoading = ref(true)
const currentPage = ref(1)
const totalPages = ref(1)
const totalItems = ref(0)

const taskDetails = ref(null)

// --- Helper Functions for Formatting ---
const formatPercent = (val) => {
  if (val === null || val === undefined) return 'N/A'
  return (val * 100).toFixed(2) + '%'
}

const formatNumber = (val, decimals = 2) => {
  if (val === null || val === undefined) return 'N/A'
  return val.toFixed(decimals)
}

// --- NEW: Copy to Clipboard Function ---
const copyToClipboard = async (text) => {
  try {
    await navigator.clipboard.writeText(text)
    alert('JSON copied to clipboard!')
  } catch (err) {
    console.error('Failed to copy text', err)
    alert('Failed to copy text.')
  }
}

// --- API Calls ---
const fetchTaskDetails = async () => {
  try {
    const token = localStorage.getItem('token')
    const response = await axios.get(`${API_URL}/llm/lora/evaluations/${taskId}`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    taskDetails.value = response.data
  } catch (error) {
    console.error("Failed to fetch task details:", error)
  }
}

const fetchResults = async (page = 1) => {
  isLoading.value = true
  try {
    const token = localStorage.getItem('token')

    const response = await axios.get(`${API_URL}/llm/lora/evaluations/${taskId}/results`, {
      params: { page, size: 50 },
      headers: { 'Authorization': `Bearer ${token}` }
    })

    results.value = response.data.items
    currentPage.value = response.data.page
    totalPages.value = response.data.pages
    totalItems.value = response.data.total
  } catch (error) {
    console.error("Failed to fetch evaluation results:", error)
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  fetchTaskDetails()
  fetchResults()
})
</script>