<template>
  <div class="flex flex-col gap-2 mb-6">
    <label class="text-xs font-black text-slate-400 uppercase tracking-widest">Select Judges (Optional)</label>
    <div class="p-4 rounded-xl bg-slate-50 border border-slate-200 min-h-[60px]">

      <p v-if="isLoading" class="text-sm text-blue-500 font-medium animate-pulse">
        Loading judges from API...
      </p>

      <p v-else-if="error" class="text-sm text-red-500 font-medium mb-3">
        {{ error }}
      </p>

      <div v-else-if="judges.length > 0" class="flex flex-col gap-3">
        <label v-for="judge in judges" :key="judge.id" class="flex items-center gap-3 cursor-pointer group">
          <input
              type="checkbox"
              :value="judge.id"
              :checked="modelValue.includes(judge.id)"
              @change="updateSelection(judge.id, $event.target.checked)"
              class="w-5 h-5 text-blue-600 bg-white border-slate-300 rounded focus:ring-blue-500 focus:ring-2"
          />
          <span class="font-medium text-slate-700 group-hover:text-slate-900">{{ judge.name }}</span>
        </label>
      </div>

      <p v-else class="text-sm text-slate-500 font-medium">
        No judges available in the system.
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const props = defineProps({
  modelValue: {
    type: Array,
    default: () => []
  },
  apiUrl: {
    type: String,
    required: true
  }
})

const emit = defineEmits(['update:modelValue'])

const judges = ref([])
const isLoading = ref(false)
const error = ref('')

const fetchJudges = async () => {
  isLoading.value = true
  error.value = ''

  try {
    const token = localStorage.getItem('token')
    const response = await axios.get(`${props.apiUrl}/llm/judges/`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })

    judges.value = Array.isArray(response.data)
        ? response.data
        : (response.data?.items || response.data?.data || [])

  } catch (err) {
    console.error('Failed to fetch judges from API:', err)
    error.value = 'API failed. Using hardcoded mock list for testing.'

    judges.value = [
      { id: 1, name: 'LLM as a Judge (Qwen 2.5 Coder)' },
      { id: 2, name: 'Accuracy Evaluator (Rule-based)' },
      { id: 3, name: 'Toxicity Checker' }
    ]
  } finally {
    isLoading.value = false
  }
}

const updateSelection = (id, checked) => {
  const updated = [...props.modelValue]
  if (checked) {
    updated.push(id)
  } else {
    const index = updated.indexOf(id)
    if (index > -1) updated.splice(index, 1)
  }
  emit('update:modelValue', updated)
}

onMounted(() => {
  fetchJudges()
})
</script>