<template>
  <div class="max-w-5xl mx-auto p-6 space-y-8 pb-20">

    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
      <button @click="$router.push('/models')" class="text-sm font-bold text-slate-500 hover:text-slate-800 flex items-center gap-2">
        <span>&larr;</span> {{ t('common.back') || 'Back to Models' }}
      </button>
    </div>

    <div v-if="loading" class="text-center py-20 text-slate-400 font-medium animate-pulse">
      {{ t('modelDetails.loading') || 'Loading model data...' }}
    </div>

    <div v-else-if="model" class="space-y-6">

      <div class="bg-white p-6 rounded-[2rem] shadow-sm border border-slate-100 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 class="text-3xl font-black text-slate-800 tracking-tight">{{ model.name }}</h1>
          <p class="text-sm text-slate-500 mt-2 flex items-center gap-3">
            <span class="font-mono bg-slate-100 px-2 py-0.5 rounded text-xs">ID: {{ model.id }}</span>
            <span class="flex items-center gap-1.5">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
              {{ new Date(model.created_at).toLocaleString() }}
            </span>
          </p>
        </div>

        <button @click="$router.push(`/models/${model.id}/edit`)" class="px-4 py-2 bg-blue-50 text-blue-600 font-bold rounded-xl hover:bg-blue-100 transition-colors text-sm">
          {{ t('modelsTable.edit') || 'Edit Model' }}
        </button>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div class="bg-white p-6 rounded-[2rem] shadow-sm border border-slate-100">
          <h3 class="font-bold text-slate-700 mb-4 flex items-center gap-2">
            <span class="text-xl">⚙️</span> Model Details
          </h3>
          <ul class="space-y-3 text-sm">
            <li class="flex justify-between items-center border-b border-slate-50 pb-3">
              <span class="text-slate-500">Architecture File ID</span>
              <span class="font-mono font-bold text-slate-800 bg-slate-50 px-2 py-1 rounded">{{ model.arch_file_id || '—' }}</span>
            </li>
            <li class="flex justify-between items-center border-b border-slate-50 pb-3">
              <span class="text-slate-500">Weights File ID</span>
              <span class="font-mono font-bold text-slate-800 bg-slate-50 px-2 py-1 rounded">{{ model.weights_file_id || '—' }}</span>
            </li>
          </ul>

          <div class="mt-4">
            <span class="text-slate-500 text-sm block mb-2">Description</span>
            <div class="bg-slate-50 rounded-xl p-4 border border-slate-100 text-sm text-slate-600 whitespace-pre-wrap">
              {{ model.description || 'No description provided.' }}
            </div>
          </div>
        </div>

        <div class="bg-white p-6 rounded-[2rem] shadow-sm border border-slate-100">
          <h3 class="font-bold text-slate-700 mb-4 flex items-center gap-2">
            <span class="text-xl">📊</span> Test Runs ({{ model.evaluations?.length || 0 }})
          </h3>

          <div v-if="model.evaluations && model.evaluations.length > 0" class="space-y-3 max-h-[300px] overflow-y-auto pr-2">
            <router-link
                v-for="evalItem in model.evaluations"
                :key="evalItem.id"
                :to="`/evaluations/${evalItem.id}`"
                class="block bg-slate-50 hover:bg-slate-100 border border-slate-100 p-3 rounded-xl transition-colors group"
            >
              <div class="flex justify-between items-center mb-1">
                <span class="font-bold text-slate-700 group-hover:text-blue-600 transition-colors">Evaluation #{{ evalItem.id }}</span>
                <span class="text-[10px] font-black uppercase px-2 py-0.5 rounded-full"
                      :class="{
                        'bg-green-100 text-green-700': evalItem.status === 'completed',
                        'bg-red-100 text-red-700': evalItem.status === 'failed',
                        'bg-blue-100 text-blue-700': evalItem.status === 'processing' || evalItem.status === 'pending'
                      }">
                  {{ evalItem.status }}
                </span>
              </div>
              <div class="text-xs text-slate-400 flex justify-between">
                <span>{{ new Date(evalItem.created_at).toLocaleDateString() }}</span>
                <span class="group-hover:translate-x-1 transition-transform">&rarr;</span>
              </div>
            </router-link>
          </div>

          <div v-else class="text-center py-10 bg-slate-50 rounded-xl text-slate-400 text-sm font-medium">
            {{ t('modelDetails.noRuns') || 'No runs yet' }}
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
const model = ref(null)
const loading = ref(true)

const API_URL = import.meta.env.VITE_API_URL || ''

const fetchModelDetails = async () => {
  loading.value = true
  try {
    const token = localStorage.getItem('token')
    const response = await axios.get(`${API_URL}/models/${route.params.id}`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    model.value = response.data
  } catch (error) {
    console.error("Error fetching models:", error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchModelDetails()
})
</script>