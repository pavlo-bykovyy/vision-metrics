<!-- Батьківський компонент (наприклад, EvaluationTasks.vue) -->
<template>
  <div class="w-full px-6 lg:px-8 space-y-6 mt-8 pb-20">
    <div class="flex items-center justify-between">
      <div>
        <h2 class="text-2xl font-black text-slate-900 tracking-tight">Evaluation Tasks</h2>
        <p class="text-slate-500 font-medium mt-1">Monitor the status of your LoRA adapter evaluations.</p>
      </div>
      <button @click="fetchTasks" class="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold rounded-xl transition-colors text-sm">
        Refresh List
      </button>
    </div>

    <div class="bg-white rounded-[2rem] shadow-sm border border-slate-100 overflow-hidden">

      <TasksTable
          :tasks="tasks"
          :is-loading="isLoading"
          :resolve-route="(id) => ({ name: 'LoraTaskResults', params: { id: id } })"
          @delete="deleteTask"
          @cancel="cancelTask"
      />

    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useLoraTasks } from '@/composables/useLoraTasks'
import TasksTable from '@/components/TasksTable.vue'

const API_URL = import.meta.env.VITE_API_URL || ''
const { tasks, isLoading, fetchTasks, deleteTask, cancelTask } = useLoraTasks(API_URL)

onMounted(() => {
  fetchTasks()
})
</script>