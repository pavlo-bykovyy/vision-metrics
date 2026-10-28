<template>
  <div class="max-w-4xl mx-auto space-y-8 pb-20">

    <div>
      <router-link to="/datasets" class="text-sm font-bold text-slate-400 hover:text-blue-600 transition-colors flex items-center gap-2 mb-4">
        ← Back to Datasets
      </router-link>
      <h1 class="text-3xl font-black text-slate-900 tracking-tight">Upload New Dataset</h1>
      <p class="text-slate-500 font-medium mt-1">Provide a local file or an external URL to be used in evaluations.</p>
    </div>

    <div class="bg-white p-8 rounded-[2rem] shadow-sm border border-slate-100">
      <form @submit.prevent="handleUploadSubmit" class="grid grid-cols-1 md:grid-cols-2 gap-6">

        <!-- Dataset Name -->
        <div class="col-span-1 md:col-span-2 flex flex-col gap-2">
          <label class="text-xs font-black text-slate-400 uppercase tracking-widest">Dataset Name</label>
          <input v-model="formData.name" type="text" placeholder="e.g., Math Prompts v1" class="px-4 py-3 rounded-xl bg-slate-50 border border-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500 font-medium text-slate-700" required />
        </div>

        <div class="col-span-1 md:col-span-2 flex flex-col gap-2">
          <label class="text-xs font-black text-slate-400 uppercase tracking-widest">Dataset Type</label>
          <select v-model="formData.dataset_type" class="px-4 py-3 rounded-xl bg-slate-50 border border-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500 font-medium text-slate-700 appearance-none cursor-pointer">
            <option v-for="option in TYPE_OPTIONS" :key="option.value" :value="option.value">
              {{ option.label }}
            </option>
          </select>
        </div>

        <div class="flex flex-col gap-2">
          <label class="text-xs font-black text-slate-400 uppercase tracking-widest">Data Source</label>
          <select v-model="formData.file_source" @change="onSourceChange" class="px-4 py-3 rounded-xl bg-slate-50 border border-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500 font-medium text-slate-700 appearance-none cursor-pointer">
            <option v-for="option in SOURCE_OPTIONS" :key="option.value" :value="option.value">
              {{ option.label }}
            </option>
          </select>
        </div>

        <!-- Data Format -->
        <div class="flex flex-col gap-2">
          <label class="text-xs font-black text-slate-400 uppercase tracking-widest">Data Format</label>
          <select v-model="formData.file_format" class="px-4 py-3 rounded-xl bg-slate-50 border border-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500 font-medium text-slate-700 appearance-none cursor-pointer">
            <option v-for="option in FORMAT_OPTIONS" :key="option.value" :value="option.value">
              {{ option.label }}
            </option>
          </select>
        </div>

        <div v-if="formData.file_source === DatasetSource.LOCAL_FILE" class="col-span-1 md:col-span-2 flex flex-col gap-2">
          <label class="text-xs font-black text-slate-400 uppercase tracking-widest">Dataset File</label>
          <input
              type="file"
              accept=".csv,.jsonl,.zip"
              ref="fileInput"
              @change="onFileSelected"
              class="block w-full text-sm text-slate-500 file:mr-4 file:py-3 file:px-4 file:rounded-xl file:border-0 file:text-sm file:font-bold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100 transition-all cursor-pointer"
              :required="formData.file_source === DatasetSource.LOCAL_FILE"
          />
        </div>

        <div v-if="formData.file_source !== DatasetSource.LOCAL_FILE" class="col-span-1 md:col-span-2 flex flex-col gap-2">
          <label class="text-xs font-black text-slate-400 uppercase tracking-widest">Source URL</label>
          <input
              v-model="formData.source_url"
              type="url"
              placeholder="hamzaboulahia/hardfakevsrealfaces"
              class="px-4 py-3 rounded-xl bg-slate-50 border border-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500 font-medium text-slate-700"
              :required="formData.file_source !== DatasetSource.LOCAL_FILE"
          />
        </div>

        <template v-if="![DatasetFormat.IMAGE_FOLDER, DatasetFormat.NONE].includes(formData.file_format)">
          <div class="col-span-1 md:col-span-2 flex flex-col gap-2 mt-4">
            <label class="text-xs font-black text-slate-400 uppercase tracking-widest">ID Column (Optional)</label>
            <input v-model="formData.id_column" type="text" placeholder="e.g., uuid, row_id" class="px-4 py-3 rounded-xl bg-slate-50 border border-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500 font-medium text-slate-700" />
            <p class="text-[11px] text-slate-400 font-medium">Name of the column containing unique identifiers for each row.</p>
          </div>

          <div class="col-span-1 md:col-span-2 grid grid-cols-1 md:grid-cols-3 gap-4 p-5 bg-slate-50 rounded-2xl border border-slate-200 mt-2">
            <div class="md:col-span-3">
              <h3 class="text-sm font-bold text-slate-800">Schema Configuration</h3>
              <p class="text-xs text-slate-500">Define which columns from your dataset should be used. Separate multiple values with commas.</p>
            </div>

            <div class="flex flex-col gap-2">
              <label class="text-[10px] font-black text-slate-400 uppercase tracking-widest">Input Fields</label>
              <input v-model="formData.input_fields" type="text" placeholder="question, choice_a" class="px-3 py-2 rounded-lg bg-white border border-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm text-slate-700" />
            </div>

            <div class="flex flex-col gap-2">
              <label class="text-[10px] font-black text-slate-400 uppercase tracking-widest">Target Fields</label>
              <input v-model="formData.target_fields" type="text" placeholder="correct_answer" class="px-3 py-2 rounded-lg bg-white border border-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm text-slate-700" />
            </div>

            <div class="flex flex-col gap-2">
              <label class="text-[10px] font-black text-slate-400 uppercase tracking-widest">Metadata Fields</label>
              <input v-model="formData.metadata_fields" type="text" placeholder="subject, category" class="px-3 py-2 rounded-lg bg-white border border-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm text-slate-700" />
            </div>
          </div>
        </template>

        <div v-if="formData.file_format === DatasetFormat.IMAGE_FOLDER" class="col-span-1 md:col-span-2 flex flex-col gap-2 mt-4">
          <label class="text-xs font-black text-slate-400 uppercase tracking-widest">Class Mapping (JSON format, Optional)</label>
          <textarea v-model="formData.class_mapping" rows="4" placeholder='{&#10;  "real": 0,&#10;  "fake": 1&#10;}' class="px-4 py-3 rounded-xl bg-slate-50 border border-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500 font-medium text-slate-700 font-mono text-sm resize-y"></textarea>
          <p class="text-[11px] text-slate-400 font-medium">Use valid JSON with double quotes. Required if you want to strictly define class indices for ML models.</p>
        </div>

        <div class="col-span-1 md:col-span-2 flex items-center justify-between mt-4 border-t border-slate-100 pt-6">
          <div :class="['text-sm font-bold', statusMessage.isError ? 'text-red-500' : 'text-green-500']">
            {{ statusMessage.text }}
          </div>
          <button type="submit" :disabled="isUploading" class="px-8 py-3 bg-blue-600 text-white rounded-xl font-black shadow-lg shadow-blue-600/20 hover:bg-blue-700 disabled:bg-slate-300 transition-all flex items-center gap-2">
            <span v-if="isUploading" class="animate-spin inline-block">⏳</span>
            {{ isUploading ? 'Uploading...' : 'Save Dataset' }}
          </button>
        </div>

      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useDatasets } from '@/composables/useDatasets'

import {
  DatasetType,
  DatasetSource,
  DatasetFormat,
  TYPE_OPTIONS,
  SOURCE_OPTIONS,
  FORMAT_OPTIONS
} from '@/constants/dataset'

const API_URL = import.meta.env.VITE_API_URL || ''
const router = useRouter()

const { uploadDataset, isUploading } = useDatasets(API_URL)

const fileInput = ref(null)
const selectedFile = ref(null)
const statusMessage = ref({ text: '', isError: false })

const formData = ref({
  name: '',
  dataset_type: DatasetType.LLM,
  file_source: DatasetSource.LOCAL_FILE,
  file_format: DatasetFormat.CSV,
  source_url: '',
  id_column: '',
  input_fields: '',
  target_fields: '',
  metadata_fields: '',
  class_mapping: '{\n  "real": 0,\n  "fake": 1\n}'
})

const onSourceChange = () => {
  if (formData.value.file_source === DatasetSource.HUGGING_FACE) {
    formData.value.file_format = DatasetFormat.ARROW
  } else if (formData.value.file_source === DatasetSource.KAGGLE || formData.value.file_source === DatasetSource.DIRECT_URL) {
    formData.value.file_format = DatasetFormat.CSV
  }
}

const onFileSelected = (event) => {
  const file = event.target.files[0]
  if (file) {
    selectedFile.value = file

    if (file.name.endsWith('.jsonl')) {
      formData.value.file_format = DatasetFormat.JSONL
      formData.value.dataset_type = DatasetType.LLM
    } else {
      formData.value.file_format = DatasetFormat.CSV
    }

    if (!formData.value.name) {
      formData.value.name = file.name.split('.').slice(0, -1).join('.')
    }
  }
}

const showMessage = (text, isError) => {
  statusMessage.value = { text, isError }
  if (!isError) {
    setTimeout(() => { statusMessage.value.text = '' }, 3000)
  }
}

const parseCommaSeparatedString = (str) => {
  if (!str) return []
  return str.split(',').map(item => item.trim()).filter(Boolean)
}

const handleUploadSubmit = async () => {
  const isLocalFile = formData.value.file_source === DatasetSource.LOCAL_FILE;

  if (isLocalFile && !selectedFile.value) {
    showMessage('Please select a file first.', true)
    return
  }
  if (!isLocalFile && !formData.value.source_url) {
    showMessage('Please provide a source URL.', true)
    return
  }

  showMessage('', false)

  const payload = new FormData()
  payload.append('name', formData.value.name.trim())
  payload.append('dataset_type', formData.value.dataset_type)
  payload.append('file_source', formData.value.file_source)
  payload.append('file_format', formData.value.file_format)

  if (isLocalFile && selectedFile.value) {
    payload.append('file', selectedFile.value)
  } else {
    payload.append('source_url', formData.value.source_url.trim())
  }

  if (![DatasetFormat.IMAGE_FOLDER, DatasetFormat.NONE].includes(formData.value.file_format)) {
    if (formData.value.id_column) {
      payload.append('id_column', formData.value.id_column.trim())
    }

    const schemaConfig = {
      input_fields: parseCommaSeparatedString(formData.value.input_fields),
      target_fields: parseCommaSeparatedString(formData.value.target_fields),
      metadata_fields: parseCommaSeparatedString(formData.value.metadata_fields),
    }

    payload.append('schema_config', JSON.stringify(schemaConfig))
  }

  if (formData.value.file_format === DatasetFormat.IMAGE_FOLDER) {
    if (formData.value.class_mapping) {
      try {
        JSON.parse(formData.value.class_mapping)
        payload.append('mapping_config', formData.value.class_mapping.trim())
      } catch (e) {
        showMessage('Invalid JSON format in Class Mapping.', true)
        return
      }
    }
  }

  try {
    await uploadDataset(payload)
    showMessage('Dataset successfully uploaded! Redirecting...', false)
    setTimeout(() => { router.push('/datasets') }, 1000)
  } catch (error) {
    showMessage(error.response?.data?.detail || 'Failed to upload dataset.', true)
  }
}
</script>