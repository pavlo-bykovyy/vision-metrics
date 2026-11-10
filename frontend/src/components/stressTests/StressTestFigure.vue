<template>
  <div class="bg-white rounded-[2rem] shadow-sm border border-slate-100 overflow-hidden flex flex-col">
    <div class="px-6 py-4 border-b border-slate-50 bg-slate-50/30 flex items-center justify-between gap-3">
      <h3 class="text-sm font-black text-slate-800 tracking-tight truncate" :title="path">{{ title }}</h3>
      <div class="flex gap-2 shrink-0">
        <button
            v-for="variant in variants"
            :key="variant.path"
            @click="$emit('download', variant.path)"
            class="text-[10px] font-black uppercase tracking-widest py-1.5 px-2.5 rounded-lg bg-blue-50 text-blue-600 hover:bg-blue-600 hover:text-white transition-all"
        >
          {{ variant.ext }}
        </button>
      </div>
    </div>

    <div class="flex-1 flex items-center justify-center p-4 min-h-[16rem] bg-white">
      <div v-if="loading" class="text-slate-400 font-medium animate-pulse">{{ t('common.loading') }}</div>
      <div v-else-if="error" class="text-sm text-red-500 font-medium">{{ error }}</div>
      <img
          v-else-if="src"
          :src="src"
          :alt="title"
          class="max-w-full max-h-[28rem] object-contain cursor-zoom-in"
          @click="$emit('open', src)"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { stressTestsApi } from '@/composables/useStressTests'

const props = defineProps({
  runId: { type: [Number, String], required: true },
  path: { type: String, required: true },
  title: { type: String, required: true },
  variants: { type: Array, default: () => [] },
})
defineEmits(['download', 'open'])

const { t } = useI18n()
const src = ref('')
const loading = ref(false)
const error = ref('')

const release = () => {
  if (src.value) URL.revokeObjectURL(src.value)
  src.value = ''
}

const load = async () => {
  release()
  loading.value = true
  error.value = ''
  try {
    const blob = await stressTestsApi.fetchFileBlob(props.runId, props.path)
    src.value = URL.createObjectURL(blob)
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

watch(() => [props.runId, props.path], load)
onMounted(load)
onBeforeUnmount(release)
</script>
