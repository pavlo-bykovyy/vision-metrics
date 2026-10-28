<template>
  <div class="space-y-8 pb-12">
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
      <div>
        <h1 class="text-3xl font-black text-slate-900 tracking-tight">{{ t('dashboard.title') }}</h1>
        <p class="text-slate-500 font-medium">{{ t('dashboard.subtitle') }}</p>
      </div>

    </div>

    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-6">
      <StatCard :title="t('dashboard.stats.total')" :value="totalModels" icon="📁" iconBgClass="bg-blue-50" iconTextClass="text-blue-600" />
      <StatCard :title="t('dashboard.stats.accuracy')" :value="`${averageMetrics.accuracy}%`" icon="🎯" iconBgClass="bg-orange-50" iconTextClass="text-orange-600" />
      <StatCard :title="t('dashboard.stats.precision')" :value="`${averageMetrics.precision}%`" icon="🔍" iconBgClass="bg-cyan-50" iconTextClass="text-cyan-600" />
      <StatCard :title="t('dashboard.stats.recall')" :value="`${averageMetrics.recall}%`" icon="📢" iconBgClass="bg-pink-50" iconTextClass="text-pink-600" />
      <StatCard :title="t('dashboard.stats.f1')" :value="`${averageMetrics.f1}%`" icon="📊" iconBgClass="bg-green-50" iconTextClass="text-green-600" />
      <StatCard :title="t('dashboard.stats.roc')" :value="`${averageMetrics.roc}%`" icon="📈" iconBgClass="bg-purple-50" iconTextClass="text-purple-600" />
    </div>

    <div class="max-w-md">
      <DiskUsageCard
          :used="storageData.used"
          :total="storageData.total"
          :free="storageData.free"
          :percentage="storageData.percentage"
          :unit="storageData.unit"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import axios from 'axios'
import StatCard from '@/components/StatCard.vue'
import DiskUsageCard from "@/components/DiskUsageCard.vue"

const { t } = useI18n()
const models = ref([])
const totalModels = ref(0)
const storageData = ref({ used: 0, total: 0, free: 0, percentage: 0, unit: 'GB' })
const API_URL = import.meta.env.VITE_API_URL || ''

const averageMetrics = computed(() => {
  const testedModels = models.value.filter(m => {
    if (!m.evaluations || m.evaluations.length === 0) return false;
    const lastEval = m.evaluations[m.evaluations.length - 1];
    return lastEval.metrics !== null && lastEval.metrics !== undefined;
  })

  if (testedModels.length === 0) return { accuracy: '0.0', f1: '0.0', roc: '0.0', precision: '0.0', recall: '0.0' }

  let accSum = 0, f1Sum = 0, rocSum = 0, precSum = 0, recSum = 0

  testedModels.forEach(m => {
    const lastEval = m.evaluations[m.evaluations.length - 1];
    accSum += lastEval.metrics.accuracy || 0
    f1Sum += lastEval.metrics.f1_score || 0
    rocSum += lastEval.metrics.roc_auc || 0
    precSum += lastEval.metrics.precision || 0
    recSum += lastEval.metrics.recall || 0
  })

  const count = testedModels.length
  return {
    accuracy: ((accSum / count) * 100).toFixed(1),
    f1: ((f1Sum / count) * 100).toFixed(1),
    roc: ((rocSum / count) * 100).toFixed(1),
    precision: ((precSum / count) * 100).toFixed(1),
    recall: ((recSum / count) * 100).toFixed(1),
  }
})

const fetchModels = async () => {
  try {
    const response = await axios.get(`${API_URL}/models/`, {
      params: { page: 1, size: 50 }
    })
    models.value = response.data.items
    totalModels.value = response.data.total
  } catch (error) {
    console.error("Error fetching models:", error)
  }
}

const fetchStorageInfo = async () => {
  try {
    const response = await axios.get(`${API_URL}/storage-info/`)
    storageData.value = response.data
  } catch (error) {
    console.error("Error fetching storage info:", error)
  }
}

onMounted(() => {
  fetchModels()
  fetchStorageInfo()
})
</script>