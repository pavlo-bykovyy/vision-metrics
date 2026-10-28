<template>
  <div class="flex flex-col gap-2 mb-6 p-4 bg-slate-50 rounded-xl border border-slate-100">
    <label class="flex items-center gap-2 cursor-pointer">
      <input
          type="checkbox"
          :checked="useCustom"
          @change="$emit('update:useCustom', $event.target.checked)"
          class="w-4 h-4 text-blue-600 rounded border-slate-300 focus:ring-blue-500"
      >
      <span class="font-bold text-slate-700">Use Custom Prompt Template (Optional)</span>
    </label>

    <div v-if="useCustom" class="mt-3 flex flex-col gap-2">
      <label class="text-xs font-black text-slate-400 uppercase tracking-widest">Template Layout</label>
      <textarea
          :value="templateText"
          @input="$emit('update:templateText', $event.target.value)"
          rows="6"
          placeholder="e.g., Classify this text as REAL or FAKE.&#10;Text: {input_text}"
          class="px-4 py-4 rounded-xl bg-white border border-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono text-sm text-slate-700 resize-y"
      ></textarea>
      <p class="text-xs font-medium text-slate-500">
        Use <code class="bg-slate-200 px-1 py-0.5 rounded text-slate-700 font-bold">{input_text}</code> where you want the prompt or dataset text to be injected.
      </p>
    </div>
  </div>
</template>

<script setup>
/**
 * Defines the properties passed down from the parent component.
 * @property {boolean} useCustom - Determines if the custom template UI should be displayed.
 * @property {string} templateText - The actual template string provided by the user.
 */
defineProps({
  useCustom: {
    type: Boolean,
    default: false
  },
  templateText: {
    type: String,
    default: ''
  }
})

/**
 * Defines the events emitted to the parent component.
 * Supports multiple v-model bindings on this component.
 */
defineEmits(['update:useCustom', 'update:templateText'])
</script>