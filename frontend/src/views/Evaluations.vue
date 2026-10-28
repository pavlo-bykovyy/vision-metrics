<template>
  <div class="space-y-8 pb-12">
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
      <div>
        <h1 class="text-3xl font-black text-slate-900 tracking-tight">{{ t('evaluation.title') || 'Evaluations' }}</h1>
        <p class="text-slate-500 font-medium">{{ t('evaluation.historySubtitle') || 'History of all test runs' }}</p>
      </div>

      <router-link
          to="/evaluations/create"
          class="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2.5 rounded-xl shadow-lg shadow-blue-600/20 transition-all font-bold flex items-center text-sm"
      >
        <span class="mr-2">+</span>
        {{ t('evaluation.startTestBtn') || 'Start New Test' }}
      </router-link>
    </div>

    <div class="bg-white rounded-[2.5rem] shadow-xl shadow-slate-200/50 border border-slate-100 overflow-hidden">
      <div class="px-10 py-8 border-b border-slate-50 flex items-center justify-between bg-slate-50/30">
        <h2 class="text-xl font-black text-slate-800 tracking-tight">{{ t('evaluation.allEvaluations') || 'All Evaluations' }}</h2>
        <div class="flex gap-2">
          <div class="w-3 h-3 rounded-full bg-green-500 animate-pulse"></div>
          <span class="text-xs font-bold text-slate-400 uppercase tracking-widest">{{ t('evaluation.liveUpdates') || 'Live Updates' }}</span>
        </div>
      </div>
      <RunsTable
          :evaluations="evaluations"
          :current-page="currentPage"
          :total-pages="totalPages"
          @page-change="handlePageChange"
          @reevaluate="handleReevaluate"
          @delete="handleDelete"
          @cancel="handleCancel"
      />
    </div>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import RunsTable from '@/components/RunsTable.vue'
import { useEvaluations } from '@/composables/useEvaluations'

const { t } = useI18n()

const {
  evaluations,
  currentPage,
  totalPages,
  fetchEvaluations,
  triggerReevaluate,
  deleteEvaluation,
  cancelEvaluation
} = useEvaluations()

let pollingInterval = null

const startPolling = () => {
  pollingInterval = setInterval(() => {
    fetchEvaluations(currentPage.value)
  }, 5000)
}

const stopPolling = () => {
  if (pollingInterval) {
    clearInterval(pollingInterval)
    pollingInterval = null
  }
}

const handlePageChange = (newPage) => {
  fetchEvaluations(newPage)
}

const handleReevaluate = async (id) => {
  try {
    await triggerReevaluate(id)
    await fetchEvaluations(currentPage.value)
  } catch (error) {
    console.error("Failed to re-evaluate.")
  }
}

const handleDelete = async (id) => {
  const confirmMessage = t('evaluation.confirmDelete') || 'Are you sure you want to delete this evaluation?'

  if (confirm(confirmMessage)) {
    try {
      await deleteEvaluation(id)

      if (evaluations.value?.length === 1 && currentPage.value > 1) {
        await fetchEvaluations(currentPage.value - 1)
      } else {
        await fetchEvaluations(currentPage.value)
      }
    } catch (error) {
      console.error("Failed to delete.", error)
    }
  }
}

const handleCancel = async (id) => {
  const confirmMessage = t('evaluation.confirmCancel') || 'Are you sure you want to cancel this ongoing evaluation?'

  if (confirm(confirmMessage)) {
    try {
      await cancelEvaluation(id)
      await fetchEvaluations(currentPage.value)
    } catch (error) {
      console.error("Failed to cancel evaluation.", error)
      alert("Could not cancel the evaluation. It may have already finished or failed.")
    }
  }
}

onMounted(() => {
  fetchEvaluations()
  startPolling()
})

onUnmounted(() => {
  stopPolling()
})
</script>