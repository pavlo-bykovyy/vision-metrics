<template>
  <div class="max-w-4xl mx-auto space-y-8 pb-20">
    <div>
      <h1 class="text-3xl font-black text-slate-900 tracking-tight">Test LoRA Adapter</h1>
      <p class="text-slate-500 font-medium mt-1">Select an existing adapter or upload a new ZIP containing one or multiple adapters.</p>
    </div>

    <LoraAdapterSetup v-model="selectedAdapter" />

    <div class="bg-white p-8 rounded-[2rem] shadow-sm border border-slate-100 transition-opacity duration-300" :class="{ 'opacity-50 pointer-events-none': !selectedAdapter }">
      <h2 class="text-xl font-black text-slate-800 mb-6 flex items-center gap-3">
        <span class="w-8 h-8 rounded-full flex items-center justify-center text-sm transition-colors" :class="selectedAdapter ? 'bg-blue-100 text-blue-600' : 'bg-slate-100 text-slate-600'">2</span>
        Generate Text
      </h2>

      <div class="flex flex-col gap-2 mb-6">
        <label class="text-xs font-black text-slate-400 uppercase tracking-widest">Test Name</label>
        <input
            v-model="testName"
            type="text"
            placeholder="e.g., Evaluation Run 1"
            class="px-4 py-3 rounded-xl bg-slate-50 border border-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500 font-medium text-slate-700 h-[50px]"
        />
      </div>

      <div class="flex flex-col gap-2 mb-6">
        <label class="text-xs font-black text-slate-400 uppercase tracking-widest">Description (Optional)</label>
        <textarea
            v-model="testDescription"
            rows="3"
            placeholder="e.g., Testing base model with higher temperature"
            class="px-4 py-3 rounded-xl bg-slate-50 border border-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500 font-medium text-slate-700 resize-none"
        ></textarea>
      </div>

      <div class="flex flex-col gap-2 mb-6">
        <label class="text-xs font-black text-slate-400 uppercase tracking-widest">
          Base Model ID <span v-if="isFetchingModel" class="text-blue-500 lowercase ml-1">(loading...)</span>
        </label>
        <input
            v-model="baseModelId"
            type="text"
            placeholder="e.g., Qwen/Qwen2.5-3B-Instruct"
            class="px-4 py-3 rounded-xl bg-slate-50 border border-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500 font-medium text-slate-700 h-[50px]"
            :disabled="isFetchingModel"
        />
      </div>

      <EvaluationJudgeSelector
          v-model="selectedJudgeIds"
          :apiUrl="API_URL"
      />

      <!-- Generation Parameters JSON -->
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

      <button @click="handleEvaluate" :disabled="isSubmitDisabled" class="w-full py-4 bg-slate-800 text-white rounded-2xl font-black hover:bg-slate-900 disabled:bg-slate-300 transition-all shadow-lg">
        <span v-if="isGenerating" class="flex items-center justify-center gap-2">
          <svg class="animate-spin h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          Starting background task...
        </span>
        <span v-else>Start Evaluation</span>
      </button>

      <div v-if="generateError" class="mt-6 p-4 bg-red-50 text-red-700 rounded-xl font-medium text-sm border border-red-100">
        {{ generateError }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, computed } from 'vue'
import LoraAdapterSetup from '@/components/LoraAdapterSetup.vue'
import CustomPromptTemplate from '@/components/CustomPromptTemplate.vue'
import EvaluationModeSelector from '@/components/EvaluationModeSelector.vue'
import EvaluationJudgeSelector from '@/components/EvaluationJudgeSelector.vue'

import { useDatasets } from '@/composables/useDatasets'
import { useLoraAdapter } from '@/composables/useLoraAdapter'
import { useLoraEvaluation } from '@/composables/useLoraEvaluation'

const API_URL = import.meta.env.VITE_API_URL || ''

const selectedAdapter = ref(null)
const evaluationMode = ref('prompt')
const prompt = ref('')
const selectedDatasetId = ref('')
const testName = ref('')
const testDescription = ref('')

const useCustomTemplate = ref(false)
const promptTemplate = ref('{input_text}')

const selectedJudgeIds = ref([])

const generationParamsStr = ref(JSON.stringify({
  max_new_tokens: 128,
  temperature: 0.1,
  top_k: 40,
  top_p: 0.9,
  repetition_penalty: 1.15,
  do_sample: true,
  system_prompt: null
}, null, 2))

const jsonError = ref('')

const { datasets, fetchDatasets } = useDatasets(API_URL)
const { baseModelId, isFetchingModel, fetchAdapterDetails } = useLoraAdapter(API_URL)
const { isGenerating, generateError, submitEvaluation } = useLoraEvaluation(API_URL)

onMounted(() => {
  fetchDatasets()
})

watch(selectedAdapter, (newAdapterId) => {
  fetchAdapterDetails(newAdapterId)
})

watch(generationParamsStr, (newValue) => {
  try {
    JSON.parse(newValue)
    jsonError.value = ''
  } catch (e) {
    jsonError.value = 'Invalid JSON format'
  }
})

const isSubmitDisabled = computed(() => {
  if (isGenerating.value || !selectedAdapter.value || !baseModelId.value || jsonError.value || !testName.value) return true;

  if (evaluationMode.value === 'prompt') {
    return !prompt.value;
  } else {
    return !selectedDatasetId.value;
  }
})

const handleEvaluate = async () => {
  if (isSubmitDisabled.value) return

  const parsedParams = JSON.parse(generationParamsStr.value)

  const payload = {
    name: testName.value,
    description: testDescription.value,
    adapter_id: selectedAdapter.value,
    base_model_id: baseModelId.value,
    generation_params: parsedParams,
    judge_ids: selectedJudgeIds.value
  }

  if (useCustomTemplate.value && promptTemplate.value.trim() !== '') {
    payload.prompt_template = promptTemplate.value.trim()
  }

  if (evaluationMode.value === 'prompt') {
    payload.prompt = prompt.value
  } else {
    payload.dataset_id = selectedDatasetId.value
  }

  await submitEvaluation(payload)
}
</script>