<template>
  <div class="max-w-5xl mx-auto space-y-8 pb-20">
    <div class="flex items-center">
      <button @click="$router.push('/stress-tests')" class="text-sm font-bold text-slate-500 hover:text-slate-800 flex items-center gap-2">
        <span>&larr;</span> {{ t('stressTests.create.back') }}
      </button>
    </div>

    <div>
      <h1 class="text-3xl font-black text-slate-900 tracking-tight">{{ t('stressTests.create.title') }}</h1>
      <p class="text-slate-500 font-medium mt-1">{{ t('stressTests.create.subtitle') }}</p>
    </div>

    <div v-if="isLoading" class="text-slate-500 font-medium animate-pulse">{{ t('common.loading') }}</div>

    <template v-else-if="form">
      <!-- General -->
      <div class="bg-white p-8 rounded-[2rem] shadow-sm border border-slate-100 space-y-6">
        <h2 class="text-xl font-black text-slate-800">{{ t('stressTests.create.sections.general') }}</h2>

        <div class="flex flex-col gap-2">
          <label class="label">{{ t('stressTests.create.fields.name') }}</label>
          <input v-model="form.name" type="text" maxlength="255" :placeholder="t('stressTests.create.namePlaceholder')" class="input" />
        </div>

        <div class="flex flex-col gap-2">
          <label class="label">{{ t('stressTests.create.fields.preset') }}</label>
          <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
            <button
                v-for="(values, key) in STRESS_TEST_PRESETS"
                :key="key"
                type="button"
                @click="applyPreset(key)"
                class="text-left p-4 rounded-2xl border-2 transition-all"
                :class="activePreset === key ? 'border-blue-500 bg-blue-50/50' : 'border-slate-100 hover:border-slate-200 bg-slate-50/50'"
            >
              <div class="font-black text-slate-800">{{ t(`stressTests.create.presets.${key}.title`) }}</div>
              <div class="text-xs text-slate-500 font-medium mt-1">{{ t(`stressTests.create.presets.${key}.desc`) }}</div>
              <div class="text-[10px] font-mono font-bold text-slate-400 mt-2">
                R={{ values.replicates }} · OOD={{ values.ood_replicates }} · boot={{ values.n_boot }}
              </div>
            </button>
          </div>
        </div>
      </div>

      <!-- Steps -->
      <div class="bg-white p-8 rounded-[2rem] shadow-sm border border-slate-100 space-y-6">
        <h2 class="text-xl font-black text-slate-800">{{ t('stressTests.create.sections.steps') }}</h2>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
          <label
              v-for="step in STRESS_TEST_STEPS"
              :key="step"
              class="flex items-start gap-3 p-4 rounded-2xl border-2 transition-all"
              :class="[
                form.steps.includes(step) ? 'border-blue-500 bg-blue-50/50' : 'border-slate-100 bg-slate-50/50',
                step === 'simulate' ? 'cursor-not-allowed' : 'cursor-pointer hover:border-slate-200'
              ]"
          >
            <input
                type="checkbox"
                :value="step"
                v-model="form.steps"
                :disabled="step === 'simulate'"
                class="mt-1 w-4 h-4 accent-blue-600"
            />
            <div>
              <div class="font-black text-slate-800">{{ t(`stressTests.steps.${step}.title`) }}</div>
              <div class="text-xs text-slate-500 font-medium mt-1">{{ t(`stressTests.steps.${step}.desc`) }}</div>
            </div>
          </label>
        </div>

        <div v-if="form.steps.includes('figures')" class="grid grid-cols-1 md:grid-cols-2 gap-6 pt-2">
          <div class="flex flex-col gap-2">
            <label class="label">{{ t('stressTests.create.fields.figureFormats') }}</label>
            <div class="flex gap-2">
              <button
                  v-for="fmt in FIGURE_FORMATS"
                  :key="fmt"
                  type="button"
                  @click="toggleFormat(fmt)"
                  class="px-4 py-2 rounded-xl text-sm font-black uppercase tracking-wide border transition-all"
                  :class="form.figure_formats.includes(fmt) ? 'bg-blue-600 text-white border-blue-600' : 'bg-slate-50 text-slate-500 border-slate-200 hover:bg-slate-100'"
              >
                {{ fmt }}
              </button>
            </div>
            <p class="text-xs text-slate-400 font-medium">{{ t('stressTests.create.hints.pngRequired') }}</p>
          </div>
          <div class="flex flex-col gap-2">
            <label class="label">DPI</label>
            <input v-model.number="form.figure_dpi" type="number" min="72" max="600" step="1" class="input" />
          </div>
        </div>
      </div>

      <!-- Simulation design -->
      <div class="bg-white p-8 rounded-[2rem] shadow-sm border border-slate-100 space-y-6">
        <h2 class="text-xl font-black text-slate-800">{{ t('stressTests.create.sections.design') }}</h2>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div class="flex flex-col gap-2">
            <label class="label">{{ t('stressTests.create.fields.n') }}</label>
            <input v-model.number="form.config.n" type="number" min="50" max="100000" class="input" />
          </div>
          <div class="flex flex-col gap-2">
            <label class="label">{{ t('stressTests.create.fields.replicates') }}</label>
            <input v-model.number="form.config.replicates" type="number" min="2" max="10000" class="input" @input="activePreset = null" />
          </div>
          <div class="flex flex-col gap-2">
            <label class="label">{{ t('stressTests.create.fields.seed') }}</label>
            <input v-model.number="form.config.seed" type="number" min="0" class="input" />
          </div>
          <div class="flex flex-col gap-2 md:col-span-2">
            <label class="label">{{ t('stressTests.create.fields.prevalences') }}</label>
            <input v-model="prevalencesText" type="text" class="input font-mono" placeholder="0.5, 0.3, 0.1, 0.05" />
          </div>
          <div class="flex flex-col gap-2">
            <label class="label">{{ t('stressTests.create.fields.severityLevels') }}</label>
            <input v-model.number="form.config.severity_levels" type="number" min="2" max="51" class="input" />
          </div>
        </div>

        <div class="p-5 bg-slate-50 rounded-2xl border border-slate-100 flex flex-wrap gap-x-10 gap-y-3 text-sm">
          <div>
            <div class="text-[10px] font-black text-slate-400 uppercase tracking-widest">{{ t('stressTests.create.estimate.rows') }}</div>
            <div class="font-mono font-black text-slate-800 text-lg">{{ estimatedRows.toLocaleString('en-US') }}</div>
          </div>
          <div>
            <div class="text-[10px] font-black text-slate-400 uppercase tracking-widest">{{ t('stressTests.create.estimate.paths') }}</div>
            <div class="font-mono font-black text-slate-800 text-lg">{{ failurePaths.length }}</div>
          </div>
          <div class="flex-1 min-w-[16rem]">
            <div class="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1">{{ t('stressTests.create.estimate.failurePaths') }}</div>
            <div class="flex flex-wrap gap-1">
              <span
                  v-for="path in failurePaths"
                  :key="path"
                  class="px-2 py-0.5 rounded-md border text-[10px] font-bold"
                  :class="FAILURE_PATH_STYLES[path] || 'bg-slate-100 text-slate-600 border-slate-200'"
              >{{ path }}</span>
            </div>
          </div>
        </div>

        <!-- Advanced -->
        <div>
          <button
              type="button"
              @click="showAdvanced = !showAdvanced"
              class="text-sm font-bold text-blue-600 hover:text-blue-800 flex items-center gap-2"
          >
            <span class="inline-block transition-transform" :class="showAdvanced ? 'rotate-90' : ''">▶</span>
            {{ t('stressTests.create.sections.advanced') }}
          </button>

          <div v-if="showAdvanced" class="grid grid-cols-1 md:grid-cols-3 gap-6 mt-6">
            <div v-for="field in advancedFields" :key="field.key" class="flex flex-col gap-2">
              <label class="label">{{ field.label }}</label>
              <input v-model.number="form.config[field.key]" type="number" :step="field.step" :min="field.min" class="input" />
            </div>
            <div class="flex flex-col gap-2">
              <label class="label">{{ t('stressTests.create.fields.oodPrevalences') }}</label>
              <input v-model="oodPrevalencesText" type="text" class="input font-mono" placeholder="0.5, 0.3, 0.1" />
            </div>
            <div class="flex flex-col gap-2 md:col-span-3">
              <label class="label">{{ t('stressTests.create.fields.publicLinks') }}</label>
              <textarea
                v-model="publicLinksText"
                rows="2"
                class="input font-mono text-xs"
                placeholder="GitHub: https://github.com/..."
              ></textarea>
              <p class="text-xs text-slate-400">{{ t('stressTests.create.hints.publicLinks') }}</p>
            </div>
          </div>
        </div>
      </div>

      <div v-if="errorMessage" class="p-4 bg-red-50 text-red-700 rounded-xl font-medium text-sm border border-red-100 whitespace-pre-line">
        {{ errorMessage }}
      </div>

      <div class="flex flex-col md:flex-row gap-3">
        <button
            type="button"
            @click="resetDefaults"
            class="md:w-auto px-6 py-4 bg-slate-100 text-slate-700 rounded-2xl font-black hover:bg-slate-200 transition-all"
        >
          {{ t('stressTests.create.reset') }}
        </button>
        <button
            @click="submit"
            :disabled="isSubmitting"
            class="flex-1 py-4 bg-blue-600 text-white rounded-2xl font-black shadow-lg shadow-blue-600/20 hover:bg-blue-700 disabled:bg-slate-300 transition-all flex items-center justify-center"
        >
          <span v-if="isSubmitting" class="animate-spin inline-block mr-2">⏳</span>
          {{ isSubmitting ? t('stressTests.create.submitting') : t('stressTests.create.submit') }}
        </button>
      </div>
    </template>

    <div v-else-if="errorMessage" class="p-4 bg-red-50 text-red-700 rounded-xl font-medium text-sm border border-red-100">
      {{ errorMessage }}
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { stressTestsApi } from '@/composables/useStressTests'
import {
  STRESS_TEST_STEPS,
  STRESS_TEST_PRESETS,
  FIGURE_FORMATS,
  FAILURE_PATH_STYLES,
} from '@/constants/stressTests'

const router = useRouter()
const { t } = useI18n()

const defaults = ref(null)
const form = ref(null)
const prevalencesText = ref('')
const oodPrevalencesText = ref('')
const publicLinksText = ref('')
const activePreset = ref('article')
const showAdvanced = ref(false)
const isLoading = ref(true)
const isSubmitting = ref(false)
const errorMessage = ref('')

const failurePaths = computed(() => defaults.value?.failure_paths || [])

const advancedFields = computed(() => [
  { key: 'mu', label: 'μ (class separation)', step: 0.1, min: 0 },
  { key: 'sigma', label: 'σ', step: 0.1, min: 0 },
  { key: 'max_logit_bias', label: t('stressTests.create.fields.maxLogitBias'), step: 0.5, min: 0 },
  { key: 'min_temperature', label: t('stressTests.create.fields.minTemperature'), step: 0.05, min: 0 },
  { key: 'max_temperature', label: t('stressTests.create.fields.maxTemperature'), step: 0.5, min: 1 },
  { key: 'collapse_positive_target', label: t('stressTests.create.fields.collapsePositiveTarget'), step: 0.01, min: 0.5 },
  { key: 'collapse_negative_target', label: t('stressTests.create.fields.collapseNegativeTarget'), step: 0.01, min: 0 },
  { key: 'severity_mild_max', label: t('stressTests.create.fields.severityMildMax'), step: 0.05, min: 0 },
  { key: 'severity_moderate_max', label: t('stressTests.create.fields.severityModerateMax'), step: 0.05, min: 0 },
  { key: 'cv_splits', label: t('stressTests.create.fields.cvSplits'), step: 1, min: 2 },
  { key: 'n_boot', label: t('stressTests.create.fields.nBoot'), step: 100, min: 10 },
  { key: 'ood_replicates', label: t('stressTests.create.fields.oodReplicates'), step: 1, min: 1 },
])

const parseList = (text) =>
    text.split(/[,;\s]+/).map((s) => s.trim()).filter(Boolean).map(Number)

const estimatedRows = computed(() => {
  if (!form.value) return 0
  const prevalences = parseList(prevalencesText.value).filter((v) => !Number.isNaN(v)).length
  return prevalences * (form.value.config.replicates || 0) * failurePaths.value.length * (form.value.config.severity_levels || 0)
})

const resetDefaults = () => {
  const d = defaults.value
  form.value = {
    name: '',
    steps: [...d.steps],
    figure_formats: [...d.figure_formats],
    figure_dpi: d.figure_dpi,
    config: { ...d.config },
  }
  prevalencesText.value = d.config.prevalences.join(', ')
  oodPrevalencesText.value = d.config.ood_prevalences.join(', ')
  publicLinksText.value = (d.config.public_links || []).join('\n')
  activePreset.value = 'article'
  errorMessage.value = ''
}

const applyPreset = (key) => {
  Object.assign(form.value.config, STRESS_TEST_PRESETS[key])
  activePreset.value = key
}

const toggleFormat = (fmt) => {
  const formats = form.value.figure_formats
  if (formats.includes(fmt)) {
    if (formats.length > 1) form.value.figure_formats = formats.filter((f) => f !== fmt)
  } else {
    form.value.figure_formats = [...formats, fmt]
  }
}

const submit = async () => {
  errorMessage.value = ''
  const prevalences = parseList(prevalencesText.value)
  const oodPrevalences = parseList(oodPrevalencesText.value)
  if ([...prevalences, ...oodPrevalences].some((v) => Number.isNaN(v) || v <= 0 || v >= 1) || !prevalences.length || !oodPrevalences.length) {
    errorMessage.value = t('stressTests.create.errors.prevalences')
    return
  }

  isSubmitting.value = true
  try {
    const run = await stressTestsApi.create({
      name: form.value.name?.trim() || null,
      steps: form.value.steps,
      figure_formats: form.value.figure_formats,
      figure_dpi: form.value.figure_dpi,
      config: {
        ...form.value.config,
        prevalences,
        ood_prevalences: oodPrevalences,
        public_links: publicLinksText.value.split('\n').map((s) => s.trim()).filter(Boolean),
      },
    })
    router.push(`/stress-tests/${run.id}`)
  } catch (e) {
    errorMessage.value = e.message
  } finally {
    isSubmitting.value = false
  }
}

onMounted(async () => {
  try {
    defaults.value = await stressTestsApi.getDefaults()
    resetDefaults()
  } catch (e) {
    errorMessage.value = e.message
  } finally {
    isLoading.value = false
  }
})
</script>

<style scoped>
@reference "@/assets/main.css";

.label {
  @apply text-xs font-black text-slate-400 uppercase tracking-widest;
}

.input {
  @apply px-4 py-3 rounded-xl bg-slate-50 border border-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500 font-medium text-slate-700;
}
</style>
