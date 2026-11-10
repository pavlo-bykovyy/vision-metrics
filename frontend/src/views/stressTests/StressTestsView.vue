<template>
  <div class="space-y-8 pb-12">
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
      <div>
        <h1 class="text-3xl font-black text-slate-900 tracking-tight">{{ t('stressTests.title') }}</h1>
        <p class="text-slate-500 font-medium">{{ t('stressTests.subtitle') }}</p>
      </div>

      <div class="flex flex-wrap items-center gap-3">
        <button
            @click="fetchRuns(currentPage)"
            class="px-4 py-2.5 bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold rounded-xl transition-colors text-sm"
        >
          {{ t('stressTests.refresh') }}
        </button>
        <router-link
            to="/stress-tests/create"
            class="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2.5 rounded-xl shadow-lg shadow-blue-600/20 transition-all font-bold flex items-center text-sm"
        >
          <span class="mr-2">+</span>
          {{ t('stressTests.newRun') }}
        </router-link>
      </div>
    </div>

    <div v-if="error" class="p-4 bg-red-50 text-red-700 rounded-xl font-medium text-sm border border-red-100">
      {{ error }}
    </div>

    <div class="bg-white rounded-[2.5rem] shadow-xl shadow-slate-200/50 border border-slate-100 overflow-hidden">
      <div class="px-10 py-8 border-b border-slate-50 flex items-center justify-between bg-slate-50/30">
        <h2 class="text-xl font-black text-slate-800 tracking-tight">{{ t('stressTests.allRuns') }}</h2>
        <div class="flex items-center gap-2">
          <div class="w-3 h-3 rounded-full bg-green-500 animate-pulse"></div>
          <span class="text-xs font-bold text-slate-400 uppercase tracking-widest">
            {{ t('stressTests.total') }}: {{ total }}
          </span>
        </div>
      </div>

      <div v-if="!isLoading && runs.length === 0" class="py-12 flex flex-col items-center justify-center text-center">
        <div class="text-6xl mb-4 opacity-50">🧪</div>
        <h3 class="text-lg font-bold text-slate-700">{{ t('stressTests.emptyTitle') }}</h3>
        <p class="text-slate-500 mt-1">{{ t('stressTests.emptyDesc') }}</p>
      </div>

      <div v-else class="overflow-x-auto">
        <table class="w-full text-left border-collapse">
          <thead>
          <tr class="bg-slate-50 text-slate-500 text-sm border-b border-slate-100">
            <th class="p-4 font-semibold">{{ t('stressTests.table.name') }}</th>
            <th class="p-4 font-semibold">{{ t('stressTests.table.status') }}</th>
            <th class="p-4 font-semibold">{{ t('stressTests.table.progress') }}</th>
            <th class="p-4 font-semibold">{{ t('stressTests.table.design') }}</th>
            <th class="p-4 font-semibold">{{ t('stressTests.table.steps') }}</th>
            <th class="p-4 font-semibold">{{ t('stressTests.table.duration') }}</th>
            <th class="p-4 font-semibold text-right">{{ t('stressTests.table.actions') }}</th>
          </tr>
          </thead>
          <tbody>
          <tr v-if="isLoading && runs.length === 0">
            <td colspan="7" class="p-8 text-center text-slate-400 font-medium">{{ t('common.loading') }}</td>
          </tr>

          <tr
              v-for="run in runs"
              :key="run.id"
              class="border-b border-slate-50 hover:bg-slate-50/50 transition-colors group text-sm"
          >
            <td class="p-4 font-bold text-slate-800">
              <router-link
                  :to="`/stress-tests/${run.id}`"
                  class="hover:text-blue-600 hover:underline transition-colors flex items-center gap-1.5 w-fit"
              >
                {{ run.name || `Stress test #${run.id}` }}
                <svg class="w-3.5 h-3.5 text-slate-300 group-hover:text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                </svg>
              </router-link>
              <div class="text-xs text-slate-400 font-medium mt-0.5">{{ formatDate(run.created_at) }}</div>
            </td>

            <td class="p-4">
              <div class="flex flex-col items-start gap-1">
                <span
                    class="flex items-center px-3 py-1 text-[10px] font-black uppercase tracking-wider rounded-full"
                    :class="[getStatusData(run.status).bgClass, getStatusData(run.status).textClass]"
                >
                  <svg v-if="getStatusData(run.status).isSpinning" class="animate-spin -ml-1 mr-2 h-3 w-3" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  {{ t(getStatusData(run.status).labelKey) }}
                </span>
                <span
                    v-if="run.status === 'failed' && run.error_message"
                    class="text-[10px] text-red-500 max-w-[180px] truncate cursor-help"
                    :title="run.error_message"
                >
                  {{ run.error_message }}
                </span>
              </div>
            </td>

            <td class="p-4 min-w-[10rem]">
              <div class="flex items-center gap-3">
                <div class="flex-1 h-2 bg-slate-100 rounded-full overflow-hidden">
                  <div
                      class="h-full rounded-full transition-all duration-500"
                      :class="progressBarClass(run.status)"
                      :style="{ width: `${run.progress || 0}%` }"
                  ></div>
                </div>
                <span class="text-xs font-mono font-bold text-slate-500 w-12 text-right">{{ Math.round(run.progress || 0) }}%</span>
              </div>
              <div v-if="run.stage && isActive(run)" class="text-[10px] font-black text-blue-500 uppercase tracking-widest mt-1">
                {{ t(`stressTests.steps.${run.stage}.title`) }}
              </div>
            </td>

            <td class="p-4 text-xs text-slate-600 font-medium whitespace-nowrap">
              <div><span class="text-slate-400">N</span> <span class="font-mono font-bold">{{ run.config?.n }}</span></div>
              <div><span class="text-slate-400">R</span> <span class="font-mono font-bold">{{ run.config?.replicates }}</span></div>
              <div><span class="text-slate-400">π</span> <span class="font-mono font-bold">{{ (run.config?.prevalences || []).join(', ') }}</span></div>
            </td>

            <td class="p-4">
              <div class="flex flex-wrap gap-1">
                <span
                    v-for="step in run.steps"
                    :key="step"
                    class="px-2 py-0.5 text-[10px] font-bold rounded-md bg-slate-100 text-slate-600 uppercase tracking-wide"
                >
                  {{ step }}
                </span>
              </div>
            </td>

            <td class="p-4 text-xs font-mono font-bold text-slate-500 whitespace-nowrap">
              {{ formatDuration(run.started_at, run.finished_at) }}
            </td>

            <td class="p-4 text-right">
              <div v-if="!isActive(run)" class="flex items-center justify-end gap-2">
                <button
                    @click="handleRerun(run.id)"
                    class="text-xs font-black py-2 px-4 rounded-xl transition-all shadow-sm active:scale-95 whitespace-nowrap bg-blue-50 hover:bg-blue-600 hover:text-white text-blue-600"
                >
                  {{ t('stressTests.actions.rerun') }}
                </button>
                <button
                    @click="handleDelete(run.id)"
                    class="text-xs font-black py-2 px-4 rounded-xl transition-all shadow-sm active:scale-95 whitespace-nowrap bg-red-50 hover:bg-red-600 hover:text-white text-red-600"
                >
                  {{ t('common.delete') }}
                </button>
              </div>
              <div v-else class="flex items-center justify-end">
                <button
                    @click="handleCancel(run.id)"
                    class="text-xs font-black py-2 px-3 rounded-xl transition-all shadow-sm active:scale-95 whitespace-nowrap bg-orange-50 hover:bg-orange-500 hover:text-white text-orange-600"
                >
                  {{ t('common.cancel') }}
                </button>
              </div>
            </td>
          </tr>
          </tbody>
        </table>
      </div>

      <div v-if="totalPages > 1" class="px-10 py-6 border-t border-slate-50 flex items-center justify-between">
        <button
            :disabled="currentPage <= 1"
            @click="fetchRuns(currentPage - 1)"
            class="px-4 py-2 rounded-xl text-sm font-bold bg-slate-100 text-slate-600 hover:bg-slate-200 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
        >
          &larr;
        </button>
        <span class="text-sm font-bold text-slate-500">{{ t('pagination.page') }} {{ currentPage }} / {{ totalPages }}</span>
        <button
            :disabled="currentPage >= totalPages"
            @click="fetchRuns(currentPage + 1)"
            class="px-4 py-2 rounded-xl text-sm font-bold bg-slate-100 text-slate-600 hover:bg-slate-200 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
        >
          &rarr;
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useStressTests, stressTestsApi } from '@/composables/useStressTests'
import { getStatusData } from '@/constants/evaluationStatuses'
import { ACTIVE_STATUSES, formatDuration } from '@/constants/stressTests'

const { t, locale } = useI18n()
const router = useRouter()
const { runs, currentPage, totalPages, total, isLoading, error, fetchRuns } = useStressTests()

const isActive = (run) => ACTIVE_STATUSES.includes(run.status)

const progressBarClass = (status) => ({
  completed: 'bg-green-500',
  failed: 'bg-red-500',
  canceled: 'bg-orange-400',
}[status] || 'bg-blue-500')

const formatDate = (value) => {
  if (!value) return '—'
  return new Date(value).toLocaleString(locale.value === 'uk' ? 'uk-UA' : 'en-US', {
    day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit',
  })
}

const handleRerun = async (id) => {
  try {
    const run = await stressTestsApi.rerun(id)
    router.push(`/stress-tests/${run.id}`)
  } catch (e) {
    alert(e.message)
  }
}

const handleCancel = async (id) => {
  if (!confirm(t('stressTests.confirmCancel'))) return
  try {
    await stressTestsApi.cancel(id)
    await fetchRuns(currentPage.value, { silent: true })
  } catch (e) {
    alert(e.message)
  }
}

const handleDelete = async (id) => {
  if (!confirm(t('stressTests.confirmDelete'))) return
  try {
    await stressTestsApi.remove(id)
    const page = runs.value.length === 1 && currentPage.value > 1 ? currentPage.value - 1 : currentPage.value
    await fetchRuns(page)
  } catch (e) {
    alert(e.message)
  }
}

let pollingInterval = null

onMounted(() => {
  fetchRuns(1)
  pollingInterval = setInterval(() => fetchRuns(currentPage.value, { silent: true }), 5000)
})

onUnmounted(() => {
  if (pollingInterval) clearInterval(pollingInterval)
})
</script>
