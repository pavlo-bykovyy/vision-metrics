<script setup>
/**
 * src/components/attacks/AttackCharts.vue
 *
 * Saved charts & statistical reports for attack runs. Each visualization run is
 * persisted in PostgreSQL and linked many-to-many with the evaluation tasks and
 * judge runs it was built from (POST/GET /llm/attacks/visualizations).
 * Charts are rendered from the server-generated SVG (`svg_content`).
 */

import { computed, onMounted, ref, watch } from 'vue'
import { useAttacks } from '@/composables/useAttacks'

const props = defineProps({
  apiUrl: { type: String, required: true },
  initialTaskId: { type: Number, default: null },
})

const attacksApi = useAttacks(props.apiUrl)

const extraTaskIds = ref('')
const judgeRunIds = ref('')
const reportName = ref('')
const excludeRussian = ref(true)
const nPermutations = ref(2000)

const runs = ref([])
const activeRun = ref(null)
const activeRunId = ref(null)
const loadingList = ref(false)
const loadingRun = ref(false)
const building = ref(false)
const error = ref('')

const parseIds = (s) =>
    [...new Set(String(s || '').split(/[\s,;]+/).map(Number).filter((n) => Number.isInteger(n) && n > 0))]

const charts = computed(() => activeRun.value?.charts ?? [])
const summary = computed(() => activeRun.value?.summary_payload ?? {})

/** Tables from summary_payload rendered generically (array of flat records). */
const tables = computed(() => {
  const s = summary.value
  const defs = [
    { title: 'Зведення за моделями', rows: s.summary_by_model },
    { title: 'ARI (Alignment Robustness Index)', rows: s.ari?.ari_by_task },
    { title: 'MCDM: SRD / DnE / DnM / WSM / TOPSIS', rows: s.mcdm_scores },
    { title: 'Factorial ANOVA (Type III)', rows: s.anova_table },
    { title: 'ANOVA: діагностика та причини пропуску', rows: s.anova_diagnostics },
    { title: 'Tukey post-hoc', rows: s.tukey_posthoc },
  ]
  return defs
      .filter((d) => Array.isArray(d.rows) && d.rows.length)
      .map((d) => ({ title: d.title, columns: Object.keys(d.rows[0]), rows: d.rows.slice(0, 200) }))
})

const fmtCell = (v) => {
  if (v == null) return '—'
  if (typeof v === 'number') return Number.isInteger(v) ? v : v.toFixed(3)
  if (typeof v === 'object') return JSON.stringify(v)
  return String(v)
}

const fmtDate = (d) => (d ? new Date(d).toLocaleString() : '')

async function loadList() {
  loadingList.value = true
  try {
    runs.value = await attacksApi.listVisualizations(props.initialTaskId)
    error.value = ''
    if (!activeRunId.value && runs.value.length) await openRun(runs.value[0].id)
  } catch (e) {
    error.value = e?.message || 'Помилка завантаження списку звітів'
  } finally {
    loadingList.value = false
  }
}

async function openRun(id) {
  activeRunId.value = id
  loadingRun.value = true
  try {
    activeRun.value = await attacksApi.getVisualization(id)
    error.value = ''
  } catch (e) {
    error.value = e?.message || 'Помилка завантаження звіту'
  } finally {
    loadingRun.value = false
  }
}

async function build() {
  const taskIds = [...new Set([props.initialTaskId, ...parseIds(extraTaskIds.value)].filter(Boolean))]
  if (!taskIds.length) {
    error.value = 'Вкажіть хоча б один ID задачі'
    return
  }
  building.value = true
  try {
    const run = await attacksApi.buildVisualizations({
      name: reportName.value.trim() || null,
      task_ids: taskIds,
      judge_task_run_ids: parseIds(judgeRunIds.value),
      exclude_russian: excludeRussian.value,
      n_permutations: Number(nPermutations.value) || 2000,
    })
    error.value = ''
    activeRun.value = run
    activeRunId.value = run.id
    await loadList()
  } catch (e) {
    error.value = e?.message || 'Не вдалося побудувати графіки'
  } finally {
    building.value = false
  }
}

async function removeRun() {
  if (!activeRunId.value || !window.confirm('Видалити цей звіт разом з усіма графіками?')) return
  try {
    await attacksApi.deleteVisualization(activeRunId.value)
    activeRun.value = null
    activeRunId.value = null
    await loadList()
  } catch (e) {
    error.value = e?.message || 'Не вдалося видалити звіт'
  }
}

function downloadSvg(chart) {
  if (!chart.svg_content) return
  const blob = new Blob([chart.svg_content], { type: 'image/svg+xml' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `${chart.chart_type}_${chart.task_scope || 'all'}_${chart.id}.svg`
  a.click()
  URL.revokeObjectURL(url)
}

watch(() => props.initialTaskId, () => {
  activeRun.value = null
  activeRunId.value = null
  loadList()
})

onMounted(loadList)
</script>

<template>
  <div class="space-y-6">
    <!-- Build controls -->
    <div class="p-6 bg-slate-50 border border-slate-200 rounded-2xl space-y-4">
      <div>
        <h2 class="text-lg font-black text-slate-800 tracking-tight">Графіки та статистичний аналіз</h2>
        <p class="text-xs text-slate-500 font-medium">
          Звіт зберігається в БД та пов'язується (M2M) із задачами й запусками суддів.
        </p>
      </div>

      <form @submit.prevent="build" class="grid grid-cols-1 md:grid-cols-12 gap-4 items-end">
        <div class="md:col-span-4 flex flex-col gap-1.5">
          <label class="text-xs font-black text-slate-400 uppercase tracking-widest">Назва звіту</label>
          <input v-model="reportName" type="text" placeholder="Опціонально"
                 class="w-full px-4 py-2.5 rounded-xl bg-white border border-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500 font-medium text-slate-700" />
        </div>
        <div class="md:col-span-3 flex flex-col gap-1.5">
          <label class="text-xs font-black text-slate-400 uppercase tracking-widest">
            Додаткові задачі <span class="font-normal lowercase">(ID через кому)</span>
          </label>
          <input v-model="extraTaskIds" type="text" placeholder="напр. 12, 15"
                 class="w-full px-4 py-2.5 rounded-xl bg-white border border-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500 font-medium text-slate-700" />
        </div>
        <div class="md:col-span-3 flex flex-col gap-1.5">
          <label class="text-xs font-black text-slate-400 uppercase tracking-widest">
            Запуски суддів <span class="font-normal lowercase">(опц.)</span>
          </label>
          <input v-model="judgeRunIds" type="text" placeholder="напр. 3, 4"
                 class="w-full px-4 py-2.5 rounded-xl bg-white border border-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500 font-medium text-slate-700" />
        </div>
        <div class="md:col-span-2 flex flex-col gap-1.5">
          <label class="text-xs font-black text-slate-400 uppercase tracking-widest">Перестановок</label>
          <input v-model.number="nPermutations" type="number" min="100" max="20000" step="100"
                 class="w-full px-4 py-2.5 rounded-xl bg-white border border-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500 font-medium text-slate-700" />
        </div>

        <div class="md:col-span-8 flex items-center">
          <label class="flex items-center gap-2 text-xs font-semibold text-slate-500 cursor-pointer select-none">
            <input v-model="excludeRussian" type="checkbox"
                   class="w-4 h-4 text-blue-600 rounded border-slate-300 focus:ring-blue-500" />
            <span>Виключити RUSSIAN (білінгвальні ENGLISH + UKRAINIAN графіки)</span>
          </label>
        </div>
        <div class="md:col-span-4">
          <button type="submit" :disabled="building || !initialTaskId"
                  class="w-full px-6 py-2.5 bg-blue-600 text-white font-bold rounded-xl shadow-md shadow-blue-600/20 hover:bg-blue-700 disabled:bg-slate-300 disabled:shadow-none transition-all">
            {{ building ? 'Обчислення…' : 'Побудувати графіки' }}
          </button>
        </div>
      </form>
    </div>

    <div v-if="error" class="p-4 bg-red-50 border border-red-200 text-red-700 rounded-xl font-medium text-sm whitespace-pre-line" role="alert">
      🚨 {{ error }}
    </div>

    <!-- Saved runs -->
    <div v-if="runs.length" class="flex flex-wrap items-center gap-3">
      <label class="text-xs font-black text-slate-400 uppercase tracking-widest">Збережені звіти</label>
      <select :value="activeRunId" @change="openRun(Number($event.target.value))"
              class="px-4 py-2 rounded-xl bg-white border border-slate-200 text-sm font-medium text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500">
        <option v-for="r in runs" :key="r.id" :value="r.id">
          #{{ r.id }} · {{ r.name }} · {{ r.charts_count }} граф. · {{ fmtDate(r.created_at) }}
        </option>
      </select>
      <button v-if="activeRunId" @click="removeRun" type="button"
              class="px-3 py-2 text-xs font-bold text-red-600 bg-red-50 border border-red-100 rounded-xl hover:bg-red-100 transition-colors">
        Видалити
      </button>
    </div>

    <div v-if="!runs.length && !loadingList && !error"
         class="p-4 bg-blue-50 border border-blue-100 text-blue-800 rounded-xl font-medium text-sm">
      ℹ️ Збережених звітів для цієї задачі ще немає. Натисніть «Побудувати графіки».
    </div>

    <div v-if="loadingRun" class="h-40 rounded-2xl bg-slate-50 animate-pulse"></div>

    <template v-if="activeRun && !loadingRun">
      <!-- Run meta (M2M tasks) -->
      <div class="flex flex-wrap items-center gap-2 text-xs">
        <span class="font-black text-slate-400 uppercase tracking-widest">Задачі:</span>
        <span v-for="id in activeRun.task_ids" :key="id"
              class="font-mono font-bold text-indigo-700 bg-indigo-50 border border-indigo-100 px-2 py-0.5 rounded-lg">#{{ id }}</span>
        <span v-if="summary.total_rows != null" class="text-slate-500 font-medium">
          · рядків: <strong class="text-slate-700">{{ summary.total_rows }}</strong>
        </span>
      </div>

      <!-- Charts -->
      <div class="grid grid-cols-1 xl:grid-cols-2 gap-6">
        <figure v-for="c in charts" :key="c.id"
                class="bg-white border border-slate-200 rounded-2xl overflow-hidden flex flex-col">
          <div v-if="c.svg_content" class="p-2 [&>svg]:w-full [&>svg]:h-auto" v-html="c.svg_content"></div>
          <div v-else class="p-6 text-sm text-slate-400 italic">{{ c.title }} — SVG недоступний</div>
          <figcaption class="px-4 py-3 border-t border-slate-100 bg-slate-50/50 flex flex-wrap items-center gap-2 text-[11px]">
            <span class="font-mono font-bold text-slate-600">{{ c.chart_type }}</span>
            <span v-if="c.task_scope && c.task_scope !== 'all'"
                  class="px-2 py-0.5 rounded-full bg-slate-200 text-slate-600 font-bold">{{ c.task_scope }}</span>
            <span v-if="c.judge_task_run_ids.length" class="text-slate-400">
              судді: {{ c.judge_task_run_ids.map((j) => `#${j}`).join(', ') }}
            </span>
            <button type="button" @click="downloadSvg(c)" :disabled="!c.svg_content"
                    class="ml-auto px-3 py-1 font-bold text-blue-600 bg-blue-50 border border-blue-100 rounded-lg hover:bg-blue-100 disabled:opacity-40 transition-colors">
              ⬇ SVG
            </button>
          </figcaption>
        </figure>
      </div>

      <!-- Interpretation -->
      <section v-if="summary.interpretation_text" class="p-6 bg-slate-50 border border-slate-200 rounded-2xl space-y-2">
        <h3 class="text-sm font-black text-slate-400 uppercase tracking-widest">Інтерпретація</h3>
        <p class="text-sm text-slate-700 leading-relaxed whitespace-pre-line">{{ summary.interpretation_text }}</p>
      </section>

      <!-- Summary tables -->
      <section v-for="t in tables" :key="t.title" class="space-y-3">
        <h3 class="text-sm font-black text-slate-400 uppercase tracking-widest">{{ t.title }}</h3>
        <div class="overflow-x-auto rounded-xl border border-slate-200">
          <table class="w-full text-left text-xs text-slate-700 border-collapse">
            <thead class="bg-slate-50 font-black uppercase tracking-wider text-slate-400 border-b border-slate-200">
            <tr>
              <th v-for="col in t.columns" :key="col" scope="col" class="py-2.5 px-3 whitespace-nowrap">{{ col }}</th>
            </tr>
            </thead>
            <tbody class="divide-y divide-slate-100 bg-white">
            <tr v-for="(row, i) in t.rows" :key="i" class="hover:bg-slate-50/50">
              <td v-for="col in t.columns" :key="col" class="py-2 px-3 font-mono whitespace-nowrap">{{ fmtCell(row[col]) }}</td>
            </tr>
            </tbody>
          </table>
        </div>
      </section>
    </template>
  </div>
</template>
