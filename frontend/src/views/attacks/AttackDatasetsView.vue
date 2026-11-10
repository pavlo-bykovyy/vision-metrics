<script setup>
/**
 * src/views/attacks/AttackDatasetsView.vue
 *
 * Dedicated page for managing generated Attack Datasets.
 * Provides the "+ Create New Attack Dataset" button, lists all attack datasets
 * with their task, languages, intents/techniques count, row count, config inspector modal,
 * and quick actions to launch an attack run on a LoRA Adapter or Base Model, view rows, or delete.
 */

import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAttacks } from '@/composables/useAttacks'

const router = useRouter()
const { locale } = useI18n()

const API_URL = import.meta.env.VITE_API_URL || '/api'
const attacksApi = useAttacks(API_URL)

const datasets = ref([])
const isLoading = ref(false)
const error = ref('')
const onlyAttackKind = ref(true)

// Config Inspector state
const inspectedDataset = ref(null)
const inspectedConfig = ref(null)
const loadingConfig = ref(false)

async function fetchDatasets() {
  isLoading.value = true
  error.value = ''
  try {
    const res = await attacksApi.listDatasets({
      only_attack_kind: onlyAttackKind.value,
      limit: 200,
    })
    datasets.value = Array.isArray(res) ? res : res?.items || []
  } catch (e) {
    error.value = e?.message || 'Не вдалося завантажити датасети атак.'
  } finally {
    isLoading.value = false
  }
}

watch(onlyAttackKind, () => {
  fetchDatasets()
})

function goToCreateDataset() {
  router.push('/attacks/datasets/create')
}

function goToRunAttack(datasetId) {
  router.push({
    path: '/attacks/run',
    query: datasetId ? { datasetId } : undefined,
  })
}

function openDatasetDetail(datasetId) {
  router.push(`/datasets/${datasetId}`)
}

async function inspectDatasetConfig(ds) {
  inspectedDataset.value = ds
  inspectedConfig.value = null
  loadingConfig.value = true
  try {
    inspectedConfig.value = await attacksApi.getDatasetConfig(ds.id)
  } catch (e) {
    error.value = e?.message || 'Не вдалося завантажити конфігурацію датасету.'
  } finally {
    loadingConfig.value = false
  }
}

async function handleDeleteDataset(ds) {
  if (!confirm(`Ви впевнені, що хочете видалити датасет атаки "${ds.name}" (#${ds.id})?`)) {
    return
  }
  try {
    await attacksApi.deleteDataset(ds.id)
    datasets.value = datasets.value.filter((item) => item.id !== ds.id)
    if (inspectedDataset.value?.id === ds.id) {
      inspectedDataset.value = null
      inspectedConfig.value = null
    }
  } catch (e) {
    alert(e?.message || 'Помилка видалення датасету.')
  }
}

function formatDate(dateString) {
  if (!dateString) return '—'
  const date = new Date(dateString)
  const currentLocale = locale.value === 'uk' ? 'uk-UA' : 'en-US'
  return date.toLocaleString(currentLocale, {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

onMounted(() => {
  fetchDatasets()
})
</script>

<template>
  <div class="space-y-8 pb-12 px-4 md:px-8 mt-8">

    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <h1 class="text-3xl font-black text-slate-900 tracking-tight">
          Attack Datasets
        </h1>
        <p class="text-slate-500 font-medium mt-1">
          Керуйте згенерованими наборами атак (мутованими промптами), редагуйте шаблони та запускайте їх на LoRA або Base Model.
        </p>
      </div>

      <div class="flex flex-wrap items-center gap-3">
        <button
          type="button"
          @click="fetchDatasets"
          class="px-4 py-2.5 bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold rounded-xl transition-colors text-sm"
        >
          Оновити
        </button>

        <button
          type="button"
          @click="goToCreateDataset"
          class="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2.5 rounded-xl shadow-lg shadow-blue-600/20 transition-all font-bold text-sm flex items-center gap-2"
        >
          <span>+</span> Створити новий Attack Dataset
        </button>
      </div>
    </div>

    <!-- Error Banner -->
    <div
      v-if="error"
      class="p-4 bg-red-50 border border-red-200 text-red-700 rounded-2xl text-sm font-medium"
    >
      ⚠️ {{ error }}
    </div>

    <!-- Datasets Table Card -->
    <div class="bg-white rounded-[2.5rem] shadow-xl shadow-slate-200/50 border border-slate-100 overflow-hidden relative">
      <div class="px-8 py-6 border-b border-slate-50 flex flex-wrap items-center justify-between gap-4 bg-slate-50/30">
        <div class="flex items-center gap-3">
          <h2 class="text-xl font-black text-slate-800 tracking-tight">
            Мої датасети для атаки
          </h2>
          <span class="px-2.5 py-0.5 rounded-full text-xs font-bold bg-blue-50 text-blue-700 border border-blue-200">
            {{ datasets.length }}
          </span>
        </div>

        <label class="flex items-center gap-2 text-xs font-bold text-slate-600 cursor-pointer select-none">
          <input
            v-model="onlyAttackKind"
            type="checkbox"
            class="w-4 h-4 text-blue-600 rounded border-slate-300 focus:ring-blue-500"
          />
          <span>Показувати лише згенеровані Attack Datasets</span>
        </label>
      </div>

      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse">
          <thead>
            <tr class="bg-slate-50 border-b border-slate-100">
              <th class="px-6 py-4 text-xs font-black text-slate-400 uppercase tracking-widest">
                ID
              </th>
              <th class="px-6 py-4 text-xs font-black text-slate-400 uppercase tracking-widest">
                Назва датасету
              </th>
              <th class="px-6 py-4 text-xs font-black text-slate-400 uppercase tracking-widest">
                Задача (Task)
              </th>
              <th class="px-6 py-4 text-xs font-black text-slate-400 uppercase tracking-widest">
                Мови
              </th>
              <th class="px-6 py-4 text-xs font-black text-slate-400 uppercase tracking-widest">
                Конфігурація
              </th>
              <th class="px-6 py-4 text-xs font-black text-slate-400 uppercase tracking-widest text-right">
                Рядків
              </th>
              <th class="px-6 py-4 text-xs font-black text-slate-400 uppercase tracking-widest text-right">
                Дата створення
              </th>
              <th class="px-6 py-4 text-xs font-black text-slate-400 uppercase tracking-widest text-right">
                Дії
              </th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
            <tr v-if="isLoading">
              <td colspan="8" class="px-6 py-12 text-center text-slate-400 font-medium animate-pulse">
                Завантаження датасетів для атак...
              </td>
            </tr>

            <tr v-else-if="datasets.length === 0">
              <td colspan="8" class="px-6 py-12 text-center">
                <div class="text-4xl mb-3 opacity-50">🧪</div>
                <h3 class="text-lg font-bold text-slate-700">Датасетів для атак ще немає</h3>
                <p class="text-slate-500 text-sm mt-1 mb-4">
                  Натисніть «+ Створити новий Attack Dataset», щоб згенерувати мутовані промпти для тестування.
                </p>
                <button
                  type="button"
                  @click="goToCreateDataset"
                  class="px-5 py-2.5 bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold rounded-xl shadow-md transition-all"
                >
                  + Створити новий Attack Dataset
                </button>
              </td>
            </tr>

            <tr v-for="ds in datasets" :key="ds.id" class="hover:bg-slate-50 transition-colors">
              <td class="px-6 py-4 font-mono font-bold text-slate-400">#{{ ds.id }}</td>

              <td class="px-6 py-4">
                <button
                  type="button"
                  @click="openDatasetDetail(ds.id)"
                  class="font-bold text-slate-800 hover:text-blue-600 transition-colors text-left"
                >
                  {{ ds.name }}
                </button>
              </td>

              <td class="px-6 py-4">
                <span
                  v-if="ds.task_name"
                  class="px-2.5 py-1 rounded-lg bg-slate-100 text-slate-700 font-mono text-xs font-bold"
                >
                  {{ ds.task_name }}
                </span>
                <span v-else class="text-slate-400 text-xs">—</span>
              </td>

              <td class="px-6 py-4">
                <div v-if="ds.languages && ds.languages.length" class="flex flex-wrap gap-1">
                  <span
                    v-for="lang in ds.languages"
                    :key="lang"
                    class="px-2 py-0.5 rounded-md bg-blue-50 text-blue-700 border border-blue-200 text-[10px] font-bold uppercase"
                  >
                    {{ lang }}
                  </span>
                </div>
                <span v-else class="text-slate-400 text-xs">—</span>
              </td>

              <td class="px-6 py-4 text-xs text-slate-600">
                <span v-if="ds.intents_count != null || ds.techniques_count != null">
                  Intents: <strong>{{ ds.intents_count ?? 0 }}</strong> ·
                  Techs: <strong>{{ ds.techniques_count ?? 0 }}</strong>
                </span>
                <span v-else class="text-slate-400">—</span>
              </td>

              <td class="px-6 py-4 text-right font-mono font-bold text-slate-700">
                {{ ds.rows ?? '—' }}
              </td>

              <td class="px-6 py-4 text-sm font-medium text-slate-600 text-right whitespace-nowrap">
                {{ formatDate(ds.created_at) }}
              </td>

              <td class="px-6 py-4 text-right whitespace-nowrap space-x-2">
                <button
                  type="button"
                  @click="goToRunAttack(ds.id)"
                  class="px-3 py-1.5 text-xs font-bold text-white bg-red-600 hover:bg-red-700 rounded-lg shadow-sm transition-colors"
                >
                  🚀 Запустити
                </button>
                <button
                  type="button"
                  @click="inspectDatasetConfig(ds)"
                  class="px-3 py-1.5 text-xs font-bold text-slate-700 bg-slate-100 hover:bg-slate-200 rounded-lg transition-colors"
                >
                  ⚙️ Конфіг
                </button>
                <button
                  type="button"
                  @click="openDatasetDetail(ds.id)"
                  class="px-3 py-1.5 text-xs font-bold text-blue-600 bg-blue-50 hover:bg-blue-100 rounded-lg transition-colors"
                >
                  Рядки
                </button>
                <button
                  type="button"
                  @click="handleDeleteDataset(ds)"
                  class="px-3 py-1.5 text-xs font-bold text-red-600 bg-red-50 hover:bg-red-100 rounded-lg transition-colors"
                >
                  Видалити
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Dataset Schema Config Inspector Drawer / Card -->
    <div
      v-if="inspectedDataset"
      class="bg-white rounded-[2rem] shadow-lg border border-slate-200 p-6 space-y-4"
    >
      <div class="flex items-center justify-between border-b border-slate-100 pb-4">
        <div>
          <h3 class="text-lg font-black text-slate-900">
            Конфігурація генерації датасету #{{ inspectedDataset.id }} · {{ inspectedDataset.name }}
          </h3>
          <p class="text-xs text-slate-500">
            Збережені шаблони <code>intents</code>, <code>techniques</code>, <code>entities</code> та <code>inference_prompts</code>
          </p>
        </div>
        <button
          type="button"
          @click="inspectedDataset = null; inspectedConfig = null"
          class="px-3 py-1.5 text-xs font-bold bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl"
        >
          Закрити &times;
        </button>
      </div>

      <div v-if="loadingConfig" class="text-sm text-slate-400 py-4">
        Завантаження конфігурації...
      </div>

      <div v-else-if="inspectedConfig?.schema_config" class="space-y-4 text-xs">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div class="p-3 bg-slate-50 rounded-xl border border-slate-200">
            <span class="font-bold text-slate-400 uppercase block">Задача (Task)</span>
            <span class="font-mono font-bold text-slate-800 text-sm">
              {{ inspectedConfig.schema_config.task_name || '—' }}
            </span>
          </div>
          <div class="p-3 bg-slate-50 rounded-xl border border-slate-200">
            <span class="font-bold text-slate-400 uppercase block">Активні наміри (Intents)</span>
            <span class="font-mono text-slate-800">
              {{ Object.keys(inspectedConfig.schema_config.intents || {}).join(', ') || '—' }}
            </span>
          </div>
          <div class="p-3 bg-slate-50 rounded-xl border border-slate-200">
            <span class="font-bold text-slate-400 uppercase block">Техніки мутації</span>
            <span class="font-mono text-slate-800">
              {{ Object.keys(inspectedConfig.schema_config.techniques || {}).join(', ') || '—' }}
            </span>
          </div>
        </div>

        <div
          v-if="inspectedConfig.schema_config.entities?.length"
          class="p-3 bg-slate-50 rounded-xl border border-slate-200"
        >
          <span class="font-bold text-slate-400 uppercase block mb-1">
            Сутності ({{ inspectedConfig.schema_config.entities.length }}):
          </span>
          <div class="flex flex-wrap gap-1.5">
            <span
              v-for="ent in inspectedConfig.schema_config.entities"
              :key="ent"
              class="px-2 py-0.5 rounded bg-white border border-slate-200 text-slate-700 font-medium"
            >
              {{ ent }}
            </span>
          </div>
        </div>

        <details class="p-3 bg-slate-900 text-slate-200 rounded-xl">
          <summary class="cursor-pointer font-bold text-blue-300">
            Переглянути повний JSON schema_config
          </summary>
          <pre class="mt-3 overflow-x-auto text-[11px] font-mono leading-relaxed">{{ JSON.stringify(inspectedConfig.schema_config, null, 2) }}</pre>
        </details>
      </div>
    </div>
  </div>
</template>
