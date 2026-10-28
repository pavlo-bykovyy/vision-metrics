<template>
  <div>
    <div v-if="models.length === 0" class="py-12 flex flex-col items-center justify-center text-center">
      <div class="text-6xl mb-4 opacity-50">🤖</div>
      <h3 class="text-lg font-bold text-slate-700">{{ t('modelsTable.noModels') }}</h3>
      <p class="text-slate-500 mt-1">{{ t('modelsTable.noModelsDesc') }}</p>
    </div>

    <div v-else class="overflow-x-auto border border-slate-100 rounded-2xl overflow-hidden">
      <table class="w-full text-left border-collapse">
        <thead>
        <tr class="bg-slate-50 text-slate-500 text-sm border-b border-slate-100">
          <th class="p-4 font-semibold w-16">ID</th>
          <th class="p-4 font-semibold">{{ t('modelsTable.name') }}</th>
          <th class="p-4 font-semibold">{{ t('modelsTable.description') }}</th>
          <th class="p-4 font-semibold">{{ t('modelsTable.createdAt') }}</th>
          <th class="p-4 font-semibold text-right">{{ t('modelsTable.actions') }}</th>
        </tr>
        </thead>
        <tbody>
        <tr
            v-for="(model, index) in models"
            :key="model.id"
            class="hover:bg-slate-50/50 transition-colors text-sm"
            :class="index !== models.length - 1 ? 'border-b border-slate-50' : ''"
        >
          <td class="p-4 font-mono font-bold text-slate-400">#{{ model.id }}</td>

          <td class="p-4 font-bold text-slate-800">
            <router-link :to="`/models/${model.id}`" class="hover:text-blue-600 hover:underline transition-colors">
              {{ model.name }}
            </router-link>
          </td>

          <td class="p-4 text-slate-500 max-w-xs truncate" :title="model.description">
            {{ model.description || '—' }}
          </td>

          <td class="p-4 text-slate-600 font-medium">
            {{ formatDate(model.created_at) }}
          </td>

          <td class="p-4 text-right space-x-2">
            <button
                @click="$emit('edit', model)"
                class="px-3 py-1.5 text-xs font-bold text-blue-600 bg-blue-50 hover:bg-blue-100 rounded-lg transition-colors"
            >
              {{ t('modelsTable.edit') }}
            </button>
            <button
                @click="$emit('delete', model)"
                class="px-3 py-1.5 text-xs font-bold text-red-600 bg-red-50 hover:bg-red-100 rounded-lg transition-colors"
            >
              {{ t('modelsTable.delete') }}
            </button>
          </td>
        </tr>
        </tbody>
      </table>
    </div>

    <div v-if="totalPages > 1" class="px-6 py-4 bg-slate-50/50 border-t border-slate-100 flex items-center justify-between mt-4 rounded-xl">
      <div class="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em]">
        {{ t('pagination.page') }} {{ currentPage }} / {{ totalPages }}
      </div>

      <div class="flex items-center gap-2">
        <button
            @click="$emit('page-change', currentPage - 1)"
            :disabled="currentPage === 1"
            class="p-2 rounded-xl border border-slate-200 bg-white hover:bg-slate-50 disabled:opacity-30 disabled:cursor-not-allowed transition-all shadow-sm"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" /></svg>
        </button>

        <div class="flex items-center gap-1">
          <button
              v-for="p in visiblePages" :key="p"
              @click="$emit('page-change', p)"
              class="w-8 h-8 rounded-lg text-[11px] font-black transition-all"
              :class="p === currentPage ? 'bg-blue-600 text-white shadow-lg shadow-blue-500/30' : 'bg-white border border-slate-100 text-slate-500 hover:bg-slate-50'"
          >
            {{ p }}
          </button>
        </div>

        <button
            @click="$emit('page-change', currentPage + 1)"
            :disabled="currentPage === totalPages"
            class="p-2 rounded-xl border border-slate-200 bg-white hover:bg-slate-50 disabled:opacity-30 disabled:cursor-not-allowed transition-all shadow-sm"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" /></svg>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const props = defineProps({
  models: { type: Array, required: true },
  currentPage: { type: Number, default: 1 },
  totalPages: { type: Number, default: 1 }
})

const emit = defineEmits(['edit', 'delete', 'page-change'])

const visiblePages = computed(() => {
  const pages = []
  for (let i = 1; i <= props.totalPages; i++) {
    pages.push(i)
  }
  return pages
})

const formatDate = (isoString) => {
  if (!isoString) return '—'
  const date = new Date(isoString)
  return date.toLocaleString('uk-UA', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>