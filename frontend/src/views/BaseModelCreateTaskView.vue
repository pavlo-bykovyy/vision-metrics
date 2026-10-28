<template>
  <div class="max-w-4xl mx-auto space-y-8 pb-20 p-6">
    <div class="flex items-center mb-6">
      <button @click="$router.push('/base-model-tasks')" class="text-sm font-bold text-slate-500 hover:text-slate-800 flex items-center gap-2">
        <span>&larr;</span> Back to Base Models Table
      </button>
    </div>

    <div>
      <h1 class="text-3xl font-black text-slate-900 tracking-tight">Create Base Model Evaluation</h1>
      <p class="text-slate-500 font-medium mt-1">Configure parameters for pure base model testing.</p>
    </div>

    <div class="bg-white p-8 rounded-[2rem] shadow-sm border border-slate-100">
      <h2 class="text-xl font-black text-slate-800 mb-6 flex items-center gap-3">
        Evaluation Parameters
      </h2>

      <div v-if="isLoading" class="text-slate-500 font-medium animate-pulse">
        Loading datasets...
      </div>

      <div v-else class="space-y-6">
        <div class="flex flex-col gap-2">
          <label class="text-xs font-black text-slate-400 uppercase tracking-widest">
            Task Name
          </label>
          <input
              v-model="taskName"
              type="text"
              placeholder="e.g., Llama-2-7b base test"
              class="px-4 py-3 rounded-xl bg-slate-50 border border-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500 font-medium text-slate-700"
          />
        </div>

        <div class="flex flex-col gap-2">
          <label class="text-xs font-black text-slate-400 uppercase tracking-widest">
            Description (Optional)
          </label>
          <textarea
              v-model="taskDescription"
              placeholder="Short description of this evaluation run..."
              class="px-4 py-3 rounded-xl bg-slate-50 border border-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500 font-medium text-slate-700 min-h-[100px]"
          ></textarea>
        </div>

        <div class="flex flex-col gap-2">
          <label class="text-xs font-black text-slate-400 uppercase tracking-widest">
            Base Model ID (HuggingFace)
          </label>
          <input
              v-model="baseModelId"
              type="text"
              placeholder="e.g., gpt2, meta-llama/Llama-2-7b-hf"
              class="px-4 py-3 rounded-xl bg-slate-50 border border-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500 font-medium text-slate-700"
          />
        </div>

        <EvaluationJudgeSelector
            v-model="selectedJudgeIds"
            :apiUrl="API_URL"
        />

        <hr class="border-slate-100 my-6" />

        <div class="flex flex-col gap-2 mb-6">
          <div class="flex justify-between items-end">
            <label class="text-xs font-black text-slate-400 uppercase tracking-widest">Generation Parameters (JSON)</label>
            <span v-if="jsonError" class="text-xs font-bold text-red-500">{{ jsonError }}</span>
          </div>
          <textarea
              v-model="generationParamsStr"
              rows="8"
              class="px-4 py-4 rounded-xl bg-slate-50 border focus:outline-none focus:ring-2 resize-y font-mono text-sm text-slate-700"
              :class="jsonError ? 'border-red-300 focus:ring-red-500' : 'border-slate-200 focus:ring-blue-500'"
          ></textarea>
        </div>

        <CustomPromptTemplate
            v-model:useCustom="useCustomTemplate"
            v-model:templateText="promptTemplate"
        />

        <EvaluationModeSelector
            v-model:mode="evaluationMode"
            v-model:promptText="prompt"
            v-model:datasetId="selectedDatasetId"
            :datasets="datasets"
        />

        <div v-if="errorMessage" class="p-4 bg-red-50 text-red-700 rounded-xl font-medium text-sm border border-red-100">
          {{ errorMessage }}
        </div>

        <button
            @click="startEvaluation"
            :disabled="!isFormValid || isSubmitting"
            class="w-full py-4 bg-blue-600 text-white rounded-2xl font-black shadow-lg shadow-blue-600/20 hover:bg-blue-700 disabled:bg-slate-300 transition-all flex items-center justify-center mt-4"
        >
          <span v-if="isSubmitting" class="animate-spin inline-block mr-2">⏳</span>
          {{ isSubmitting ? 'Starting Test...' : 'Start Base Model Test' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import CustomPromptTemplate from '@/components/CustomPromptTemplate.vue'
import EvaluationModeSelector from "@/components/EvaluationModeSelector.vue"
import EvaluationJudgeSelector from '@/components/EvaluationJudgeSelector.vue'

const router = useRouter()
const API_URL = import.meta.env.VITE_API_URL || ''

const taskName = ref('')
const taskDescription = ref('')
const baseModelId = ref('')
const evaluationMode = ref('prompt')
const prompt = ref('')
const selectedDatasetId = ref('')

const selectedJudgeIds = ref([])

const useCustomTemplate = ref(false)
const promptTemplate = ref('{input_text}')

const defaultParams = {
  max_new_tokens: 128,
  temperature: 0.1,
  top_k: 40,
  top_p: 0.9,
  repetition_penalty: 1.15,
  do_sample: true,
  system_prompt: null
}

const generationParamsStr = ref(JSON.stringify(defaultParams, null, 2))
const jsonError = ref('')

const datasets = ref([])
const isLoading = ref(true)
const isSubmitting = ref(false)
const errorMessage = ref('')

watch(generationParamsStr, (newValue) => {
  try {
    JSON.parse(newValue)
    jsonError.value = ''
  } catch (e) {
    jsonError.value = 'Invalid JSON format'
  }
})

const isFormValid = computed(() => {
  if (!baseModelId.value || !taskName.value) return false
  if (jsonError.value) return false

  if (evaluationMode.value === 'dataset' && !selectedDatasetId.value) return false
  if (evaluationMode.value === 'prompt' && !prompt.value.trim()) return false

  return true
})

const fetchData = async () => {
  isLoading.value = true
  errorMessage.value = ''

  try {
    const token = localStorage.getItem('token')
    const config = { headers: { 'Authorization': `Bearer ${token}` } }

    const datasetsRes = await axios.get(`${API_URL}/datasets/`, config)
    datasets.value = datasetsRes.data

  } catch (error) {
    console.error(error)
    errorMessage.value = 'Failed to load datasets. Please check your connection.'
  } finally {
    isLoading.value = false
  }
}

const startEvaluation = async () => {
  if (!isFormValid.value) return

  isSubmitting.value = true
  errorMessage.value = ''

  try {
    const token = localStorage.getItem('token')

    const payload = {
      name: taskName.value,
      description: taskDescription.value,
      base_model_id: baseModelId.value,
      dataset_id: evaluationMode.value === 'dataset' ? selectedDatasetId.value : null,
      prompt: evaluationMode.value === 'prompt' ? prompt.value : null,
      generation_params: JSON.parse(generationParamsStr.value),
      judge_ids: selectedJudgeIds.value
    }

    if (useCustomTemplate.value && promptTemplate.value.trim() !== '') {
      payload.prompt_template = promptTemplate.value.trim()
    }

    await axios.post(
        `${API_URL}/llm/base-models/evaluations/`,
        payload,
        {
          headers: { 'Authorization': `Bearer ${token}` }
        }
    )

    router.push('/base-model-tasks')
  } catch (error) {
    errorMessage.value = error.response?.data?.detail || 'An error occurred while starting the evaluation.'
  } finally {
    isSubmitting.value = false
  }
}

onMounted(() => {
  fetchData()
})
</script>