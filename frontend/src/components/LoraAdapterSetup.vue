<template>
  <div class="bg-white p-8 rounded-[2rem] shadow-sm border border-slate-100">
    <h2 class="text-xl font-black text-slate-800 mb-6 flex items-center gap-3">
      <span class="w-8 h-8 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center text-sm">1</span>
      Select or Upload LoRA
    </h2>

    <div class="flex bg-slate-100 p-1 rounded-xl mb-6">
      <button
          @click="activeTab = 'select'"
          :class="activeTab === 'select' ? 'bg-white shadow-sm text-slate-800' : 'text-slate-500 hover:text-slate-700'"
          class="flex-1 py-2.5 text-sm font-bold rounded-lg transition-all"
      >
        Select Existing
      </button>
      <button
          @click="activeTab = 'upload'"
          :class="activeTab === 'upload' ? 'bg-white shadow-sm text-slate-800' : 'text-slate-500 hover:text-slate-700'"
          class="flex-1 py-2.5 text-sm font-bold rounded-lg transition-all"
      >
        Upload New ZIP
      </button>
    </div>

    <div class="mt-4">
      <div v-if="activeTab === 'select'">
        <LoraAdapterSelector
            v-model="internalSelectedAdapter"
            :adapters="availableAdapters"
            :is-loading="isLoadingAdapters"
        />
      </div>

      <div v-else>
        <LoraAdapterUploader
            @upload-success="handleUploadSuccess"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import LoraAdapterSelector from './LoraAdapterSelector.vue'
import LoraAdapterUploader from './LoraAdapterUploader.vue'

// Import Composables
import { useLoraAdaptersList } from '@/composables/useLoraAdaptersList'

const props = defineProps({
  modelValue: {
    type: [String, Number],
    default: ''
  }
})

const emit = defineEmits(['update:modelValue', 'adapter-selected'])

const API_URL = import.meta.env.VITE_API_URL || ''
const activeTab = ref('select')

const internalSelectedAdapter = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const { availableAdapters, isLoadingAdapters, fetchAdapters } = useLoraAdaptersList(API_URL)

watch(internalSelectedAdapter, (newId) => {
  if (newId) {
    const adapter = availableAdapters.value.find(a => a.id === newId)
    if (adapter) {
      emit('adapter-selected', adapter)
    }
  }
})

const handleUploadSuccess = async (newAdapter) => {
  await fetchAdapters()

  if (newAdapter && newAdapter.id) {
    internalSelectedAdapter.value = newAdapter.id
    emit('adapter-selected', newAdapter)
  }

  activeTab.value = 'select'
}

onMounted(() => {
  fetchAdapters()
})
</script>