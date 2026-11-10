<script setup>
/**
 * src/views/attacks/RunAttackView.vue
 *
 * Dedicated view for launching an attack evaluation run (EvaluationTask in models.py)
 * on either a LoRA Adapter or a Base Model using an existing/generated attack dataset.
 */

import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AttackRunStarter from '@/components/attacks/AttackRunStarter.vue'

const route = useRoute()
const router = useRouter()

const API_URL = import.meta.env.VITE_API_URL || '/api'

const initialDatasetId = computed(() => {
  const raw = route.query.datasetId || route.params.datasetId
  return raw ? Number(raw) : null
})

function handleStarted(started) {
  if (started?.task_id) {
    router.push(`/attacks/${started.task_id}`)
  } else {
    router.push('/attacks')
  }
}
</script>

<template>
  <div class="max-w-4xl mx-auto space-y-8 pb-20 p-6">
    <!-- Top Navigation -->
    <div class="flex flex-wrap items-center justify-between gap-4">
      <button
          type="button"
          @click="router.push('/attacks')"
          class="text-sm font-bold text-slate-500 hover:text-slate-800 flex items-center gap-2 transition-colors"
      >
        <span>&larr;</span> Назад до списку атак
      </button>
    </div>

    <!-- Header -->
    <div>
      <h1 class="text-3xl font-black text-slate-900 tracking-tight">
        Запуск Атаки на Моделі (LoRA / Base Model)
      </h1>
      <p class="text-slate-500 font-medium mt-1">
        Оберіть згенерований датасет атаки, цільовий LoRA адаптер або базову модель (Base Model),
        суддів (LLM-as-a-Judge) та запустіть тестування.
      </p>
    </div>

    <!-- Attack Runner Card -->
    <div class="bg-white p-8 rounded-[2rem] shadow-sm border border-slate-100">
      <AttackRunStarter
          :api-url="API_URL"
          :dataset-id="initialDatasetId"
          @started="handleStarted"
      />
    </div>
  </div>
</template>
