<template>
  <div class="space-y-8 pb-12">
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <h1 class="text-3xl font-black text-slate-900 tracking-tight">Base Model Evaluations</h1>
        <p class="text-slate-500 font-medium">Manage and view evaluations for pure base models</p>
      </div>

      <router-link
          to="/base-models-tasks/create"
          class="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2.5 rounded-xl shadow-lg shadow-blue-600/20 transition-all font-bold flex items-center text-sm"
      >
        <span class="mr-2">+</span>
        New Evaluation
      </router-link>
    </div>

    <div class="bg-white rounded-[2.5rem] shadow-xl shadow-slate-200/50 border border-slate-100 overflow-hidden relative">

      <TasksTable
          :tasks="tasks"
          :is-loading="isLoading"
          :resolve-route="(id) => ({ name: 'BaseModelCreateTaskResults', params: { id: id } })"
          @delete="handleDelete"
      />

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import TasksTable from '@/components/TasksTable.vue'

const API_URL = import.meta.env.VITE_API_URL || ''
const tasks = ref([])
const isLoading = ref(false)

const fetchTasks = async () => {
  isLoading.value = true
  try {
    const token = localStorage.getItem('token')
    const response = await axios.get(`${API_URL}/llm/base-models/evaluations/`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    tasks.value = response.data.tasks || []
  } catch (error) {
    console.error('Error fetching base model tasks:', error)
  } finally {
    isLoading.value = false
  }
}

const handleDelete = async (id) => {
  if (confirm(`Are you sure you want to delete evaluation task #${id}?`)) {
    try {
      const token = localStorage.getItem('token')
      await axios.delete(`${API_URL}/llm/base-models/evaluations/${id}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      await fetchTasks()
    } catch (error) {
      alert(error.response?.data?.detail || 'Failed to delete task. It might still be running.')
      console.error(error)
    }
  }
}

onMounted(() => {
  fetchTasks()
})
</script>