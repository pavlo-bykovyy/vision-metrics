<template>
  <div class="w-full px-4 md:px-8 space-y-8 pb-20">

    <!-- Page Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-black text-slate-900 tracking-tight">Active Models</h1>
        <p class="text-slate-500 font-medium mt-1">Start, monitor, and manage your running LoRA instances.</p>
      </div>
    </div>

    <!-- Start New Active Model Card -->
    <div class="bg-white p-8 rounded-[2rem] shadow-sm border border-slate-100 flex flex-col md:flex-row gap-4 items-end">
      <div class="flex-1 w-full flex flex-col gap-2">
        <label class="text-xs font-black text-slate-400 uppercase tracking-widest">Select Adapter to Start</label>
        <div class="relative">
          <select
              v-model="selectedAdapterId"
              :disabled="isLoadingAdapters"
              class="w-full px-4 py-3 rounded-xl bg-slate-50 border border-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500 font-medium text-slate-700 appearance-none cursor-pointer disabled:opacity-50"
          >
            <option value="" disabled>-- Choose an adapter --</option>
            <option v-for="adapter in availableAdapters" :key="adapter.id" :value="adapter.id">
              {{ adapter.folder_name || `Adapter #${adapter.id}` }} {{ adapter.base_model_name_or_path ? `(${adapter.base_model_name_or_path})` : '' }}
            </option>
          </select>
          <div class="pointer-events-none absolute inset-y-0 right-0 flex items-center px-4 text-slate-400">
            <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
            </svg>
          </div>
        </div>
        <p v-if="availableAdapters.length === 0 && !isLoadingAdapters" class="text-xs text-orange-500 font-medium mt-1">
          No adapters found. Please upload one first.
        </p>
      </div>

      <button
          @click="startActiveModel"
          :disabled="!selectedAdapterId || isStarting"
          class="px-8 py-3 h-[50px] bg-blue-600 text-white rounded-xl font-black shadow-lg shadow-blue-600/20 hover:bg-blue-700 disabled:bg-slate-300 transition-all flex items-center shrink-0"
      >
        <span v-if="isStarting" class="animate-spin inline-block mr-2">⏳</span>
        {{ isStarting ? 'Starting...' : '+ Start Model' }}
      </button>
    </div>

    <!-- Active Models Table -->
    <div class="bg-white rounded-[2rem] shadow-sm border border-slate-100 overflow-hidden">
      <div class="px-8 py-6 border-b border-slate-50 flex items-center justify-between bg-slate-50/30">
        <h2 class="text-xl font-black text-slate-800 tracking-tight">Running Instances</h2>
        <button @click="fetchActiveModels" class="text-sm font-bold text-blue-500 hover:text-blue-700 transition-colors flex items-center gap-1">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" /></svg>
          Refresh
        </button>
      </div>

      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse">
          <thead>
          <tr class="bg-slate-50 text-slate-400 text-xs uppercase tracking-widest border-b border-slate-100">
            <th class="px-6 py-4 font-black">Model ID</th>
            <th class="px-6 py-4 font-black">Adapter ID</th>
            <th class="px-6 py-4 font-black">Queue Name</th>
            <th class="px-6 py-4 font-black">Status</th>
            <th class="px-6 py-4 font-black text-right">Actions</th>
          </tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
          <tr v-if="isLoadingData" class="text-center">
            <td colspan="5" class="py-8 text-slate-400 font-medium">Loading active models...</td>
          </tr>
          <tr v-else-if="activeModels.length === 0" class="text-center">
            <td colspan="5" class="py-8 text-slate-400 font-medium">No models are currently running.</td>
          </tr>
          <tr v-for="model in activeModels" :key="model.id" class="hover:bg-slate-50/50 transition-colors text-sm">
            <td class="px-6 py-4 font-mono font-bold text-slate-800">#{{ model.id }}</td>
            <td class="px-6 py-4 font-mono text-slate-500">Adapter {{ model.adapter_id }}</td>
            <td class="px-6 py-4 font-mono text-blue-600 bg-blue-50/50 rounded">{{ model.queue_name }}</td>
            <td class="px-6 py-4">
                <span
                    class="px-3 py-1 text-[10px] font-black uppercase tracking-wider rounded-full inline-flex items-center"
                    :class="{
                    'bg-green-100 text-green-700': model.status === 'running' || model.status === 'active',
                    'bg-blue-50 text-blue-600': model.status === 'starting' || model.status === 'pending',
                    'bg-red-100 text-red-700': model.status === 'failed',
                    'bg-slate-100 text-slate-600': !['running', 'active', 'starting', 'pending', 'failed'].includes(model.status)
                  }"
                >
                  <span v-if="model.status === 'starting' || model.status === 'pending'" class="inline-block animate-pulse mr-1">●</span>
                  {{ model.status }}
                </span>
            </td>
            <td class="px-6 py-4 text-right">
              <button
                  @click="stopActiveModel(model.adapter_id)"
                  class="text-red-500 hover:text-red-700 font-bold px-3 py-1.5 bg-red-50 hover:bg-red-100 rounded-lg transition-colors inline-flex items-center gap-1"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 10a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 01-1-1v-4z" /></svg>
                Stop
              </button>
            </td>
          </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useLoraAdaptersList } from '@/composables/useLoraAdaptersList'

const API_URL = import.meta.env.VITE_API_URL || ''

// Composable for dropdown data
const { availableAdapters, isLoadingAdapters, fetchAdapters } = useLoraAdaptersList(API_URL)

const activeModels = ref([])
const isLoadingData = ref(false)
const selectedAdapterId = ref('')
const isStarting = ref(false)

const getHeaders = () => {
  const token = localStorage.getItem('token')
  return token ? { 'Authorization': `Bearer ${token}` } : {}
}

const fetchActiveModels = async () => {
  isLoadingData.value = true
  try {
    const response = await axios.get(`${API_URL}/llm/lora/active-models/`, { headers: getHeaders() })
    activeModels.value = response.data
  } catch (error) {
    console.error("Failed to fetch active models:", error)
  } finally {
    isLoadingData.value = false
  }
}

const startActiveModel = async () => {
  if (!selectedAdapterId.value) return

  isStarting.value = true
  try {
    await axios.post(`${API_URL}/llm/lora/active-models/`,
        { adapter_id: selectedAdapterId.value },
        { headers: getHeaders() }
    )
    selectedAdapterId.value = '' // reset dropdown
    await fetchActiveModels()    // refresh table
  } catch (error) {
    console.error("Failed to start active model:", error)
    alert(error.response?.data?.detail || "Error starting the model.")
  } finally {
    isStarting.value = false
  }
}

const stopActiveModel = async (adapterId) => {
  if (!confirm('Are you sure you want to stop and delete this active model instance?')) return

  try {
    // Note: The FastAPI endpoint expects the adapter_id in the URL path for DELETE
    await axios.delete(`${API_URL}/llm/lora/active-models/${adapterId}`, { headers: getHeaders() })
    await fetchActiveModels() // refresh table
  } catch (error) {
    console.error("Failed to stop active model:", error)
    alert(error.response?.data?.detail || "Error stopping the model.")
  }
}

onMounted(() => {
  fetchAdapters()
  fetchActiveModels()
})
</script>