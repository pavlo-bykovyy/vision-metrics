<script setup>
/**
 * src/components/AttackSummary.vue
 *
 * Displays the aggregated Attack Success Rate (ASR) summary for a completed or
 * running evaluation task. Polls GET /llm/attacks/runs/{task_id}/summary every
 * 5 seconds when autoRefresh is enabled and renders breakdowns by metric category,
 * attack technique, and language.
 */

import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useAttacks } from '@/composables/useAttacks'
import { ASR_IS_RATIO } from '@/constants/attacks'

const props = defineProps({
  apiUrl: { type: String, required: true },
  initialTaskId: { type: Number, default: null },
})

const attacksApi = useAttacks(props.apiUrl)

const POLL_MS = 5000

const taskId = ref(props.initialTaskId)
const judgeTaskRunId = ref('')
const autoRefresh = ref(true)

const summary = ref(null)
const loading = ref(false)
const error = ref('')
let timer = null

/**
 * Convert ratio (0..1) to percentage (0..100) if ASR_IS_RATIO is true.
 */
const toPercent = (v) => (v == null ? null : ASR_IS_RATIO ? v * 100 : v)
const fmt = (v) => (v == null ? '—' : `${toPercent(v).toFixed(1)}%`)
const barWidth = (v) => `${Math.min(100, Math.max(0, toPercent(v) ?? 0))}%`

/**
 * Fetch the latest ASR summary from the backend.
 */
async function load() {
  if (!taskId.value) return
  loading.value = true
  try {
    summary.value = await attacksApi.getSummary(
        taskId.value,
        judgeTaskRunId.value ? Number(judgeTaskRunId.value) : undefined,
    )
    error.value = ''
  } catch (e) {
    error.value = e?.message || 'Помилка завантаження даних'
  } finally {
    loading.value = false
  }
}

/**
 * Stop the background polling timer.
 */
function stopPolling() {
  if (timer) {
    clearInterval(timer)
    timer = null
  }
}

/**
 * Start or restart the periodic polling timer.
 */
function startPolling() {
  stopPolling()
  if (autoRefresh.value && taskId.value) {
    timer = setInterval(load, POLL_MS)
  }
}

watch([autoRefresh, taskId], startPolling)

watch(
    () => props.initialTaskId,
    (newId) => {
      if (newId) {
        taskId.value = newId
        load()
      }
    },
)

onMounted(() => {
  if (taskId.value) load()
  startPolling()
})

onBeforeUnmount(stopPolling)

/**
 * Manual form submission handler.
 */
function submit() {
  summary.value = null
  load()
  startPolling()
}

/**
 * Transform summary dictionaries into sorted table sections.
 */
const sections = computed(() => {
  if (!summary.value) return []
  const sortBuckets = (obj) =>
      Object.entries(obj ?? {})
          .map(([key, b]) => ({ key, ...b }))
          .sort((a, b) => (b.asr ?? 0) - (a.asr ?? 0))

  return [
    { title: 'За категорією метрики', rows: sortBuckets(summary.value.by_metric_category) },
    { title: 'За технікою атаки', rows: sortBuckets(summary.value.by_attack_technique) },
    { title: 'За мовою', rows: sortBuckets(summary.value.by_language) },
  ]
})
</script>

<template>
  <div class="space-y-6">
    <!-- Filter & Auto-Refresh Controls -->
    <div class="p-6 bg-slate-50 border border-slate-200 rounded-2xl space-y-4">
      <form @submit.prevent="submit" class="grid grid-cols-1 md:grid-cols-12 gap-4 items-end">
        <div class="md:col-span-4 flex flex-col gap-1.5">
          <label for="atk-task" class="text-xs font-black text-slate-400 uppercase tracking-widest">
            ID задачі
          </label>
          <input
              id="atk-task"
              v-model.number="taskId"
              type="number"
              min="1"
              required
              placeholder="Введіть ID задачі..."
              class="w-full px-4 py-2.5 rounded-xl bg-white border border-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500 font-medium text-slate-700 transition-all"
          />
        </div>

        <div class="md:col-span-5 flex flex-col gap-1.5">
          <label for="atk-judge-run" class="text-xs font-black text-slate-400 uppercase tracking-widest">
            ID запуску судді <span class="text-slate-400 font-normal lowercase">(опціонально)</span>
          </label>
          <input
              id="atk-judge-run"
              v-model="judgeTaskRunId"
              type="number"
              min="1"
              placeholder="Введіть ID запуску судді..."
              class="w-full px-4 py-2.5 rounded-xl bg-white border border-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500 font-medium text-slate-700 transition-all"
          />
        </div>

        <div class="md:col-span-3">
          <button
              type="submit"
              :disabled="!taskId || loading"
              class="w-full px-6 py-2.5 bg-blue-600 text-white font-bold rounded-xl shadow-md shadow-blue-600/20 hover:bg-blue-700 disabled:bg-slate-300 disabled:shadow-none transition-all flex items-center justify-center gap-2"
          >
            <svg
                v-if="loading"
                class="animate-spin h-4 w-4 text-white"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
            >
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path
                  class="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              ></path>
            </svg>
            <span>{{ loading ? 'Завантаження…' : 'Показати' }}</span>
          </button>
        </div>
      </form>

      <div class="flex items-center justify-between pt-2 border-t border-slate-200/60">
        <label class="flex items-center gap-2 text-xs font-semibold text-slate-500 cursor-pointer select-none">
          <input
              v-model="autoRefresh"
              type="checkbox"
              class="w-4 h-4 text-blue-600 rounded border-slate-300 focus:ring-blue-500"
          />
          <span>Автоматично оновлювати кожні {{ POLL_MS / 1000 }} с</span>
        </label>

        <span v-if="loading" class="text-xs text-blue-600 font-medium flex items-center gap-1">
          <span class="inline-block w-2 h-2 rounded-full bg-blue-600 animate-ping"></span>
          Оновлення даних...
        </span>
      </div>
    </div>

    <!-- Error Banner -->
    <div
        v-if="error"
        class="p-4 bg-red-50 border border-red-200 text-red-700 rounded-xl font-medium text-sm flex items-center gap-2"
        role="alert"
    >
      <span>🚨 {{ error }}</span>
    </div>

    <!-- Empty State Banner -->
    <div
        v-if="!summary && !error"
        class="p-4 bg-blue-50 border border-blue-100 text-blue-800 rounded-xl font-medium text-sm flex items-center gap-2"
    >
      <span>ℹ️ Введіть ID задачі, щоб побачити результати. Після запуску атаки він підставиться автоматично.</span>
    </div>

    <!-- Results Breakdown -->
    <template v-if="summary">
      <section
          class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-6 p-6 bg-slate-50 border border-slate-200 rounded-2xl"
          aria-label="Загальний ASR"
      >
        <div class="flex flex-col sm:flex-row items-start sm:items-center gap-6">
          <div class="text-4xl font-black text-slate-900 tracking-tight font-mono min-w-[5ch]">
            {{ fmt(summary.overall_asr) }}
          </div>
          <div class="space-y-1">
            <h3 class="font-bold text-slate-800 text-base">Загальний рівень успішності атак (Overall ASR)</h3>
            <p class="text-xs text-slate-500 font-medium">
              Оцінено відповідей: <strong class="text-slate-700">{{ summary.scored }}</strong>.
              <template v-if="summary.overall_asr == null">
                Загальний ASR з'явиться, коли судді закінчать оцінювання.
              </template>
            </p>
          </div>
        </div>

        <div v-if="summary.mean_safety_score != null || summary.mean_accuracy_score != null" class="flex gap-4">
          <div class="px-4 py-2.5 bg-white rounded-xl border border-slate-200 text-center">
            <div class="text-[10px] font-black uppercase tracking-wider text-slate-400">Safety (1–5)</div>
            <div class="text-lg font-black font-mono text-emerald-600">
              {{ summary.mean_safety_score ?? '—' }}
            </div>
          </div>
          <div class="px-4 py-2.5 bg-white rounded-xl border border-slate-200 text-center">
            <div class="text-[10px] font-black uppercase tracking-wider text-slate-400">Accuracy (1–5)</div>
            <div class="text-lg font-black font-mono text-blue-600">
              {{ summary.mean_accuracy_score ?? '—' }}
            </div>
          </div>
        </div>
      </section>

      <section v-for="s in sections" :key="s.title" class="space-y-3">
        <h2 class="text-sm font-black text-slate-400 uppercase tracking-widest">
          {{ s.title }}
        </h2>

        <div
            v-if="!s.rows.length"
            class="text-sm text-slate-400 italic p-4 bg-slate-50 rounded-xl border border-slate-200"
        >
          Немає даних для цієї категорії.
        </div>

        <div v-else class="overflow-x-auto rounded-xl border border-slate-200">
          <table class="w-full text-left text-sm text-slate-700 border-collapse">
            <thead class="bg-slate-50 text-xs font-black uppercase tracking-wider text-slate-400 border-b border-slate-200">
            <tr>
              <th scope="col" class="py-3 px-4">Категорія</th>
              <th scope="col" class="py-3 px-4 text-right">Атак</th>
              <th scope="col" class="py-3 px-4 text-right">Успішних</th>
              <th scope="col" class="py-3 px-4 text-right">Safety (1–5)</th>
              <th scope="col" class="py-3 px-4 text-right">Accuracy (1–5)</th>
              <th scope="col" class="py-3 px-4 w-64">ASR</th>
            </tr>
            </thead>
            <tbody class="divide-y divide-slate-100 bg-white">
            <tr v-for="r in s.rows" :key="r.key" class="hover:bg-slate-50/50 transition-colors">
              <th scope="row" class="py-3 px-4 font-semibold text-slate-900 whitespace-nowrap">
                {{ r.key }}
              </th>
              <td class="py-3 px-4 text-right font-mono text-slate-600">
                {{ r.n }}
              </td>
              <td class="py-3 px-4 text-right font-mono text-slate-600">
                {{ r.successful_attacks }}
              </td>
              <td class="py-3 px-4 text-right font-mono font-semibold text-emerald-700">
                {{ r.mean_safety_score ?? '—' }}
              </td>
              <td class="py-3 px-4 text-right font-mono font-semibold text-blue-700">
                {{ r.mean_accuracy_score ?? '—' }}
              </td>
              <td class="py-3 px-4">
                <div class="flex items-center gap-3">
                  <div class="flex-1 h-2 bg-slate-100 rounded-full overflow-hidden" aria-hidden="true">
                    <div
                        class="h-full bg-red-500 rounded-full transition-all duration-500"
                        :style="{ width: barWidth(r.asr) }"
                    />
                  </div>
                  <span class="text-xs font-mono font-bold text-slate-700 w-12 text-right">
                      {{ fmt(r.asr) }}
                    </span>
                </div>
              </td>
            </tr>
            </tbody>
          </table>
        </div>
      </section>
    </template>
  </div>
</template>