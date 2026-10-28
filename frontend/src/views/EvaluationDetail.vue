<template>
  <div class="space-y-8 pb-12">

    <!-- Header Section -->
    <div class="flex flex-col md:flex-row md:items-start justify-between gap-4">
      <div>
        <button @click="$router.push('/evaluations')" class="text-sm font-bold text-slate-500 hover:text-slate-800 flex items-center gap-2 mb-4">
          <span>&larr;</span> {{ t('common.back') }}
        </button>
        <h1 class="text-3xl font-black text-slate-900 tracking-tight">
          <template v-if="evaluation">Evaluation #{{ evaluation.id }}</template>
          <template v-else>{{ t('modelDetails.loading') || 'Loading...' }}</template>
        </h1>

        <div v-if="evaluation" class="text-sm text-slate-500 mt-3 flex flex-wrap gap-6 font-medium">
          <!-- Model Link -->
          <span class="flex items-center gap-1.5">
            <strong class="text-slate-700">Model:</strong>
            <router-link v-if="evaluation.model" :to="`/models/${evaluation.model.id}`" class="text-blue-600 hover:text-blue-800 hover:underline flex items-center gap-1 transition-colors">
              {{ evaluation.model.name }}
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"></path></svg>
            </router-link>
            <span v-else>Unknown</span>
          </span>

          <!-- Dataset Link -->
          <span class="flex items-center gap-1.5">
            <strong class="text-slate-700">Dataset:</strong>
            <router-link v-if="evaluation.dataset" to="/datasets" class="text-blue-600 hover:text-blue-800 hover:underline flex items-center gap-1 transition-colors">
              {{ evaluation.dataset.name }}
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"></path></svg>
            </router-link>
            <span v-else>Unknown</span>
          </span>

          <!-- Date -->
          <span class="flex items-center gap-1.5 text-slate-400">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
            {{ new Date(evaluation.created_at).toLocaleString() }}
          </span>
        </div>
      </div>

      <div v-if="evaluation" class="mt-2 md:mt-10">
        <span class="px-6 py-2.5 rounded-xl text-sm font-black uppercase tracking-wider shadow-sm border"
              :class="{
                'bg-green-50 text-green-700 border-green-100': evaluation.status === 'completed',
                'bg-red-50 text-red-700 border-red-100': evaluation.status === 'failed',
                'bg-blue-50 text-blue-700 border-blue-100': evaluation.status === 'processing' || evaluation.status === 'pending'
              }">
          <span v-if="evaluation.status === 'processing'" class="inline-block animate-pulse mr-1">●</span>
          {{ evaluation.status }}
        </span>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-20 text-slate-400 font-medium animate-pulse"></div>

    <!-- Content Container -->
    <div v-else-if="evaluation" class="space-y-8">

      <!-- Failed Status Error Message -->
      <div v-if="evaluation.status === 'failed' && evaluation.error_message" class="bg-red-50 rounded-[2.5rem] shadow-xl shadow-red-200/20 border border-red-100 overflow-hidden">
        <div class="px-10 py-6 border-b border-red-100/50 bg-red-100/30 flex items-center gap-3">
          <h3 class="text-lg font-black text-red-800">{{ t('modelDetails.executionError') }}</h3>
        </div>
        <div class="px-10 py-8">
          <p class="text-red-600 font-mono text-sm whitespace-pre-wrap">{{ evaluation.error_message }}</p>
        </div>
      </div>

      <div v-if="evaluation.metrics" class="grid grid-cols-1 lg:grid-cols-2 gap-8">

        <!-- Main Metrics Box -->
        <div class="bg-white rounded-[2.5rem] shadow-xl shadow-slate-200/50 border border-slate-100 overflow-hidden flex flex-col">
          <div class="px-10 py-8 border-b border-slate-50 flex items-center justify-between bg-slate-50/30">
            <h2 class="text-xl font-black text-slate-800 tracking-tight">{{ t('modelDetails.mainMetrics') }}</h2>
          </div>
          <div class="p-10">
            <ul class="space-y-4 text-base">
              <!-- Original Metrics -->
              <li class="flex justify-between border-b border-slate-50 pb-3">
                <span class="text-slate-500 font-medium">Accuracy</span>
                <span class="font-bold text-slate-800">{{ formatMetric(evaluation.metrics.accuracy) }}</span>
              </li>
              <li class="flex justify-between border-b border-slate-50 pb-3">
                <span class="text-slate-500 font-medium">Precision</span>
                <span class="font-bold text-slate-800">{{ formatMetric(evaluation.metrics.precision) }}</span>
              </li>
              <li class="flex justify-between border-b border-slate-50 pb-3">
                <span class="text-slate-500 font-medium">Recall</span>
                <span class="font-bold text-slate-800">{{ formatMetric(evaluation.metrics.recall) }}</span>
              </li>
              <li class="flex justify-between border-b border-slate-50 pb-3">
                <span class="text-slate-500 font-medium">F1 Score</span>
                <span class="font-bold text-slate-800">{{ formatMetric(evaluation.metrics.f1_score) }}</span>
              </li>
              <li class="flex justify-between border-b border-slate-50 pb-3">
                <span class="text-slate-500 font-medium">ROC AUC</span>
                <span class="font-bold text-slate-800">{{ formatMetric(evaluation.metrics.roc_auc) }}</span>
              </li>
              <li class="flex justify-between border-b border-slate-50 pb-3">
                <span class="text-slate-500 font-medium">Balanced Accuracy</span>
                <span class="font-bold text-slate-800">{{ formatMetric(evaluation.metrics.balanced_accuracy) }}</span>
              </li>
              <!-- Newly Added Metrics -->
              <li class="flex justify-between border-b border-slate-50 pb-3">
                <span class="text-slate-500 font-medium">PR AUC</span>
                <span class="font-bold text-slate-800">{{ formatMetric(evaluation.metrics.pr_auc) }}</span>
              </li>
              <li class="flex justify-between border-b border-slate-50 pb-3">
                <span class="text-slate-500 font-medium">MCC (Matthews)</span>
                <span class="font-bold text-slate-800">{{ evaluation.metrics.mcc?.toFixed(4) || '—' }}</span>
              </li>
              <li class="flex justify-between border-b border-slate-50 pb-3">
                <span class="text-slate-500 font-medium">Log Loss</span>
                <span class="font-bold text-slate-800">{{ evaluation.metrics.log_loss_value?.toFixed(4) || '—' }}</span>
              </li>
              <li class="flex justify-between pb-1">
                <span class="text-slate-500 font-medium">Brier Score</span>
                <span class="font-bold text-slate-800">{{ evaluation.metrics.brier_score?.toFixed(4) || '—' }}</span>
              </li>
            </ul>
          </div>
        </div>

        <div class="space-y-8">

          <!-- Confusion Matrix Box -->
          <div class="bg-white rounded-[2.5rem] shadow-xl shadow-slate-200/50 border border-slate-100 overflow-hidden">
            <div class="px-10 py-8 border-b border-slate-50 flex items-center justify-between bg-slate-50/30">
              <h2 class="text-xl font-black text-slate-800 tracking-tight">{{ t('modelDetails.confusionMatrix') }}</h2>
            </div>
            <div class="p-10">
              <div v-if="hasConfusionMatrix(evaluation.metrics)" class="grid grid-cols-2 gap-4 text-center h-32">
                <div class="bg-slate-50 rounded-2xl flex flex-col justify-center border border-slate-100 shadow-sm">
                  <span class="text-xs text-slate-400 font-bold uppercase tracking-wider">{{ t('modelDetails.matrix.tn') || 'TN' }}</span>
                  <span class="text-3xl font-black text-slate-700 mt-1">{{ evaluation.metrics.tn }}</span>
                </div>
                <div class="bg-red-50 rounded-2xl flex flex-col justify-center border border-red-100 shadow-sm">
                  <span class="text-xs text-red-400 font-bold uppercase tracking-wider">{{ t('modelDetails.matrix.fp') || 'FP' }}</span>
                  <span class="text-3xl font-black text-red-700 mt-1">{{ evaluation.metrics.fp }}</span>
                </div>
                <div class="bg-orange-50 rounded-2xl flex flex-col justify-center border border-orange-100 shadow-sm">
                  <span class="text-xs text-orange-400 font-bold uppercase tracking-wider">{{ t('modelDetails.matrix.fn') || 'FN' }}</span>
                  <span class="text-3xl font-black text-orange-700 mt-1">{{ evaluation.metrics.fn }}</span>
                </div>
                <div class="bg-green-50 rounded-2xl flex flex-col justify-center border border-green-100 shadow-sm">
                  <span class="text-xs text-green-400 font-bold uppercase tracking-wider">{{ t('modelDetails.matrix.tp') || 'TP' }}</span>
                  <span class="text-3xl font-black text-green-700 mt-1">{{ evaluation.metrics.tp }}</span>
                </div>
              </div>
              <div v-else class="h-32 flex items-center justify-center text-slate-400 text-sm font-medium bg-slate-50 rounded-2xl border border-slate-100">
                Matrix data not available
              </div>
            </div>
          </div>

          <!-- Technical Details Box -->
          <div class="bg-white rounded-[2.5rem] shadow-xl shadow-slate-200/50 border border-slate-100 overflow-hidden">
            <div class="px-10 py-8 border-b border-slate-50 flex items-center justify-between bg-slate-50/30">
              <h2 class="text-xl font-black text-slate-800 tracking-tight">Technical Details</h2>
            </div>
            <div class="p-10">
              <ul class="space-y-4 text-base">
                <li class="flex justify-between border-b border-slate-50 pb-3">
                  <span class="text-slate-500 font-medium">Latency (ms)</span>
                  <span class="font-bold text-slate-800">{{ evaluation.metrics.mean_latency_ms?.toFixed(2) || '—' }}</span>
                </li>
                <li class="flex justify-between border-b border-slate-50 pb-3">
                  <span class="text-slate-500 font-medium">Averaging Mode</span>
                  <span class="font-bold text-slate-800 capitalize">{{ evaluation.metrics.averaging_mode || '—' }}</span>
                </li>
                <li class="flex justify-between border-b border-slate-50 pb-3">
                  <span class="text-slate-500 font-medium">Decision Threshold</span>
                  <span class="font-bold text-slate-800">{{ evaluation.metrics.decision_threshold || '0.5' }}</span>
                </li>
                <li class="flex justify-between border-b border-slate-50 pb-3">
                  <span class="text-slate-500 font-medium">Model Size</span>
                  <span class="font-bold text-slate-800">{{ formatBytes(evaluation.metrics.model_size_bytes) }}</span>
                </li>
                <li class="flex justify-between items-start pt-1">
                  <span class="text-slate-500 font-medium">Class Mapping</span>
                  <div class="font-mono text-xs text-slate-800 bg-slate-50 p-2 rounded text-right">
                    <span v-if="evaluation.metrics.class_mapping">{{ JSON.stringify(evaluation.metrics.class_mapping) }}</span>
                    <span v-else>—</span>
                  </div>
                </li>
              </ul>
            </div>
          </div>

        </div>
      </div>

      <!-- Raw JSON Data Box -->
      <div class="bg-white rounded-[2.5rem] shadow-xl shadow-slate-200/50 border border-slate-100 overflow-hidden mt-8">
        <div class="px-10 py-6 border-b border-slate-50 flex items-center justify-between bg-slate-50/30">
          <div>
            <h2 class="text-xl font-black text-slate-800 tracking-tight">Raw Evaluation Data</h2>
            <p class="text-sm text-slate-500 mt-1 font-medium">Full JSON response for this evaluation run.</p>
          </div>
          <button @click="copyToClipboard(JSON.stringify(evaluation, null, 2))" class="flex items-center gap-2 px-4 py-2 text-sm font-bold text-slate-600 hover:text-blue-600 bg-white border border-slate-200 hover:border-blue-200 rounded-xl transition-colors shadow-sm" title="Copy JSON">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"></path></svg>
            Copy JSON
          </button>
        </div>
        <div class="p-6 bg-slate-50/50">
          <pre class="text-xs font-mono text-slate-700 overflow-x-auto whitespace-pre-wrap p-4 bg-white rounded-2xl border border-slate-100 shadow-inner">{{ JSON.stringify(evaluation, null, 4) }}</pre>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
const route = useRoute()
const evaluation = ref(null)
const loading = ref(true)

const API_URL = import.meta.env.VITE_API_URL || ''

const formatMetric = (value) => {
  if (value === null || value === undefined) return '—'
  return (value * 100).toFixed(2) + '%'
}

const formatBytes = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  if (!bytes) return '—'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const hasConfusionMatrix = (metrics) => {
  return metrics.tn !== null && metrics.fp !== null && metrics.fn !== null && metrics.tp !== null
}

const copyToClipboard = async (text) => {
  try {
    await navigator.clipboard.writeText(text)
    alert('JSON copied to clipboard!')
  } catch (err) {
    console.error('Failed to copy text', err)
    alert('Failed to copy text.')
  }
}

const fetchEvaluationDetails = async () => {
  loading.value = true
  try {
    const token = localStorage.getItem('token')
    const response = await axios.get(`${API_URL}/evaluations/${route.params.id}`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    evaluation.value = response.data
  } catch (error) {
    console.error("Error fetching evaluation details:", error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchEvaluationDetails()
})
</script>