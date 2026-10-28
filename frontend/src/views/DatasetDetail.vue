<template>
  <div class="max-w-5xl mx-auto p-6 space-y-8 pb-20">

    <!-- Back Button -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
      <button @click="$router.push('/datasets')" class="text-sm font-bold text-slate-500 hover:text-slate-800 flex items-center gap-2">
        <span>&larr;</span> {{ t('common.back') || 'Back to Datasets' }}
      </button>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-20 text-slate-400 font-medium animate-pulse">
      {{ t('common.loading') || 'Loading dataset details...' }}
    </div>

    <!-- Main Content -->
    <div v-else-if="dataset" class="space-y-6">

      <!-- Header Card -->
      <div class="bg-white p-6 rounded-[2rem] shadow-sm border border-slate-100 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 class="text-3xl font-black text-slate-800 tracking-tight">
            {{ dataset.name }}
          </h1>
          <p class="text-sm text-slate-500 mt-2 flex items-center gap-3">
            <span class="font-mono bg-slate-100 px-2 py-0.5 rounded text-xs">ID: {{ dataset.id }}</span>
            <span class="flex items-center gap-1.5">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
              {{ new Date(dataset.created_at).toLocaleString() }}
            </span>
          </p>
        </div>

        <span class="px-4 py-1.5 rounded-full text-xs font-black uppercase tracking-wider bg-blue-50 text-blue-600 border border-blue-100">
          {{ dataset.file_format }}
        </span>
      </div>

      <!-- Details Grid -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">

        <!-- Configuration Data -->
        <div class="bg-white p-6 rounded-[2rem] shadow-sm border border-slate-100">
          <h3 class="font-bold text-slate-700 mb-4 flex items-center gap-2">
            <span class="text-xl">⚙️</span> Configuration
          </h3>
          <ul class="space-y-3 text-sm">
            <li class="flex justify-between items-center border-b border-slate-50 pb-3">
              <span class="text-slate-500">ID Column</span>
              <span class="font-mono font-bold text-slate-800 bg-slate-50 px-2 py-1 rounded">{{ dataset.id_column || '—' }}</span>
            </li>
            <li class="flex justify-between items-center border-b border-slate-50 pb-3">
              <span class="text-slate-500">Dataset Type</span>
              <span class="font-mono font-bold text-slate-800 bg-slate-50 px-2 py-1 rounded uppercase">{{ dataset.dataset_type || '—' }}</span>
            </li>
            <li class="flex justify-between items-center border-b border-slate-50 pb-3">
              <span class="text-slate-500">File Source</span>
              <span class="font-mono font-bold text-slate-800 bg-slate-50 px-2 py-1 rounded uppercase">{{ dataset.file_source || '—' }}</span>
            </li>
            <li class="flex justify-between items-center border-b border-slate-50 pb-3">
              <span class="text-slate-500">Artifact ID</span>
              <span class="font-mono font-bold text-slate-800 bg-slate-50 px-2 py-1 rounded">{{ dataset.artifact_id || '—' }}</span>
            </li>
            <li class="flex justify-between items-center border-b border-slate-50 pb-3">
              <span class="text-slate-500">Source URL</span>
              <a v-if="dataset.source_url" :href="dataset.source_url" target="_blank" class="font-bold text-blue-600 hover:underline truncate max-w-[200px]">
                {{ dataset.source_url }}
              </a>
              <span v-else class="font-bold text-slate-800">—</span>
            </li>
            <li class="flex justify-between items-start pt-1">
              <span class="text-slate-500 mt-1">Mapping Config</span>
              <div v-if="dataset.mapping_config && Object.keys(dataset.mapping_config).length > 0" class="font-mono text-xs text-slate-800 bg-slate-50 p-2 rounded max-w-[200px] overflow-x-auto whitespace-pre-wrap">
                {{ JSON.stringify(dataset.mapping_config, null, 2) }}
              </div>
              <span v-else class="font-mono font-bold text-slate-800 bg-slate-50 px-2 py-1 rounded">—</span>
            </li>
          </ul>
        </div>

        <!-- Schema Configuration -->
        <div class="bg-white p-6 rounded-[2rem] shadow-sm border border-slate-100 flex flex-col">
          <h3 class="font-bold text-slate-700 mb-4 flex items-center gap-2">
            <span class="text-xl">📋</span> Schema Configuration
          </h3>
          <div class="flex-1 bg-slate-50 rounded-xl p-5 border border-slate-100 text-sm flex flex-col gap-5 overflow-y-auto max-h-[300px]">
            <template v-if="dataset.schema_config && Object.keys(dataset.schema_config).length > 0">

              <!-- Input Fields -->
              <div>
                <span class="block text-[10px] font-black text-slate-400 uppercase tracking-widest mb-2">Input Fields</span>
                <div class="flex flex-wrap gap-2">
                  <span v-for="field in dataset.schema_config.input_fields" :key="field" class="px-2 py-1 bg-blue-50 text-blue-700 rounded-md font-mono text-xs font-bold border border-blue-100">
                    {{ field }}
                  </span>
                  <span v-if="!dataset.schema_config.input_fields?.length" class="text-slate-400 italic text-xs">None</span>
                </div>
              </div>

              <!-- Target Fields -->
              <div>
                <span class="block text-[10px] font-black text-slate-400 uppercase tracking-widest mb-2">Target Fields</span>
                <div class="flex flex-wrap gap-2">
                  <span v-for="field in dataset.schema_config.target_fields" :key="field" class="px-2 py-1 bg-emerald-50 text-emerald-700 rounded-md font-mono text-xs font-bold border border-emerald-100">
                    {{ field }}
                  </span>
                  <span v-if="!dataset.schema_config.target_fields?.length" class="text-slate-400 italic text-xs">None</span>
                </div>
              </div>

              <!-- Metadata Fields -->
              <div>
                <span class="block text-[10px] font-black text-slate-400 uppercase tracking-widest mb-2">Metadata Fields</span>
                <div class="flex flex-wrap gap-2">
                  <span v-for="field in dataset.schema_config.metadata_fields" :key="field" class="px-2 py-1 bg-purple-50 text-purple-700 rounded-md font-mono text-xs font-bold border border-purple-100">
                    {{ field }}
                  </span>
                  <span v-if="!dataset.schema_config.metadata_fields?.length" class="text-slate-400 italic text-xs">None</span>
                </div>
              </div>

            </template>
            <template v-else>
              <div class="text-slate-400 italic text-center py-4 text-xs font-medium">No schema configuration provided for this dataset.</div>
            </template>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
const route = useRoute()

const dataset = ref(null)
const loading = ref(true)

const API_URL = import.meta.env.VITE_API_URL || ''

const fetchDatasetDetails = async () => {
  loading.value = true
  try {
    const token = localStorage.getItem('token')
    const response = await axios.get(`${API_URL}/datasets/${route.params.id}`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    dataset.value = response.data
  } catch (error) {
    console.error("Error fetching dataset details:", error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchDatasetDetails()
})
</script>