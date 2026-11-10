<template>
  <div>
    <div v-if="loading" class="py-10 text-center text-slate-400 font-medium animate-pulse">
      {{ t('common.loading') }}
    </div>

    <div v-else-if="error" class="m-6 p-4 bg-red-50 text-red-700 rounded-xl font-medium text-sm border border-red-100">
      {{ error }}
    </div>

    <div v-else-if="!table || table.rows.length === 0" class="py-10 text-center text-slate-400 font-medium">
      {{ t('stressTests.detail.emptyTable') }}
    </div>

    <template v-else>
      <div class="overflow-auto" :class="maxHeightClass">
        <table class="w-full text-left border-collapse text-sm">
          <thead class="sticky top-0 z-10">
          <tr class="bg-slate-50 text-slate-500 border-b border-slate-100">
            <th
                v-for="(col, i) in table.columns"
                :key="i"
                class="px-4 py-3 text-[10px] font-black uppercase tracking-widest whitespace-nowrap"
                :class="isNumericColumn[i] ? 'text-right' : ''"
            >
              {{ col || '#' }}
            </th>
          </tr>
          </thead>
          <tbody>
          <tr
              v-for="(row, r) in table.rows"
              :key="r"
              class="border-b border-slate-50 hover:bg-slate-50/50 transition-colors"
          >
            <td
                v-for="(cell, c) in row"
                :key="c"
                class="px-4 py-2.5 whitespace-nowrap"
                :class="[
                  isNumericColumn[c] ? 'text-right font-mono font-bold text-slate-700' : 'text-slate-600 font-medium',
                  c === 0 ? 'text-slate-800 font-bold' : ''
                ]"
            >
              <span
                  v-if="typeof cell === 'string' && FAILURE_PATH_STYLES[cell]"
                  class="px-2.5 py-1 rounded-lg border text-xs font-bold"
                  :class="FAILURE_PATH_STYLES[cell]"
              >{{ cell }}</span>
              <template v-else>{{ formatCell(cell) }}</template>
            </td>
          </tr>
          </tbody>
        </table>
      </div>

      <div
          v-if="table.truncated"
          class="px-6 py-3 text-xs font-bold text-slate-400 uppercase tracking-widest border-t border-slate-50 bg-slate-50/30"
      >
        {{ t('stressTests.detail.truncated', { shown: table.rows.length, total: table.total_rows }) }}
      </div>
    </template>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { FAILURE_PATH_STYLES } from '@/constants/stressTests'

const props = defineProps({
  table: { type: Object, default: null },
  loading: { type: Boolean, default: false },
  error: { type: String, default: '' },
  maxHeightClass: { type: String, default: 'max-h-[32rem]' },
})

const { t } = useI18n()

const isNumericColumn = computed(() => {
  if (!props.table) return []
  return props.table.columns.map((_, c) =>
      props.table.rows.some((row) => typeof row[c] === 'number') &&
      props.table.rows.every((row) => row[c] == null || typeof row[c] === 'number'),
  )
})

const formatCell = (value) => {
  if (value === null || value === undefined || value === '') return '—'
  if (typeof value === 'number') {
    if (Number.isInteger(value)) return value.toLocaleString('en-US')
    const abs = Math.abs(value)
    if (abs !== 0 && (abs < 1e-4 || abs >= 1e6)) return value.toExponential(3)
    return value.toFixed(4)
  }
  if (typeof value === 'boolean') return value ? '✓' : '✗'
  return value
}
</script>
