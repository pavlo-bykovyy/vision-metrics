<template>
  <div class="bg-white p-6 rounded-[2rem] shadow-xl shadow-slate-200/50 border border-slate-100 transition-all hover:scale-[1.02]">
    <div class="flex items-center justify-between mb-4">
      <div class="flex items-center gap-3">
        <div class="w-12 h-12 bg-indigo-50 text-indigo-600 rounded-2xl flex items-center justify-center text-xl shadow-inner">
          💾
        </div>
        <div>
          <p class="text-sm font-bold text-slate-400 uppercase tracking-wider">{{ t('dashboard.storage.title') }}</p>
          <h4 class="text-xl font-black text-slate-800 tracking-tight">{{ used }} {{ unit }} / {{ total }} {{ unit }}</h4>
        </div>
      </div>
      <div class="text-right">
        <span :class="percentageColorClass" class="text-sm font-black px-3 py-1 rounded-full bg-slate-50">
          {{ percentage }}%
        </span>
      </div>
    </div>

    <div class="w-full bg-slate-100 h-3 rounded-full overflow-hidden border border-slate-50">
      <div
          class="h-full transition-all duration-1000 ease-out shadow-[0_0_10px_rgba(79,70,229,0.3)]"
          :class="progressBarColorClass"
          :style="{ width: `${percentage}%` }"
      ></div>
    </div>

    <p class="text-xs text-slate-400 mt-3 font-medium flex justify-between">
      <span>{{ t('dashboard.storage.used') }}: {{ used }} {{ unit }}</span>
      <span>{{ t('dashboard.storage.available') }}: {{ free }} {{ unit }}</span>
    </p>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const props = defineProps({
  used: { type: Number, default: 0 },
  total: { type: Number, default: 0 },
  free: { type: Number, default: 0 },
  percentage: { type: Number, default: 0 },
  unit: { type: String, default: 'GB' }
})

const percentageColorClass = computed(() => {
  if (props.percentage > 90) return 'text-red-600'
  if (props.percentage > 70) return 'text-orange-600'
  return 'text-indigo-600'
})

const progressBarColorClass = computed(() => {
  if (props.percentage > 90) return 'bg-gradient-to-r from-red-500 to-rose-600'
  if (props.percentage > 70) return 'bg-gradient-to-r from-orange-400 to-red-500'
  return 'bg-gradient-to-r from-indigo-500 to-blue-600'
})
</script>