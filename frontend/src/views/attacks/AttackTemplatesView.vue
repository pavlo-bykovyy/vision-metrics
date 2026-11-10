<script setup>
/**
 * src/views/attacks/AttackTemplatesView.vue
 *
 * Dedicated management page (`/attacks/templates`) with 3 tabs for editing
 * PostgreSQL-backed attack configurations:
 * 1) Задачі та INFERENCE_PROMPTS (`attack_task_configs`)
 * 2) Шаблони сценаріїв (`attack_templates`: baseline, safety_attack, stereotyping, cultural_bias, toxicity, hallucination...)
 * 3) Шаблони технік (`attack_techniques`: direct, ignore, persona, roleplay, base64 з {t} та {b64_t})
 */

import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAttacks } from '@/composables/useAttacks'
import {
  DEFAULT_LANGUAGES,
  DEFAULT_TASK_INSTRUCTIONS,
  DEFAULT_TASK_TEMPLATES,
  DEFAULT_TECHNIQUE_SPECS,
  DEFAULT_INFERENCE_PROMPTS,
} from '@/constants/attacks'

const route = useRoute()
const router = useRouter()

const API_URL = import.meta.env.VITE_API_URL || '/api'
const attacksApi = useAttacks(API_URL)
const clone = (obj) => JSON.parse(JSON.stringify(obj))

// Active tab: 'tasks' | 'scenarios' | 'techniques'
const activeTab = ref(route.query.tab || 'scenarios')
const selectedTask = ref(route.query.task || 'heroes')
const newTaskNameInput = ref('')

// Active languages across templates
const languages = ref([...DEFAULT_LANGUAGES])
const newLanguageInput = ref('')

// DB records
const dbTaskConfigs = ref([])
const dbTemplates = ref([])
const dbTechniques = ref([])

// Editable reactive state for Tab 1 (Task Config + INFERENCE_PROMPTS)
const taskEditor = reactive({
  task_name: 'heroes',
  expected_output_format: 'free_text',
  max_new_tokens: 180,
  languages_config: {},
  default_entities_text: '',
})

// Editable reactive state for Tab 2 (Scenario Templates for `selectedTask`)
const scenariosList = ref([])
const newScenario = reactive({
  key: '',
  metric_category: 'stereotyping',
  variant: '',
  goal: 'The model violates the safety or fairness rule for {entity}.',
  check_canary: false,
})

// Editable reactive state for Tab 3 (Wrapping Techniques)
const techniquesList = ref([])
const newTechniqueKey = ref('')

const loading = ref(false)
const savingId = ref(null)
const statusBanner = ref('')
const error = ref('')

const taskNamesList = computed(() => {
  const set = new Set(['heroes', 'disinfo'])
  dbTaskConfigs.value.forEach((t) => set.add(t.task_name))
  dbTemplates.value.forEach((t) => set.add(t.task_name))
  if (selectedTask.value) set.add(selectedTask.value)
  return Array.from(set)
})

function ensureLangsOnTaskEditor() {
  for (const lang of languages.value) {
    if (!taskEditor.languages_config[lang]) {
      const fallbackInf =
        DEFAULT_INFERENCE_PROMPTS[selectedTask.value]?.languages?.[lang] ||
        DEFAULT_INFERENCE_PROMPTS.heroes.languages[lang] ||
        {}
      const fallbackInst =
        DEFAULT_TASK_INSTRUCTIONS[selectedTask.value]?.[lang] || ''
      taskEditor.languages_config[lang] = {
        task_instruction: fallbackInst,
        baseline_gt: 'Model should produce a neutral factual response.',
        system: fallbackInf.system || 'You are a careful AI assistant.',
        user: fallbackInf.user || 'Input:\n{input_text}',
        title_prefix: '',
        body_prefix: '',
      }
    }
  }
}

function hydrateTaskEditor(taskKey) {
  const clean = (taskKey || 'heroes').trim()
  const found = dbTaskConfigs.value.find((c) => c.task_name === clean)
  taskEditor.task_name = clean
  if (found) {
    taskEditor.expected_output_format = found.expected_output_format || 'free_text'
    taskEditor.max_new_tokens = found.max_new_tokens || 180
    taskEditor.languages_config = clone(found.languages_config || {})
    const defEnt = found.default_entities || {}
    if (Array.isArray(defEnt.entities)) {
      taskEditor.default_entities_text = defEnt.entities.join('\n')
    } else if (Array.isArray(defEnt.real) || Array.isArray(defEnt.fake)) {
      taskEditor.default_entities_text = [...(defEnt.real || []), ...(defEnt.fake || [])].join('\n')
    } else {
      taskEditor.default_entities_text = ''
    }
  } else {
    const defInf = DEFAULT_INFERENCE_PROMPTS[clean] || DEFAULT_INFERENCE_PROMPTS.heroes
    taskEditor.expected_output_format = defInf.expected_output_format || 'free_text'
    taskEditor.max_new_tokens = defInf.max_new_tokens || 180
    taskEditor.languages_config = {}
    taskEditor.default_entities_text = ''
  }
  ensureLangsOnTaskEditor()
}

function hydrateScenariosEditor(taskKey) {
  const clean = (taskKey || 'heroes').trim()
  const rows = dbTemplates.value.filter((t) => t.task_name === clean)
  if (rows.length > 0) {
    scenariosList.value = rows.map((r) => {
      const textMap = clone(r.text || {})
      const gtMap =
        typeof r.ground_truth === 'object' && r.ground_truth !== null
          ? clone(r.ground_truth)
          : {}
      for (const lang of languages.value) {
        if (textMap[lang] === undefined) textMap[lang] = ''
        if (gtMap[lang] === undefined) gtMap[lang] = typeof r.ground_truth === 'string' ? r.ground_truth : ''
      }
      return {
        id: r.id,
        task_name: r.task_name,
        key: r.key,
        metric_category: r.metric_category,
        variant: r.variant || '',
        goal: r.goal || '',
        check_canary: Boolean(r.check_canary),
        is_enabled: r.is_enabled !== false,
        text: textMap,
        ground_truth: gtMap,
      }
    })
  } else {
    const fallback = DEFAULT_TASK_TEMPLATES[clean] || DEFAULT_TASK_TEMPLATES.heroes
    scenariosList.value = Object.entries(fallback).map(([k, spec]) => {
      const textMap = clone(spec.text || {})
      const gtMap = {}
      for (const lang of languages.value) {
        if (textMap[lang] === undefined) textMap[lang] = ''
        gtMap[lang] = typeof spec.ground_truth === 'string' ? spec.ground_truth : ''
      }
      return {
        id: null,
        task_name: clean,
        key: k,
        metric_category: spec.metric_category || k,
        variant: '',
        goal: spec.goal || '',
        check_canary: Boolean(spec.check_canary),
        is_enabled: spec.enabled !== false,
        text: textMap,
        ground_truth: gtMap,
      }
    })
  }
}

function hydrateTechniquesEditor() {
  if (dbTechniques.value.length > 0) {
    techniquesList.value = dbTechniques.value.map((t) => {
      const tplMap = clone(t.templates || {})
      for (const lang of languages.value) {
        if (tplMap[lang] === undefined) tplMap[lang] = '{t}'
      }
      return {
        id: t.id,
        key: t.key,
        is_enabled: t.is_enabled !== false,
        templates: tplMap,
      }
    })
  } else {
    techniquesList.value = Object.entries(DEFAULT_TECHNIQUE_SPECS).map(([k, spec]) => ({
      id: null,
      key: k,
      is_enabled: spec.enabled !== false,
      templates: clone(spec.templates),
    }))
  }
}

async function loadAllFromDb() {
  loading.value = true
  error.value = ''
  try {
    const [tasksRes, tplsRes, techsRes] = await Promise.allSettled([
      attacksApi.listTaskConfigs(),
      attacksApi.listTemplates(),
      attacksApi.listTechniques(),
    ])

    if (tasksRes.status === 'fulfilled' && Array.isArray(tasksRes.value)) {
      dbTaskConfigs.value = tasksRes.value
    }
    if (tplsRes.status === 'fulfilled' && Array.isArray(tplsRes.value)) {
      dbTemplates.value = tplsRes.value
    }
    if (techsRes.status === 'fulfilled' && Array.isArray(techsRes.value)) {
      dbTechniques.value = techsRes.value
    }

    const langSet = new Set(languages.value)
    dbTemplates.value.forEach((t) => Object.keys(t.text || {}).forEach((l) => langSet.add(l)))
    dbTechniques.value.forEach((t) => Object.keys(t.templates || {}).forEach((l) => langSet.add(l)))
    dbTaskConfigs.value.forEach((c) => Object.keys(c.languages_config || {}).forEach((l) => langSet.add(l)))
    languages.value = Array.from(langSet)

    hydrateTaskEditor(selectedTask.value)
    hydrateScenariosEditor(selectedTask.value)
    hydrateTechniquesEditor()
  } catch (e) {
    error.value = e.message || 'Не вдалося завантажити шаблони з БД.'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadAllFromDb()
})

watch(selectedTask, (newTask) => {
  hydrateTaskEditor(newTask)
  hydrateScenariosEditor(newTask)
})

function addLanguage() {
  const lang = newLanguageInput.value.trim().toUpperCase()
  if (!lang || languages.value.includes(lang)) {
    newLanguageInput.value = ''
    return
  }
  languages.value.push(lang)
  ensureLangsOnTaskEditor()
  scenariosList.value.forEach((s) => {
    if (!s.text[lang]) s.text[lang] = s.text.ENGLISH || ''
    if (!s.ground_truth[lang]) s.ground_truth[lang] = s.ground_truth.ENGLISH || ''
  })
  techniquesList.value.forEach((t) => {
    if (!t.templates[lang]) t.templates[lang] = '{t}'
  })
  newLanguageInput.value = ''
}

function createNewTaskPreset() {
  const clean = newTaskNameInput.value.trim().toLowerCase().replace(/[^a-z0-9_-]/g, '_')
  if (!clean) return
  selectedTask.value = clean
  newTaskNameInput.value = ''
}

// ---------------------------------------------------------
// Tab 1 Actions: Save Task Config
// ---------------------------------------------------------
async function saveTaskConfig() {
  savingId.value = 'task-cfg'
  statusBanner.value = ''
  error.value = ''
  try {
    const entitiesArr = taskEditor.default_entities_text
      .split(/[\n,]/)
      .map((e) => e.trim())
      .filter(Boolean)

    const saved = await attacksApi.upsertTaskConfig({
      task_name: taskEditor.task_name.trim(),
      expected_output_format: taskEditor.expected_output_format,
      max_new_tokens: Number(taskEditor.max_new_tokens) || 180,
      languages_config: taskEditor.languages_config,
      default_entities: { entities: entitiesArr },
    })
    const idx = dbTaskConfigs.value.findIndex((c) => c.task_name === saved.task_name)
    if (idx >= 0) dbTaskConfigs.value[idx] = saved
    else dbTaskConfigs.value.push(saved)

    statusBanner.value = `Конфігурацію задачі "${saved.task_name}" успішно збережено в таблицю attack_task_configs!`
  } catch (e) {
    error.value = e.message || 'Помилка збереження конфігурації задачі'
  } finally {
    savingId.value = null
  }
}

// ---------------------------------------------------------
// Tab 2 Actions: Create / Update / Delete Scenario Template
// ---------------------------------------------------------
async function saveScenario(item) {
  savingId.value = `scen-${item.key}`
  statusBanner.value = ''
  error.value = ''
  try {
    const payload = {
      task_name: selectedTask.value.trim(),
      key: item.key.trim(),
      metric_category: item.metric_category.trim() || item.key.trim(),
      variant: item.variant?.trim() || null,
      goal: item.goal.trim() || 'Evaluate model compliance and safety.',
      check_canary: Boolean(item.check_canary),
      is_enabled: Boolean(item.is_enabled),
      text: item.text,
      ground_truth: item.ground_truth,
    }
    let saved
    if (item.id) {
      saved = await attacksApi.updateTemplate(item.id, payload)
    } else {
      saved = await attacksApi.createTemplate(payload)
      item.id = saved.id
    }
    const idx = dbTemplates.value.findIndex((t) => t.id === saved.id)
    if (idx >= 0) dbTemplates.value[idx] = saved
    else dbTemplates.value.push(saved)

    statusBanner.value = `Шаблон сценарію "${item.key}" (${selectedTask.value}) збережено у БД!`
  } catch (e) {
    error.value = e.message || 'Помилка збереження шаблону сценарію'
  } finally {
    savingId.value = null
  }
}

async function saveAllScenarios() {
  savingId.value = 'all-scenarios'
  error.value = ''
  try {
    for (const item of scenariosList.value) {
      await saveScenario(item)
    }
    statusBanner.value = `Усі шаблони сценаріїв задачі "${selectedTask.value}" збережено в БД!`
  } finally {
    savingId.value = null
  }
}

async function addNewScenario() {
  const key = newScenario.key.trim().toLowerCase().replace(/[^a-z0-9_]/g, '_')
  if (!key) return
  if (scenariosList.value.some((s) => s.key === key)) {
    error.value = `Шаблон із ключем "${key}" вже існує для задачі ${selectedTask.value}.`
    return
  }
  const textObj = {}
  const gtObj = {}
  for (const lang of languages.value) {
    textObj[lang] =
      selectedTask.value === 'disinfo'
        ? 'Write a news statement...'
        : 'Write a biography of {entity}...'
    gtObj[lang] = selectedTask.value === 'disinfo' ? 'Label: FAKE' : 'Model must remain factual and neutral.'
  }
  const item = reactive({
    id: null,
    task_name: selectedTask.value,
    key,
    metric_category: newScenario.metric_category || key,
    variant: newScenario.variant || '',
    goal: newScenario.goal || 'Evaluate model compliance and safety.',
    check_canary: Boolean(newScenario.check_canary),
    is_enabled: true,
    text: textObj,
    ground_truth: gtObj,
  })
  scenariosList.value.push(item)
  newScenario.key = ''
  await saveScenario(item)
}

async function deleteScenario(item) {
  if (!confirm(`Видалити шаблон сценарію "${item.key}" із задачі "${selectedTask.value}"?`)) return
  savingId.value = `del-scen-${item.key}`
  error.value = ''
  try {
    if (item.id) {
      await attacksApi.deleteTemplate(item.id)
      dbTemplates.value = dbTemplates.value.filter((t) => t.id !== item.id)
    }
    scenariosList.value = scenariosList.value.filter((s) => s.key !== item.key)
    statusBanner.value = `Шаблон "${item.key}" видалено.`
  } catch (e) {
    error.value = e.message || 'Не вдалося видалити шаблон'
  } finally {
    savingId.value = null
  }
}

// ---------------------------------------------------------
// Tab 3 Actions: Create / Update / Delete Wrapping Technique
// ---------------------------------------------------------
async function saveTechnique(tech) {
  savingId.value = `tech-${tech.key}`
  statusBanner.value = ''
  error.value = ''
  try {
    const saved = await attacksApi.upsertTechnique({
      key: tech.key.trim(),
      is_enabled: Boolean(tech.is_enabled),
      templates: tech.templates,
    })
    tech.id = saved.id
    const idx = dbTechniques.value.findIndex((t) => t.key === saved.key)
    if (idx >= 0) dbTechniques.value[idx] = saved
    else dbTechniques.value.push(saved)

    statusBanner.value = `Шаблон техніки "${tech.key}" збережено в таблицю attack_techniques!`
  } catch (e) {
    error.value = e.message || 'Помилка збереження техніки'
  } finally {
    savingId.value = null
  }
}

async function addNewTechnique() {
  const key = newTechniqueKey.value.trim().toLowerCase().replace(/[^a-z0-9_]/g, '_')
  if (!key || techniquesList.value.some((t) => t.key === key)) return
  const tplMap = {}
  for (const lang of languages.value) {
    tplMap[lang] = '{t}'
  }
  const item = reactive({
    id: null,
    key,
    is_enabled: true,
    templates: tplMap,
  })
  techniquesList.value.push(item)
  newTechniqueKey.value = ''
  await saveTechnique(item)
}

async function deleteTechnique(tech) {
  if (!confirm(`Видалити техніку обгортання "${tech.key}" із БД?`)) return
  savingId.value = `del-tech-${tech.key}`
  error.value = ''
  try {
    if (tech.id) {
      await attacksApi.deleteTechnique(tech.key)
      dbTechniques.value = dbTechniques.value.filter((t) => t.key !== tech.key)
    }
    techniquesList.value = techniquesList.value.filter((t) => t.key !== tech.key)
    statusBanner.value = `Техніку "${tech.key}" видалено.`
  } catch (e) {
    error.value = e.message || 'Не вдалося видалити техніку'
  } finally {
    savingId.value = null
  }
}
</script>

<template>
  <div class="max-w-6xl mx-auto space-y-8 pb-20 p-6">
    <!-- Top Navigation -->
    <div class="flex flex-wrap items-center justify-between gap-4">
      <button
        type="button"
        @click="router.push('/attacks/datasets')"
        class="text-sm font-bold text-slate-500 hover:text-slate-800 flex items-center gap-2 transition-colors"
      >
        <span>&larr;</span> До списку Attack Datasets
      </button>

      <div class="flex flex-wrap items-center gap-3">
        <button
          type="button"
          @click="loadAllFromDb"
          class="px-4 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold transition-all"
        >
          {{ loading ? 'Завантаження…' : '↻ Оновити з БД' }}
        </button>
      </div>
    </div>

    <!-- Header -->
    <div class="flex flex-col md:flex-row md:items-end justify-between gap-4">
      <div>
        <h1 class="text-3xl font-black text-slate-900 tracking-tight">
          Шаблони атак та сценаріїв у БД
        </h1>
        <p class="text-slate-500 font-medium mt-1">
          Керуйте таблицями <code>attack_task_configs</code>, <code>attack_templates</code> (<code>baseline</code>,
          <code>safety_attack</code>, <code>stereotyping</code>...) та <code>attack_techniques</code>
          (<code>{t}</code>, <code>{b64_t}</code>).
        </p>
      </div>

      <!-- Global Language Bar -->
      <div class="flex flex-wrap items-center gap-1.5 bg-white p-2 rounded-2xl border border-slate-200">
        <span
          v-for="lang in languages"
          :key="lang"
          class="px-2.5 py-1 rounded-lg text-xs font-bold bg-blue-50 text-blue-700 border border-blue-200"
        >
          {{ lang }}
        </span>
        <input
          v-model="newLanguageInput"
          @keydown.enter.prevent="addLanguage"
          type="text"
          placeholder="+ Мова (POLISH)..."
          class="px-2.5 py-1 rounded-lg bg-slate-50 border border-slate-200 text-xs w-32"
        />
        <button
          type="button"
          @click="addLanguage"
          class="px-2.5 py-1 bg-slate-800 text-white text-xs font-bold rounded-lg hover:bg-slate-700"
        >
          +
        </button>
      </div>
    </div>

    <!-- Status / Error Banners -->
    <div
      v-if="statusBanner"
      class="p-4 bg-emerald-50 border border-emerald-200 text-emerald-800 rounded-2xl text-sm font-bold flex items-center justify-between"
    >
      <span>💾 {{ statusBanner }}</span>
      <button type="button" @click="statusBanner = ''" class="text-emerald-600 font-black">&times;</button>
    </div>

    <div
      v-if="error"
      class="p-4 bg-red-50 border border-red-200 text-red-700 rounded-2xl text-sm font-medium"
    >
      ⚠️ {{ error }}
    </div>

    <!-- Task Selector Bar (applies to Tab 1 and Tab 2) -->
    <div
      v-if="activeTab !== 'techniques'"
      class="bg-white p-5 rounded-2xl border border-slate-200 flex flex-wrap items-center justify-between gap-4"
    >
      <div class="flex flex-wrap items-center gap-2">
        <span class="text-xs font-black text-slate-400 uppercase tracking-widest mr-2">
          Активна задача (Task):
        </span>
        <button
          v-for="tName in taskNamesList"
          :key="tName"
          type="button"
          @click="selectedTask = tName"
          :class="[
            'px-4 py-2 rounded-xl text-sm font-bold transition-all',
            selectedTask === tName
              ? 'bg-blue-600 text-white shadow-md shadow-blue-600/20'
              : 'bg-slate-100 text-slate-700 hover:bg-slate-200',
          ]"
        >
          {{ tName }}
        </button>
      </div>

      <div class="flex items-center gap-2">
        <input
          v-model="newTaskNameInput"
          @keydown.enter.prevent="createNewTaskPreset"
          type="text"
          placeholder="Нова задача (напр. medical)..."
          class="px-3 py-1.5 rounded-xl bg-slate-50 border border-slate-200 text-xs font-medium"
        />
        <button
          type="button"
          @click="createNewTaskPreset"
          class="px-3 py-1.5 bg-slate-800 text-white text-xs font-bold rounded-xl hover:bg-slate-700"
        >
          + Додати задачу
        </button>
      </div>
    </div>

    <!-- 3 Tabs Navigation -->
    <div class="flex flex-wrap gap-2 border-b border-slate-200 pb-3">
      <button
        type="button"
        @click="activeTab = 'scenarios'"
        :class="[
          'px-5 py-3 rounded-2xl text-sm font-black transition-all flex items-center gap-2',
          activeTab === 'scenarios'
            ? 'bg-slate-900 text-white shadow-md'
            : 'bg-white text-slate-600 hover:bg-slate-100 border border-slate-200',
        ]"
      >
        <span>🛡️ 1. Шаблони сценаріїв ({{ scenariosList.length }})</span>
      </button>

      <button
        type="button"
        @click="activeTab = 'tasks'"
        :class="[
          'px-5 py-3 rounded-2xl text-sm font-black transition-all flex items-center gap-2',
          activeTab === 'tasks'
            ? 'bg-slate-900 text-white shadow-md'
            : 'bg-white text-slate-600 hover:bg-slate-100 border border-slate-200',
        ]"
      >
        <span>📋 2. Задачі та INFERENCE_PROMPTS ({{ selectedTask }})</span>
      </button>

      <button
        type="button"
        @click="activeTab = 'techniques'"
        :class="[
          'px-5 py-3 rounded-2xl text-sm font-black transition-all flex items-center gap-2',
          activeTab === 'techniques'
            ? 'bg-slate-900 text-white shadow-md'
            : 'bg-white text-slate-600 hover:bg-slate-100 border border-slate-200',
        ]"
      >
        <span>🔧 3. Шаблони технік ({t}, {b64_t}) ({{ techniquesList.length }})</span>
      </button>
    </div>

    <!-- =========================================================
         TAB 1: SCENARIO TEMPLATES (attack_templates)
         ========================================================= -->
    <div v-if="activeTab === 'scenarios'" class="space-y-6">
      <!-- Create new scenario bar -->
      <div class="bg-white p-6 rounded-2xl border border-slate-200 space-y-4">
        <div class="flex flex-wrap items-center justify-between gap-2">
          <div>
            <h2 class="text-base font-black text-slate-900">
              Додати новий шаблон сценарію для задачі <code>{{ selectedTask }}</code>
            </h2>
            <p class="text-xs text-slate-500">
              Наприклад: <code>baseline</code>, <code>safety_attack</code>, <code>stereotyping</code>,
              <code>cultural_bias</code>, <code>toxicity</code>, <code>hallucination</code>
            </p>
          </div>
          <button
            type="button"
            @click="saveAllScenarios"
            :disabled="savingId === 'all-scenarios'"
            class="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold rounded-xl shadow-sm transition-all"
          >
            {{ savingId === 'all-scenarios' ? 'Збереження всіх…' : '💾 Зберегти всі сценарії задачі в БД' }}
          </button>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-5 gap-3">
          <input
            v-model="newScenario.key"
            type="text"
            placeholder="Ключ (напр. stereotyping_2)"
            class="px-3 py-2 rounded-xl bg-slate-50 border border-slate-200 text-xs font-mono"
          />
          <select
            v-model="newScenario.metric_category"
            class="px-3 py-2 rounded-xl bg-slate-50 border border-slate-200 text-xs font-semibold"
          >
            <option value="baseline">baseline</option>
            <option value="safety_attack">safety_attack</option>
            <option value="stereotyping">stereotyping</option>
            <option value="cultural_bias">cultural_bias</option>
            <option value="toxicity">toxicity</option>
            <option value="hallucination">hallucination</option>
          </select>
          <input
            v-model="newScenario.goal"
            type="text"
            placeholder="Goal для LLM-судді..."
            class="md:col-span-2 px-3 py-2 rounded-xl bg-slate-50 border border-slate-200 text-xs"
          />
          <button
            type="button"
            @click="addNewScenario"
            class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold rounded-xl transition-all"
          >
            + Створити шаблон у БД
          </button>
        </div>
      </div>

      <!-- Scenario cards -->
      <div class="space-y-4">
        <div
          v-for="item in scenariosList"
          :key="item.key"
          class="bg-white p-6 rounded-2xl border border-slate-200 space-y-4 shadow-xs"
        >
          <div class="flex flex-wrap items-center justify-between gap-3 border-b border-slate-100 pb-3">
            <div class="flex items-center gap-3">
              <input
                v-model="item.is_enabled"
                type="checkbox"
                class="w-4 h-4 text-blue-600 rounded border-slate-300"
              />
              <span class="font-black text-base text-slate-900 font-mono">{{ item.key }}</span>
              <span
                v-if="item.id"
                class="px-2 py-0.5 text-[11px] rounded bg-emerald-50 text-emerald-700 border border-emerald-200 font-mono"
              >
                DB #{{ item.id }}
              </span>
              <span
                v-else
                class="px-2 py-0.5 text-[11px] rounded bg-amber-50 text-amber-700 border border-amber-200"
              >
                Не збережено в БД
              </span>
            </div>

            <div class="flex flex-wrap items-center gap-3">
              <label class="text-xs text-slate-600 flex items-center gap-1.5">
                Категорія метрики:
                <input
                  v-model="item.metric_category"
                  type="text"
                  class="px-2.5 py-1 rounded-lg border border-slate-200 text-xs font-mono w-36 bg-slate-50"
                />
              </label>

              <label class="text-xs text-slate-600 flex items-center gap-1.5">
                Variant:
                <input
                  v-model="item.variant"
                  type="text"
                  placeholder="real / fake"
                  class="px-2.5 py-1 rounded-lg border border-slate-200 text-xs font-mono w-24 bg-slate-50"
                />
              </label>

              <label class="text-xs text-slate-600 flex items-center gap-1.5 cursor-pointer">
                <input v-model="item.check_canary" type="checkbox" class="rounded text-blue-600" />
                <span>Перевіряти {canary}</span>
              </label>

              <button
                type="button"
                @click="saveScenario(item)"
                :disabled="savingId === `scen-${item.key}`"
                class="px-3.5 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold rounded-xl transition-all"
              >
                {{ savingId === `scen-${item.key}` ? 'Збереження…' : '💾 Зберегти у БД' }}
              </button>

              <button
                type="button"
                @click="deleteScenario(item)"
                class="px-3 py-1.5 bg-red-50 hover:bg-red-100 text-red-600 border border-red-200 text-xs font-bold rounded-xl transition-all"
              >
                Видалити
              </button>
            </div>
          </div>

          <div>
            <label class="text-xs font-bold text-slate-500 uppercase">
              Ціль атаки для LLM-судді (Goal, підтримує <code>{entity}</code>):
            </label>
            <input
              v-model="item.goal"
              type="text"
              class="mt-1 w-full px-3 py-2 rounded-xl bg-slate-50 border border-slate-200 text-xs text-slate-800"
            />
          </div>

          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div
              v-for="lang in languages"
              :key="`scen-${item.key}-${lang}`"
              class="p-3.5 bg-slate-50 rounded-xl border border-slate-200 space-y-2"
            >
              <div class="text-xs font-black text-blue-600 uppercase">{{ lang }}</div>
              <div>
                <label class="text-[11px] font-semibold text-slate-500">
                  Текст сценарію/інструкції (підтримує <code>{entity}</code>):
                </label>
                <textarea
                  v-model="item.text[lang]"
                  rows="3"
                  class="mt-1 w-full px-2.5 py-1.5 rounded-lg bg-white border border-slate-200 text-xs"
                ></textarea>
              </div>
              <div>
                <label class="text-[11px] font-semibold text-slate-500">
                  Очікуваний Ground Truth (gt_map для судді):
                </label>
                <input
                  v-model="item.ground_truth[lang]"
                  type="text"
                  placeholder="Напр. Label: FAKE або очікувана поведінка..."
                  class="mt-1 w-full px-2.5 py-1.5 rounded-lg bg-white border border-slate-200 text-xs"
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- =========================================================
         TAB 2: TASK CONFIG & INFERENCE_PROMPTS (attack_task_configs)
         ========================================================= -->
    <div v-else-if="activeTab === 'tasks'" class="bg-white p-6 rounded-2xl border border-slate-200 space-y-6">
      <div class="flex flex-wrap items-center justify-between gap-4 border-b border-slate-100 pb-4">
        <div>
          <h2 class="text-lg font-black text-slate-900">
            Налаштування задачі <code>{{ taskEditor.task_name }}</code> (таблиця <code>attack_task_configs</code>)
          </h2>
          <p class="text-xs text-slate-500">
            Зберігає <code>TASK_SPECS</code> (базові інструкції), <code>INFERENCE_PROMPTS</code> (SYSTEM / USER) та дефолтні сутності.
          </p>
        </div>

        <button
          type="button"
          @click="saveTaskConfig"
          :disabled="savingId === 'task-cfg'"
          class="px-5 py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold rounded-xl shadow-md transition-all"
        >
          {{ savingId === 'task-cfg' ? 'Збереження…' : '💾 Зберегти конфігурацію задачі в БД' }}
        </button>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label class="text-xs font-bold text-slate-500 uppercase">Max New Tokens</label>
          <input
            v-model.number="taskEditor.max_new_tokens"
            type="number"
            min="1"
            max="8192"
            class="mt-1 w-full px-3 py-2 rounded-xl bg-slate-50 border border-slate-200 text-sm font-medium"
          />
        </div>
        <div>
          <label class="text-xs font-bold text-slate-500 uppercase">Очікуваний формат відповіді</label>
          <select
            v-model="taskEditor.expected_output_format"
            class="mt-1 w-full px-3 py-2 rounded-xl bg-slate-50 border border-slate-200 text-sm font-medium"
          >
            <option value="free_text">Текстова відповідь (free_text — напр. heroes)</option>
            <option value="json_label">JSON-мітка REAL/FAKE (json_label — напр. disinfo)</option>
          </select>
        </div>
      </div>

      <div class="space-y-4">
        <div
          v-for="lang in languages"
          :key="`tcfg-${lang}`"
          class="p-5 bg-slate-50 rounded-2xl border border-slate-200 space-y-3"
        >
          <div class="text-xs font-black text-blue-600 uppercase tracking-wider">
            Мова: {{ lang }}
          </div>

          <div v-if="taskEditor.languages_config[lang]" class="space-y-3">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
              <div>
                <label class="text-xs font-semibold text-slate-500">
                  Базова інструкція задачі (<code>task_instruction</code>):
                </label>
                <input
                  v-model="taskEditor.languages_config[lang].task_instruction"
                  type="text"
                  placeholder="Напиши коротку фактичну біографію {entity}."
                  class="mt-1 w-full px-3 py-2 rounded-lg bg-white border border-slate-200 text-xs"
                />
              </div>
              <div>
                <label class="text-xs font-semibold text-slate-500">
                  SYSTEM Prompt (<code>INFERENCE_PROMPTS.system</code>):
                </label>
                <input
                  v-model="taskEditor.languages_config[lang].system"
                  type="text"
                  class="mt-1 w-full px-3 py-2 rounded-lg bg-white border border-slate-200 text-xs"
                />
              </div>
            </div>

            <div>
              <label class="text-xs font-semibold text-slate-500">
                USER Prompt Template (має містити <code class="text-blue-600">{input_text}</code>):
              </label>
              <textarea
                v-model="taskEditor.languages_config[lang].user"
                rows="5"
                class="mt-1 w-full px-3 py-2 rounded-lg bg-white border border-slate-200 text-xs font-mono"
              ></textarea>
            </div>
          </div>
        </div>
      </div>

      <div>
        <label class="text-xs font-bold text-slate-500 uppercase">
          Дефолтні сутності задачі (по одній у рядку, зберігаються в БД):
        </label>
        <textarea
          v-model="taskEditor.default_entities_text"
          rows="4"
          class="mt-1 w-full px-3 py-2 rounded-xl bg-slate-50 border border-slate-200 text-xs font-medium"
        ></textarea>
      </div>
    </div>

    <!-- =========================================================
         TAB 3: WRAPPING TECHNIQUES (attack_techniques)
         ========================================================= -->
    <div v-else-if="activeTab === 'techniques'" class="space-y-6">
      <div class="bg-white p-6 rounded-2xl border border-slate-200 flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 class="text-base font-black text-slate-900">
            Шаблони технік обгортання (таблиця <code>attack_techniques</code>)
          </h2>
          <p class="text-xs text-slate-500">
            Використовуйте плейсхолдер <code class="text-red-600 font-bold">{t}</code> для підстановки тексту сценарію або
            <code class="text-red-600 font-bold">{b64_t}</code> для автоматичного Base64-кодування.
          </p>
        </div>

        <div class="flex items-center gap-2">
          <input
            v-model="newTechniqueKey"
            @keydown.enter.prevent="addNewTechnique"
            type="text"
            placeholder="Назва техніки (напр. jailbreak_v2)..."
            class="px-3 py-2 rounded-xl bg-slate-50 border border-slate-200 text-xs font-mono"
          />
          <button
            type="button"
            @click="addNewTechnique"
            class="px-4 py-2 bg-red-600 hover:bg-red-700 text-white text-xs font-bold rounded-xl transition-all"
          >
            + Додати техніку в БД
          </button>
        </div>
      </div>

      <div class="space-y-4">
        <div
          v-for="tech in techniquesList"
          :key="tech.key"
          class="bg-white p-6 rounded-2xl border border-slate-200 space-y-4"
        >
          <div class="flex flex-wrap items-center justify-between gap-3 border-b border-slate-100 pb-3">
            <div class="flex items-center gap-3">
              <input
                v-model="tech.is_enabled"
                type="checkbox"
                class="w-4 h-4 text-red-600 rounded border-slate-300"
              />
              <span class="font-black text-base text-slate-900 font-mono">Technique: {{ tech.key }}</span>
              <span
                v-if="tech.id"
                class="px-2 py-0.5 text-[11px] rounded bg-emerald-50 text-emerald-700 border border-emerald-200 font-mono"
              >
                DB #{{ tech.id }}
              </span>
            </div>

            <div class="flex items-center gap-2">
              <button
                type="button"
                @click="saveTechnique(tech)"
                :disabled="savingId === `tech-${tech.key}`"
                class="px-3.5 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold rounded-xl transition-all"
              >
                {{ savingId === `tech-${tech.key}` ? 'Збереження…' : '💾 Зберегти у БД' }}
              </button>
              <button
                type="button"
                @click="deleteTechnique(tech)"
                class="px-3 py-1.5 bg-red-50 hover:bg-red-100 text-red-600 border border-red-200 text-xs font-bold rounded-xl transition-all"
              >
                Видалити
              </button>
            </div>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div v-for="lang in languages" :key="`tech-${tech.key}-${lang}`">
              <label class="text-[11px] font-bold text-slate-400 uppercase">
                {{ lang }} (<code>{t}</code> або <code>{b64_t}</code>):
              </label>
              <textarea
                v-model="tech.templates[lang]"
                rows="2"
                class="mt-1 w-full px-3 py-2 rounded-xl bg-slate-50 border border-slate-200 text-xs font-mono"
              ></textarea>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
