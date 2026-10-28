<template>
  <div class="max-w-4xl mx-auto space-y-8 pb-20 p-6">
    <div class="flex items-center mb-6">
      <button @click="$router.push('/judge-tasks')" class="text-sm font-bold text-slate-500 hover:text-slate-800 flex items-center gap-2">
        <span>&larr;</span> Back to Tasks
      </button>
    </div>

    <div>
      <h1 class="text-3xl font-black text-slate-900 tracking-tight">Run Judge Evaluation</h1>
      <p class="text-slate-500 font-medium mt-1">Configure parameters and start an automated judging process.</p>
    </div>

    <div class="bg-white p-8 rounded-[2rem] shadow-sm border border-slate-100">
      <div v-if="isLoadingData" class="text-slate-500 font-medium animate-pulse">
        Loading required data...
      </div>

      <div v-else class="space-y-6">

        <div class="flex flex-col gap-2">
          <label class="text-xs font-black text-slate-400 uppercase tracking-widest">
            Select Evaluation Task <span class="text-red-500">*</span>
          </label>
          <select
              v-model="selectedEvaluationTaskId"
              class="px-4 py-3 rounded-xl bg-slate-50 border border-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500 font-medium text-slate-700 cursor-pointer"
          >
            <option value="" disabled>-- Choose an evaluation task --</option>
            <option v-for="task in availableTasks" :key="task.id" :value="task.id">
              {{ task.name || `Task #${task.id}` }}
            </option>
          </select>
        </div>

        <div class="flex flex-col gap-2">
          <label class="text-xs font-black text-slate-400 uppercase tracking-widest">
            Select Judge Model <span class="text-red-500">*</span>
          </label>
          <select
              v-model="selectedJudgeId"
              class="px-4 py-3 rounded-xl bg-slate-50 border border-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500 font-medium text-slate-700 cursor-pointer"
          >
            <option value="" disabled>-- Choose a judge --</option>
            <option v-for="judge in availableJudges" :key="judge.id" :value="judge.id">
              {{ judge.model_name }}
            </option>
          </select>
        </div>

        <div class="flex flex-col gap-2">
          <label class="text-xs font-black text-slate-400 uppercase tracking-widest">Run Name (Optional)</label>
          <input
              v-model="runName"
              type="text"
              placeholder="e.g. Strict Evaluation Run"
              class="px-4 py-3 rounded-xl bg-slate-50 border border-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500 font-medium text-slate-700"
          />
        </div>

        <div class="flex flex-col gap-2">
          <label class="text-xs font-black text-slate-400 uppercase tracking-widest">Description (Optional)</label>
          <textarea
              v-model="runDescription"
              placeholder="Context or notes about this run..."
              class="px-4 py-3 rounded-xl bg-slate-50 border border-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500 font-medium text-slate-700 min-h-[100px]"
          ></textarea>
        </div>

        <div class="flex flex-col gap-2 mb-6">
          <div class="flex justify-between items-end">
            <label class="text-xs font-black text-slate-400 uppercase tracking-widest">Judge Parameters (JSON)</label>
            <span v-if="jsonError" class="text-xs font-bold text-red-500">{{ jsonError }}</span>
          </div>
          <textarea
              v-model="judgeParamsStr"
              rows="6"
              class="px-4 py-4 rounded-xl bg-slate-50 border focus:outline-none focus:ring-2 resize-y font-mono text-sm text-slate-700"
              :class="jsonError ? 'border-red-300 focus:ring-red-500' : 'border-slate-200 focus:ring-blue-500'"
          ></textarea>
        </div>

        <div v-if="errorMessage" class="p-4 bg-red-50 text-red-700 rounded-xl font-medium text-sm border border-red-100">
          {{ errorMessage }}
        </div>

        <button
            @click="startJudgeRun"
            :disabled="!isFormValid || isSubmitting"
            class="w-full py-4 bg-blue-600 text-white rounded-2xl font-black shadow-lg shadow-blue-600/20 hover:bg-blue-700 disabled:bg-slate-300 transition-all flex items-center justify-center mt-4"
        >
          <span v-if="isSubmitting" class="animate-spin inline-block mr-2">⏳</span>
          {{ isSubmitting ? 'Starting...' : 'Start Evaluation' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const route = useRoute()
const API_URL = import.meta.env.VITE_API_URL || ''

const availableJudges = ref([])
const availableTasks = ref([])
const isLoadingData = ref(false)

const selectedEvaluationTaskId = ref(route.query.taskId ? Number(route.query.taskId) : '')
const selectedJudgeId = ref('')
const runName = ref('')
const runDescription = ref('')

const defaultParams = {
  temperature: 0.0,
  max_new_tokens: 512,
  system_prompt: null
}

const judgeParamsStr = ref(JSON.stringify(defaultParams, null, 2))
const jsonError = ref('')

const isSubmitting = ref(false)
const errorMessage = ref('')

watch(judgeParamsStr, (newValue) => {
  try {
    JSON.parse(newValue)
    jsonError.value = ''
  } catch (e) {
    jsonError.value = 'Invalid JSON format'
  }
})

const isFormValid = computed(() => {
  if (!selectedEvaluationTaskId.value) return false
  if (!selectedJudgeId.value) return false
  if (jsonError.value) return false
  return true
})

const fetchFormData = async () => {
  isLoadingData.value = true
  errorMessage.value = ''

  try {
    const token = localStorage.getItem('token')
    const headers = { 'Authorization': `Bearer ${token}` }

    const params = { size: 100 }

    const [judgesRes, tasksRes] = await Promise.all([
      axios.get(`${API_URL}/llm/judges/`, { headers, params }),

      axios.get(`${API_URL}/llm/judge-runs/evaluation-tasks/`, { headers, params })
    ])

    availableJudges.value = judgesRes.data.items || []

    availableTasks.value = tasksRes.data.tasks || tasksRes.data.items || tasksRes.data || []

  } catch (error) {
    errorMessage.value = 'Failed to load form data.'
    console.error("Fetch form data error:", error)
  } finally {
    isLoadingData.value = false
  }
}

const startJudgeRun = async () => {
  if (!isFormValid.value) return

  isSubmitting.value = true
  errorMessage.value = ''

  try {
    const token = localStorage.getItem('token')

    const payload = {
      evaluation_task_id: selectedEvaluationTaskId.value,
      judge_id: selectedJudgeId.value,
      name: runName.value.trim() || null,
      description: runDescription.value.trim() || null,
      judge_params: JSON.parse(judgeParamsStr.value)
    }

    await axios.post(`${API_URL}/llm/judge-runs/`, payload, {
      headers: { 'Authorization': `Bearer ${token}` }
    })

    router.push('/judge-tasks')
  } catch (error) {
    errorMessage.value = error.response?.data?.detail || 'An error occurred while starting.'
  } finally {
    isSubmitting.value = false
  }
}

onMounted(() => {
  fetchFormData()
})
</script>