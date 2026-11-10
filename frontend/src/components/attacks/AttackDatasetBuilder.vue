<script setup>
/**
 * src/components/attacks/AttackDatasetBuilder.vue
 *
 * Compact Attack Dataset Builder UI.
 * Loads tasks (`attack_task_configs`), scenario templates (`attack_templates`),
 * and wrapping techniques (`attack_techniques`) from PostgreSQL, lets the user
 * toggle active scenarios/techniques/languages with checkboxes, configure/extract
 * entities and batching, and generate a new `.jsonl` Attack Dataset.
 * Full template editing is separated onto `/attacks/templates` (`AttackTemplatesView.vue`).
 */

import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAttacks } from '@/composables/useAttacks'
import {
  DEFAULT_LANGUAGES,
  DEFAULT_SECRET_SYSTEM_PROMPT,
  DEFAULT_TASK_TEMPLATES,
  DEFAULT_TECHNIQUE_SPECS,
  DEFAULT_INFERENCE_PROMPTS,
} from '@/constants/attacks'

const props = defineProps({
  apiUrl: {
    type: String,
    default: () => import.meta.env.VITE_API_URL || '/api',
  },
})

const emit = defineEmits(['created'])
const route = useRoute()
const router = useRouter()
const attacksApi = useAttacks(props.apiUrl)

const clone = (obj) => JSON.parse(JSON.stringify(obj))

// Core dataset metadata
const name = ref('')
const taskName = ref(route.query.task || 'heroes')
const useInferencePrompts = ref(true)
const canaryPrefix = ref('CANARY')
const secretSystemPrompt = ref(DEFAULT_SECRET_SYSTEM_PROMPT)
const entitiesText = ref('Тарас Шевченко\nЛеся Українка\nІван Франко\nВасиль Стус\nГригорій Сковорода')

// Entity batching & extraction (from code_from_ipynb.txt)
const useEntityBatching = ref(false)
const batchSize = ref(20)
const batchIndex = ref(0)
const shuffleEntities = ref(false)

// Entity extraction source: 'text' | 'dataset'
const extractMode = ref('text')
const rawExtractInput = ref('')
const sourceDatasetId = ref('')
const availableDatasets = ref([])
const extractingEntities = ref(false)

// Active languages
const languages = ref([...DEFAULT_LANGUAGES])

// DB-backed task configs, templates, and techniques
const dbTaskConfigs = ref([])
const dbTemplates = ref([])
const dbTechniques = ref([])
const loadingDbConfig = ref(false)
const statusBanner = ref('')

// Reactive selection state populated from DB
const intentsConfig = reactive(clone(DEFAULT_TASK_TEMPLATES.heroes))
const techniquesConfig = reactive(clone(DEFAULT_TECHNIQUE_SPECS))
const inferencePromptsConfig = reactive(clone(DEFAULT_INFERENCE_PROMPTS))

const loading = ref(false)
const error = ref('')
const created = ref(null)

/**
 * Parse entities from textarea (split by newline or comma).
 */
const allEntities = computed(() =>
  entitiesText.value
    .split(/[\n,]/)
    .map((e) => e.trim())
    .filter(Boolean),
)

/**
 * Preview sliced entity count when batching is enabled.
 */
const activeEntitiesCount = computed(() => {
  const total = allEntities.value.length
  if (!useEntityBatching.value || !batchSize.value || batchSize.value <= 0) {
    return total
  }
  const start = batchIndex.value * batchSize.value
  if (start >= total) return 0
  return Math.min(batchSize.value, total - start)
})

function ensureTaskPromptStructure(taskKey) {
  const cleanKey = (taskKey || 'heroes').trim()
  if (!cleanKey) return
  if (!inferencePromptsConfig[cleanKey]) {
    const langObj = {}
    for (const lang of languages.value) {
      langObj[lang] = {
        system: 'You are a careful AI assistant.',
        user: 'Process the following input carefully:\n\n{input_text}',
      }
    }
    inferencePromptsConfig[cleanKey] = {
      max_new_tokens: 180,
      expected_output_format: 'text',
      languages: langObj,
    }
  }
}

/**
 * Apply loaded DB task config & templates for `targetTask` into selection state.
 */
function applyTaskFromDb(targetTask) {
  const cleanKey = (targetTask || 'heroes').trim()
  ensureTaskPromptStructure(cleanKey)

  // 1. Apply AttackTaskConfig from DB
  const foundTaskCfg = dbTaskConfigs.value.find((t) => t.task_name === cleanKey)
  if (foundTaskCfg) {
    if (foundTaskCfg.languages_config && Object.keys(foundTaskCfg.languages_config).length > 0) {
      inferencePromptsConfig[cleanKey] = {
        max_new_tokens: foundTaskCfg.max_new_tokens || 180,
        expected_output_format: foundTaskCfg.expected_output_format || 'free_text',
        languages: clone(foundTaskCfg.languages_config),
      }
    }
    const defEnt = foundTaskCfg.default_entities || {}
    if (Array.isArray(defEnt.entities) && defEnt.entities.length > 0) {
      entitiesText.value = defEnt.entities.join('\n')
    } else if (Array.isArray(defEnt.real) || Array.isArray(defEnt.fake)) {
      entitiesText.value = [...(defEnt.real || []), ...(defEnt.fake || [])].join('\n')
    }
  }

  // 2. Apply AttackTemplates for this task from DB
  const taskTemplates = dbTemplates.value.filter((tpl) => tpl.task_name === cleanKey)
  for (const k of Object.keys(intentsConfig)) {
    delete intentsConfig[k]
  }

  if (taskTemplates.length > 0) {
    for (const tpl of taskTemplates) {
      intentsConfig[tpl.key] = {
        id: tpl.id,
        enabled: tpl.is_enabled !== false,
        metric_category: tpl.metric_category || tpl.key,
        variant: tpl.variant || null,
        goal: tpl.goal || '',
        ground_truth: tpl.ground_truth || {},
        check_canary: Boolean(tpl.check_canary),
        text: clone(tpl.text || {}),
      }
    }
  } else {
    const presetTemplates = clone(
      DEFAULT_TASK_TEMPLATES[cleanKey] || DEFAULT_TASK_TEMPLATES.heroes,
    )
    for (const [k, spec] of Object.entries(presetTemplates)) {
      intentsConfig[k] = spec
    }
  }

  // 3. Apply AttackTechniques from DB
  if (dbTechniques.value.length > 0) {
    for (const k of Object.keys(techniquesConfig)) {
      delete techniquesConfig[k]
    }
    for (const tech of dbTechniques.value) {
      techniquesConfig[tech.key] = {
        id: tech.id,
        enabled: tech.is_enabled !== false,
        templates: clone(tech.templates || {}),
      }
    }
  }
}

/**
 * Load task configs, attack templates, techniques, and datasets from PostgreSQL.
 */
async function loadFromDatabase() {
  loadingDbConfig.value = true
  error.value = ''
  try {
    const [taskConfigsRes, templatesRes, techniquesRes, datasetsRes] = await Promise.allSettled([
      attacksApi.listTaskConfigs(),
      attacksApi.listTemplates(),
      attacksApi.listTechniques(),
      attacksApi.listDatasets({ limit: 200 }),
    ])

    if (taskConfigsRes.status === 'fulfilled' && Array.isArray(taskConfigsRes.value)) {
      dbTaskConfigs.value = taskConfigsRes.value
    }
    if (templatesRes.status === 'fulfilled' && Array.isArray(templatesRes.value)) {
      dbTemplates.value = templatesRes.value
    }
    if (techniquesRes.status === 'fulfilled' && Array.isArray(techniquesRes.value)) {
      dbTechniques.value = techniquesRes.value
    }
    if (datasetsRes.status === 'fulfilled') {
      availableDatasets.value = Array.isArray(datasetsRes.value)
        ? datasetsRes.value
        : datasetsRes.value?.items || []
    }

    const discoveredLangs = new Set(languages.value)
    for (const tpl of dbTemplates.value) {
      Object.keys(tpl.text || {}).forEach((l) => discoveredLangs.add(l))
    }
    languages.value = Array.from(discoveredLangs)

    applyTaskFromDb(taskName.value)
  } catch (e) {
    error.value = `Не вдалося завантажити шаблони з БД: ${e.message}`
  } finally {
    loadingDbConfig.value = false
  }
}

onMounted(() => {
  loadFromDatabase()
})

function selectTaskPreset(presetKey) {
  taskName.value = presetKey
  applyTaskFromDb(presetKey)
}

function goToTemplatesPage(tab = 'scenarios') {
  router.push({
    path: '/attacks/templates',
    query: { tab, task: taskName.value },
  })
}

/**
 * Extract hero/person names dynamically from raw text OR an existing Dataset.
 */
async function handleExtractEntities() {
  extractingEntities.value = true
  error.value = ''
  statusBanner.value = ''
  try {
    const reqPayload = {
      filter_hero_names: true,
    }
    if (extractMode.value === 'dataset') {
      if (!sourceDatasetId.value) {
        error.value = 'Оберіть датасет для витягнення імен.'
        extractingEntities.value = false
        return
      }
      reqPayload.source_dataset_id = Number(sourceDatasetId.value)
    } else {
      if (!rawExtractInput.value.trim()) {
        extractingEntities.value = false
        return
      }
      reqPayload.raw_text = rawExtractInput.value
    }

    const res = await attacksApi.extractEntities(reqPayload)
    if (res.entities && res.entities.length > 0) {
      const merged = Array.from(new Set([...allEntities.value, ...res.entities]))
      entitiesText.value = merged.join('\n')
      rawExtractInput.value = ''
      statusBanner.value = `Витягнуто сутностей: ${res.entities.length} (усього у списку: ${merged.length})`
    } else {
      statusBanner.value = 'Не знайдено імен формату «Ім’я Прізвище» у вказаному джерелі.'
    }
  } catch (e) {
    error.value = e.message || 'Помилка автоматичного витягнення сутностей'
  } finally {
    extractingEntities.value = false
  }
}

const activeIntentKeys = computed(() =>
  Object.keys(intentsConfig).filter((k) => intentsConfig[k].enabled),
)

const activeTechniqueKeys = computed(() =>
  Object.keys(techniquesConfig).filter((k) => techniquesConfig[k].enabled),
)

const requiresEntities = computed(() =>
  activeIntentKeys.value.some((k) =>
    languages.value.some((lang) => (intentsConfig[k].text[lang] || '').includes('{entity}')),
  ),
)

const totalRowsForecast = computed(() => {
  if (!activeIntentKeys.value.length || !activeTechniqueKeys.value.length || !languages.value.length) {
    return 0
  }
  let total = 0
  const techCount = activeTechniqueKeys.value.length
  const langCount = languages.value.length

  for (const key of activeIntentKeys.value) {
    const usesEntity = languages.value.some((lang) =>
      (intentsConfig[key].text[lang] || '').includes('{entity}'),
    )
    const entityMultiplier = usesEntity ? activeEntitiesCount.value : 1
    total += entityMultiplier * techCount * langCount
  }
  return total
})

const canSubmit = computed(() => {
  if (!name.value.trim() || !taskName.value.trim() || loading.value) return false
  if (!activeIntentKeys.value.length || !activeTechniqueKeys.value.length || !languages.value.length) {
    return false
  }
  if (requiresEntities.value && activeEntitiesCount.value === 0) return false
  return true
})

async function submit() {
  if (!canSubmit.value) return

  error.value = ''
  created.value = null
  loading.value = true

  try {
    const currentTaskKey = taskName.value.trim()
    ensureTaskPromptStructure(currentTaskKey)

    // 1. Assemble enabled intents dictionary
    const intentsPayload = {}
    for (const k of activeIntentKeys.value) {
      const spec = intentsConfig[k]
      const filteredText = {}
      for (const lang of languages.value) {
        filteredText[lang] = spec.text[lang] || spec.text.ENGLISH || ''
      }
      const gtDict =
        typeof spec.ground_truth === 'object' && spec.ground_truth !== null
          ? spec.ground_truth
          : null

      intentsPayload[k] = {
        metric_category: spec.metric_category || k,
        variant: spec.variant || null,
        goal: spec.goal || 'Evaluate model compliance and safety.',
        ground_truth: gtDict,
        check_canary: Boolean(spec.check_canary),
        text: filteredText,
      }
    }

    // 2. Assemble enabled techniques dictionary
    const techniquesPayload = {}
    for (const k of activeTechniqueKeys.value) {
      const spec = techniquesConfig[k]
      const filteredTemplates = {}
      for (const lang of languages.value) {
        filteredTemplates[lang] = spec.templates[lang] || '{t}'
      }
      techniquesPayload[k] = {
        templates: filteredTemplates,
      }
    }

    // 3. Assemble dynamic INFERENCE_PROMPTS if enabled
    let inferencePromptsPayload = null
    if (useInferencePrompts.value) {
      const taskCfg = inferencePromptsConfig[currentTaskKey]
      const filteredLangs = {}
      for (const lang of languages.value) {
        const lObj = taskCfg?.languages?.[lang] || {}
        filteredLangs[lang] = {
          system: lObj.system || 'You are a careful AI assistant.',
          user: lObj.user || '{input_text}',
          task_instruction: lObj.task_instruction || null,
          baseline_gt: lObj.baseline_gt || null,
          baseline_gt_real: lObj.baseline_gt_real || null,
          baseline_gt_fake: lObj.baseline_gt_fake || null,
          title_prefix: lObj.title_prefix || null,
          body_prefix: lObj.body_prefix || null,
        }
      }
      inferencePromptsPayload = {
        [currentTaskKey]: {
          max_new_tokens: Number(taskCfg?.max_new_tokens) || 180,
          expected_output_format: taskCfg?.expected_output_format || 'free_text',
          languages: filteredLangs,
        },
      }
    }

    const payload = {
      name: name.value.trim(),
      task_name: currentTaskKey,
      languages: languages.value,
      entities: allEntities.value,
      batch_size: useEntityBatching.value ? Number(batchSize.value) || null : null,
      batch_index: useEntityBatching.value ? Number(batchIndex.value) || 0 : 0,
      shuffle_entities: Boolean(useEntityBatching.value && shuffleEntities.value),
      canary_prefix: canaryPrefix.value.trim() || 'CANARY',
      secret_system_prompt_template: secretSystemPrompt.value.trim() || null,
      intents: intentsPayload,
      techniques: techniquesPayload,
      inference_prompts: inferencePromptsPayload,
    }

    const result = await attacksApi.buildDataset(payload)
    created.value = result
    emit('created', result)
  } catch (e) {
    error.value = e?.message || 'Сталася помилка при створенні датасету.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <form @submit.prevent="submit" class="space-y-7">
    <!-- Status Banner -->
    <div
      v-if="statusBanner"
      class="p-3.5 bg-emerald-50 border border-emerald-200 text-emerald-800 rounded-xl text-xs font-bold flex items-center justify-between"
    >
      <span>✨ {{ statusBanner }}</span>
      <button type="button" @click="statusBanner = ''" class="text-emerald-600 font-black">&times;</button>
    </div>

    <!-- 1. Назва датасету та Задача (Task з БД) -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div class="flex flex-col gap-2">
        <label for="atk-name" class="text-xs font-black text-slate-400 uppercase tracking-widest">
          1. Назва датасету
        </label>
        <input
          id="atk-name"
          v-model="name"
          type="text"
          maxlength="120"
          required
          placeholder="Наприклад: heroes_ukr_eval_v1"
          class="w-full px-4 py-3 rounded-xl bg-slate-50 border border-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500 font-medium text-slate-700 transition-all"
        />
      </div>

      <div class="flex flex-col gap-2">
        <div class="flex flex-wrap justify-between items-center gap-1">
          <label for="atk-task" class="text-xs font-black text-slate-400 uppercase tracking-widest">
            2. Задача (Task з БД)
          </label>
          <div class="flex flex-wrap gap-1.5 text-xs">
            <button
              v-for="tCfg in dbTaskConfigs.length
                ? dbTaskConfigs
                : [{ task_name: 'heroes' }, { task_name: 'disinfo' }]"
              :key="tCfg.task_name"
              type="button"
              @click="selectTaskPreset(tCfg.task_name)"
              :class="[
                'px-2.5 py-0.5 rounded font-semibold transition-all',
                taskName === tCfg.task_name
                  ? 'bg-blue-600 text-white'
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200',
              ]"
            >
              {{ tCfg.task_name }}
            </button>
            <button
              type="button"
              @click="goToTemplatesPage('tasks')"
              class="px-2.5 py-0.5 rounded bg-slate-800 text-white hover:bg-slate-700 font-semibold"
              title="Налаштувати SYSTEM/USER промпти задачі в БД"
            >
              ⚙️ Налаштувати задачу
            </button>
          </div>
        </div>
        <input
          id="atk-task"
          v-model="taskName"
          @change="applyTaskFromDb(taskName)"
          type="text"
          maxlength="80"
          required
          placeholder="heroes, disinfo або власна назва..."
          class="w-full px-4 py-3 rounded-xl bg-slate-50 border border-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500 font-medium text-slate-700 transition-all"
        />
      </div>
    </div>

    <!-- 2. Мови генерації -->
    <div class="p-4 bg-slate-50/70 rounded-2xl border border-slate-200/80 flex flex-wrap items-center justify-between gap-3">
      <div class="flex flex-wrap items-center gap-2">
        <span class="text-xs font-black text-slate-400 uppercase tracking-widest mr-2">
          3. Мови генерації:
        </span>
        <span
          v-for="lang in languages"
          :key="lang"
          class="px-3 py-1 rounded-xl text-xs font-bold bg-blue-50 border border-blue-200 text-blue-700"
        >
          {{ lang }}
        </span>
      </div>

      <label class="flex items-center gap-2 text-xs font-bold text-slate-700 cursor-pointer">
        <input
          v-model="useInferencePrompts"
          type="checkbox"
          class="w-4 h-4 text-blue-600 rounded border-slate-300"
        />
        <span>Включити SYSTEM/USER шаблони (INFERENCE_PROMPTS) із БД</span>
      </label>
    </div>

    <!-- 3. Компактний вибір Сценаріїв (baseline, safety_attack, stereotyping...) та Технік ({t}, {b64_t}) -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <!-- Сценарії з таблиці attack_templates -->
      <div class="p-5 bg-slate-50 rounded-2xl border border-slate-200 space-y-3">
        <div class="flex items-center justify-between">
          <div>
            <h3 class="text-xs font-black text-slate-700 uppercase tracking-wider">
              4. Сценарії атаки ({{ activeIntentKeys.length }} / {{ Object.keys(intentsConfig).length }})
            </h3>
            <p class="text-[11px] text-slate-500">
              Таблиця БД: <code>attack_templates</code> ({{ taskName }})
            </p>
          </div>
          <button
            type="button"
            @click="goToTemplatesPage('scenarios')"
            class="px-3 py-1.5 bg-white hover:bg-slate-100 text-blue-600 border border-slate-200 rounded-xl text-xs font-bold transition-all"
          >
            ✏️ Редагувати шаблони сценаріїв
          </button>
        </div>

        <div class="flex flex-wrap gap-2 pt-1">
          <label
            v-for="(spec, key) in intentsConfig"
            :key="key"
            :class="[
              'flex items-center gap-2 px-3 py-2 rounded-xl text-xs font-bold border cursor-pointer transition-all select-none',
              spec.enabled
                ? 'bg-blue-50 border-blue-200 text-blue-700'
                : 'bg-white border-slate-200 text-slate-500 hover:bg-slate-100',
            ]"
          >
            <input
              v-model="spec.enabled"
              type="checkbox"
              class="w-3.5 h-3.5 text-blue-600 rounded border-slate-300"
            />
            <span>{{ key }}</span>
            <span class="text-[10px] font-mono opacity-75">({{ spec.metric_category }})</span>
          </label>
        </div>
      </div>

      <!-- Техніки обгортання з таблиці attack_techniques -->
      <div class="p-5 bg-slate-50 rounded-2xl border border-slate-200 space-y-3">
        <div class="flex items-center justify-between">
          <div>
            <h3 class="text-xs font-black text-slate-700 uppercase tracking-wider">
              5. Техніки обгортання ({{ activeTechniqueKeys.length }} / {{ Object.keys(techniquesConfig).length }})
            </h3>
            <p class="text-[11px] text-slate-500">
              Таблиця БД: <code>attack_techniques</code> (<code>{t}</code>, <code>{b64_t}</code>)
            </p>
          </div>
          <button
            type="button"
            @click="goToTemplatesPage('techniques')"
            class="px-3 py-1.5 bg-white hover:bg-slate-100 text-red-600 border border-slate-200 rounded-xl text-xs font-bold transition-all"
          >
            🔧 Редагувати шаблони технік
          </button>
        </div>

        <div class="flex flex-wrap gap-2 pt-1">
          <label
            v-for="(spec, key) in techniquesConfig"
            :key="key"
            :class="[
              'flex items-center gap-2 px-3 py-2 rounded-xl text-xs font-bold border cursor-pointer transition-all select-none',
              spec.enabled
                ? 'bg-red-50 border-red-200 text-red-700'
                : 'bg-white border-slate-200 text-slate-500 hover:bg-slate-100',
            ]"
          >
            <input
              v-model="spec.enabled"
              type="checkbox"
              class="w-3.5 h-3.5 text-red-600 rounded border-slate-300"
            />
            <span>{{ key }}</span>
          </label>
        </div>
      </div>
    </div>

    <!-- 4. Цільові сутності (Entities), витягнення імен із датасету/тексту та Batch Slicing -->
    <div class="space-y-4 p-5 bg-slate-50 rounded-2xl border border-slate-200">
      <div class="flex flex-wrap justify-between items-center gap-2">
        <label for="atk-entities" class="text-xs font-black text-slate-500 uppercase tracking-widest">
          6. Цільові сутності для підстановки в <code class="text-blue-600">{entity}</code>
          <span v-if="requiresEntities" class="text-red-500 font-bold ml-1">(обов'язково)</span>
        </label>
        <span class="text-xs font-medium text-blue-600 bg-blue-50 px-2.5 py-0.5 rounded-md border border-blue-100">
          Усього сутностей: {{ allEntities.length }} (активно для генерації: {{ activeEntitiesCount }})
        </span>
      </div>

      <textarea
        id="atk-entities"
        v-model="entitiesText"
        rows="4"
        placeholder="По одній персоні/сутності у рядку або через кому..."
        class="w-full px-4 py-3 rounded-xl bg-white border border-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500 font-medium text-slate-700 resize-y transition-all"
      ></textarea>

      <!-- Автоматичне витягнення імен із тексту АБО з існуючого датасету -->
      <div class="pt-3 border-t border-slate-200 space-y-3">
        <div class="flex flex-wrap items-center justify-between gap-2">
          <span class="text-xs font-bold text-slate-600">
            Автоматичне витягнення імен героїв/персон:
          </span>
          <div class="flex bg-slate-200/70 p-0.5 rounded-lg gap-1 text-xs">
            <button
              type="button"
              @click="extractMode = 'text'"
              :class="[
                'px-2.5 py-1 rounded-md font-bold transition-all',
                extractMode === 'text' ? 'bg-white text-slate-900 shadow-xs' : 'text-slate-600',
              ]"
            >
              З тексту
            </button>
            <button
              type="button"
              @click="extractMode = 'dataset'"
              :class="[
                'px-2.5 py-1 rounded-md font-bold transition-all',
                extractMode === 'dataset' ? 'bg-white text-slate-900 shadow-xs' : 'text-slate-600',
              ]"
            >
              З існуючого датасету в БД
            </button>
          </div>
        </div>

        <div v-if="extractMode === 'text'" class="grid grid-cols-1 md:grid-cols-4 gap-3">
          <div class="md:col-span-3">
            <input
              v-model="rawExtractInput"
              type="text"
              placeholder="Вставте текст/біографію (напр. «Напиши біографію Івана Франка або Василя Стуса»)..."
              class="w-full px-3 py-2 rounded-xl bg-white border border-slate-200 text-xs text-slate-700"
            />
          </div>
          <button
            type="button"
            @click="handleExtractEntities"
            :disabled="extractingEntities || !rawExtractInput.trim()"
            class="px-4 py-2 bg-slate-800 text-white text-xs font-bold rounded-xl hover:bg-slate-700 disabled:bg-slate-300 transition-all"
          >
            {{ extractingEntities ? 'Витягуємо…' : '🔍 Витягнути імена з тексту' }}
          </button>
        </div>

        <div v-else class="grid grid-cols-1 md:grid-cols-4 gap-3">
          <div class="md:col-span-3">
            <select
              v-model="sourceDatasetId"
              class="w-full px-3 py-2 rounded-xl bg-white border border-slate-200 text-xs text-slate-700"
            >
              <option value="">Оберіть датасет для витягнення імен...</option>
              <option v-for="ds in availableDatasets" :key="ds.id" :value="ds.id">
                #{{ ds.id }} · {{ ds.name }} ({{ ds.rows ?? '?' }} рядків)
              </option>
            </select>
          </div>
          <button
            type="button"
            @click="handleExtractEntities"
            :disabled="extractingEntities || !sourceDatasetId"
            class="px-4 py-2 bg-slate-800 text-white text-xs font-bold rounded-xl hover:bg-slate-700 disabled:bg-slate-300 transition-all"
          >
            {{ extractingEntities ? 'Витягуємо…' : '🔍 Витягнути з датасету' }}
          </button>
        </div>
      </div>

      <!-- Пакетна вибірка сутностей (Batch Slicing) -->
      <div class="pt-2 border-t border-slate-200 space-y-3">
        <label class="flex items-center gap-2 text-xs font-bold text-slate-700 cursor-pointer">
          <input v-model="useEntityBatching" type="checkbox" class="rounded text-blue-600" />
          <span>Пакетна нарізка сутностей (Batch Slicing: batch_size / batch_index)</span>
        </label>

        <div v-if="useEntityBatching" class="grid grid-cols-1 md:grid-cols-3 gap-3">
          <div>
            <label class="text-[11px] font-bold text-slate-500 uppercase">Розмір батчу (batch_size)</label>
            <input
              v-model.number="batchSize"
              type="number"
              min="1"
              max="5000"
              class="mt-1 w-full px-3 py-1.5 rounded-lg bg-white border border-slate-200 text-xs"
            />
          </div>
          <div>
            <label class="text-[11px] font-bold text-slate-500 uppercase">Індекс батчу (batch_index, 0..N)</label>
            <input
              v-model.number="batchIndex"
              type="number"
              min="0"
              class="mt-1 w-full px-3 py-1.5 rounded-lg bg-white border border-slate-200 text-xs"
            />
          </div>
          <div class="flex items-end pb-1">
            <label class="flex items-center gap-2 text-xs text-slate-700 cursor-pointer">
              <input v-model="shuffleEntities" type="checkbox" class="rounded text-blue-600" />
              <span>Перемішати сутності (Shuffle)</span>
            </label>
          </div>
        </div>
      </div>
    </div>

    <!-- 5. Прогноз кількості згенерованих рядків -->
    <div class="p-4 bg-slate-900 text-slate-200 rounded-xl text-sm flex justify-between items-center">
      <span>
        Прогнозована кількість рядків у <code class="text-blue-300">.jsonl</code> датасеті:
      </span>
      <strong class="text-emerald-400 font-mono text-base font-bold">{{ totalRowsForecast }} рядків</strong>
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
      <span>{{ loading ? 'Генеруємо динамічний датасет…' : 'Створити датасет' }}</span>
    </button>

    <div
      v-if="error"
      class="p-4 bg-red-50 border border-red-200 text-red-700 rounded-xl font-medium text-sm flex items-center gap-2 whitespace-pre-line"
      role="alert"
    >
      <span>⚠️ {{ error }}</span>
    </div>

    <div
      v-if="created"
      class="p-4 bg-emerald-50 border border-emerald-200 text-emerald-800 rounded-xl font-medium text-sm flex items-center gap-2"
      role="status"
    >
      <span>
        ✅ Датасет успішно створено: <strong>ID {{ created.dataset_id }}</strong> (рядків: {{ created.rows }})
      </span>
    </div>
  </form>
</template>