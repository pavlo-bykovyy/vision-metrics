<template>
  <div class="flex flex-col gap-3">
    <label class="text-xs font-black text-slate-400 uppercase tracking-widest">Available Adapters</label>
    <div class="relative">
      <select
          v-model="selectedValue"
          class="w-full px-4 py-4 rounded-xl bg-slate-50 border border-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500 font-medium text-slate-700 appearance-none cursor-pointer disabled:opacity-50"
          :disabled="isLoading"
      >
        <option value="" disabled>-- Select an adapter --</option>
        <option
            v-for="adapter in adapters"
            :key="adapter.id"
            :value="adapter.id"
        >
          {{ adapter.folder_name }} {{ adapter.base_model_name_or_path ? `(${adapter.base_model_name_or_path})` : '' }}
        </option>
      </select>
      <div class="pointer-events-none absolute inset-y-0 right-0 flex items-center px-4 text-slate-400">
        <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
        </svg>
      </div>
    </div>
    <p v-if="adapters.length === 0 && !isLoading" class="text-xs text-orange-500 font-medium">
      No adapters found on server. Please upload one.
    </p>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  modelValue: {
    type: [String, Number],
    default: ''
  },
  adapters: {
    type: Array,
    default: () => []
  },
  isLoading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue'])

const selectedValue = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})
</script>