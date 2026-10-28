<!-- src/components/EvaluationModeSelector.vue -->
<template>
  <div class="evaluation-mode-selector w-full">
    <div class="flex items-center gap-4 mb-4">
      <label class="flex items-center gap-2 cursor-pointer">
        <input
            type="radio"
            :checked="mode === 'prompt'"
            @change="$emit('update:mode', 'prompt')"
            class="text-blue-600 focus:ring-blue-500"
        >
        <span class="font-bold text-slate-700">Single Prompt</span>
      </label>
      <label class="flex items-center gap-2 cursor-pointer">
        <input
            type="radio"
            :checked="mode === 'dataset'"
            @change="$emit('update:mode', 'dataset')"
            class="text-blue-600 focus:ring-blue-500"
        >
        <span class="font-bold text-slate-700">Use Dataset</span>
      </label>
    </div>

    <div v-if="mode === 'prompt'" class="flex flex-col gap-2 mb-6">
      <label class="text-xs font-black text-slate-400 uppercase tracking-widest">Prompt</label>
      <textarea
          :value="promptText"
          @input="$emit('update:promptText', $event.target.value)"
          rows="4"
          placeholder="e.g., Хто такий Ян Тарновський?"
          class="px-4 py-4 rounded-2xl bg-slate-50 border border-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none font-medium text-slate-700"
      ></textarea>
    </div>

    <div v-if="mode === 'dataset'" class="flex flex-col gap-2 mb-6">
      <label class="text-xs font-black text-slate-400 uppercase tracking-widest">Select Dataset</label>
      <select
          :value="datasetId"
          @change="$emit('update:datasetId', $event.target.value)"
          class="px-4 py-3 rounded-xl bg-slate-50 border border-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500 font-medium text-slate-700 appearance-none cursor-pointer"
      >
        <option value="" disabled>Select a dataset...</option>
        <option v-for="dataset in datasets" :key="dataset.id" :value="dataset.id">
          {{ dataset.name }} ({{ dataset.file_format }})
        </option>
      </select>
      <p v-if="datasets.length === 0" class="text-sm text-slate-500 mt-1">
        No datasets found. Please upload one in the Datasets tab.
      </p>
    </div>
  </div>
</template>

<script setup>
/**
 * Defines the properties required by this component.
 * @property {string} mode - The current evaluation mode ('prompt' or 'dataset').
 * @property {string} promptText - The text entered for a single prompt evaluation.
 * @property {string|number} datasetId - The ID of the selected dataset.
 * @property {Array} datasets - The list of available datasets fetched from the backend.
 */
defineProps({
  mode: {
    type: String,
    required: true
  },
  promptText: {
    type: String,
    default: ''
  },
  datasetId: {
    type: [String, Number],
    default: ''
  },
  datasets: {
    type: Array,
    default: () => []
  }
})

/**
 * Defines the events to update the parent component's state using v-model.
 */
defineEmits(['update:mode', 'update:promptText', 'update:datasetId'])
</script>