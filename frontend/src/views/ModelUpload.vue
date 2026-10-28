<template>
  <div class="max-w-4xl mx-auto space-y-8 pb-20">
    <!-- Step 1: Uploads -->
    <div class="bg-white p-8 rounded-[2rem] shadow-sm border border-slate-100">
      <h2 class="text-2xl font-black text-slate-800 mb-6">
        {{ t('modelSetup.step1Title') }}
      </h2>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">

        <!-- JSON Uploader -->
        <FileUploaderCard
            :label="`${t('modelSetup.archLabel')} (JSON)`"
            accept=".json"
            :is-uploading="jsonUploader.isUploading.value"
            :progress="jsonUploader.progress.value"
            :asset="jsonUploader.asset.value"
            :uploading-text="t('modelSetup.uploading')"
            :select-text="t('modelSetup.selectJson')"
            @file-selected="file => jsonUploader.uploadFile(file)"
        />

        <!-- H5 Uploader -->
        <FileUploaderCard
            :label="`${t('modelSetup.weightsLabel')} (H5)`"
            accept=".h5"
            :is-uploading="h5Uploader.isUploading.value"
            :progress="h5Uploader.progress.value"
            :asset="h5Uploader.asset.value"
            :disabled="!jsonUploader.asset.value"
            helper-text="Please upload the JSON architecture first."
            :uploading-text="t('modelSetup.uploading')"
            :select-text="t('modelSetup.selectH5')"
            @file-selected="file => h5Uploader.uploadFile(file)"
        />

      </div>
    </div>

    <!-- Step 2: Model Configuration -->
    <div class="bg-white p-8 rounded-[2rem] shadow-sm border border-slate-100" v-if="jsonUploader.asset.value && h5Uploader.asset.value">
      <h2 class="text-2xl font-black text-slate-800 mb-6">
        {{ t('modelSetup.step2Title') }}
      </h2>

      <div class="space-y-6">
        <div class="flex flex-col gap-2">
          <label class="text-xs font-black text-slate-400 uppercase tracking-widest">{{ t('modelsTable.name') }}</label>
          <input v-model="modelName" type="text" :placeholder="t('modelSetup.namePlaceholder')" class="px-4 py-3 rounded-xl bg-slate-50 border border-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500 font-medium text-slate-700" />
        </div>

        <div class="flex flex-col gap-2">
          <label class="text-xs font-black text-slate-400 uppercase tracking-widest">{{ t('modelsTable.description') }} (Optional)</label>
          <textarea v-model="modelDescription" rows="3" class="px-4 py-3 rounded-xl bg-slate-50 border border-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500 font-medium text-slate-700 resize-none"></textarea>
        </div>

        <div class="flex flex-col gap-2">
          <label class="text-xs font-black text-slate-400 uppercase tracking-widest">Class Mapping (JSON, Optional)</label>
          <textarea v-model="classMapping" rows="6" placeholder='{"real": 0, "fake": 1}' class="px-4 py-3 rounded-xl bg-slate-50 border border-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono text-sm text-slate-700 resize-none"></textarea>
        </div>

        <div class="flex justify-end gap-4 mt-8 pt-6 border-t border-slate-50">
          <button @click="confirmModel" :disabled="!modelName || isCreating" class="px-8 py-3 bg-blue-600 text-white rounded-xl font-black shadow-lg shadow-blue-600/20 hover:bg-blue-700 disabled:bg-slate-300 transition-all flex items-center">
            <span v-if="isCreating" class="animate-spin inline-block mr-2">⏳</span>
            {{ isCreating ? t('modelSetup.creating') : t('modelSetup.createBtn') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import axios from 'axios'
import FileUploaderCard from '@/components/FileUploaderCard.vue'
import { useFileUpload } from '@/composables/useFileUpload'

const { t } = useI18n()
const API_URL = import.meta.env.VITE_API_URL || ''
const router = useRouter()

// Initialize composables for each file type
const jsonUploader = useFileUpload(API_URL)
const h5Uploader = useFileUpload(API_URL)

// Form State
const modelName = ref('')
const modelDescription = ref('')
const classMapping = ref('{ "real": 0,  "fake": 1 }')
const isCreating = ref(false)

const confirmModel = async () => {
  let mappingDict = null
  if (classMapping.value.trim()) {
    try {
      mappingDict = JSON.parse(classMapping.value)
    } catch (e) {
      alert('Invalid JSON format in Class Mapping field. Please fix it before submitting.')
      return
    }
  }

  isCreating.value = true
  try {
    await axios.post(`${API_URL}/create-model/`, {
      name: modelName.value,
      description: modelDescription.value || null,
      arch_id: jsonUploader.asset.value.id,
      weights_id: h5Uploader.asset.value.id,
      class_mapping: mappingDict
    })
    router.push({ name: 'Models' })
  } catch (err) {
    alert(t('modelSetup.errorCreate'))
  } finally {
    isCreating.value = false
  }
}
</script>