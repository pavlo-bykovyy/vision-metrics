<template>
  <div class="p-6 bg-slate-50 rounded-3xl border-2 border-dashed border-slate-200">
    <p class="text-xs font-black uppercase text-slate-400 mb-4 tracking-widest">
      {{ label }}
    </p>

    <input
        type="file"
        @change="e => $emit('file-selected', e.target.files[0])"
        :accept="accept"
        class="hidden"
        ref="fileInput"
        :disabled="disabled || isUploading"
    />

    <button
        @click="$refs.fileInput.click()"
        :disabled="disabled || isUploading"
        :title="asset ? asset.filename : ''"
        :class="[
          'w-full py-3 px-4 border border-slate-200 rounded-xl font-bold flex items-center justify-center transition-all min-w-0 overflow-hidden',
          disabled ? 'bg-slate-100 opacity-50 cursor-not-allowed' : 'bg-white hover:bg-slate-100'
        ]"
    >
      <span v-if="isUploading" class="flex-shrink-0 mr-2 animate-spin">⏳</span>
      <span class="truncate">
        {{ isUploading ? uploadingText : (asset ? asset.filename : selectText) }}
      </span>
    </button>

    <div v-if="isUploading" class="mt-4">
      <div class="w-full bg-gray-200 rounded-full h-1.5">
        <div class="bg-blue-600 h-1.5 rounded-full transition-all duration-300" :style="{ width: `${progress}%` }"></div>
      </div>
      <p class="text-[10px] text-slate-500 text-right mt-1 font-bold">{{ progress }}%</p>
    </div>

    <p v-if="helperText && disabled" class="text-[10px] text-slate-400 mt-2 text-center font-bold">
      {{ helperText }}
    </p>
  </div>
</template>

<script setup>
defineProps({
  label: String,
  accept: String,
  isUploading: Boolean,
  progress: Number,
  asset: Object,
  disabled: Boolean,
  uploadingText: String,
  selectText: String,
  helperText: String
})

defineEmits(['file-selected'])
</script>