<template>
  <div>
    <!-- Empty State -->
    <div v-if="evaluations.length === 0" class="py-12 flex flex-col items-center justify-center text-center">
      <div class="text-6xl mb-4 opacity-50">📁</div>
      <h3 class="text-lg font-bold text-slate-700">{{ t('runsTable.noEvaluationsTitle') || 'No Evaluations Found' }}</h3>
      <p class="text-slate-500 mt-1">{{ t('runsTable.noEvaluationsDesc') || 'Start your first evaluation to see the results here.' }}</p>
    </div>

    <!-- Table -->
    <div v-else class="overflow-x-auto">
      <table class="w-full text-left border-collapse">
        <thead>
        <tr class="bg-slate-50 text-slate-500 text-sm border-b border-slate-100">
          <th class="p-4 font-semibold rounded-tl-xl">{{ t('runsTable.name') || 'Evaluation Name' }}</th>
          <th class="p-4 font-semibold">{{ t('runsTable.status') || 'Status' }}</th>
          <th class="p-4 font-semibold">{{ t('runsTable.accuracy') || 'Accuracy' }}</th>
          <th class="p-4 font-semibold">{{ t('runsTable.precision') || 'Precision' }}</th>
          <th class="p-4 font-semibold">{{ t('runsTable.recall') || 'Recall' }}</th>
          <th class="p-4 font-semibold">{{ t('runsTable.f1Score') || 'F1 Score' }}</th>
          <th class="p-4 font-semibold">{{ t('runsTable.rocAuc') || 'ROC AUC' }}</th>
          <th class="p-4 font-semibold">{{ t('runsTable.confMatrix') || 'Matrix' }}</th>
          <th class="p-4 font-semibold text-right rounded-tr-xl">{{ t('runsTable.action') || 'Action' }}</th>
        </tr>
        </thead>
        <tbody>
        <tr
            v-for="evaluation in evaluations"
            :key="evaluation.id"
            class="border-b border-slate-50 hover:bg-slate-50/50 transition-colors group text-sm"
        >
          <td class="p-4 font-bold text-slate-800">
            <router-link
                :to="`/evaluations/${evaluation.id}`"
                class="hover:text-blue-600 hover:underline transition-colors flex items-center gap-1.5 w-fit"
            >
              {{ evaluation.name || `Evaluation #${evaluation.id}` }}
              <svg class="w-3.5 h-3.5 text-slate-300 group-hover:text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
              </svg>
            </router-link>
          </td>

          <td class="p-4">
            <div class="flex flex-col items-start gap-1">
              <span
                  class="flex items-center px-3 py-1 text-[10px] font-black uppercase tracking-wider rounded-full"
                  :class="[getStatusData(evaluation.status).bgClass, getStatusData(evaluation.status).textClass]"
              >
                <svg v-if="getStatusData(evaluation.status).isSpinning" class="animate-spin -ml-1 mr-2 h-3 w-3" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>

                {{ t(getStatusData(evaluation.status).labelKey) || getStatusData(evaluation.status).fallbackLabel }}
              </span>

              <span
                  v-if="evaluation.status?.toLowerCase() === 'failed' && evaluation.error_message"
                  class="text-[10px] text-red-500 max-w-[150px] truncate cursor-help"
                  :title="evaluation.error_message"
              >
                {{ evaluation.error_message }}
              </span>
            </div>
          </td>

          <td class="p-4 text-slate-600 font-mono font-bold">{{ evaluation.metrics ? (evaluation.metrics.accuracy * 100).toFixed(1) + '%' : '—' }}</td>
          <td class="p-4 text-slate-600 font-mono font-bold">{{ evaluation.metrics ? (evaluation.metrics.precision * 100).toFixed(1) + '%' : '—' }}</td>
          <td class="p-4 text-slate-600 font-mono font-bold">{{ evaluation.metrics ? (evaluation.metrics.recall * 100).toFixed(1) + '%' : '—' }}</td>
          <td class="p-4 text-slate-600 font-mono font-bold">{{ evaluation.metrics ? (evaluation.metrics.f1_score * 100).toFixed(1) + '%' : '—' }}</td>
          <td class="p-4 text-slate-600 font-mono font-bold">{{ evaluation.metrics ? (evaluation.metrics.roc_auc * 100).toFixed(1) + '%' : '—' }}</td>

          <td class="p-4">
            <div v-if="evaluation.metrics" class="flex flex-col gap-1">
              <div class="grid grid-cols-2 gap-px w-14 bg-slate-200 border border-slate-200 rounded overflow-hidden shadow-sm">
                <div title="TN (True Negative)" class="bg-white text-[9px] text-center p-0.5 text-slate-400">{{ evaluation.metrics.tn }}</div>
                <div title="FP (False Positive)" class="bg-red-50 text-[9px] text-center p-0.5 text-red-600 font-bold">{{ evaluation.metrics.fp }}</div>
                <div title="FN (False Negative)" class="bg-orange-50 text-[9px] text-center p-0.5 text-orange-600 font-bold">{{ evaluation.metrics.fn }}</div>
                <div title="TP (True Positive)" class="bg-green-50 text-[9px] text-center p-0.5 text-green-600 font-bold">{{ evaluation.metrics.tp }}</div>
              </div>
            </div>
            <span v-else class="text-slate-300">—</span>
          </td>

          <!-- Actions -->
          <td class="p-4 text-right">
            <div v-if="!getStatusData(evaluation.status).isActive" class="flex items-center justify-end gap-2">
              <button
                  @click="$emit('reevaluate', evaluation.id)"
                  class="text-xs font-black py-2 px-4 rounded-xl transition-all shadow-sm active:scale-95 whitespace-nowrap bg-blue-50 hover:bg-blue-600 hover:text-white text-blue-600"
              >
                {{ t('runsTable.reevaluate') || 'Reevaluate' }}
              </button>

              <button
                  @click="$emit('delete', evaluation.id)"
                  class="text-xs font-black py-2 px-4 rounded-xl transition-all shadow-sm active:scale-95 whitespace-nowrap bg-red-50 hover:bg-red-600 hover:text-white text-red-600"
              >
                {{ t('common.delete') || 'Delete' }}
              </button>
            </div>

            <div v-else class="flex items-center justify-end gap-3">
              <div class="flex items-center text-blue-500 text-xs font-black animate-pulse">
                <svg class="animate-spin h-3 w-3 mr-1" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                {{ t(getStatusData(evaluation.status).labelKey).toUpperCase() || getStatusData(evaluation.status).fallbackLabel.toUpperCase() }}
              </div>

              <button
                  @click="$emit('cancel', evaluation.id)"
                  class="text-xs font-black py-2 px-3 rounded-xl transition-all shadow-sm active:scale-95 whitespace-nowrap bg-orange-50 hover:bg-orange-500 hover:text-white text-orange-600"
              >
                {{ t('common.cancel') || 'Cancel' }}
              </button>
            </div>
          </td>
        </tr>
        </tbody>
      </table>
    </div>

    <!-- Pagination -->
    <div v-if="totalPages > 1" class="px-6 py-4 bg-slate-50/50 border-t border-slate-100 flex items-center justify-between">
      <div class="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em]">
        {{ t('pagination.page') || 'Сторінка' }} {{ currentPage }} / {{ totalPages }}
      </div>
      <div class="flex items-center gap-2">
        <button
            @click="$emit('page-change', currentPage - 1)"
            :disabled="currentPage === 1"
            class="p-2 rounded-xl border border-slate-200 bg-white hover:bg-slate-50 disabled:opacity-30 disabled:cursor-not-allowed transition-all shadow-sm"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" /></svg>
        </button>

        <div class="flex items-center gap-1">
          <button
              v-for="p in visiblePages" :key="p"
              @click="$emit('page-change', p)"
              class="w-8 h-8 rounded-lg text-[11px] font-black transition-all"
              :class="p === currentPage ? 'bg-blue-600 text-white shadow-lg shadow-blue-500/30' : 'bg-white border border-slate-100 text-slate-500 hover:bg-slate-50'"
          >
            {{ p }}
          </button>
        </div>

        <button
            @click="$emit('page-change', currentPage + 1)"
            :disabled="currentPage === totalPages"
            class="p-2 rounded-xl border border-slate-200 bg-white hover:bg-slate-50 disabled:opacity-30 disabled:cursor-not-allowed transition-all shadow-sm"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" /></svg>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { getStatusData } from '@/constants/evaluationStatuses'

const { t } = useI18n()

const props = defineProps({
  evaluations: { type: Array, required: true },
  currentPage: { type: Number, default: 1 },
  totalPages: { type: Number, default: 1 }
})

const emit = defineEmits(['page-change', 'reevaluate', 'delete', 'cancel'])

const visiblePages = computed(() => {
  const pages = []
  for (let i = 1; i <= props.totalPages; i++) {
    pages.push(i)
  }
  return pages
})
</script>