<script setup>
/**
 * src/views/attacks/AttackVisualizationView.vue
 *
 * Dedicated page for visualizing attack results of a single evaluation task
 * (route: /attacks/:id/visualizations). Hosts the persisted charts & statistical
 * reports (AttackCharts) and a legend with the judge rubric from `code_judge.txt`.
 */

import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import AttackCharts from '@/components/attacks/AttackCharts.vue'
import { useLoraEvaluationTask } from '@/composables/useLoraEvaluationTask'
import { JUDGE_RUBRIC } from '@/constants/attacks'

const props = defineProps({
  id: { type: [String, Number], required: true },
})

const router = useRouter()
const API_URL = import.meta.env.VITE_API_URL || '/api'
const taskId = computed(() => props.id)

const { taskDetails, fetchTaskDetails, detailsError } = useLoraEvaluationTask(taskId)

const rubricLang = ref('UKRAINIAN')
const rubricRows = computed(() => Object.entries(JUDGE_RUBRIC[rubricLang.value] ?? {}))

onMounted(fetchTaskDetails)
</script>

<template>
  <div class="space-y-8 pb-12 mt-8">
    <div>
      <button @click="router.push(`/attacks/${taskId}`)"
              class="text-sm font-bold text-slate-500 hover:text-slate-800 flex items-center gap-2 mb-2">
        <span>&larr;</span> Назад до деталей атаки
      </button>
      <h1 class="text-3xl font-black text-slate-900 tracking-tight flex items-center gap-3 flex-wrap">
        Візуалізація результатів
        <span class="text-sm font-bold text-slate-400 bg-slate-100 px-2 py-1 rounded-lg">#{{ taskId }}</span>
        <span v-if="taskDetails?.base_model_to_use"
              class="text-xs font-mono font-semibold text-indigo-700 bg-indigo-50 border border-indigo-100 px-2.5 py-1 rounded-lg">
          {{ taskDetails.base_model_to_use }}
        </span>
      </h1>
      <p class="text-slate-500 font-medium mt-2 max-w-3xl">
        {{ taskDetails?.name || `Attack Run #${taskId}` }} — теплові карти, радар, ARI, ANOVA та MCDM-рейтинг за оцінками Judge.
      </p>
    </div>

    <div v-if="detailsError" class="bg-red-50 border border-red-100 text-red-600 text-sm font-medium rounded-2xl px-6 py-4">
      {{ detailsError }}
    </div>

    <div class="bg-white p-8 rounded-[2rem] shadow-sm border border-slate-100">
      <AttackCharts :api-url="API_URL" :initial-task-id="Number(taskId)" />
    </div>

    <!-- Judge rubric legend (code_judge.txt) -->
    <details class="bg-white p-6 rounded-[2rem] shadow-sm border border-slate-100">
      <summary class="cursor-pointer text-sm font-black text-slate-400 uppercase tracking-widest select-none">
        Критерії оцінювання Judge (шкала 1–5)
      </summary>
      <div class="mt-4 space-y-3">
        <div class="flex gap-2">
          <button v-for="lang in Object.keys(JUDGE_RUBRIC)" :key="lang" type="button" @click="rubricLang = lang"
                  class="px-3 py-1 text-xs font-bold rounded-lg border transition-colors"
                  :class="rubricLang === lang ? 'bg-blue-600 text-white border-blue-600' : 'bg-white text-slate-500 border-slate-200 hover:bg-slate-50'">
            {{ lang }}
          </button>
        </div>
        <dl class="divide-y divide-slate-100 text-sm">
          <div v-for="[key, text] in rubricRows" :key="key" class="py-2.5 grid grid-cols-1 md:grid-cols-4 gap-2">
            <dt class="font-mono font-bold text-slate-700">{{ key }}</dt>
            <dd class="md:col-span-3 text-slate-600">{{ text }}</dd>
          </div>
        </dl>
      </div>
    </details>
  </div>
</template>
