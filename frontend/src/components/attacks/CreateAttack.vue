<script setup>
/**
 * src/components/attacks/CreateAttack.vue
 *
 * Dedicated component for creating and generating a dynamic attack dataset (Dataset in models.py).
 * Separated from the execution/run logic so dataset creation & prompt mutation generation
 * happens independently from running the attack on a LoRA Adapter or Base Model.
 */

import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import AttackDatasetBuilder from '@/components/attacks/AttackDatasetBuilder.vue'

const props = defineProps({
  apiUrl: {
    type: String,
    default: () => import.meta.env.VITE_API_URL || '/api',
  },
})

const emit = defineEmits(['created'])
const router = useRouter()
const { t } = useI18n()

const lastCreated = ref(null)

function handleCreated(result) {
  lastCreated.value = result
  emit('created', result)
}

function goToRunAttack(datasetId) {
  router.push({
    path: '/attacks/run',
    query: datasetId ? { datasetId } : undefined,
  })
}
</script>

<template>
  <div class="max-w-5xl mx-auto space-y-8 pb-20 p-6">
    <!-- Top Navigation -->
    <div class="flex flex-wrap items-center justify-between gap-4">
      <button
          type="button"
          @click="router.push('/attacks/datasets')"
          class="text-sm font-bold text-slate-500 hover:text-slate-800 flex items-center gap-2 transition-colors"
      >
        <span>&larr;</span> Назад до Attack Datasets
      </button>

      <div class="flex flex-wrap items-center gap-3">
        <button
            type="button"
            @click="router.push('/attacks/templates')"
            class="px-4 py-2 rounded-xl bg-white hover:bg-slate-50 text-slate-700 border border-slate-200 text-xs font-bold transition-all flex items-center gap-2"
        >
          <span>⚙️</span> Шаблони сценаріїв і технік у БД
        </button>

        <button
            type="button"
            @click="goToRunAttack(lastCreated?.dataset_id)"
            class="px-4 py-2 rounded-xl bg-slate-900 hover:bg-slate-800 text-white text-xs font-bold transition-all flex items-center gap-2"
        >
          <span>🚀</span> Перейти до запуску атаки (LoRA / Base Model)
        </button>
      </div>
    </div>

    <!-- Header -->
    <div>
      <h1 class="text-3xl font-black text-slate-900 tracking-tight">
        Створення нового Attack Dataset
      </h1>
      <p class="text-slate-500 font-medium mt-1">
        Налаштуйте наміри (intents), техніки мутації, мови, сутності та динамічні шаблони
        <code>INFERENCE_PROMPTS</code> для генерації нового датасету атаки.
      </p>
    </div>

    <!-- Dataset Builder Card -->
    <div class="bg-white p-8 rounded-[2rem] shadow-sm border border-slate-100 space-y-6">
      <AttackDatasetBuilder
          :api-url="props.apiUrl"
          @created="handleCreated"
      />

      <!-- Quick Action to Launch Run or Return to Attack Datasets List After Creation -->
      <div
          v-if="lastCreated"
          class="pt-4 border-t border-slate-100 flex flex-col sm:flex-row sm:items-center justify-between gap-4"
      >
        <div class="text-sm text-slate-600">
          Згенерований датасет <strong>#{{ lastCreated.dataset_id }}</strong> збережено у списку Attack Datasets.
        </div>
        <div class="flex flex-wrap items-center gap-3">
          <button
              type="button"
              @click="router.push('/attacks/datasets')"
              class="px-5 py-3 bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold text-sm rounded-xl transition-all"
          >
            До списку Attack Datasets
          </button>
          <button
              type="button"
              @click="goToRunAttack(lastCreated.dataset_id)"
              class="px-6 py-3 bg-emerald-600 hover:bg-emerald-700 text-white font-black text-sm rounded-xl shadow-lg shadow-emerald-600/20 transition-all flex items-center justify-center gap-2"
          >
            <span>🚀 Запустити цю атаку на моделі</span>
            <span>&rarr;</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>