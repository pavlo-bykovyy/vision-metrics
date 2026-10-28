<template>
  <div class="max-w-4xl mx-auto space-y-8 pb-20 p-6">
    <div class="flex items-center mb-6">
      <button @click="$router.push('/judges')" class="text-sm font-bold text-slate-500 hover:text-slate-800 flex items-center gap-2">
        <span>&larr;</span> Back to Judges
      </button>
    </div>

    <div>
      <h1 class="text-3xl font-black text-slate-900 tracking-tight">Register New Judge</h1>
      <p class="text-slate-500 font-medium mt-1">Add a new LLM model to your registry of automated judges.</p>
    </div>

    <div class="bg-white p-8 rounded-[2rem] shadow-sm border border-slate-100">
      <div class="space-y-6">
        <div class="flex flex-col gap-2">
          <label class="text-xs font-black text-slate-400 uppercase tracking-widest">
            Model Name (Identifier)
          </label>
          <input
              v-model="modelName"
              type="text"
              placeholder="e.g. gpt-4-turbo"
              class="px-4 py-3 rounded-xl bg-slate-50 border focus:outline-none focus:ring-2 font-medium text-slate-700 transition-all"
              :class="errorMessage ? 'border-red-300 focus:ring-red-500' : 'border-slate-200 focus:ring-blue-500'"
              @input="errorMessage = ''"
          />
        </div>

        <div class="flex flex-col gap-2">
          <label class="text-xs font-black text-slate-400 uppercase tracking-widest">
            Display Name (Optional)
          </label>
          <input
              v-model="name"
              type="text"
              placeholder="e.g. GPT-4 Strict Evaluator"
              class="px-4 py-3 rounded-xl bg-slate-50 border border-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500 font-medium text-slate-700"
          />
        </div>

        <div class="flex flex-col gap-2">
          <label class="text-xs font-black text-slate-400 uppercase tracking-widest">
            Description (Optional)
          </label>
          <textarea
              v-model="description"
              placeholder="Short description of this judge..."
              class="px-4 py-3 rounded-xl bg-slate-50 border border-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500 font-medium text-slate-700 min-h-[100px]"
          ></textarea>
        </div>

        <div v-if="errorMessage" class="p-4 bg-red-50 text-red-700 rounded-xl font-medium text-sm border border-red-100">
          {{ errorMessage }}
        </div>

        <button
            @click="saveJudge"
            :disabled="!modelName.trim() || isSubmitting"
            class="w-full py-4 bg-blue-600 text-white rounded-2xl font-black shadow-lg shadow-blue-600/20 hover:bg-blue-700 disabled:bg-slate-300 transition-all flex items-center justify-center mt-4"
        >
          <span v-if="isSubmitting" class="animate-spin inline-block mr-2">⏳</span>
          {{ isSubmitting ? 'Saving...' : 'Add to Registry' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const API_URL = import.meta.env.VITE_API_URL || ''

const modelName = ref('')
const name = ref('')
const description = ref('')
const isSubmitting = ref(false)
const errorMessage = ref('')

const saveJudge = async () => {
  if (!modelName.value.trim()) return
  isSubmitting.value = true
  errorMessage.value = ''

  try {
    const token = localStorage.getItem('token')

    const payload = {
      model_name: modelName.value.trim(),
      name: name.value.trim() || null,
      description: description.value.trim() || null
    }

    await axios.post(`${API_URL}/llm/judges/`, payload, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    router.push('/judges')
  } catch (error) {
    errorMessage.value = error.response?.data?.detail || 'An error occurred while saving the judge.'
  } finally {
    isSubmitting.value = false
  }
}
</script>