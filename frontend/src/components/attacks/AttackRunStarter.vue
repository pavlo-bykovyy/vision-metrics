<script setup>
/**
 * src/components/attacks/AttackRunStarter.vue
 *
 * Component for starting an attack/evaluation run on an existing dataset
 * targeting either a LoRA Adapter or a Base Model.
 * Automatically inspects the selected dataset's stored schema_config (and DB task configs)
 * to allow optional runtime overrides of dynamic INFERENCE_PROMPTS and canary system prompts.
 */

import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAttacks } from '@/composables/useAttacks'
import { DEFAULT_INFERENCE_PROMPTS } from '@/constants/attacks'

const props = defineProps({
  apiUrl: { type: String, default: () => import.meta.env.VITE_API_URL || '/api' },
  datasetId: { type: [Number, String], default: null },
})

const emit = defineEmits(['started'])
const router = useRouter()

const attacksApi = useAttacks(props.apiUrl)
const clone = (obj) => JSON.parse(JSON.stringify(obj))

const defaultParams = {
  max_new_tokens: 128,
  temperature: 0.1,
  top_k: 40,
  top_p: 0.9,
  repetition_penalty: 1.15,
  do_sample: true,
  system_prompt: null,
}

// Judge generation defaults (same as the regular judge run form): greedy decoding + enough tokens for a full JSON verdict
const defaultJudgeParams = {
  temperature: 0.0,
  max_new_tokens: 512,
  system_prompt: null,
}

// Core selection state
const datasetId = ref(props.datasetId ? Number(props.datasetId) : '')
const onlyAttackDatasets = ref(true)
const targetMode = ref('lora') // 'lora' | 'base_model'
const adapterId = ref('')
const baseModelId = ref('')
const judgeIds = ref([])
const paramsText = ref(JSON.stringify(defaultParams, null, 2))
const judgeParamsText = ref(JSON.stringify(defaultJudgeParams, null, 2))

// Dynamic prompt override state loaded from the selected dataset or DB task config
const enablePromptOverride = ref(false)
const activeTaskName = ref('heroes')
const datasetLanguages = ref(['UKRAINIAN', 'ENGLISH', 'RUSSIAN'])
const secretSystemPrompt = ref('')
const inferencePrompts = reactive(clone(DEFAULT_INFERENCE_PROMPTS))

// Resource lists from backend
const datasets = ref([])
const adapters = ref([])
const judges = ref([])

// UI status flags
const listsError = ref('')
const loading = ref(false)
const error = ref('')

const asList = (data) => (Array.isArray(data) ? data : data?.items ?? [])
const label = (x) => x.name ?? x.title ?? x.folder_name ?? x.model_name ?? `#${x.id}`
const datasetLabel = (d) =>
  `#${d.id} · ${d.name}${d.task_name ? ` [${d.task_name}]` : ''}${d.rows != null ? ` (${d.rows} рядків)` : ''}`

const DEFAULT_BASE_MODEL_PRESETS = [
  'Qwen/Qwen2.5-3B-Instruct',
  'Qwen/Qwen2.5-7B-Instruct',
  'HuggingFaceTB/SmolLM2-1.7B-Instruct',
  'TinyLlama/TinyLlama-1.1B-Chat-v1.0',
  'mistralai/Mistral-7B-Instruct-v0.3',
]

/**
 * Extract unique base_model_name_or_path values from registered LoRA adapters + default presets.
 */
const knownBaseModels = computed(() => {
  const set = new Set()
  for (const a of adapters.value) {
    const bm = (a.base_model_name_or_path || '').trim()
    if (bm) set.add(bm)
  }
  for (const preset of DEFAULT_BASE_MODEL_PRESETS) {
    set.add(preset)
  }
  return Array.from(set)
})

/**
 * Ensure the active task entry exists in inferencePrompts for all dataset languages.
 */
function ensureTaskStructure(taskKey) {
  const key = (taskKey || 'heroes').trim()
  if (!inferencePrompts[key]) {
    inferencePrompts[key] = {
      max_new_tokens: 180,
      expected_output_format: 'text',
      languages: {},
    }
  }
  if (!inferencePrompts[key].languages) {
    inferencePrompts[key].languages = {}
  }
  for (const lang of datasetLanguages.value) {
    if (!inferencePrompts[key].languages[lang]) {
      inferencePrompts[key].languages[lang] = {
        system: 'You are a careful AI assistant.',
        user: 'Input:\n{input_text}',
      }
    }
  }
}

/**
 * Load available datasets from the backend.
 */
async function loadDatasets() {
  datasets.value = asList(
    await attacksApi.listDatasets({
      only_attack_kind: onlyAttackDatasets.value,
      limit: 200,
    }),
  )
}

watch(onlyAttackDatasets, () => {
  loadDatasets().catch(() => {})
})

/**
 * Load dynamic configuration stored inside Dataset.schema_config when datasetId changes.
 */
async function loadSelectedDatasetConfig(id) {
  if (!id) return
  try {
    const cfg = await attacksApi.getDatasetConfig(Number(id))
    const schema = cfg?.schema_config || {}

    if (Array.isArray(schema.languages) && schema.languages.length) {
      datasetLanguages.value = [...schema.languages]
    }
    if (schema.task_name) {
      activeTaskName.value = schema.task_name
    }
    if (schema.secret_system_prompt_template) {
      secretSystemPrompt.value = schema.secret_system_prompt_template
    }
    if (schema.inference_prompts && typeof schema.inference_prompts === 'object') {
      Object.assign(inferencePrompts, clone(schema.inference_prompts))
    }
    ensureTaskStructure(activeTaskName.value)
  } catch {
    ensureTaskStructure(activeTaskName.value)
  }
}

onMounted(async () => {
  ensureTaskStructure(activeTaskName.value)

  const [d, a, j, taskCfgs] = await Promise.allSettled([
    loadDatasets(),
    attacksApi.listAdapters(),
    attacksApi.listJudges(),
    attacksApi.listTaskConfigs(),
  ])

  if (a.status === 'fulfilled') adapters.value = asList(a.value)
  if (j.status === 'fulfilled') {
    judges.value = asList(j.value)
    if (!judgeIds.value.length && judges.value.length) {
      judgeIds.value = [judges.value[0].id]
    }
  }
  if (taskCfgs.status === 'fulfilled' && Array.isArray(taskCfgs.value)) {
    for (const tc of taskCfgs.value) {
      if (tc.task_name && tc.inference_prompts) {
        inferencePrompts[tc.task_name] = {
          max_new_tokens: tc.max_new_tokens || 180,
          expected_output_format: tc.expected_output_format || 'text',
          languages: clone(tc.inference_prompts),
        }
      }
    }
  }

  const failed = []
  if (d.status === 'rejected') failed.push('датасети')
  if (a.status === 'rejected') failed.push('адаптери')
  if (j.status === 'rejected') failed.push('суддів')

  if (failed.length) {
    listsError.value = `Не вдалося завантажити: ${failed.join(', ')}. Перевірте з'єднання з бекендом.`
  }

  if (datasetId.value) {
    await loadSelectedDatasetConfig(datasetId.value)
  }
})

watch(
  () => props.datasetId,
  async (id) => {
    if (!id) return
    const numId = Number(id)
    datasetId.value = numId
    if (!datasets.value.some((d) => d.id === numId)) {
      try {
        await loadDatasets()
      } catch {
        // Keep ID selected even if list refresh fails
      }
    }
    await loadSelectedDatasetConfig(numId)
  },
)

watch(datasetId, async (newId) => {
  if (newId) await loadSelectedDatasetConfig(newId)
})

/**
 * Validate optional JSON generation parameters.
 */
const parsedParams = computed(() => {
  const text = paramsText.value.trim()
  if (!text) return { value: null }

  try {
    const value = JSON.parse(text)
    if (value === null || typeof value !== 'object' || Array.isArray(value)) {
      return { error: 'Потрібен JSON-об\'єкт, наприклад {"max_new_tokens": 256}' }
    }
    return { value }
  } catch {
    return { error: 'Некоректний формат JSON' }
  }
})

const parsedJudgeParams = computed(() => {
  const text = judgeParamsText.value.trim()
  if (!text) return { value: { ...defaultJudgeParams } }

  try {
    const value = JSON.parse(text)
    if (value === null || typeof value !== 'object' || Array.isArray(value)) {
      return { error: 'Потрібен JSON-об\'єкт, наприклад {"temperature": 0.0, "max_new_tokens": 512}' }
    }
    return { value }
  } catch {
    return { error: 'Некоректний формат JSON' }
  }
})

const hasValidTarget = computed(() => {
  if (targetMode.value === 'lora') {
    return Boolean(adapterId.value)
  }
  return Boolean(baseModelId.value.trim())
})

const canSubmit = computed(
  () =>
    Boolean(datasetId.value) &&
    hasValidTarget.value &&
    !parsedParams.value.error &&
    !parsedJudgeParams.value.error &&
    !loading.value,
)

/**
 * Submit the run request to POST /llm/attacks/runs with optional dynamic prompt overrides.
 */
async function submit() {
  if (!canSubmit.value) return

  error.value = ''
  loading.value = true

  try {
    let overridePayload = null
    if (enablePromptOverride.value && inferencePrompts[activeTaskName.value]) {
      overridePayload = {
        [activeTaskName.value]: inferencePrompts[activeTaskName.value],
      }
    }

    const started = await attacksApi.startRun({
      dataset_id: Number(datasetId.value),
      adapter_id: targetMode.value === 'lora' ? Number(adapterId.value) : null,
      base_model_id: targetMode.value === 'base_model' ? baseModelId.value.trim() : null,
      judge_ids: judgeIds.value.map(Number),
      generation_params: parsedParams.value.value,
      judge_params: judgeIds.value.length ? parsedJudgeParams.value.value : null,
      secret_system_prompt_template: secretSystemPrompt.value.trim() || null,
      inference_prompts_override: overridePayload,
    })
    emit('started', started)
  } catch (e) {
    error.value = e?.message || 'Сталася помилка при запуску атаки.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <form @submit.prevent="submit" class="space-y-6">
    <!-- Connection Warning -->
    <div
      v-if="listsError"
      class="p-4 bg-amber-50 text-amber-800 rounded-xl font-medium text-sm border border-amber-200 flex items-center gap-2"
    >
      <span>⚠️ {{ listsError }}</span>
    </div>

    <!-- 1. Dataset Selector -->
    <div class="flex flex-col gap-2">
      <div class="flex flex-wrap items-center justify-between gap-2">
        <label for="atk-dataset" class="text-xs font-black text-slate-400 uppercase tracking-widest">
          1. Датасет атаки
        </label>
        <div class="flex items-center gap-4">
          <label class="flex items-center gap-1.5 text-xs font-semibold text-slate-600 cursor-pointer">
            <input
              v-model="onlyAttackDatasets"
              type="checkbox"
              class="w-3.5 h-3.5 text-blue-600 rounded border-slate-300"
            />
            <span>Лише Attack Datasets</span>
          </label>
          <button
            type="button"
            @click="router.push('/attacks/datasets/create')"
            class="text-xs font-bold text-blue-600 hover:text-blue-800 underline"
          >
            + Створити новий Attack Dataset
          </button>
        </div>
      </div>

      <select
        v-if="datasets.length"
        id="atk-dataset"
        v-model.number="datasetId"
        required
        class="w-full px-4 py-3 rounded-xl bg-slate-50 border border-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500 font-medium text-slate-700 transition-all cursor-pointer"
      >
        <option value="" disabled>Оберіть згенерований або завантажений датасет...</option>
        <option v-for="d in datasets" :key="d.id" :value="d.id">
          {{ datasetLabel(d) }}
        </option>
      </select>
      <input
        v-else
        id="atk-dataset"
        v-model.number="datasetId"
        type="number"
        min="1"
        required
        placeholder="Введіть ID датасету (або створіть новий Attack Dataset)"
        class="w-full px-4 py-3 rounded-xl bg-slate-50 border border-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500 font-medium text-slate-700 transition-all"
      />
    </div>

    <!-- 2. Target Model Mode: LoRA Adapter vs Base Model -->
    <div class="space-y-3 p-5 bg-slate-50/70 rounded-2xl border border-slate-200/80">
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
        <label class="text-xs font-black text-slate-400 uppercase tracking-widest">
          2. Цільова модель для атаки
        </label>
        <div class="flex bg-slate-200/70 p-1 rounded-xl gap-1">
          <button
            type="button"
            @click="targetMode = 'lora'"
            :class="[
              'px-3.5 py-1.5 text-xs font-bold rounded-lg transition-all',
              targetMode === 'lora'
                ? 'bg-white shadow-sm text-slate-900'
                : 'text-slate-600 hover:text-slate-900',
            ]"
          >
            🔌 LoRA Adapter
          </button>
          <button
            type="button"
            @click="targetMode = 'base_model'"
            :class="[
              'px-3.5 py-1.5 text-xs font-bold rounded-lg transition-all',
              targetMode === 'base_model'
                ? 'bg-white shadow-sm text-slate-900'
                : 'text-slate-600 hover:text-slate-900',
            ]"
          >
            📦 Base Model
          </button>
        </div>
      </div>

      <!-- Mode A: LoRA Adapter -->
      <div v-if="targetMode === 'lora'" class="space-y-2">
        <select
          v-if="adapters.length"
          id="atk-adapter"
          v-model="adapterId"
          required
          class="w-full px-4 py-3 rounded-xl bg-white border border-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500 font-medium text-slate-700 transition-all cursor-pointer"
        >
          <option value="" disabled>Оберіть LoRA адаптер...</option>
          <option v-for="a in adapters" :key="a.id" :value="a.id">
            {{ label(a) }}{{ a.base_model_name_or_path ? ` (Base: ${a.base_model_name_or_path})` : '' }}
          </option>
        </select>
        <input
          v-else
          id="atk-adapter"
          v-model.number="adapterId"
          type="number"
          min="1"
          required
          placeholder="Введіть ID LoRA адаптера"
          class="w-full px-4 py-3 rounded-xl bg-white border border-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500 font-medium text-slate-700 transition-all"
        />
      </div>

      <!-- Mode B: Base Model -->
      <div v-else class="space-y-3">
        <div class="flex flex-col gap-2">
          <label for="atk-base-model" class="text-xs font-black text-slate-400 uppercase tracking-widest">
            Base Model ID (HuggingFace)
          </label>
          <input
            id="atk-base-model"
            v-model="baseModelId"
            type="text"
            required
            placeholder="e.g., Qwen/Qwen2.5-3B-Instruct, gpt2"
            class="px-4 py-3 rounded-xl bg-white border border-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500 font-medium text-slate-700"
          />
        </div>

        <div v-if="knownBaseModels.length" class="p-3.5 bg-white rounded-xl border border-slate-200/80 space-y-2">
          <span class="text-[11px] font-bold text-slate-400 uppercase tracking-wider block">
            ⚡ Швидкий вибір базової моделі (пресети + моделі з адаптерів):
          </span>
          <div class="flex flex-wrap gap-2">
            <button
              v-for="bm in knownBaseModels"
              :key="bm"
              type="button"
              @click="baseModelId = bm"
              :class="[
                'px-3 py-1.5 rounded-xl text-xs font-bold border transition-all',
                baseModelId === bm
                  ? 'bg-blue-600 text-white border-blue-600 shadow-sm'
                  : 'bg-slate-50 text-slate-600 border-slate-200 hover:bg-slate-100',
              ]"
            >
              {{ bm }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Judges Selection -->
    <fieldset class="flex flex-col gap-2">
      <div class="flex justify-between items-center mb-1">
        <legend class="text-xs font-black text-slate-400 uppercase tracking-widest">
          3. Судді (LLM-as-a-Judge)
        </legend>
        <span class="text-xs font-medium text-slate-400 bg-slate-100 px-2 py-0.5 rounded-md">
          Без суддів запуститься лише генерація відповідей
        </span>
      </div>

      <div v-if="judges.length" class="flex flex-wrap gap-2">
        <label
          v-for="j in judges"
          :key="j.id"
          :class="[
            'flex items-center gap-2 px-3 py-2 rounded-xl text-sm font-medium border cursor-pointer transition-all select-none',
            judgeIds.includes(j.id)
              ? 'bg-blue-50 border-blue-200 text-blue-700 font-semibold'
              : 'bg-slate-50 border-slate-200 text-slate-600 hover:bg-slate-100',
          ]"
        >
          <input
            v-model="judgeIds"
            type="checkbox"
            :value="j.id"
            class="w-4 h-4 text-blue-600 rounded border-slate-300 focus:ring-blue-500"
          />
          <span>{{ label(j) }}</span>
        </label>
      </div>
      <p v-else class="text-sm text-slate-500 italic p-3 bg-slate-50 rounded-xl border border-slate-200">
        Список доступних суддів порожній.
      </p>

      <div v-if="judgeIds.length" class="flex flex-col gap-2 mt-2">
        <label for="atk-judge-params" class="text-xs font-black text-slate-400 uppercase tracking-widest">
          Параметри судді <span class="text-slate-400 font-normal lowercase">(JSON)</span>
        </label>
        <textarea
          id="atk-judge-params"
          v-model="judgeParamsText"
          spellcheck="false"
          rows="4"
          placeholder='{"temperature": 0.0, "max_new_tokens": 512}'
          class="w-full px-4 py-3 rounded-xl bg-slate-50 border border-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono text-sm text-slate-700 resize-y transition-all"
        ></textarea>
        <span class="text-xs text-slate-400">
          temperature 0.0 = жадібне декодування (рекомендовано); max_new_tokens має вистачати на повний JSON-вердикт.
        </span>
        <span v-if="parsedJudgeParams.error" class="text-xs font-semibold text-red-500 flex items-center gap-1">
          ⚠️ {{ parsedJudgeParams.error }}
        </span>
      </div>
    </fieldset>

    <!-- Dynamic INFERENCE_PROMPTS Override Section -->
    <div class="p-4 bg-slate-50 rounded-2xl border border-slate-200 space-y-4">
      <div class="flex items-center justify-between">
        <div>
          <span class="text-xs font-black text-slate-700 uppercase tracking-wider block">
            Перевизначити шаблони промптів (INFERENCE_PROMPTS Override)
          </span>
          <span class="text-xs text-slate-500">
            Задача датасету: <strong>{{ activeTaskName }}</strong> (мови: {{ datasetLanguages.join(', ') }})
          </span>
        </div>
        <input
          v-model="enablePromptOverride"
          type="checkbox"
          class="w-4 h-4 text-blue-600 rounded border-slate-300 focus:ring-blue-500 cursor-pointer"
        />
      </div>

      <div
        v-if="enablePromptOverride && inferencePrompts[activeTaskName]"
        class="space-y-3 pt-3 border-t border-slate-200"
      >
        <div
          v-for="lang in datasetLanguages"
          :key="`run-ovr-${lang}`"
          class="p-3 bg-white rounded-xl border border-slate-200 space-y-2"
        >
          <div class="text-xs font-black text-blue-600 uppercase">{{ lang }}</div>
          <div v-if="inferencePrompts[activeTaskName].languages[lang]" class="space-y-2">
            <input
              v-model="inferencePrompts[activeTaskName].languages[lang].system"
              type="text"
              placeholder="SYSTEM prompt..."
              class="w-full px-3 py-1.5 rounded-lg bg-slate-50 border border-slate-200 text-xs"
            />
            <textarea
              v-model="inferencePrompts[activeTaskName].languages[lang].user"
              rows="3"
              placeholder="USER template with {input_text}..."
              class="w-full px-3 py-1.5 rounded-lg bg-slate-50 border border-slate-200 text-xs font-mono"
            ></textarea>
          </div>
        </div>
      </div>
    </div>

    <!-- Optional JSON Generation Parameters -->
    <div class="flex flex-col gap-2">
      <label for="atk-params" class="text-xs font-black text-slate-400 uppercase tracking-widest">
        Параметри генерації <span class="text-slate-400 font-normal lowercase">(JSON)</span>
      </label>
      <textarea
        id="atk-params"
        v-model="paramsText"
        spellcheck="false"
        rows="4"
        placeholder='{"max_new_tokens": 256, "temperature": 0.1}'
        class="w-full px-4 py-3 rounded-xl bg-slate-50 border border-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono text-sm text-slate-700 resize-y transition-all"
      ></textarea>

      <span
        v-if="parsedParams.error"
        class="text-xs font-semibold text-red-500 mt-1 flex items-center gap-1"
      >
        ⚠️ {{ parsedParams.error }}
      </span>
    </div>

    <button
      type="submit"
      :disabled="!canSubmit"
      class="w-full md:w-auto px-8 py-3 bg-blue-600 text-white font-bold rounded-xl shadow-lg shadow-blue-600/20 hover:bg-blue-700 disabled:bg-slate-300 disabled:shadow-none disabled:cursor-not-allowed transition-all flex items-center justify-center gap-2"
    >
      <svg
        v-if="loading"
        class="animate-spin h-5 w-5 text-white"
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
      <span>{{ loading ? 'Запускаємо оцінювання…' : 'Запустити атаку' }}</span>
    </button>

    <div
      v-if="error"
      class="p-4 bg-red-50 border border-red-200 text-red-700 rounded-xl font-medium text-sm flex items-center gap-2"
      role="alert"
    >
      <span>🚨 {{ error }}</span>
    </div>
  </form>
</template>