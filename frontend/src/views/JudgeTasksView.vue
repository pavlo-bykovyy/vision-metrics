<template>
  <div class="space-y-8 pb-12 px-4 md:px-8 mt-8">
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <h1 class="text-3xl font-black text-slate-900 tracking-tight">Judge Tasks</h1>
        <p class="text-slate-500 font-medium">Manage and monitor automated judge evaluations.</p>
      </div>

      <div class="flex flex-col sm:items-end gap-2">
        <router-link
            to="/judge-tasks/create"
            class="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2.5 rounded-xl shadow-lg shadow-blue-600/20 transition-all font-bold flex items-center justify-center text-sm w-full sm:w-auto"
        >
          <span class="mr-2">+</span>
          Create Judge Test
        </router-link>

        <button
            @click="fetchTasks"
            class="bg-slate-100 hover:bg-slate-200 text-slate-700 px-6 py-2.5 rounded-xl transition-all font-bold text-sm w-full sm:w-auto text-center"
        >
          Refresh List
        </button>
      </div>
    </div>

    <div class="bg-white rounded-[2.5rem] shadow-xl shadow-slate-200/50 border border-slate-100 overflow-hidden relative">
      <TasksTable
          :tasks="tasks"
          :is-loading="isLoading"
          :resolve-route="(id) => ({ name: 'JudgeTaskResults', params: { id: id } })"
          @delete="handleDelete"
          @cancel="handleCancel"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import axios from 'axios'
import TasksTable from '@/components/TasksTable.vue'

const API_URL = import.meta.env.VITE_API_URL || ''
const tasks = ref([])
const isLoading = ref(false)
let pollingInterval = null

const getHeaders = () => {
  const token = localStorage.getItem('token')
  return token ? { 'Authorization': `Bearer ${token}` } : {}
}

const fetchTasks = async () => {
  isLoading.value = true
  try {
    const response = await axios.get(`${API_URL}/llm/judge-runs/`, {
      headers: getHeaders()
    })

    tasks.value = response.data.items || response.data.tasks || response.data || []
  } catch (error) {
    console.error('Error fetching judge tasks:', error)
  } finally {
    isLoading.value = false
  }
}

const handleDelete = async (id) => {
  if (confirm(`Are you sure you want to delete judge task #${id}?`)) {
    try {
      await axios.delete(`${API_URL}/llm/judge-runs/${id}`, {
        headers: getHeaders()
      })
      await fetchTasks()
    } catch (error) {
      alert(error.response?.data?.detail || 'Failed to delete task. It might still be running.')
      console.error(error)
    }
  }
}

const handleCancel = async (id) => {
  if (confirm(`Are you sure you want to cancel judge task #${id}?`)) {
    try {
      await axios.post(`${API_URL}/llm/judge-runs/${id}/cancel`, {}, {
        headers: getHeaders()
      })
      await fetchTasks()
    } catch (error) {
      alert(error.response?.data?.detail || 'Failed to cancel task.')
      console.error(error)
    }
  }
}

const startPolling = () => {
  if (!pollingInterval) {
    pollingInterval = setInterval(() => {
      fetchTasks()
    }, 5000)
  }
}

const stopPolling = () => {
  if (pollingInterval) {
    clearInterval(pollingInterval)
    pollingInterval = null
  }
}

onMounted(() => {
  fetchTasks()
  startPolling()
})

onUnmounted(() => {
  stopPolling()
})
</script>