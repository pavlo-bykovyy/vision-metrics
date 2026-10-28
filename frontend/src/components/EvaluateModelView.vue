<template>
  <div class="max-w-4xl mx-auto space-y-8 pb-20 p-6">
    <div class="flex items-center mb-6">
      <button @click="$router.push('/')" class="text-sm font-bold text-slate-500 hover:text-slate-800 flex items-center gap-2">
        <span>&larr;</span> {{ t('evaluation.backToTable') }}
      </button>
    </div>

    <div>
      <h1 class="text-3xl font-black text-slate-900 tracking-tight">{{ t('evaluation.pageTitle') }}</h1>
      <p class="text-slate-500 font-medium mt-1">{{ t('evaluation.pageSubtitle') }}</p>
    </div>

    <div class="bg-white p-8 rounded-[2rem] shadow-sm border border-slate-100">
      <h2 class="text-xl font-black text-slate-800 mb-6 flex items-center gap-3">
        {{ t('evaluation.parametersHeader') }}
      </h2>

      <div v-if="isLoading" class="text-slate-500 font-medium animate-pulse">
        {{ t('evaluation.loadingData') }}
      </div>

      <div v-else class="space-y-6">

        <div class="flex flex-col gap-2">
          <label class="text-xs font-black text-slate-400 uppercase tracking-widest">
            {{ t('evaluation.selectedModel') }}
          </label>
          <select
              v-model="selectedModelId"
              class="px-4 py-3 rounded-xl bg-slate-50 border border-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500 font-medium text-slate-700 cursor-pointer"
          >
            <option value="" disabled>-- Select a model for testing --</option>
            <option v-for="model in models" :key="model.id" :value="model.id">
              {{ model.name }} (ID: {{ model.id }})
            </option>
          </select>
        </div>

        <div class="flex flex-col gap-2">
          <label class="text-xs font-black text-slate-400 uppercase tracking-widest">
            {{ t('evaluation.selectDatasetLabel') }}
          </label>
          <select
              v-model="selectedDatasetId"
              class="px-4 py-3 rounded-xl bg-slate-50 border border-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500 font-medium text-slate-700 cursor-pointer"
          >
            <option value="" disabled>{{ t('evaluation.selectDatasetPlaceholder') }}</option>
            <option v-for="dataset in datasets" :key="dataset.id" :value="dataset.id">
              {{ dataset.name }} ({{ t('evaluation.formatLabel') }}: {{ dataset.file_format }})
            </option>
          </select>
          <p v-if="datasets.length === 0" class="text-sm text-orange-500 font-medium mt-1">
            {{ t('evaluation.noDatasetsText') }}
          </p>
        </div>

        <div v-if="errorMessage" class="p-4 bg-red-50 text-red-700 rounded-xl font-medium text-sm border border-red-100">
          {{ errorMessage }}
        </div>

        <button
            @click="startEvaluation"
            :disabled="!selectedDatasetId || !selectedModelId || isSubmitting"
            class="w-full py-4 bg-blue-600 text-white rounded-2xl font-black shadow-lg shadow-blue-600/20 hover:bg-blue-700 disabled:bg-slate-300 transition-all flex items-center justify-center mt-4"
        >
          <span v-if="isSubmitting" class="animate-spin inline-block mr-2">⏳</span>
          {{ isSubmitting ? t('evaluation.startingTest') : t('evaluation.startTestBtn') }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import axios from 'axios'

const router = useRouter()
const { t } = useI18n()
const API_URL = import.meta.env.VITE_API_URL || ''

const models = ref([])
const datasets = ref([])

const selectedModelId = ref('')
const selectedDatasetId = ref('')

const isLoading = ref(true)
const isSubmitting = ref(false)
const errorMessage = ref('')

const fetchData = async () => {
  isLoading.value = true
  errorMessage.value = ''

  try {
    const token = localStorage.getItem('token')
    const config = { headers: { 'Authorization': `Bearer ${token}` } }

    const datasetsRes = await axios.get(`${API_URL}/datasets/`, config)
    datasets.value = datasetsRes.data

    const modelsRes = await axios.get(`${API_URL}/models/?size=100`, config)
    models.value = modelsRes.data.items

  } catch (error) {
    console.error(error)
    errorMessage.value = t('evaluation.fetchError')
  } finally {
    isLoading.value = false
  }
}

const startEvaluation = async () => {
  if (!selectedDatasetId.value || !selectedModelId.value) return

  isSubmitting.value = true
  errorMessage.value = ''

  try {
    const token = localStorage.getItem('token')

    await axios.post(
        `${API_URL}/evaluations/create`,
        {
          dataset_id: selectedDatasetId.value,
          model_id: selectedModelId.value
        },
        {
          headers: { 'Authorization': `Bearer ${token}` }
        }
    )

    router.push('/evaluations')
  } catch (error) {
    errorMessage.value = error.response?.data?.detail || t('evaluation.startError')
  } finally {
    isSubmitting.value = false
  }
}

onMounted(() => {
  fetchData()
})
</script>