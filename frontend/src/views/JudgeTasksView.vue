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
          :resolve-route="(id) => `/judge-tasks/${id}/results`"
          @delete="handleDelete"
          @cancel="handleCancel"
      />
    </div>
  </div>
</template>

<script setup>
import TasksTable from '@/components/TasksTable.vue'
import { useTaskList } from '@/composables/useTaskList'

const { tasks, isLoading, fetchTasks, handleDelete, handleCancel } =
    useTaskList('/llm/judge-runs', { label: 'judge task' })
</script>