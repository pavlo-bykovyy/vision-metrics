<template>
  <div class="flex flex-col gap-3">
    <label class="text-xs font-black text-slate-400 uppercase tracking-widest">Upload New ZIP</label>
    <input type="file" accept=".zip" ref="zipInput" class="hidden" @change="onFileSelected" />
    <div class="flex gap-2">
      <button
          @click="$refs.zipInput.click()"
          :disabled="isUploading"
          class="flex-1 px-4 py-4 bg-white border border-dashed border-slate-300 text-slate-600 rounded-xl font-bold hover:bg-slate-50 hover:border-blue-400 transition-all truncate text-left disabled:opacity-50"
      >
        {{ zipFile ? zipFile.name : 'Click to select .zip' }}
      </button>

      <button
          v-if="zipFile"
          @click="uploadZip"
          :disabled="isUploading"
          class="px-6 py-4 bg-blue-600 text-white rounded-xl font-bold hover:bg-blue-700 transition-all shadow-md disabled:bg-blue-400 flex items-center justify-center"
      >
        <span v-if="isUploading" class="animate-spin mr-2">
          <svg class="h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
        </span>
        {{ isUploading ? 'Extracting...' : 'Upload' }}
      </button>
    </div>

    <div v-if="uploadMessage" :class="['mt-2 p-3 rounded-xl font-medium text-sm border', isUploadError ? 'bg-red-50 text-red-700 border-red-100' : 'bg-green-50 text-green-700 border-green-100']">
      {{ uploadMessage }}
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useLoraUpload } from '@/composables/useLoraUpload'

const emit = defineEmits(['upload-success'])
const API_URL = import.meta.env.VITE_API_URL || ''

const zipInput = ref(null)

// Ініціалізація Composable
const {
  zipFile,
  isUploading,
  uploadMessage,
  isUploadError,
  handleFileSelection,
  uploadZipFile
} = useLoraUpload(API_URL)

const onFileSelected = (event) => {
  handleFileSelection(event)
}

const uploadZip = async () => {
  const newAdapter = await uploadZipFile()

  if (newAdapter) {
    emit('upload-success', newAdapter)

    if (zipInput.value) {
      zipInput.value.value = ''
    }
  }
}
</script>