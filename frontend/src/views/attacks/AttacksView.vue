<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAttacks } from '@/composables/useAttacks'

const router = useRouter()
const { t, locale } = useI18n()

const API_URL = import.meta.env.VITE_API_URL || '/api'
const attacksApi = useAttacks(API_URL)

const tasks = ref([])
const isLoading = ref(false)

async function fetchTasks() {
  isLoading.value = true
  try {
    const response = await attacksApi.listTasks()
    tasks.value = Array.isArray(response) ? response : (response?.items || response?.tasks || [])
  } catch (e) {
    console.error('Помилка завантаження атак:', e)
  } finally {
    isLoading.value = false
  }
}


function goToRunAttack() {
  router.push('/attacks/run')
}

function openResults(id) {
  router.push(`/attacks/${id}`)
}

function formatDate(dateString) {
  if (!dateString) return '—'
  const date = new Date(dateString)
  const currentLocale = locale.value === 'uk' ? 'uk-UA' : 'en-US'
  return date.toLocaleString(currentLocale, {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

onMounted(() => {
  fetchTasks()
})
</script>

<template>
  <div class="space-y-8 pb-12 px-4 md:px-8 mt-8">
    <!-- Top Header -->
    <div class="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
      <div>
        <h1 class="text-3xl font-black text-slate-900 tracking-tight">
          {{ t('attacks.title') }}
        </h1>
        <p class="text-slate-500 font-medium mt-1">
          {{ t('attacks.subtitle') }}
        </p>
      </div>

      <div class="flex flex-wrap items-center gap-3">
        <button
            @click="fetchTasks"
            class="px-4 py-2.5 bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold rounded-xl transition-colors text-sm"
        >
          {{ t('attacks.refresh') }}
        </button>

        <button
            @click="goToRunAttack"
            class="px-4 py-2.5 bg-blue-600 hover:bg-blue-700 text-white shadow-lg shadow-blue-600/20 font-bold rounded-xl transition-all text-sm flex items-center gap-2"
        >
          <span>+</span> Запустити атаку (LoRA / Base Model)
        </button>

      </div>
    </div>

    <!-- Attack Evaluation Runs Table -->
    <div class="bg-white rounded-[2.5rem] shadow-xl shadow-slate-200/50 border border-slate-100 overflow-hidden relative">
      <div class="px-8 py-6 border-b border-slate-50 flex items-center justify-between bg-slate-50/30">
        <h2 class="text-xl font-black text-slate-800 tracking-tight">
          {{ t('attacks.runsTitle') }}
        </h2>
        <span class="text-xs font-bold text-slate-400 uppercase tracking-widest">
          {{ t('attacks.total') }}: {{ tasks.length }}
        </span>
      </div>

      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse">
          <thead>
          <tr class="bg-slate-50 border-b border-slate-100">
            <th class="px-6 py-4 text-xs font-black text-slate-400 uppercase tracking-widest">
              {{ t('attacks.table.id') }}
            </th>
            <th class="px-6 py-4 text-xs font-black text-slate-400 uppercase tracking-widest">
              {{ t('attacks.table.taskName') }}
            </th>
            <th class="px-6 py-4 text-xs font-black text-slate-400 uppercase tracking-widest">
              Ціль (LoRA / Base)
            </th>
            <th class="px-6 py-4 text-xs font-black text-slate-400 uppercase tracking-widest">
              {{ t('attacks.table.status') }}
            </th>
            <th class="px-6 py-4 text-xs font-black text-slate-400 uppercase tracking-widest text-right">
              {{ t('attacks.table.date') }}
            </th>
            <th class="px-6 py-4 text-xs font-black text-slate-400 uppercase tracking-widest text-right">
              {{ t('attacks.table.actions') }}
            </th>
          </tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
          <tr v-if="isLoading">
            <td colspan="6" class="px-6 py-8 text-center text-slate-400 font-medium">
              {{ t('attacks.table.loading') }}
            </td>
          </tr>

          <tr v-else-if="tasks.length === 0">
            <td colspan="6" class="px-6 py-8 text-center text-slate-400 font-medium">
              {{ t('attacks.table.noTasks') }}
            </td>
          </tr>

          <tr v-for="task in tasks" :key="task.id" class="hover:bg-slate-50 transition-colors">
            <td class="px-6 py-4 font-mono font-bold text-slate-400">#{{ task.id }}</td>

            <td class="px-6 py-4">
              <button @click="openResults(task.id)" class="text-left group">
                <div class="font-bold text-slate-800 group-hover:text-blue-600 transition-colors flex items-center gap-1.5">
                  {{ task.name || t('attacks.table.defaultTaskName', { id: task.id }) }}
                  <svg class="w-3.5 h-3.5 text-slate-300 group-hover:text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                  </svg>
                </div>
              </button>
            </td>

            <td class="px-6 py-4 text-xs font-semibold text-slate-600">
              <span
                  v-if="task.adapter_id"
                  class="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-purple-50 text-purple-700 border border-purple-200"
              >
                🔌 LoRA #{{ task.adapter_id }}
              </span>
              <span
                  v-else-if="task.base_model_to_use"
                  class="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-slate-100 text-slate-700 border border-slate-200 font-mono"
              >
                📦 {{ task.base_model_to_use }}
              </span>
              <span v-else class="text-slate-400">—</span>
            </td>

            <td class="px-6 py-4">
              <span class="px-3 py-1 text-xs font-bold rounded-full uppercase tracking-wide bg-blue-50 text-blue-600">
                {{ task.status || t('attacks.table.completed') }}
              </span>
            </td>

            <td class="px-6 py-4 text-sm font-medium text-slate-600 text-right whitespace-nowrap">
              {{ formatDate(task.created_at) }}
            </td>

            <td class="px-6 py-4 text-right">
              <button
                  @click="openResults(task.id)"
                  class="px-3 py-1.5 text-xs font-bold text-blue-600 bg-blue-50 hover:bg-blue-100 rounded-lg transition-colors"
              >
                {{ t('attacks.table.results') }}
              </button>
            </td>
          </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>