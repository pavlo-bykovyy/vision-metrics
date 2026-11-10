<template>
  <div class="space-y-8 pb-12">

    <!-- Header -->
    <div class="flex flex-col md:flex-row md:items-start justify-between gap-4">
      <div>
        <button @click="$router.push('/stress-tests')" class="text-sm font-bold text-slate-500 hover:text-slate-800 flex items-center gap-2 mb-4">
          <span>&larr;</span> {{ t('stressTests.detail.back') }}
        </button>
        <h1 class="text-3xl font-black text-slate-900 tracking-tight">
          <template v-if="run">{{ run.name || `Stress test #${run.id}` }}</template>
          <template v-else>{{ t('common.loading') }}</template>
        </h1>
        <div v-if="run" class="text-sm text-slate-500 mt-3 flex flex-wrap gap-6 font-medium">
          <span class="flex items-center gap-1.5">
            <strong class="text-slate-700">ID:</strong> <span class="font-mono">#{{ run.id }}</span>
          </span>
          <span class="flex items-center gap-1.5 text-slate-400">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
            {{ new Date(run.created_at).toLocaleString() }}
          </span>
          <span class="flex items-center gap-1.5">
            <strong class="text-slate-700">{{ t('stressTests.table.duration') }}:</strong>
            <span class="font-mono">{{ formatDuration(run.started_at, run.finished_at) }}</span>
          </span>
        </div>
      </div>

      <div v-if="run" class="flex flex-wrap items-center gap-3 md:mt-10">
        <span
            class="px-6 py-2.5 rounded-xl text-sm font-black uppercase tracking-wider shadow-sm border flex items-center"
            :class="[getStatusData(run.status).bgClass, getStatusData(run.status).textClass, 'border-transparent']"
        >
          <span v-if="getStatusData(run.status).isSpinning" class="inline-block animate-pulse mr-2">●</span>
          {{ t(getStatusData(run.status).labelKey) }}
        </span>

        <button
            v-if="isActive"
            @click="handleCancel"
            class="px-4 py-2.5 rounded-xl text-sm font-black bg-orange-50 hover:bg-orange-500 hover:text-white text-orange-600 transition-all"
        >
          {{ t('common.cancel') }}
        </button>
        <template v-else>
          <button
              v-if="run.has_archive"
              @click="downloadArchive"
              :disabled="isDownloadingArchive"
              class="px-4 py-2.5 rounded-xl text-sm font-black bg-blue-600 hover:bg-blue-700 text-white shadow-lg shadow-blue-600/20 transition-all disabled:bg-slate-300"
          >
            {{ isDownloadingArchive ? t('stressTests.detail.downloading') : t('stressTests.detail.downloadArchive') }}
          </button>
          <button
              @click="handleRerun"
              class="px-4 py-2.5 rounded-xl text-sm font-black bg-blue-50 hover:bg-blue-600 hover:text-white text-blue-600 transition-all"
          >
            {{ t('stressTests.actions.rerun') }}
          </button>
        </template>
      </div>
    </div>

    <div v-if="loadError" class="p-4 bg-red-50 text-red-700 rounded-xl font-medium text-sm border border-red-100">
      {{ loadError }}
    </div>

    <template v-if="run">
      <!-- Progress -->
      <div v-if="isActive" class="bg-white rounded-[2.5rem] shadow-xl shadow-slate-200/50 border border-slate-100 p-10 space-y-6">
        <div class="flex items-center justify-between">
          <h2 class="text-xl font-black text-slate-800 tracking-tight">{{ t('stressTests.detail.progress') }}</h2>
          <span class="font-mono font-black text-2xl text-blue-600">{{ Math.round(run.progress || 0) }}%</span>
        </div>
        <div class="h-3 bg-slate-100 rounded-full overflow-hidden">
          <div class="h-full bg-blue-500 rounded-full transition-all duration-700" :style="{ width: `${run.progress || 0}%` }"></div>
        </div>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
          <div
              v-for="step in run.steps"
              :key="step"
              class="p-4 rounded-2xl border text-sm"
              :class="stepClass(step)"
          >
            <div class="text-[10px] font-black uppercase tracking-widest flex items-center gap-2">
              <span v-if="stepState(step) === 'done'">✓</span>
              <svg v-else-if="stepState(step) === 'running'" class="animate-spin h-3 w-3" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
              </svg>
              <span v-else>○</span>
              {{ t(`stressTests.steps.${step}.title`) }}
            </div>
          </div>
        </div>
        <p v-if="run.attempt > 1" class="text-xs font-bold text-amber-700 bg-amber-50 border border-amber-100 rounded-xl px-4 py-3">
          {{ t('stressTests.detail.retryNotice', { attempt: run.attempt, n_jobs: run.n_jobs ?? 'all' }) }}
        </p>
        <p class="text-xs text-slate-400 font-medium">{{ t('stressTests.detail.progressHint') }}</p>
      </div>

      <!-- Error -->
      <div v-if="run.status === 'failed' && run.error_message" class="bg-red-50 rounded-[2.5rem] shadow-xl shadow-red-200/20 border border-red-100 overflow-hidden">
        <div class="px-10 py-6 border-b border-red-100/50 bg-red-100/30">
          <h3 class="text-lg font-black text-red-800">{{ t('stressTests.detail.executionError') }}</h3>
        </div>
        <div class="px-10 py-8">
          <p class="text-red-600 font-mono text-sm whitespace-pre-wrap">{{ run.error_message }}</p>
        </div>
      </div>

      <!-- Tabs -->
      <div class="flex flex-wrap gap-2 bg-slate-100 p-1.5 rounded-2xl w-fit">
        <button
            v-for="tab in tabs"
            :key="tab"
            @click="activeTab = tab"
            class="px-5 py-2.5 rounded-xl text-sm font-black transition-all"
            :class="activeTab === tab ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-500 hover:text-slate-800'"
        >
          {{ t(`stressTests.detail.tabs.${tab}`) }}
          <span
              v-if="tab === 'figures' && figures.length"
              class="ml-1 text-[10px] px-1.5 py-0.5 rounded-md bg-slate-200 text-slate-600"
          >{{ figures.length }}</span>
          <span
              v-if="tab === 'files' && files.length"
              class="ml-1 text-[10px] px-1.5 py-0.5 rounded-md bg-slate-200 text-slate-600"
          >{{ files.length }}</span>
        </button>
      </div>

      <!-- Overview -->
      <div v-show="activeTab === 'overview'" class="space-y-8">
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div class="bg-white rounded-[2.5rem] shadow-xl shadow-slate-200/50 border border-slate-100 overflow-hidden lg:col-span-1">
            <div class="px-10 py-8 border-b border-slate-50 bg-slate-50/30">
              <h2 class="text-xl font-black text-slate-800 tracking-tight">{{ t('stressTests.detail.design') }}</h2>
            </div>
            <ul class="p-10 space-y-3 text-sm">
              <li v-for="item in designItems" :key="item.label" class="flex justify-between gap-4 border-b border-slate-50 pb-2 last:border-0">
                <span class="text-slate-500 font-medium">{{ item.label }}</span>
                <span class="font-mono font-bold text-slate-800 text-right">{{ item.value }}</span>
              </li>
            </ul>
          </div>

          <div class="lg:col-span-2 space-y-8">
            <div
                v-if="!overviewTables.length"
                class="bg-white rounded-[2.5rem] shadow-xl shadow-slate-200/50 border border-slate-100 py-16 text-center text-slate-400 font-medium"
            >
              {{ isActive ? t('stressTests.detail.waitingResults') : t('stressTests.detail.noResults') }}
            </div>
            <div
                v-for="name in overviewTables"
                :key="name"
                class="bg-white rounded-[2.5rem] shadow-xl shadow-slate-200/50 border border-slate-100 overflow-hidden"
            >
              <div class="px-8 py-6 border-b border-slate-50 bg-slate-50/30">
                <h2 class="text-lg font-black text-slate-800 tracking-tight">{{ tableTitle(name) }}</h2>
                <p v-if="tableDesc(name)" class="text-xs text-slate-500 font-medium mt-1">{{ tableDesc(name) }}</p>
              </div>
              <StressTestTable :table="tables[name]?.data" :loading="tables[name]?.loading" :error="tables[name]?.error" max-height-class="max-h-[24rem]" />
            </div>
          </div>
        </div>
      </div>

      <!-- Figures -->
      <div v-show="activeTab === 'figures'">
        <div
            v-if="!figures.length"
            class="bg-white rounded-[2.5rem] shadow-xl shadow-slate-200/50 border border-slate-100 py-16 text-center text-slate-400 font-medium"
        >
          {{ t('stressTests.detail.noFigures') }}
        </div>
        <div v-else class="grid grid-cols-1 xl:grid-cols-2 gap-8">
          <template v-for="fig in figures" :key="fig.stem">
            <StressTestFigure
                v-if="fig.preview && activeTab === 'figures'"
                :run-id="run.id"
                :path="fig.preview"
                :title="prettifyFileName(fig.stem)"
                :variants="fig.variants"
                @download="downloadFile"
                @open="lightbox = $event"
            />
            <div v-else-if="!fig.preview" class="bg-white rounded-[2rem] shadow-sm border border-slate-100 p-6 flex items-center justify-between gap-4">
              <span class="text-sm font-black text-slate-800">{{ prettifyFileName(fig.stem) }}</span>
              <div class="flex gap-2">
                <button
                    v-for="variant in fig.variants"
                    :key="variant.path"
                    @click="downloadFile(variant.path)"
                    class="text-[10px] font-black uppercase tracking-widest py-1.5 px-2.5 rounded-lg bg-blue-50 text-blue-600 hover:bg-blue-600 hover:text-white transition-all"
                >{{ variant.ext }}</button>
              </div>
            </div>
          </template>
        </div>
      </div>

      <!-- Reviewer analyses -->
      <div v-show="activeTab === 'reviewer'" class="space-y-8">
        <div
            v-if="!reviewerTables.length && !hasManuscript"
            class="bg-white rounded-[2.5rem] shadow-xl shadow-slate-200/50 border border-slate-100 py-16 text-center text-slate-400 font-medium"
        >
          {{ run.steps.includes('reviewer') ? t('stressTests.detail.waitingResults') : t('stressTests.detail.reviewerNotRequested') }}
        </div>
        <div
            v-for="name in reviewerTables"
            :key="name"
            class="bg-white rounded-[2.5rem] shadow-xl shadow-slate-200/50 border border-slate-100 overflow-hidden"
        >
          <div class="px-8 py-6 border-b border-slate-50 bg-slate-50/30">
            <h2 class="text-lg font-black text-slate-800 tracking-tight">{{ tableTitle(name) }}</h2>
            <p v-if="tableDesc(name)" class="text-xs text-slate-500 font-medium mt-1">{{ tableDesc(name) }}</p>
          </div>
          <StressTestTable :table="tables[name]?.data" :loading="tables[name]?.loading" :error="tables[name]?.error" max-height-class="max-h-[24rem]" />
        </div>

        <div v-if="hasManuscript" class="bg-white rounded-[2.5rem] shadow-xl shadow-slate-200/50 border border-slate-100 overflow-hidden">
          <div class="px-8 py-6 border-b border-slate-50 bg-slate-50/30 flex items-center justify-between">
            <h2 class="text-lg font-black text-slate-800 tracking-tight">{{ t('stressTests.detail.manuscript') }}</h2>
            <button
                @click="downloadFile(MANUSCRIPT_FILE)"
                class="text-xs font-black py-2 px-4 rounded-xl bg-blue-50 hover:bg-blue-600 hover:text-white text-blue-600 transition-all"
            >
              {{ t('stressTests.detail.download') }}
            </button>
          </div>
          <pre class="p-8 text-xs font-mono text-slate-700 overflow-auto max-h-[32rem] whitespace-pre">{{ manuscriptText || t('common.loading') }}</pre>
        </div>
      </div>

      <!-- All files -->
      <div v-show="activeTab === 'files'" class="space-y-8">
        <div class="bg-white rounded-[2.5rem] shadow-xl shadow-slate-200/50 border border-slate-100 overflow-hidden">
          <div class="px-10 py-8 border-b border-slate-50 flex items-center justify-between bg-slate-50/30">
            <h2 class="text-xl font-black text-slate-800 tracking-tight">{{ t('stressTests.detail.allFiles') }}</h2>
            <span class="text-xs font-bold text-slate-400 uppercase tracking-widest">{{ formatBytes(totalSize) }}</span>
          </div>
          <div v-if="!files.length" class="py-12 text-center text-slate-400 font-medium">{{ t('stressTests.detail.noResults') }}</div>
          <div v-else class="overflow-x-auto max-h-[28rem]">
            <table class="w-full text-left border-collapse text-sm">
              <thead class="sticky top-0">
              <tr class="bg-slate-50 text-slate-500 border-b border-slate-100">
                <th class="p-4 font-semibold">{{ t('stressTests.detail.file') }}</th>
                <th class="p-4 font-semibold">{{ t('stressTests.detail.kind') }}</th>
                <th class="p-4 font-semibold text-right">{{ t('stressTests.detail.size') }}</th>
                <th class="p-4 font-semibold text-right">{{ t('stressTests.table.actions') }}</th>
              </tr>
              </thead>
              <tbody>
              <tr
                  v-for="file in files"
                  :key="file.path"
                  class="border-b border-slate-50 hover:bg-slate-50/50 transition-colors"
                  :class="selectedFile === file.path ? 'bg-blue-50/40' : ''"
              >
                <td class="p-4 font-mono text-xs font-bold text-slate-700">{{ file.path }}</td>
                <td class="p-4">
                  <span class="px-2 py-0.5 text-[10px] font-bold rounded-md uppercase tracking-wide" :class="kindClass(file.kind)">{{ file.kind }}</span>
                </td>
                <td class="p-4 text-right font-mono text-xs text-slate-500">{{ formatBytes(file.size_bytes) }}</td>
                <td class="p-4 text-right whitespace-nowrap">
                  <button
                      v-if="file.kind === 'table' && !NO_PREVIEW_FILES.includes(file.path)"
                      @click="previewTable(file.path)"
                      class="text-xs font-black py-1.5 px-3 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-600 transition-all mr-2"
                  >
                    {{ t('stressTests.detail.preview') }}
                  </button>
                  <button
                      @click="downloadFile(file.path)"
                      class="text-xs font-black py-1.5 px-3 rounded-lg bg-blue-50 hover:bg-blue-600 hover:text-white text-blue-600 transition-all"
                  >
                    {{ t('stressTests.detail.download') }}
                  </button>
                </td>
              </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div v-if="selectedFile" class="bg-white rounded-[2.5rem] shadow-xl shadow-slate-200/50 border border-slate-100 overflow-hidden">
          <div class="px-8 py-6 border-b border-slate-50 bg-slate-50/30 flex items-center justify-between">
            <h2 class="text-lg font-black text-slate-800 tracking-tight font-mono">{{ selectedFile }}</h2>
            <button @click="selectedFile = null" class="text-slate-400 hover:text-slate-700 font-black">✕</button>
          </div>
          <StressTestTable :table="tables[selectedFile]?.data" :loading="tables[selectedFile]?.loading" :error="tables[selectedFile]?.error" />
        </div>
      </div>
    </template>

    <!-- Lightbox -->
    <div
        v-if="lightbox"
        class="fixed inset-0 z-50 bg-slate-900/80 flex items-center justify-center p-8 cursor-zoom-out"
        @click="lightbox = null"
    >
      <img :src="lightbox" class="max-w-full max-h-full bg-white rounded-2xl p-4 shadow-2xl" alt="" />
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { stressTestsApi, saveBlob } from '@/composables/useStressTests'
import { getStatusData } from '@/constants/evaluationStatuses'
import {
  ACTIVE_STATUSES,
  OVERVIEW_TABLES,
  REVIEWER_TABLES,
  MANUSCRIPT_FILE,
  NO_PREVIEW_FILES,
  formatBytes,
  formatDuration,
  prettifyFileName,
} from '@/constants/stressTests'
import StressTestTable from '@/components/stressTests/StressTestTable.vue'
import StressTestFigure from '@/components/stressTests/StressTestFigure.vue'

const props = defineProps({ id: { type: [String, Number], required: true } })

const router = useRouter()
const { t, te } = useI18n()

const run = ref(null)
const files = ref([])
const tables = reactive({})
const manuscriptText = ref('')
const loadError = ref('')
const activeTab = ref('overview')
const selectedFile = ref(null)
const lightbox = ref(null)
const isDownloadingArchive = ref(false)

const tabs = ['overview', 'figures', 'reviewer', 'files']

const isActive = computed(() => run.value && ACTIVE_STATUSES.includes(run.value.status))
const filePaths = computed(() => new Set(files.value.map((f) => f.path)))
const totalSize = computed(() => files.value.reduce((acc, f) => acc + f.size_bytes, 0))

const overviewTables = computed(() => OVERVIEW_TABLES.filter((n) => filePaths.value.has(n)))
const reviewerTables = computed(() => REVIEWER_TABLES.filter((n) => filePaths.value.has(n)))
const hasManuscript = computed(() => filePaths.value.has(MANUSCRIPT_FILE))

// Figures grouped by stem; PNG (then SVG) is previewed, every format is downloadable.
const figures = computed(() => {
  const groups = {}
  for (const f of files.value) {
    if (f.kind !== 'figure') continue
    const ext = f.path.split('.').pop().toLowerCase()
    const stem = f.path.slice(0, -(ext.length + 1))
    groups[stem] ||= { stem, variants: [] }
    groups[stem].variants.push({ ext, path: f.path })
  }
  return Object.values(groups)
      .map((g) => ({
        ...g,
        preview: (g.variants.find((v) => v.ext === 'png') || g.variants.find((v) => v.ext === 'svg'))?.path || null,
      }))
      .sort((a, b) => a.stem.localeCompare(b.stem))
})

const designItems = computed(() => {
  const c = run.value?.config || {}
  return [
    { label: t('stressTests.create.fields.n'), value: c.n },
    { label: t('stressTests.create.fields.replicates'), value: c.replicates },
    { label: t('stressTests.create.fields.prevalences'), value: (c.prevalences || []).join(', ') },
    { label: t('stressTests.create.fields.severityLevels'), value: c.severity_levels },
    { label: t('stressTests.create.fields.seed'), value: c.seed },
    { label: 'μ / σ', value: `${c.mu} / ${c.sigma}` },
    { label: t('stressTests.create.fields.maxLogitBias'), value: c.max_logit_bias },
    { label: 'T min / max', value: `${c.min_temperature} / ${c.max_temperature}` },
    { label: t('stressTests.create.fields.collapseTargets'), value: `${c.collapse_positive_target ?? 0.95} / ${c.collapse_negative_target ?? 0.05}` },
    { label: t('stressTests.create.fields.severityBands'), value: `${c.severity_mild_max ?? 0.3} / ${c.severity_moderate_max ?? 0.7}` },
    { label: t('stressTests.create.fields.cvSplits'), value: c.cv_splits },
    { label: t('stressTests.create.fields.nBoot'), value: c.n_boot },
    { label: t('stressTests.create.fields.oodPrevalences'), value: (c.ood_prevalences || []).join(', ') },
    { label: t('stressTests.create.fields.oodReplicates'), value: c.ood_replicates },
    { label: t('stressTests.create.fields.publicLinks'), value: (c.public_links || []).join(' | ') || '—' },
    { label: t('stressTests.create.fields.figureFormats'), value: `${(c.figure_formats || []).join(', ')} @ ${c.figure_dpi} dpi` },
  ]
})

const tableKey = (name) => `stressTests.tables.${name.replace(/\.(csv\.gz|csv)$/, '')}`
const tableTitle = (name) => (te(`${tableKey(name)}.title`) ? t(`${tableKey(name)}.title`) : prettifyFileName(name))
const tableDesc = (name) => (te(`${tableKey(name)}.desc`) ? t(`${tableKey(name)}.desc`) : '')

const kindClass = (kind) => ({
  table: 'bg-blue-50 text-blue-600',
  figure: 'bg-purple-50 text-purple-600',
  text: 'bg-green-50 text-green-600',
}[kind] || 'bg-slate-100 text-slate-500')

const stepState = (step) => {
  const steps = run.value.steps
  const current = steps.indexOf(run.value.stage)
  const idx = steps.indexOf(step)
  if (current === -1) return 'waiting'
  if (idx < current) return 'done'
  if (idx === current) return 'running'
  return 'waiting'
}

const stepClass = (step) => ({
  done: 'bg-green-50 border-green-100 text-green-700',
  running: 'bg-blue-50 border-blue-100 text-blue-700',
  waiting: 'bg-slate-50 border-slate-100 text-slate-400',
}[stepState(step)])

const loadTable = async (name) => {
  if (tables[name]?.data || tables[name]?.loading) return
  tables[name] = { loading: true, data: null, error: '' }
  try {
    tables[name] = { loading: false, data: await stressTestsApi.getTable(props.id, name), error: '' }
  } catch (e) {
    tables[name] = { loading: false, data: null, error: e.message }
  }
}

const loadManuscript = async () => {
  if (manuscriptText.value || !hasManuscript.value) return
  try {
    const blob = await stressTestsApi.fetchFileBlob(props.id, MANUSCRIPT_FILE)
    manuscriptText.value = await blob.text()
  } catch (e) {
    manuscriptText.value = e.message
  }
}

const loadFiles = async () => {
  try {
    files.value = await stressTestsApi.listFiles(props.id)
  } catch (e) {
    loadError.value = e.message
  }
}

const loadRun = async () => {
  try {
    run.value = await stressTestsApi.get(props.id)
    loadError.value = ''
  } catch (e) {
    loadError.value = e.message
  }
}

const previewTable = (name) => {
  selectedFile.value = name
  loadTable(name)
}

const downloadFile = async (path) => {
  try {
    saveBlob(await stressTestsApi.fetchFileBlob(props.id, path), path.split('/').pop())
  } catch (e) {
    alert(e.message)
  }
}

const downloadArchive = async () => {
  isDownloadingArchive.value = true
  try {
    saveBlob(await stressTestsApi.fetchArchiveBlob(props.id), `stress_test_${props.id}_results.zip`)
  } catch (e) {
    alert(e.message)
  } finally {
    isDownloadingArchive.value = false
  }
}

const handleCancel = async () => {
  if (!confirm(t('stressTests.confirmCancel'))) return
  try {
    run.value = await stressTestsApi.cancel(props.id)
  } catch (e) {
    alert(e.message)
  }
}

const handleRerun = async () => {
  try {
    const created = await stressTestsApi.rerun(props.id)
    router.push(`/stress-tests/${created.id}`)
  } catch (e) {
    alert(e.message)
  }
}

// Lazy-load the tables of the visible tab once the files are known.
watch([activeTab, files], () => {
  if (activeTab.value === 'overview') overviewTables.value.forEach(loadTable)
  if (activeTab.value === 'reviewer') {
    reviewerTables.value.forEach(loadTable)
    loadManuscript()
  }
})

let pollingInterval = null
const stopPolling = () => {
  if (pollingInterval) clearInterval(pollingInterval)
  pollingInterval = null
}

const init = async () => {
  stopPolling()
  run.value = null
  files.value = []
  manuscriptText.value = ''
  selectedFile.value = null
  Object.keys(tables).forEach((k) => delete tables[k])

  await loadRun()
  await loadFiles()

  pollingInterval = setInterval(async () => {
    if (!isActive.value) return
    await loadRun()
    if (!isActive.value) await loadFiles()
  }, 3000)
}

// Re-run navigates between two runs while this view stays mounted.
watch(() => props.id, init)
onMounted(init)
onUnmounted(stopPolling)
</script>
