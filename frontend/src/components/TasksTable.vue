<template>
  <div class="overflow-x-auto">
    <table class="w-full text-left border-collapse">
      <thead>
      <tr class="bg-slate-50 border-b border-slate-100">
        <th class="px-6 py-4 text-xs font-black text-slate-400 uppercase tracking-widest">ID</th>
        <th class="px-6 py-4 text-xs font-black text-slate-400 uppercase tracking-widest">Name</th>
        <th class="px-6 py-4 text-xs font-black text-slate-400 uppercase tracking-widest">Status</th>
        <th class="px-6 py-4 text-xs font-black text-slate-400 uppercase tracking-widest">Result / Error</th>
        <th class="px-6 py-4 text-xs font-black text-slate-400 uppercase tracking-widest text-right">Date Created</th>
        <th class="px-6 py-4 text-xs font-black text-slate-400 uppercase tracking-widest text-right">Actions</th>
      </tr>
      </thead>
      <tbody class="divide-y divide-slate-100">
      <tr v-if="isLoading && tasks.length === 0">
        <td colspan="6" class="px-6 py-8 text-center text-slate-400 font-medium">Loading tasks...</td>
      </tr>
      <tr v-else-if="tasks.length === 0">
        <td colspan="6" class="px-6 py-8 text-center text-slate-400 font-medium">No tasks found. Start an evaluation first.</td>
      </tr>

      <tr v-for="task in tasks" :key="task.id" class="hover:bg-slate-50 transition-colors">
        <td class="px-6 py-4">
          <router-link
              :to="resolveRoute(task.id)"
              class="font-mono text-sm text-slate-500 hover:text-blue-600 transition-colors"
              title="View Details"
          >
            {{ task.id }}
          </router-link>
        </td>

        <td class="px-6 py-4">
          <router-link
              :to="resolveRoute(task.id)"
              class="group flex flex-col w-fit"
          >
            <div class="font-bold text-slate-800 group-hover:text-blue-600 flex items-center gap-1.5 transition-colors">
              {{ task.name || 'Unnamed Task' }}
              <svg class="w-3.5 h-3.5 text-slate-300 group-hover:text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
              </svg>
            </div>
            <span v-if="task.description" class="text-xs text-slate-500 mt-0.5 truncate max-w-[200px]" :title="task.description">
              {{ task.description }}
            </span>
          </router-link>
        </td>

        <td class="px-6 py-4">
          <span
              class="px-3 py-1 text-xs font-bold rounded-full uppercase tracking-wide inline-flex items-center"
              :class="[getStatusData(task.status)?.bgClass, getStatusData(task.status)?.textClass]"
          >
            <span v-if="getStatusData(task.status)?.isActive" class="inline-block animate-pulse mr-1">●</span>
            {{ getStatusData(task.status)?.fallbackLabel || task.status }}
          </span>
        </td>

        <td class="px-6 py-4 text-sm font-medium text-slate-700 max-w-md truncate">
          <span v-if="task.status === 'completed'" class="text-slate-700" :title="task.result">
            {{ task.result }}
          </span>
          <span v-else-if="task.status === 'failed'" class="text-red-500" :title="task.error_message">
                {{ task.error_message }}
              </span>
          <span v-else class="text-slate-400 italic">Waiting for completion...</span>
        </td>

        <td class="px-6 py-4 text-sm font-medium text-slate-600 whitespace-nowrap text-right">
          {{ formatDate(task.created_at) }}
        </td>

        <td class="px-6 py-4 text-right">
          <div v-if="!getStatusData(task.status)?.isActive" class="flex justify-end gap-2">
            <button
                @click="$emit('delete', task.id)"
                class="text-red-600 hover:text-red-800 font-bold text-xs bg-red-50 hover:bg-red-100 px-3 py-2 rounded-lg transition-colors"
                title="Remove this task"
            >
              Delete
            </button>
          </div>
          <div v-else class="flex justify-end">
            <button
                @click="$emit('cancel', task.id)"
                class="text-orange-600 hover:text-orange-800 font-bold text-xs bg-orange-50 hover:bg-orange-100 px-3 py-2 rounded-lg transition-colors"
                title="Cancel this running evaluation"
            >
              Cancel
            </button>
          </div>
        </td>
      </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue'
import { getStatusData } from "@/constants/evaluationStatuses.js"

const props = defineProps({
  tasks: {
    type: Array,
    required: true,
    default: () => []
  },
  isLoading: {
    type: Boolean,
    default: false
  },
  resolveRoute: {
    type: Function,
    default: (id) => `/lora-tasks/${id}/results`
  }
})

const emit = defineEmits(['delete', 'cancel'])

const formatDate = (isoString) => {
  if (!isoString) return '—'
  const date = new Date(isoString)
  return date.toLocaleString('en-GB', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>