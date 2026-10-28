## `here_ui.md`

```markdown

```

## `App.vue`

```vue
<template>
  <router-view />
</template>

<script setup>
</script>
```

## `assets/base.css`

```css
/* color palette from <https://github.com/vuejs/theme> */
:root {
  --vt-c-white: #ffffff;
  --vt-c-white-soft: #f8f8f8;
  --vt-c-white-mute: #f2f2f2;

  --vt-c-black: #181818;
  --vt-c-black-soft: #222222;
  --vt-c-black-mute: #282828;

  --vt-c-indigo: #2c3e50;

  --vt-c-divider-light-1: rgba(60, 60, 60, 0.29);
  --vt-c-divider-light-2: rgba(60, 60, 60, 0.12);
  --vt-c-divider-dark-1: rgba(84, 84, 84, 0.65);
  --vt-c-divider-dark-2: rgba(84, 84, 84, 0.48);

  --vt-c-text-light-1: var(--vt-c-indigo);
  --vt-c-text-light-2: rgba(60, 60, 60, 0.66);
  --vt-c-text-dark-1: var(--vt-c-white);
  --vt-c-text-dark-2: rgba(235, 235, 235, 0.64);
}

/* semantic color variables for this project */
:root {
  --color-background: var(--vt-c-white);
  --color-background-soft: var(--vt-c-white-soft);
  --color-background-mute: var(--vt-c-white-mute);

  --color-border: var(--vt-c-divider-light-2);
  --color-border-hover: var(--vt-c-divider-light-1);

  --color-heading: var(--vt-c-text-light-1);
  --color-text: var(--vt-c-text-light-1);

  --section-gap: 160px;
}

@media (prefers-color-scheme: dark) {
  :root {
    --color-background: var(--vt-c-black);
    --color-background-soft: var(--vt-c-black-soft);
    --color-background-mute: var(--vt-c-black-mute);

    --color-border: var(--vt-c-divider-dark-2);
    --color-border-hover: var(--vt-c-divider-dark-1);

    --color-heading: var(--vt-c-text-dark-1);
    --color-text: var(--vt-c-text-dark-2);
  }
}

*,
*::before,
*::after {
  box-sizing: border-box;
  margin: 0;
  font-weight: normal;
}

body {
  min-height: 100vh;
  color: var(--color-text);
  background: var(--color-background);
  transition:
    color 0.5s,
    background-color 0.5s;
  line-height: 1.6;
  font-family:
    Inter,
    -apple-system,
    BlinkMacSystemFont,
    'Segoe UI',
    Roboto,
    Oxygen,
    Ubuntu,
    Cantarell,
    'Fira Sans',
    'Droid Sans',
    'Helvetica Neue',
    sans-serif;
  font-size: 15px;
  text-rendering: optimizeLegibility;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

```

## `assets/main.css`

```css
@import "tailwindcss";

body {
  background-color: #f3f4f6;
}
```

## `components/AppHeader.vue`

```vue
<template>
  <header class="h-20 bg-white border-b border-slate-100 px-8 flex items-center justify-between">
    <div class="flex items-center space-x-2 text-sm">
      <span class="text-slate-400">Pages</span>
      <span class="text-slate-300">/</span>
      <span class="text-slate-900 font-medium capitalize">{{ currentRouteName }}</span>
    </div>

    <div class="flex items-center space-x-6">
      <div class="flex bg-slate-50 p-1 rounded-lg border border-slate-100">
        <button
            v-for="lang in ['en', 'uk']" :key="lang"
            @click="changeLocale(lang)"
            :class="['px-3 py-1 rounded-md text-xs font-bold transition-all',
                   locale === lang ? 'bg-white shadow-sm text-blue-600' : 'text-slate-400 hover:text-slate-600']"
        >
          {{ lang.toUpperCase() }}
        </button>
      </div>

      <div class="h-6 w-px bg-slate-100"></div>

      <div class="flex items-center space-x-3 cursor-pointer hover:opacity-80 transition">
        <div class="text-right hidden sm:block">
          <p class="text-sm font-bold text-slate-900 leading-tight">Admin User</p>
          <p class="text-xs text-green-500 font-medium">Online</p>
        </div>
        <div class="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-500 to-blue-600 flex items-center justify-center text-white shadow-md">
          JD
        </div>
      </div>
    </div>
  </header>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'

const route = useRoute()
const { locale } = useI18n()

const currentRouteName = computed(() => route.name || 'Overview')

const changeLocale = (lang) => {
  locale.value = lang
}
</script>
```

## `components/AppSidebar.vue`

```vue
<template>
  <aside class="w-72 bg-[#0F172A] text-slate-400 flex flex-col border-r border-slate-800 h-screen sticky top-0">
    <div class="h-20 flex items-center px-8 shrink-0">
      <div class="w-8 h-8 bg-blue-500 rounded-lg flex items-center justify-center mr-3 shadow-lg shadow-blue-500/30">
        <span class="text-white font-bold text-lg">V</span>
      </div>
      <span class="text-white font-bold tracking-wider uppercase text-sm text-white">VisionMetrics</span>
    </div>

    <nav class="flex-1 px-4 py-6 space-y-8 overflow-y-auto">

      <div class="space-y-1">
        <router-link to="/" class="nav-link">
          <span class="mr-3">📊</span> Dashboard
        </router-link>
      </div>

      <!-- CV Section -->
      <div>
        <p class="px-4 text-[10px] font-black text-slate-500 uppercase tracking-[0.2em] mb-4">CV</p>
        <div class="space-y-1">
          <router-link to="/models" class="nav-link">
            <span class="mr-3">🧠</span> AI Models
          </router-link>
          <router-link to="/evaluations" class="nav-link">
            <span class="mr-3">📈</span> Evaluations
          </router-link>
        </div>
      </div>

      <!-- Datasets Section -->
      <div>
        <p class="px-4 text-[10px] font-black text-slate-500 uppercase tracking-[0.2em] mb-4">Datasets</p>
        <div class="space-y-1">
          <router-link to="/datasets" class="nav-link">
            <span class="mr-3">📂</span> Datasets
          </router-link>
        </div>
      </div>

      <!-- Base Section -->
      <div>
        <p class="px-4 text-[10px] font-black text-slate-500 uppercase tracking-[0.2em] mb-4">Base</p>
        <div class="space-y-1">
          <router-link to="/base-model-tasks" class="nav-link">
            <span class="mr-3">📦</span> Test Base Model
          </router-link>
        </div>
      </div>

      <!-- LoRA Section -->
      <div>
        <p class="px-4 text-[10px] font-black text-slate-500 uppercase tracking-[0.2em] mb-4">LoRA</p>
        <div class="space-y-1">
          <router-link to="/lora-adapters" class="nav-link">
            <span class="mr-3">🔌</span> LoRA Adapters
          </router-link>
          <router-link to="/test-lora" class="nav-link">
            <span class="mr-3">💬</span> Test LoRA
          </router-link>
          <router-link to="/lora-tasks" class="nav-link">
            <span class="mr-3">📋</span> LoRA Tasks
          </router-link>
          <router-link to="/active-models" class="nav-link">
            <span class="mr-3">🚀</span> LoRA Active Models
          </router-link>
        </div>
      </div>

      <!-- Judges Section -->
      <div>
        <p class="px-4 text-[10px] font-black text-slate-500 uppercase tracking-[0.2em] mb-4">Judges</p>
        <div class="space-y-1">
          <router-link to="/judges" class="nav-link">
            <span class="mr-3">🧑‍⚖️</span> Judges
          </router-link>
          <router-link to="/judge-tasks" class="nav-link">
            <span class="mr-3">📋</span> Judge Tasks
          </router-link>
        </div>
      </div>

      <!-- API Section -->
      <div>
        <p class="px-4 text-[10px] font-black text-slate-500 uppercase tracking-[0.2em] mb-4">API</p>
        <div class="space-y-1">
          <router-link to="/api-docs" class="nav-link">
            <span class="mr-3">📖</span> API Docs
          </router-link>
        </div>
      </div>

<!--      <div>-->
<!--        <p class="px-4 text-[10px] font-black text-slate-500 uppercase tracking-[0.2em] mb-4">Management</p>-->
<!--        <div class="space-y-1">-->
<!--          <router-link to="/users" class="nav-link">-->
<!--            <span class="mr-3">👥</span> Users-->
<!--          </router-link>-->
<!--          <router-link to="/settings" class="nav-link">-->
<!--            <span class="mr-3">⚙️</span> Settings-->
<!--          </router-link>-->
<!--        </div>-->
<!--      </div>-->
    </nav>

    <div class="p-4 border-t border-slate-800 shrink-0 mt-auto">
      <button
          @click="handleLogout"
          class="w-full flex items-center px-4 py-3 rounded-xl text-slate-400 hover:bg-red-500/10 hover:text-red-500 transition-all duration-200 font-medium text-sm group"
      >
        <svg
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            stroke-width="2"
            stroke="currentColor"
            class="w-5 h-5 mr-3 transition-transform group-hover:-translate-x-1"
        >
          <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 9V5.25A2.25 2.25 0 0013.5 3h-6a2.25 2.25 0 00-2.25 2.25v13.5A2.25 2.25 0 007.5 21h6a2.25 2.25 0 002.25-2.25V15M12 9l-3 3m0 0l3 3m-3-3h12.75" />
        </svg>
        Logout
      </button>
    </div>
  </aside>
</template>

<script setup>
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()

const handleLogout = () => {
  localStorage.removeItem('token')

  delete axios.defaults.headers.common['Authorization']

  router.push('/login')
}
</script>

<style scoped>
@reference "@/assets/main.css";

.nav-link {
  @apply flex items-center px-4 py-2.5 rounded-xl transition-all duration-200 hover:bg-slate-800 hover:text-white font-medium text-sm;
}

.router-link-exact-active {
  @apply bg-blue-600 text-white shadow-lg shadow-blue-500/20;
}
</style>
```

## `components/CustomPromptTemplate.vue`

```vue
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
```

## `components/DatasetUpload.vue`

```vue
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
```

## `components/DatasetsList.vue`

```vue
<template>
  <div class="bg-white rounded-[2rem] shadow-sm border border-slate-100 overflow-hidden">
    <div class="px-8 py-6 border-b border-slate-50 flex items-center justify-between bg-slate-50/30">
      <h2 class="text-xl font-black text-slate-800 tracking-tight">Available Datasets</h2>
      <button @click="$emit('refresh')" class="text-sm font-bold text-blue-500 hover:text-blue-700 transition-colors">
        Refresh
      </button>
    </div>

    <div class="overflow-x-auto">
      <table class="w-full text-left border-collapse">
        <thead>
        <tr class="bg-slate-50 text-slate-400 text-xs uppercase tracking-widest border-b border-slate-100">
          <th class="px-6 py-4 font-black">ID</th>
          <th class="px-6 py-4 font-black">Name</th>
          <th class="px-6 py-4 font-black">Format</th>
          <th class="px-6 py-4 font-black text-right">Actions</th>
        </tr>
        </thead>
        <tbody class="divide-y divide-slate-100">
        <tr v-if="isLoading" class="text-center">
          <td colspan="5" class="py-8 text-slate-400 font-medium">Loading datasets...</td>
        </tr>
        <tr v-else-if="datasets.length === 0" class="text-center">
          <td colspan="5" class="py-8 text-slate-400 font-medium">No datasets found. Please upload one.</td>
        </tr>
        <tr v-for="dataset in datasets" :key="dataset.id" class="hover:bg-slate-50/50 transition-colors text-sm">
          <td class="px-6 py-4 font-mono font-bold text-slate-400">#{{ dataset.id }}</td>
          <td class="px-6 py-4 font-bold text-slate-800">
            <router-link
                :to="`/datasets/${dataset.id}`"
                class="hover:text-blue-600 hover:underline flex items-center gap-1.5 transition-colors w-fit group"
            >
              {{ dataset.name }}
              <svg class="w-3.5 h-3.5 text-slate-300 group-hover:text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
              </svg>
            </router-link>
          </td>
          <td class="px-6 py-4 font-bold text-blue-600 uppercase">{{ dataset.file_format }}</td>
          <td class="px-6 py-4 text-right">
            <button @click="$emit('delete', dataset.id)" class="text-red-500 hover:text-red-700 font-bold px-3 py-1 bg-red-50 hover:bg-red-100 rounded-lg transition-colors">
              Delete
            </button>
          </td>
        </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
defineProps({
  datasets: {
    type: Array,
    required: true
  },
  isLoading: {
    type: Boolean,
    default: false
  }
})

defineEmits(['refresh', 'delete'])
</script>
```

## `components/DiskUsageCard.vue`

```vue
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
```

## `components/EvaluateModelView.vue`

```vue
<template>
  <div class="max-w-4xl mx-auto space-y-8 pb-20 p-6">
    <div class="flex items-center mb-6">
      <button @click="$router.push('/')" class="text-sm font-bold text-slate-500 hover:text-slate-800 flex items-center gap-2">
        <span>&larr;</span> {{ t('evaluation.backToTable') }}
      </button>
    </div>

    <div>
      <h1 class="text-3xl font-black text-slate-900 tracking-tight">{{ t('evaluation.pageTitle') }}</h1>
      <p class="text-slate-500 font-medium mt-1">{{ t('evaluation.pageSubtitle') }}</p>
    </div>

    <div class="bg-white p-8 rounded-[2rem] shadow-sm border border-slate-100">
      <h2 class="text-xl font-black text-slate-800 mb-6 flex items-center gap-3">
        {{ t('evaluation.parametersHeader') }}
      </h2>

      <div v-if="isLoading" class="text-slate-500 font-medium animate-pulse">
        {{ t('evaluation.loadingData') }}
      </div>

      <div v-else class="space-y-6">

        <div class="flex flex-col gap-2">
          <label class="text-xs font-black text-slate-400 uppercase tracking-widest">
            {{ t('evaluation.selectedModel') }}
          </label>
          <select
              v-model="selectedModelId"
              class="px-4 py-3 rounded-xl bg-slate-50 border border-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500 font-medium text-slate-700 cursor-pointer"
          >
            <option value="" disabled>-- Select a model for testing --</option>
            <option v-for="model in models" :key="model.id" :value="model.id">
              {{ model.name }} (ID: {{ model.id }})
            </option>
          </select>
        </div>

        <div class="flex flex-col gap-2">
          <label class="text-xs font-black text-slate-400 uppercase tracking-widest">
            {{ t('evaluation.selectDatasetLabel') }}
          </label>
          <select
              v-model="selectedDatasetId"
              class="px-4 py-3 rounded-xl bg-slate-50 border border-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500 font-medium text-slate-700 cursor-pointer"
          >
            <option value="" disabled>{{ t('evaluation.selectDatasetPlaceholder') }}</option>
            <option v-for="dataset in datasets" :key="dataset.id" :value="dataset.id">
              {{ dataset.name }} ({{ t('evaluation.formatLabel') }}: {{ dataset.file_format }})
            </option>
          </select>
          <p v-if="datasets.length === 0" class="text-sm text-orange-500 font-medium mt-1">
            {{ t('evaluation.noDatasetsText') }}
          </p>
        </div>

        <div v-if="errorMessage" class="p-4 bg-red-50 text-red-700 rounded-xl font-medium text-sm border border-red-100">
          {{ errorMessage }}
        </div>

        <button
            @click="startEvaluation"
            :disabled="!selectedDatasetId || !selectedModelId || isSubmitting"
            class="w-full py-4 bg-blue-600 text-white rounded-2xl font-black shadow-lg shadow-blue-600/20 hover:bg-blue-700 disabled:bg-slate-300 transition-all flex items-center justify-center mt-4"
        >
          <span v-if="isSubmitting" class="animate-spin inline-block mr-2">⏳</span>
          {{ isSubmitting ? t('evaluation.startingTest') : t('evaluation.startTestBtn') }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import axios from 'axios'

const router = useRouter()
const { t } = useI18n()
const API_URL = import.meta.env.VITE_API_URL || ''

const models = ref([])
const datasets = ref([])

const selectedModelId = ref('')
const selectedDatasetId = ref('')

const isLoading = ref(true)
const isSubmitting = ref(false)
const errorMessage = ref('')

const fetchData = async () => {
  isLoading.value = true
  errorMessage.value = ''

  try {
    const token = localStorage.getItem('token')
    const config = { headers: { 'Authorization': `Bearer ${token}` } }

    const datasetsRes = await axios.get(`${API_URL}/datasets/`, config)
    datasets.value = datasetsRes.data

    const modelsRes = await axios.get(`${API_URL}/models/?size=100`, config)
    models.value = modelsRes.data.items

  } catch (error) {
    console.error(error)
    errorMessage.value = t('evaluation.fetchError')
  } finally {
    isLoading.value = false
  }
}

const startEvaluation = async () => {
  if (!selectedDatasetId.value || !selectedModelId.value) return

  isSubmitting.value = true
  errorMessage.value = ''

  try {
    const token = localStorage.getItem('token')

    await axios.post(
        `${API_URL}/evaluations/create`,
        {
          dataset_id: selectedDatasetId.value,
          model_id: selectedModelId.value
        },
        {
          headers: { 'Authorization': `Bearer ${token}` }
        }
    )

    router.push('/evaluations')
  } catch (error) {
    errorMessage.value = error.response?.data?.detail || t('evaluation.startError')
  } finally {
    isSubmitting.value = false
  }
}

onMounted(() => {
  fetchData()
})
</script>
```

## `components/EvaluationJudgeSelector.vue`

```vue
<template>
  <div class="flex flex-col gap-2 mb-6">
    <label class="text-xs font-black text-slate-400 uppercase tracking-widest">Select Judges (Optional)</label>
    <div class="p-4 rounded-xl bg-slate-50 border border-slate-200 min-h-[60px]">

      <p v-if="isLoading" class="text-sm text-blue-500 font-medium animate-pulse">
        Loading judges from API...
      </p>

      <p v-else-if="error" class="text-sm text-red-500 font-medium mb-3">
        {{ error }}
      </p>

      <div v-else-if="judges.length > 0" class="flex flex-col gap-3">
        <label v-for="judge in judges" :key="judge.id" class="flex items-center gap-3 cursor-pointer group">
          <input
              type="checkbox"
              :value="judge.id"
              :checked="modelValue.includes(judge.id)"
              @change="updateSelection(judge.id, $event.target.checked)"
              class="w-5 h-5 text-blue-600 bg-white border-slate-300 rounded focus:ring-blue-500 focus:ring-2"
          />
          <span class="font-medium text-slate-700 group-hover:text-slate-900">{{ judge.name }}</span>
        </label>
      </div>

      <p v-else class="text-sm text-slate-500 font-medium">
        No judges available in the system.
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const props = defineProps({
  modelValue: {
    type: Array,
    default: () => []
  },
  apiUrl: {
    type: String,
    required: true
  }
})

const emit = defineEmits(['update:modelValue'])

const judges = ref([])
const isLoading = ref(false)
const error = ref('')

const fetchJudges = async () => {
  isLoading.value = true
  error.value = ''

  try {
    const token = localStorage.getItem('token')
    const response = await axios.get(`${props.apiUrl}/llm/judges/`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })

    judges.value = Array.isArray(response.data)
        ? response.data
        : (response.data?.items || response.data?.data || [])

  } catch (err) {
    console.error('Failed to fetch judges from API:', err)
    error.value = 'API failed. Using hardcoded mock list for testing.'

    judges.value = [
      { id: 1, name: 'LLM as a Judge (Qwen 2.5 Coder)' },
      { id: 2, name: 'Accuracy Evaluator (Rule-based)' },
      { id: 3, name: 'Toxicity Checker' }
    ]
  } finally {
    isLoading.value = false
  }
}

const updateSelection = (id, checked) => {
  const updated = [...props.modelValue]
  if (checked) {
    updated.push(id)
  } else {
    const index = updated.indexOf(id)
    if (index > -1) updated.splice(index, 1)
  }
  emit('update:modelValue', updated)
}

onMounted(() => {
  fetchJudges()
})
</script>
```

## `components/EvaluationModeSelector.vue`

```vue
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
```

## `components/FileUploaderCard.vue`

```vue
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
```

## `components/HelloWorld.vue`

```vue
<script setup>
defineProps({
  msg: {
    type: String,
    required: true,
  },
})
</script>

<template>
  <div class="greetings">
    <h1 class="green">{{ msg }}</h1>
    <h3>
      You’ve successfully created a project with
      <a href="https://vite.dev/" target="_blank" rel="noopener">Vite</a> +
      <a href="https://vuejs.org/" target="_blank" rel="noopener">Vue 3</a>.
    </h3>
  </div>
</template>

<style scoped>
h1 {
  font-weight: 500;
  font-size: 2.6rem;
  position: relative;
  top: -10px;
}

h3 {
  font-size: 1.2rem;
}

.greetings h1,
.greetings h3 {
  text-align: center;
}

@media (min-width: 1024px) {
  .greetings h1,
  .greetings h3 {
    text-align: left;
  }
}
</style>

```

## `components/LoraAdapterSelector.vue`

```vue
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
```

## `components/LoraAdapterSetup.vue`

```vue
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
```

## `components/LoraAdapterUploader.vue`

```vue
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
```

## `components/LoraAdaptersTable.vue`

```vue
<template>
  <div>
    <div v-if="adapters.length === 0" class="py-12 flex flex-col items-center justify-center text-center">
      <div class="text-6xl mb-4 opacity-50">🔌</div>
      <h3 class="text-lg font-bold text-slate-700">No LoRA adapters found</h3>
      <p class="text-slate-500 mt-1">Upload your first adapter ZIP to see it here.</p>
    </div>

    <div v-else class="overflow-x-auto border border-slate-100 rounded-2xl overflow-hidden">
      <table class="w-full text-left border-collapse">
        <thead>
        <tr class="bg-slate-50 text-slate-500 text-sm border-b border-slate-100">
          <th class="p-4 font-semibold w-16">ID</th>
          <th class="p-4 font-semibold">Folder Name</th>
          <th class="p-4 font-semibold">Base Model</th>
          <th class="p-4 font-semibold text-right">Actions</th>
        </tr>
        </thead>
        <tbody>
        <tr
            v-for="(adapter, index) in adapters"
            :key="adapter.id"
            class="hover:bg-slate-50/50 transition-colors text-sm"
            :class="index !== adapters.length - 1 ? 'border-b border-slate-50' : ''"
        >
          <td class="p-4 font-mono font-bold text-slate-400">#{{ adapter.id }}</td>

          <td class="p-4 font-bold text-slate-800">
            {{ adapter.folder_name }}
          </td>

          <td class="p-4 text-slate-500 max-w-xs truncate" :title="adapter.base_model_name_or_path">
            {{ adapter.base_model_name_or_path || '—' }}
          </td>

          <td class="p-4 text-right space-x-2">
            <button
                @click="$emit('delete', adapter)"
                class="px-3 py-1.5 text-xs font-bold text-red-600 bg-red-50 hover:bg-red-100 rounded-lg transition-colors"
            >
              Delete
            </button>
          </td>
        </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  adapters: {
    type: Array,
    required: true
  }
})

const emit = defineEmits(['delete'])
</script>
```

## `components/LoraTasksList.vue`

```vue
<!-- Батьківський компонент (наприклад, EvaluationTasks.vue) -->
<template>
  <div class="w-full px-6 lg:px-8 space-y-6 mt-8 pb-20">
    <div class="flex items-center justify-between">
      <div>
        <h2 class="text-2xl font-black text-slate-900 tracking-tight">Evaluation Tasks</h2>
        <p class="text-slate-500 font-medium mt-1">Monitor the status of your LoRA adapter evaluations.</p>
      </div>
      <button @click="fetchTasks" class="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold rounded-xl transition-colors text-sm">
        Refresh List
      </button>
    </div>

    <div class="bg-white rounded-[2rem] shadow-sm border border-slate-100 overflow-hidden">

      <TasksTable
          :tasks="tasks"
          :is-loading="isLoading"
          :resolve-route="(id) => ({ name: 'LoraTaskResults', params: { id: id } })"
          @delete="deleteTask"
          @cancel="cancelTask"
      />

    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useLoraTasks } from '@/composables/useLoraTasks'
import TasksTable from '@/components/TasksTable.vue'

const API_URL = import.meta.env.VITE_API_URL || ''
const { tasks, isLoading, fetchTasks, deleteTask, cancelTask } = useLoraTasks(API_URL)

onMounted(() => {
  fetchTasks()
})
</script>
```

## `components/ModelsTable.vue`

```vue
<template>
  <div>
    <div v-if="models.length === 0" class="py-12 flex flex-col items-center justify-center text-center">
      <div class="text-6xl mb-4 opacity-50">🤖</div>
      <h3 class="text-lg font-bold text-slate-700">{{ t('modelsTable.noModels') }}</h3>
      <p class="text-slate-500 mt-1">{{ t('modelsTable.noModelsDesc') }}</p>
    </div>

    <div v-else class="overflow-x-auto border border-slate-100 rounded-2xl overflow-hidden">
      <table class="w-full text-left border-collapse">
        <thead>
        <tr class="bg-slate-50 text-slate-500 text-sm border-b border-slate-100">
          <th class="p-4 font-semibold w-16">ID</th>
          <th class="p-4 font-semibold">{{ t('modelsTable.name') }}</th>
          <th class="p-4 font-semibold">{{ t('modelsTable.description') }}</th>
          <th class="p-4 font-semibold">{{ t('modelsTable.createdAt') }}</th>
          <th class="p-4 font-semibold text-right">{{ t('modelsTable.actions') }}</th>
        </tr>
        </thead>
        <tbody>
        <tr
            v-for="(model, index) in models"
            :key="model.id"
            class="hover:bg-slate-50/50 transition-colors text-sm"
            :class="index !== models.length - 1 ? 'border-b border-slate-50' : ''"
        >
          <td class="p-4 font-mono font-bold text-slate-400">#{{ model.id }}</td>

          <td class="p-4 font-bold text-slate-800">
            <router-link :to="`/models/${model.id}`" class="hover:text-blue-600 hover:underline transition-colors">
              {{ model.name }}
            </router-link>
          </td>

          <td class="p-4 text-slate-500 max-w-xs truncate" :title="model.description">
            {{ model.description || '—' }}
          </td>

          <td class="p-4 text-slate-600 font-medium">
            {{ formatDate(model.created_at) }}
          </td>

          <td class="p-4 text-right space-x-2">
            <button
                @click="$emit('edit', model)"
                class="px-3 py-1.5 text-xs font-bold text-blue-600 bg-blue-50 hover:bg-blue-100 rounded-lg transition-colors"
            >
              {{ t('modelsTable.edit') }}
            </button>
            <button
                @click="$emit('delete', model)"
                class="px-3 py-1.5 text-xs font-bold text-red-600 bg-red-50 hover:bg-red-100 rounded-lg transition-colors"
            >
              {{ t('modelsTable.delete') }}
            </button>
          </td>
        </tr>
        </tbody>
      </table>
    </div>

    <div v-if="totalPages > 1" class="px-6 py-4 bg-slate-50/50 border-t border-slate-100 flex items-center justify-between mt-4 rounded-xl">
      <div class="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em]">
        {{ t('pagination.page') }} {{ currentPage }} / {{ totalPages }}
      </div>

      <div class="flex items-center gap-2">
        <button
            @click="$emit('page-change', currentPage - 1)"
            :disabled="currentPage === 1"
            class="p-2 rounded-xl border border-slate-200 bg-white hover:bg-slate-50 disabled:opacity-30 disabled:cursor-not-allowed transition-all shadow-sm"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" /></svg>
        </button>

        <div class="flex items-center gap-1">
          <button
              v-for="p in visiblePages" :key="p"
              @click="$emit('page-change', p)"
              class="w-8 h-8 rounded-lg text-[11px] font-black transition-all"
              :class="p === currentPage ? 'bg-blue-600 text-white shadow-lg shadow-blue-500/30' : 'bg-white border border-slate-100 text-slate-500 hover:bg-slate-50'"
          >
            {{ p }}
          </button>
        </div>

        <button
            @click="$emit('page-change', currentPage + 1)"
            :disabled="currentPage === totalPages"
            class="p-2 rounded-xl border border-slate-200 bg-white hover:bg-slate-50 disabled:opacity-30 disabled:cursor-not-allowed transition-all shadow-sm"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" /></svg>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const props = defineProps({
  models: { type: Array, required: true },
  currentPage: { type: Number, default: 1 },
  totalPages: { type: Number, default: 1 }
})

const emit = defineEmits(['edit', 'delete', 'page-change'])

const visiblePages = computed(() => {
  const pages = []
  for (let i = 1; i <= props.totalPages; i++) {
    pages.push(i)
  }
  return pages
})

const formatDate = (isoString) => {
  if (!isoString) return '—'
  const date = new Date(isoString)
  return date.toLocaleString('uk-UA', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>
```

## `components/RunsTable.vue`

```vue
<template>
  <div>
    <!-- Empty State -->
    <div v-if="evaluations.length === 0" class="py-12 flex flex-col items-center justify-center text-center">
      <div class="text-6xl mb-4 opacity-50">📁</div>
      <h3 class="text-lg font-bold text-slate-700">{{ t('runsTable.noEvaluationsTitle') || 'No Evaluations Found' }}</h3>
      <p class="text-slate-500 mt-1">{{ t('runsTable.noEvaluationsDesc') || 'Start your first evaluation to see the results here.' }}</p>
    </div>

    <!-- Table -->
    <div v-else class="overflow-x-auto">
      <table class="w-full text-left border-collapse">
        <thead>
        <tr class="bg-slate-50 text-slate-500 text-sm border-b border-slate-100">
          <th class="p-4 font-semibold rounded-tl-xl">{{ t('runsTable.name') || 'Evaluation Name' }}</th>
          <th class="p-4 font-semibold">{{ t('runsTable.status') || 'Status' }}</th>
          <th class="p-4 font-semibold">{{ t('runsTable.accuracy') || 'Accuracy' }}</th>
          <th class="p-4 font-semibold">{{ t('runsTable.precision') || 'Precision' }}</th>
          <th class="p-4 font-semibold">{{ t('runsTable.recall') || 'Recall' }}</th>
          <th class="p-4 font-semibold">{{ t('runsTable.f1Score') || 'F1 Score' }}</th>
          <th class="p-4 font-semibold">{{ t('runsTable.rocAuc') || 'ROC AUC' }}</th>
          <th class="p-4 font-semibold">{{ t('runsTable.confMatrix') || 'Matrix' }}</th>
          <th class="p-4 font-semibold text-right rounded-tr-xl">{{ t('runsTable.action') || 'Action' }}</th>
        </tr>
        </thead>
        <tbody>
        <tr
            v-for="evaluation in evaluations"
            :key="evaluation.id"
            class="border-b border-slate-50 hover:bg-slate-50/50 transition-colors group text-sm"
        >
          <td class="p-4 font-bold text-slate-800">
            <router-link
                :to="`/evaluations/${evaluation.id}`"
                class="hover:text-blue-600 hover:underline transition-colors flex items-center gap-1.5 w-fit"
            >
              {{ evaluation.name || `Evaluation #${evaluation.id}` }}
              <svg class="w-3.5 h-3.5 text-slate-300 group-hover:text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
              </svg>
            </router-link>
          </td>

          <td class="p-4">
            <div class="flex flex-col items-start gap-1">
              <span
                  class="flex items-center px-3 py-1 text-[10px] font-black uppercase tracking-wider rounded-full"
                  :class="[getStatusData(evaluation.status).bgClass, getStatusData(evaluation.status).textClass]"
              >
                <svg v-if="getStatusData(evaluation.status).isSpinning" class="animate-spin -ml-1 mr-2 h-3 w-3" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>

                {{ t(getStatusData(evaluation.status).labelKey) || getStatusData(evaluation.status).fallbackLabel }}
              </span>

              <span
                  v-if="evaluation.status?.toLowerCase() === 'failed' && evaluation.error_message"
                  class="text-[10px] text-red-500 max-w-[150px] truncate cursor-help"
                  :title="evaluation.error_message"
              >
                {{ evaluation.error_message }}
              </span>
            </div>
          </td>

          <td class="p-4 text-slate-600 font-mono font-bold">{{ evaluation.metrics ? (evaluation.metrics.accuracy * 100).toFixed(1) + '%' : '—' }}</td>
          <td class="p-4 text-slate-600 font-mono font-bold">{{ evaluation.metrics ? (evaluation.metrics.precision * 100).toFixed(1) + '%' : '—' }}</td>
          <td class="p-4 text-slate-600 font-mono font-bold">{{ evaluation.metrics ? (evaluation.metrics.recall * 100).toFixed(1) + '%' : '—' }}</td>
          <td class="p-4 text-slate-600 font-mono font-bold">{{ evaluation.metrics ? (evaluation.metrics.f1_score * 100).toFixed(1) + '%' : '—' }}</td>
          <td class="p-4 text-slate-600 font-mono font-bold">{{ evaluation.metrics ? (evaluation.metrics.roc_auc * 100).toFixed(1) + '%' : '—' }}</td>

          <td class="p-4">
            <div v-if="evaluation.metrics" class="flex flex-col gap-1">
              <div class="grid grid-cols-2 gap-px w-14 bg-slate-200 border border-slate-200 rounded overflow-hidden shadow-sm">
                <div title="TN (True Negative)" class="bg-white text-[9px] text-center p-0.5 text-slate-400">{{ evaluation.metrics.tn }}</div>
                <div title="FP (False Positive)" class="bg-red-50 text-[9px] text-center p-0.5 text-red-600 font-bold">{{ evaluation.metrics.fp }}</div>
                <div title="FN (False Negative)" class="bg-orange-50 text-[9px] text-center p-0.5 text-orange-600 font-bold">{{ evaluation.metrics.fn }}</div>
                <div title="TP (True Positive)" class="bg-green-50 text-[9px] text-center p-0.5 text-green-600 font-bold">{{ evaluation.metrics.tp }}</div>
              </div>
            </div>
            <span v-else class="text-slate-300">—</span>
          </td>

          <!-- Actions -->
          <td class="p-4 text-right">
            <div v-if="!getStatusData(evaluation.status).isActive" class="flex items-center justify-end gap-2">
              <button
                  @click="$emit('reevaluate', evaluation.id)"
                  class="text-xs font-black py-2 px-4 rounded-xl transition-all shadow-sm active:scale-95 whitespace-nowrap bg-blue-50 hover:bg-blue-600 hover:text-white text-blue-600"
              >
                {{ t('runsTable.reevaluate') || 'Reevaluate' }}
              </button>

              <button
                  @click="$emit('delete', evaluation.id)"
                  class="text-xs font-black py-2 px-4 rounded-xl transition-all shadow-sm active:scale-95 whitespace-nowrap bg-red-50 hover:bg-red-600 hover:text-white text-red-600"
              >
                {{ t('common.delete') || 'Delete' }}
              </button>
            </div>

            <div v-else class="flex items-center justify-end gap-3">
              <div class="flex items-center text-blue-500 text-xs font-black animate-pulse">
                <svg class="animate-spin h-3 w-3 mr-1" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                {{ t(getStatusData(evaluation.status).labelKey).toUpperCase() || getStatusData(evaluation.status).fallbackLabel.toUpperCase() }}
              </div>

              <button
                  @click="$emit('cancel', evaluation.id)"
                  class="text-xs font-black py-2 px-3 rounded-xl transition-all shadow-sm active:scale-95 whitespace-nowrap bg-orange-50 hover:bg-orange-500 hover:text-white text-orange-600"
              >
                {{ t('common.cancel') || 'Cancel' }}
              </button>
            </div>
          </td>
        </tr>
        </tbody>
      </table>
    </div>

    <!-- Pagination -->
    <div v-if="totalPages > 1" class="px-6 py-4 bg-slate-50/50 border-t border-slate-100 flex items-center justify-between">
      <div class="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em]">
        {{ t('pagination.page') || 'Сторінка' }} {{ currentPage }} / {{ totalPages }}
      </div>
      <div class="flex items-center gap-2">
        <button
            @click="$emit('page-change', currentPage - 1)"
            :disabled="currentPage === 1"
            class="p-2 rounded-xl border border-slate-200 bg-white hover:bg-slate-50 disabled:opacity-30 disabled:cursor-not-allowed transition-all shadow-sm"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" /></svg>
        </button>

        <div class="flex items-center gap-1">
          <button
              v-for="p in visiblePages" :key="p"
              @click="$emit('page-change', p)"
              class="w-8 h-8 rounded-lg text-[11px] font-black transition-all"
              :class="p === currentPage ? 'bg-blue-600 text-white shadow-lg shadow-blue-500/30' : 'bg-white border border-slate-100 text-slate-500 hover:bg-slate-50'"
          >
            {{ p }}
          </button>
        </div>

        <button
            @click="$emit('page-change', currentPage + 1)"
            :disabled="currentPage === totalPages"
            class="p-2 rounded-xl border border-slate-200 bg-white hover:bg-slate-50 disabled:opacity-30 disabled:cursor-not-allowed transition-all shadow-sm"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" /></svg>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { getStatusData } from '@/constants/evaluationStatuses'

const { t } = useI18n()

const props = defineProps({
  evaluations: { type: Array, required: true },
  currentPage: { type: Number, default: 1 },
  totalPages: { type: Number, default: 1 }
})

const emit = defineEmits(['page-change', 'reevaluate', 'delete', 'cancel'])

const visiblePages = computed(() => {
  const pages = []
  for (let i = 1; i <= props.totalPages; i++) {
    pages.push(i)
  }
  return pages
})
</script>
```

## `components/StatCard.vue`

```vue
<template>
  <div class="bg-white rounded-lg shadow-sm p-6 border border-gray-100 flex items-center">
    <div :class="['w-12 h-12 rounded-full flex items-center justify-center mr-4 text-xl', iconBgClass, iconTextClass]">
      {{ icon }}
    </div>
    <div>
      <p class="text-xs text-gray-500 uppercase tracking-wide">{{ title }}</p>
      <p class="text-2xl font-semibold text-gray-800">{{ value }}</p>
    </div>
  </div>
</template>

<script setup>
defineProps({
  title: String,
  value: [String, Number],
  icon: String,
  iconBgClass: String,
  iconTextClass: String
})
</script>
```

## `components/TasksTable.vue`

```vue
<template>
  <div class="overflow-x-auto">
    <table class="w-full text-left border-collapse">
      <thead>
      <tr class="bg-slate-50 border-b border-slate-100">
        <th class="px-6 py-4 text-xs font-black text-slate-400 uppercase tracking-widest">ID</th>
        <th class="px-6 py-4 text-xs font-black text-slate-400 uppercase tracking-widest">Name</th>
        <th class="px-6 py-4 text-xs font-black text-slate-400 uppercase tracking-widest">Status</th>
        <th class="px-6 py-4 text-xs font-black text-slate-400 uppercase tracking-widest">Result / Error</th>
        <th class="px-6 py-4 text-xs font-black text-slate-400 uppercase tracking-widest text-right">Date Created</th>
        <th class="px-6 py-4 text-xs font-black text-slate-400 uppercase tracking-widest text-right">Actions</th>
      </tr>
      </thead>
      <tbody class="divide-y divide-slate-100">
      <tr v-if="isLoading && tasks.length === 0">
        <td colspan="6" class="px-6 py-8 text-center text-slate-400 font-medium">Loading tasks...</td>
      </tr>
      <tr v-else-if="tasks.length === 0">
        <td colspan="6" class="px-6 py-8 text-center text-slate-400 font-medium">No tasks found. Start an evaluation first.</td>
      </tr>

      <tr v-for="task in tasks" :key="task.id" class="hover:bg-slate-50 transition-colors">
        <td class="px-6 py-4">
          <router-link
              :to="resolveRoute(task.id)"
              class="font-mono text-sm text-slate-500 hover:text-blue-600 transition-colors"
              title="View Details"
          >
            {{ task.id }}
          </router-link>
        </td>

        <td class="px-6 py-4">
          <router-link
              :to="resolveRoute(task.id)"
              class="group flex flex-col w-fit"
          >
            <div class="font-bold text-slate-800 group-hover:text-blue-600 flex items-center gap-1.5 transition-colors">
              {{ task.name || 'Unnamed Task' }}
              <svg class="w-3.5 h-3.5 text-slate-300 group-hover:text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
              </svg>
            </div>
            <span v-if="task.description" class="text-xs text-slate-500 mt-0.5 truncate max-w-[200px]" :title="task.description">
              {{ task.description }}
            </span>
          </router-link>
        </td>

        <td class="px-6 py-4">
          <span
              class="px-3 py-1 text-xs font-bold rounded-full uppercase tracking-wide inline-flex items-center"
              :class="[getStatusData(task.status)?.bgClass, getStatusData(task.status)?.textClass]"
          >
            <span v-if="getStatusData(task.status)?.isActive" class="inline-block animate-pulse mr-1">●</span>
            {{ getStatusData(task.status)?.fallbackLabel || task.status }}
          </span>
        </td>

        <td class="px-6 py-4 text-sm font-medium text-slate-700 max-w-md truncate">
          <span v-if="task.status === 'completed'" class="text-slate-700" :title="task.result">
            {{ task.result }}
          </span>
          <span v-else-if="task.status === 'failed'" class="text-red-500" :title="task.error_message">
                {{ task.error_message }}
              </span>
          <span v-else class="text-slate-400 italic">Waiting for completion...</span>
        </td>

        <td class="px-6 py-4 text-sm font-medium text-slate-600 whitespace-nowrap text-right">
          {{ formatDate(task.created_at) }}
        </td>

        <td class="px-6 py-4 text-right">
          <div v-if="!getStatusData(task.status)?.isActive" class="flex justify-end gap-2">
            <button
                @click="$emit('delete', task.id)"
                class="text-red-600 hover:text-red-800 font-bold text-xs bg-red-50 hover:bg-red-100 px-3 py-2 rounded-lg transition-colors"
                title="Remove this task"
            >
              Delete
            </button>
          </div>
          <div v-else class="flex justify-end">
            <button
                @click="$emit('cancel', task.id)"
                class="text-orange-600 hover:text-orange-800 font-bold text-xs bg-orange-50 hover:bg-orange-100 px-3 py-2 rounded-lg transition-colors"
                title="Cancel this running evaluation"
            >
              Cancel
            </button>
          </div>
        </td>
      </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue'
import { getStatusData } from "@/constants/evaluationStatuses.js"

const props = defineProps({
  tasks: {
    type: Array,
    required: true,
    default: () => []
  },
  isLoading: {
    type: Boolean,
    default: false
  },
  resolveRoute: {
    type: Function,
    default: (id) => `/lora-tasks/${id}/results`
  }
})

const emit = defineEmits(['delete', 'cancel'])

const formatDate = (isoString) => {
  if (!isoString) return '—'
  const date = new Date(isoString)
  return date.toLocaleString('en-GB', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>
```

## `components/TheWelcome.vue`

```vue
<script setup>
import WelcomeItem from './WelcomeItem.vue'
import DocumentationIcon from './icons/IconDocumentation.vue'
import ToolingIcon from './icons/IconTooling.vue'
import EcosystemIcon from './icons/IconEcosystem.vue'
import CommunityIcon from './icons/IconCommunity.vue'
import SupportIcon from './icons/IconSupport.vue'

const openReadmeInEditor = () => fetch('/__open-in-editor?file=README.md')
</script>

<template>
  <WelcomeItem>
    <template #icon>
      <DocumentationIcon />
    </template>
    <template #heading>Documentation</template>

    Vue’s
    <a href="https://vuejs.org/" target="_blank" rel="noopener">official documentation</a>
    provides you with all information you need to get started.
  </WelcomeItem>

  <WelcomeItem>
    <template #icon>
      <ToolingIcon />
    </template>
    <template #heading>Tooling</template>

    This project is served and bundled with
    <a href="https://vite.dev/guide/features.html" target="_blank" rel="noopener">Vite</a>. The
    recommended IDE setup is
    <a href="https://code.visualstudio.com/" target="_blank" rel="noopener">VSCode</a>
    +
    <a href="https://github.com/vuejs/language-tools" target="_blank" rel="noopener"
      >Vue - Official</a
    >. If you need to test your components and web pages, check out
    <a href="https://vitest.dev/" target="_blank" rel="noopener">Vitest</a>
    and
    <a href="https://www.cypress.io/" target="_blank" rel="noopener">Cypress</a>
    /
    <a href="https://playwright.dev/" target="_blank" rel="noopener">Playwright</a>.

    <br />

    More instructions are available in
    <a href="javascript:void(0)" @click="openReadmeInEditor"><code>README.md</code></a
    >.
  </WelcomeItem>

  <WelcomeItem>
    <template #icon>
      <EcosystemIcon />
    </template>
    <template #heading>Ecosystem</template>

    Get official tools and libraries for your project:
    <a href="https://pinia.vuejs.org/" target="_blank" rel="noopener">Pinia</a>,
    <a href="https://router.vuejs.org/" target="_blank" rel="noopener">Vue Router</a>,
    <a href="https://test-utils.vuejs.org/" target="_blank" rel="noopener">Vue Test Utils</a>, and
    <a href="https://github.com/vuejs/devtools" target="_blank" rel="noopener">Vue Dev Tools</a>. If
    you need more resources, we suggest paying
    <a href="https://github.com/vuejs/awesome-vue" target="_blank" rel="noopener">Awesome Vue</a>
    a visit.
  </WelcomeItem>

  <WelcomeItem>
    <template #icon>
      <CommunityIcon />
    </template>
    <template #heading>Community</template>

    Got stuck? Ask your question on
    <a href="https://chat.vuejs.org" target="_blank" rel="noopener">Vue Land</a>
    (our official Discord server), or
    <a href="https://stackoverflow.com/questions/tagged/vue.js" target="_blank" rel="noopener"
      >StackOverflow</a
    >. You should also follow the official
    <a href="https://bsky.app/profile/vuejs.org" target="_blank" rel="noopener">@vuejs.org</a>
    Bluesky account or the
    <a href="https://x.com/vuejs" target="_blank" rel="noopener">@vuejs</a>
    X account for latest news in the Vue world.
  </WelcomeItem>

  <WelcomeItem>
    <template #icon>
      <SupportIcon />
    </template>
    <template #heading>Support Vue</template>

    As an independent project, Vue relies on community backing for its sustainability. You can help
    us by
    <a href="https://vuejs.org/sponsor/" target="_blank" rel="noopener">becoming a sponsor</a>.
  </WelcomeItem>
</template>

```

## `components/WelcomeItem.vue`

```vue
<template>
  <div class="item">
    <i>
      <slot name="icon"></slot>
    </i>
    <div class="details">
      <h3>
        <slot name="heading"></slot>
      </h3>
      <slot></slot>
    </div>
  </div>
</template>

<style scoped>
.item {
  margin-top: 2rem;
  display: flex;
  position: relative;
}

.details {
  flex: 1;
  margin-left: 1rem;
}

i {
  display: flex;
  place-items: center;
  place-content: center;
  width: 32px;
  height: 32px;

  color: var(--color-text);
}

h3 {
  font-size: 1.2rem;
  font-weight: 500;
  margin-bottom: 0.4rem;
  color: var(--color-heading);
}

@media (min-width: 1024px) {
  .item {
    margin-top: 0;
    padding: 0.4rem 0 1rem calc(var(--section-gap) / 2);
  }

  i {
    top: calc(50% - 25px);
    left: -26px;
    position: absolute;
    border: 1px solid var(--color-border);
    background: var(--color-background);
    border-radius: 8px;
    width: 50px;
    height: 50px;
  }

  .item:before {
    content: ' ';
    border-left: 1px solid var(--color-border);
    position: absolute;
    left: 0;
    bottom: calc(50% + 25px);
    height: calc(50% - 25px);
  }

  .item:after {
    content: ' ';
    border-left: 1px solid var(--color-border);
    position: absolute;
    left: 0;
    top: calc(50% + 25px);
    height: calc(50% - 25px);
  }

  .item:first-of-type:before {
    display: none;
  }

  .item:last-of-type:after {
    display: none;
  }
}
</style>

```

## `components/icons/IconCommunity.vue`

```vue
<template>
  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor">
    <path
      d="M15 4a1 1 0 1 0 0 2V4zm0 11v-1a1 1 0 0 0-1 1h1zm0 4l-.707.707A1 1 0 0 0 16 19h-1zm-4-4l.707-.707A1 1 0 0 0 11 14v1zm-4.707-1.293a1 1 0 0 0-1.414 1.414l1.414-1.414zm-.707.707l-.707-.707.707.707zM9 11v-1a1 1 0 0 0-.707.293L9 11zm-4 0h1a1 1 0 0 0-1-1v1zm0 4H4a1 1 0 0 0 1.707.707L5 15zm10-9h2V4h-2v2zm2 0a1 1 0 0 1 1 1h2a3 3 0 0 0-3-3v2zm1 1v6h2V7h-2zm0 6a1 1 0 0 1-1 1v2a3 3 0 0 0 3-3h-2zm-1 1h-2v2h2v-2zm-3 1v4h2v-4h-2zm1.707 3.293l-4-4-1.414 1.414 4 4 1.414-1.414zM11 14H7v2h4v-2zm-4 0c-.276 0-.525-.111-.707-.293l-1.414 1.414C5.42 15.663 6.172 16 7 16v-2zm-.707 1.121l3.414-3.414-1.414-1.414-3.414 3.414 1.414 1.414zM9 12h4v-2H9v2zm4 0a3 3 0 0 0 3-3h-2a1 1 0 0 1-1 1v2zm3-3V3h-2v6h2zm0-6a3 3 0 0 0-3-3v2a1 1 0 0 1 1 1h2zm-3-3H3v2h10V0zM3 0a3 3 0 0 0-3 3h2a1 1 0 0 1 1-1V0zM0 3v6h2V3H0zm0 6a3 3 0 0 0 3 3v-2a1 1 0 0 1-1-1H0zm3 3h2v-2H3v2zm1-1v4h2v-4H4zm1.707 4.707l.586-.586-1.414-1.414-.586.586 1.414 1.414z"
    />
  </svg>
</template>

```

## `components/icons/IconDocumentation.vue`

```vue
<template>
  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="17" fill="currentColor">
    <path
      d="M11 2.253a1 1 0 1 0-2 0h2zm-2 13a1 1 0 1 0 2 0H9zm.447-12.167a1 1 0 1 0 1.107-1.666L9.447 3.086zM1 2.253L.447 1.42A1 1 0 0 0 0 2.253h1zm0 13H0a1 1 0 0 0 1.553.833L1 15.253zm8.447.833a1 1 0 1 0 1.107-1.666l-1.107 1.666zm0-14.666a1 1 0 1 0 1.107 1.666L9.447 1.42zM19 2.253h1a1 1 0 0 0-.447-.833L19 2.253zm0 13l-.553.833A1 1 0 0 0 20 15.253h-1zm-9.553-.833a1 1 0 1 0 1.107 1.666L9.447 14.42zM9 2.253v13h2v-13H9zm1.553-.833C9.203.523 7.42 0 5.5 0v2c1.572 0 2.961.431 3.947 1.086l1.107-1.666zM5.5 0C3.58 0 1.797.523.447 1.42l1.107 1.666C2.539 2.431 3.928 2 5.5 2V0zM0 2.253v13h2v-13H0zm1.553 13.833C2.539 15.431 3.928 15 5.5 15v-2c-1.92 0-3.703.523-5.053 1.42l1.107 1.666zM5.5 15c1.572 0 2.961.431 3.947 1.086l1.107-1.666C9.203 13.523 7.42 13 5.5 13v2zm5.053-11.914C11.539 2.431 12.928 2 14.5 2V0c-1.92 0-3.703.523-5.053 1.42l1.107 1.666zM14.5 2c1.573 0 2.961.431 3.947 1.086l1.107-1.666C18.203.523 16.421 0 14.5 0v2zm3.5.253v13h2v-13h-2zm1.553 12.167C18.203 13.523 16.421 13 14.5 13v2c1.573 0 2.961.431 3.947 1.086l1.107-1.666zM14.5 13c-1.92 0-3.703.523-5.053 1.42l1.107 1.666C11.539 15.431 12.928 15 14.5 15v-2z"
    />
  </svg>
</template>

```

## `components/icons/IconEcosystem.vue`

```vue
<template>
  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="20" fill="currentColor">
    <path
      d="M11.447 8.894a1 1 0 1 0-.894-1.789l.894 1.789zm-2.894-.789a1 1 0 1 0 .894 1.789l-.894-1.789zm0 1.789a1 1 0 1 0 .894-1.789l-.894 1.789zM7.447 7.106a1 1 0 1 0-.894 1.789l.894-1.789zM10 9a1 1 0 1 0-2 0h2zm-2 2.5a1 1 0 1 0 2 0H8zm9.447-5.606a1 1 0 1 0-.894-1.789l.894 1.789zm-2.894-.789a1 1 0 1 0 .894 1.789l-.894-1.789zm2 .789a1 1 0 1 0 .894-1.789l-.894 1.789zm-1.106-2.789a1 1 0 1 0-.894 1.789l.894-1.789zM18 5a1 1 0 1 0-2 0h2zm-2 2.5a1 1 0 1 0 2 0h-2zm-5.447-4.606a1 1 0 1 0 .894-1.789l-.894 1.789zM9 1l.447-.894a1 1 0 0 0-.894 0L9 1zm-2.447.106a1 1 0 1 0 .894 1.789l-.894-1.789zm-6 3a1 1 0 1 0 .894 1.789L.553 4.106zm2.894.789a1 1 0 1 0-.894-1.789l.894 1.789zm-2-.789a1 1 0 1 0-.894 1.789l.894-1.789zm1.106 2.789a1 1 0 1 0 .894-1.789l-.894 1.789zM2 5a1 1 0 1 0-2 0h2zM0 7.5a1 1 0 1 0 2 0H0zm8.553 12.394a1 1 0 1 0 .894-1.789l-.894 1.789zm-1.106-2.789a1 1 0 1 0-.894 1.789l.894-1.789zm1.106 1a1 1 0 1 0 .894 1.789l-.894-1.789zm2.894.789a1 1 0 1 0-.894-1.789l.894 1.789zM8 19a1 1 0 1 0 2 0H8zm2-2.5a1 1 0 1 0-2 0h2zm-7.447.394a1 1 0 1 0 .894-1.789l-.894 1.789zM1 15H0a1 1 0 0 0 .553.894L1 15zm1-2.5a1 1 0 1 0-2 0h2zm12.553 2.606a1 1 0 1 0 .894 1.789l-.894-1.789zM17 15l.447.894A1 1 0 0 0 18 15h-1zm1-2.5a1 1 0 1 0-2 0h2zm-7.447-5.394l-2 1 .894 1.789 2-1-.894-1.789zm-1.106 1l-2-1-.894 1.789 2 1 .894-1.789zM8 9v2.5h2V9H8zm8.553-4.894l-2 1 .894 1.789 2-1-.894-1.789zm.894 0l-2-1-.894 1.789 2 1 .894-1.789zM16 5v2.5h2V5h-2zm-4.553-3.894l-2-1-.894 1.789 2 1 .894-1.789zm-2.894-1l-2 1 .894 1.789 2-1L8.553.106zM1.447 5.894l2-1-.894-1.789-2 1 .894 1.789zm-.894 0l2 1 .894-1.789-2-1-.894 1.789zM0 5v2.5h2V5H0zm9.447 13.106l-2-1-.894 1.789 2 1 .894-1.789zm0 1.789l2-1-.894-1.789-2 1 .894 1.789zM10 19v-2.5H8V19h2zm-6.553-3.894l-2-1-.894 1.789 2 1 .894-1.789zM2 15v-2.5H0V15h2zm13.447 1.894l2-1-.894-1.789-2 1 .894 1.789zM18 15v-2.5h-2V15h2z"
    />
  </svg>
</template>

```

## `components/icons/IconSupport.vue`

```vue
<template>
  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor">
    <path
      d="M10 3.22l-.61-.6a5.5 5.5 0 0 0-7.666.105 5.5 5.5 0 0 0-.114 7.665L10 18.78l8.39-8.4a5.5 5.5 0 0 0-.114-7.665 5.5 5.5 0 0 0-7.666-.105l-.61.61z"
    />
  </svg>
</template>

```

## `components/icons/IconTooling.vue`

```vue
<!-- This icon is from <https://github.com/Templarian/MaterialDesign>, distributed under Apache 2.0 (https://www.apache.org/licenses/LICENSE-2.0) license-->
<template>
  <svg
    xmlns="http://www.w3.org/2000/svg"
    xmlns:xlink="http://www.w3.org/1999/xlink"
    aria-hidden="true"
    role="img"
    class="iconify iconify--mdi"
    width="24"
    height="24"
    preserveAspectRatio="xMidYMid meet"
    viewBox="0 0 24 24"
  >
    <path
      d="M20 18v-4h-3v1h-2v-1H9v1H7v-1H4v4h16M6.33 8l-1.74 4H7v-1h2v1h6v-1h2v1h2.41l-1.74-4H6.33M9 5v1h6V5H9m12.84 7.61c.1.22.16.48.16.8V18c0 .53-.21 1-.6 1.41c-.4.4-.85.59-1.4.59H4c-.55 0-1-.19-1.4-.59C2.21 19 2 18.53 2 18v-4.59c0-.32.06-.58.16-.8L4.5 7.22C4.84 6.41 5.45 6 6.33 6H7V5c0-.55.18-1 .57-1.41C7.96 3.2 8.44 3 9 3h6c.56 0 1.04.2 1.43.59c.39.41.57.86.57 1.41v1h.67c.88 0 1.49.41 1.83 1.22l2.34 5.39z"
      fill="currentColor"
    ></path>
  </svg>
</template>

```

## `composables/useDatasets.js`

```javascript
import { ref } from 'vue'
import axios from 'axios'

export function useDatasets(apiUrl) {
    const datasets = ref([])
    const isUploading = ref(false)

    const fetchDatasets = async () => {
        try {
            const token = localStorage.getItem('token')
            const response = await axios.get(`${apiUrl}/datasets/`, {
                headers: { 'Authorization': `Bearer ${token}` }
            })
            datasets.value = response.data
        } catch (error) {
            console.error("Failed to fetch datasets:", error)
        }
    }

    const uploadDataset = async (payload) => {
        isUploading.value = true
        try {
            const token = localStorage.getItem('token')
            const response = await axios.post(`${apiUrl}/datasets/`, payload, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                    'Authorization': `Bearer ${token}`
                }
            })
            return response.data
        } catch (error) {
            console.error("Failed to upload dataset:", error)
        } finally {
            isUploading.value = false
        }
    }

    return {
        datasets,
        isUploading,
        fetchDatasets,
        uploadDataset
    }
}
```

## `composables/useEvaluations.js`

```javascript
import { ref } from 'vue'
import axios from 'axios'

export function useEvaluations() {
    const evaluations = ref([])
    const currentPage = ref(1)
    const totalPages = ref(1)
    const isLoading = ref(false)

    const API_URL = import.meta.env.VITE_API_URL || ''

    const fetchEvaluations = async (page = 1) => {
        isLoading.value = true
        try {
            const response = await axios.get(`${API_URL}/evaluations/`, {
                params: { page, size: 10 }
            })
            evaluations.value = response.data.items
            totalPages.value = response.data.pages
            currentPage.value = response.data.page
        } catch (error) {
            console.error("Error fetching evaluations:", error)
        } finally {
            isLoading.value = false
        }
    }

    const triggerReevaluate = async (id) => {
        try {
            await axios.post(`${API_URL}/evaluations/${id}/re-evaluate`)
            await fetchEvaluations(currentPage.value)
        } catch (error) {
            console.error("Error reevaluating:", error)
            throw error
        }
    }

    const deleteEvaluation = async (id) => {
        try {
            await axios.delete(`${API_URL}/evaluations/${id}`)
            await fetchEvaluations(currentPage.value)
        } catch (error) {
            console.error("Error deleting evaluation:", error)
        }
    }

    const cancelEvaluation = async (id) => {
        try {
            await axios.post(`${API_URL}/evaluations/${id}/cancel`)

            await fetchEvaluations(currentPage.value)
        } catch (error) {
            console.error("Error cancelling evaluation:", error)
        }
    }

    return {
        evaluations,
        currentPage,
        totalPages,
        isLoading,
        fetchEvaluations,
        triggerReevaluate,
        deleteEvaluation,
        cancelEvaluation
    }
}
```

## `composables/useFileUpload.js`

```javascript
import { ref } from 'vue'
import axios from 'axios'
import { useI18n } from 'vue-i18n'

export function useFileUpload(apiUrl) {
    const { t } = useI18n()

    const isUploading = ref(false)
    const progress = ref(0)
    const asset = ref(null)

    const uploadFile = async (file) => {
        if (!file) return

        isUploading.value = true
        progress.value = 0
        const formData = new FormData()
        formData.append('file', file)

        try {
            const token = localStorage.getItem('token')

            const res = await axios.post(`${apiUrl}/upload-file/`, formData, {
                headers: {
                    'Authorization': `Bearer ${token}`
                },
                onUploadProgress: (progressEvent) => {
                    progress.value = Math.round((progressEvent.loaded * 100) / progressEvent.total)
                }
            })
            asset.value = res.data
        } catch (err) {
            alert(t('modelSetup.errorUpload') + ': ' + (err.response?.data?.detail || 'Server error'))
        } finally {
            isUploading.value = false
        }
    }

    return {
        isUploading,
        progress,
        asset,
        uploadFile
    }
}
```

## `composables/useLoraAdapter.js`

```javascript
import { ref } from 'vue'
import axios from 'axios'

export function useLoraAdapter(apiUrl) {
    const baseModelId = ref('')
    const isFetchingModel = ref(false)

    const fetchAdapterDetails = async (adapterId) => {
        if (!adapterId) {
            baseModelId.value = ''
            return
        }

        isFetchingModel.value = true
        try {
            const token = localStorage.getItem('token')
            const response = await axios.get(`${apiUrl}/llm/lora/adapters/${adapterId}`, {
                headers: { 'Authorization': `Bearer ${token}` }
            })
            baseModelId.value = response.data.base_model_name_or_path || ''
        } catch (error) {
            console.error("Failed to fetch adapter details from backend", error)
            baseModelId.value = ''
        } finally {
            isFetchingModel.value = false
        }
    }

    return {
        baseModelId,
        isFetchingModel,
        fetchAdapterDetails
    }
}
```

## `composables/useLoraAdaptersList.js`

```javascript
import { ref } from 'vue'
import axios from 'axios'

export function useLoraAdaptersList(apiUrl) {
    const availableAdapters = ref([])
    const isLoadingAdapters = ref(false)

    const fetchAdapters = async () => {
        isLoadingAdapters.value = true
        try {
            const response = await axios.get(`${apiUrl}/llm/lora/adapters/`)
            availableAdapters.value = response.data.adapters
        } catch (error) {
            console.error('Failed to fetch adapters:', error)
        } finally {
            isLoadingAdapters.value = false
        }
    }

    return {
        availableAdapters,
        isLoadingAdapters,
        fetchAdapters
    }
}
```

## `composables/useLoraEvaluation.js`

```javascript
import { ref } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'

export function useLoraEvaluation(apiUrl) {
    const router = useRouter()
    const isGenerating = ref(false)
    const generateError = ref('')

    const submitEvaluation = async (payload) => {
        isGenerating.value = true
        generateError.value = ''

        try {
            const token = localStorage.getItem('token')
            await axios.post(`${apiUrl}/llm/lora/evaluations/`, payload, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            })
            router.push('/lora-tasks')
        } catch (err) {
            generateError.value = err.response?.data?.detail || 'Failed to start evaluation task.'
        } finally {
            isGenerating.value = false
        }
    }

    return {
        isGenerating,
        generateError,
        submitEvaluation
    }
}
```

## `composables/useLoraTasks.js`

```javascript
import { ref, onUnmounted } from 'vue'
import axios from 'axios'

export function useLoraTasks(apiUrl) {
    const tasks = ref([])
    const isLoading = ref(true)
    let pollingInterval = null

    const getHeaders = () => {
        const token = localStorage.getItem('token')
        return token ? { 'Authorization': `Bearer ${token}` } : {}
    }

    const fetchTasks = async () => {
        try {
            const response = await axios.get(`${apiUrl}/llm/lora/evaluations/`, {
                headers: getHeaders()
            })

            console.log("API Response Data:", response.data)

            const fetchedTasks = response.data.tasks || response.data || []

            tasks.value = Array.isArray(fetchedTasks) ? fetchedTasks : []

            const hasProcessingTasks = tasks.value.some(task =>
                task.status === 'processing' || task.status === 'pending'
            )

            if (hasProcessingTasks && !pollingInterval) {
                startPolling()
            } else if (!hasProcessingTasks && pollingInterval) {
                stopPolling()
            }
        } catch (error) {
            console.error("Failed to fetch tasks:", error)
            tasks.value = []
        } finally {
            isLoading.value = false
        }
    }

    const deleteTask = async (taskId) => {
        if (!window.confirm("Are you sure you want to delete this task?")) {
            return
        }

        try {
            await axios.delete(`${apiUrl}/llm/lora/evaluations/${taskId}`, {
                headers: getHeaders()
            })
            await fetchTasks()
        } catch (error) {
            console.error("Failed to delete task:", error)
            alert("Could not delete the task. Please try again.")
        }
    }

    const cancelTask = async (taskId) => {
        if (!window.confirm("Are you sure you want to cancel this evaluation?")) {
            return
        }

        try {
            await axios.post(`${apiUrl}/llm/lora/evaluations/${taskId}/cancel`, {}, {
                headers: getHeaders()
            })

            await fetchTasks()
        } catch (error) {
            console.error("Failed to cancel task:", error)
            const errorMessage = error.response?.data?.detail || "Could not cancel the task. It may have already finished."
            alert(errorMessage)
        }
    }

    const startPolling = () => {
        if (!pollingInterval) {
            pollingInterval = setInterval(() => {
                fetchTasks()
            }, 3000)
        }
    }

    const stopPolling = () => {
        if (pollingInterval) {
            clearInterval(pollingInterval)
            pollingInterval = null
        }
    }

    onUnmounted(() => {
        stopPolling()
    })

    return {
        tasks,
        isLoading,
        fetchTasks,
        deleteTask,
        cancelTask
    }
}
```

## `composables/useLoraUpload.js`

```javascript
import { ref } from 'vue'
import axios from 'axios'

export function useLoraUpload(apiUrl) {
    const zipFile = ref(null)
    const isUploading = ref(false)
    const uploadMessage = ref('')
    const isUploadError = ref(false)

    const handleFileSelection = (event) => {
        const file = event.target.files[0]
        if (file && file.name.endsWith('.zip')) {
            zipFile.value = file
            uploadMessage.value = ''
            isUploadError.value = false
        } else {
            zipFile.value = null
            isUploadError.value = true
            uploadMessage.value = 'Please select a valid .zip file.'
        }
    }

    const uploadZipFile = async () => {
        if (!zipFile.value) return null

        isUploading.value = true
        uploadMessage.value = ''
        isUploadError.value = false

        const formData = new FormData()
        formData.append('file', zipFile.value)

        try {
            const token = localStorage.getItem('token')

            const response = await axios.post(`${apiUrl}/llm/lora/adapters/upload`, formData, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            })

            isUploadError.value = false
            uploadMessage.value = 'ZIP uploaded and extracted successfully!'
            const uploadedData = response.data

            zipFile.value = null

            return uploadedData

        } catch (err) {
            isUploadError.value = true
            uploadMessage.value = err.response?.data?.detail || 'Failed to upload and extract ZIP file.'
            return null
        } finally {
            isUploading.value = false
        }
    }

    return {
        zipFile,
        isUploading,
        uploadMessage,
        isUploadError,
        handleFileSelection,
        uploadZipFile
    }
}
```

## `composables/useModels.js`

```javascript
import { ref } from 'vue'
import axios from 'axios'

export function useModels(apiUrl) {
    const models = ref([])
    const currentPage = ref(1)
    const totalPages = ref(1)
    const isLoading = ref(false)

    const fetchModels = async (page = 1, size = 10) => {
        isLoading.value = true
        try {
            const response = await axios.get(`${apiUrl}/models/`, {
                params: {
                    page: page,
                    size: size
                }
            })

            models.value = response.data.items
            totalPages.value = response.data.pages
            currentPage.value = response.data.page
        } catch (error) {
            console.error("Error fetching models:", error)
            throw error
        } finally {
            isLoading.value = false
        }
    }

    const deleteModelById = async (modelId) => {
        try {
            await axios.delete(`${apiUrl}/models/${modelId}`)
            return true
        } catch (error) {
            console.error("Error deleting model:", error)
            throw error
        }
    }

    const updateModel = async (modelId, updateData) => {
        try {
            const response = await axios.patch(`${apiUrl}/models/${modelId}`, updateData)
            return response.data
        } catch (error) {
            console.error("Error updating model:", error)
            throw error
        }
    }

    return {
        models,
        currentPage,
        totalPages,
        isLoading,
        fetchModels,
        deleteModelById,
        updateModel
    }
}
```

## `constants/dataset.js`

```javascript
export const DatasetType = {
    NONE: 'none',
    CV: 'cv',
    LLM: 'llm'
};

export const DatasetSource = {
    LOCAL_FILE: 'local_file',
    DIRECT_URL: 'direct_url',
    KAGGLE: 'kaggle',
    HUGGING_FACE: 'hugging_face'
};

export const DatasetFormat = {
    NONE: 'none',
    CSV: 'csv',
    JSONL: 'jsonl',
    IMAGE_FOLDER: 'image_folder',
    ARROW: 'arrow'
};

export const TYPE_OPTIONS = [
    { value: DatasetType.NONE, label: 'None / Unspecified' },
    { value: DatasetType.CV, label: 'Computer Vision (CV)' },
    { value: DatasetType.LLM, label: 'Large Language Models (LLM)' }
];

export const SOURCE_OPTIONS = [
    { value: DatasetSource.LOCAL_FILE, label: 'Upload Local File' },
    { value: DatasetSource.DIRECT_URL, label: 'Direct URL' },
    { value: DatasetSource.HUGGING_FACE, label: 'Hugging Face' },
    { value: DatasetSource.KAGGLE, label: 'Kaggle' }
];

export const FORMAT_OPTIONS = [
    { value: DatasetFormat.CSV, label: 'CSV' },
    { value: DatasetFormat.JSONL, label: 'JSONL' },
    { value: DatasetFormat.IMAGE_FOLDER, label: 'Image Folder (ZIP)' },
    { value: DatasetFormat.ARROW, label: 'Arrow (Hugging Face)' },
    { value: DatasetFormat.NONE, label: 'None' }
];
```

## `constants/evaluationStatuses.js`

```javascript
export const STATUS_CONFIG = {
    completed: {
        bgClass: 'bg-green-100',
        textClass: 'text-green-700',
        labelKey: 'common.tested',
        fallbackLabel: 'Tested',
        isSpinning: false,
        isActive: false
    },
    evaluating: {
        bgClass: 'bg-blue-50',
        textClass: 'text-blue-600',
        labelKey: 'common.evaluating',
        fallbackLabel: 'Evaluating...',
        isSpinning: true,
        isActive: true
    },
    processing: {
        bgClass: 'bg-blue-50',
        textClass: 'text-blue-600',
        labelKey: 'common.processing',
        fallbackLabel: 'Processing...',
        isSpinning: true,
        isActive: true
    },
    downloading: {
        bgClass: 'bg-indigo-50',
        textClass: 'text-indigo-600',
        labelKey: 'common.downloading',
        fallbackLabel: 'Downloading...',
        isSpinning: true,
        isActive: true
    },
    failed: {
        bgClass: 'bg-red-100',
        textClass: 'text-red-700',
        labelKey: 'common.failed',
        fallbackLabel: 'Failed',
        isSpinning: false,
        isActive: false
    },
    pending: {
        bgClass: 'bg-slate-100',
        textClass: 'text-slate-500',
        labelKey: 'common.pending',
        fallbackLabel: 'Pending',
        isSpinning: false,
        isActive: false
    },
    none: {
        bgClass: 'bg-gray-100',
        textClass: 'text-gray-400',
        labelKey: 'common.none',
        fallbackLabel: 'None',
        isSpinning: false,
        isActive: false
    }
}

export const getStatusData = (status) => {
    const normalizedStatus = status?.toLowerCase()
    return STATUS_CONFIG[normalizedStatus] || STATUS_CONFIG.pending
}
```

## `i18n.js`

```javascript
import { createI18n } from 'vue-i18n'

const messages = {
    en: {
        common: {
            back: 'Back',
            loading: 'Loading...',
            delete: 'Delete',
            none: 'None',
            cancel: "Cancel",
            tested: 'Tested',
            evaluating: 'Evaluating...',
            processing: 'Processing...',
            downloading: 'Downloading...',
            failed: 'Failed',
            pending: 'Pending',
        },
        pagination: {
            page: 'Page',
        },
        header: {
            title: 'VisionMetrics Hub',
            logout: 'LOGOUT',
            online: 'Online',
            admin: 'Admin',
            pages: 'Pages',
            overview: 'Overview'
        },
        sidebar: {
            dashboard: 'Dashboard',
            models: 'AI Models',
            testRuns: 'Test Runs',
            settings: 'Settings',
            analytics: 'Analytics',
            logout: 'Logout'
        },
        auth: {
            username: 'Username',
            password: 'Password',
            login: 'Login',
            invalid: 'Invalid username or password'
        },
        dashboard: {
            title: 'Model Dashboard',
            subtitle: 'Monitor and evaluate your neural network performances',
            uploading: 'Uploading...',
            uploadBtn: 'Create New Model',
            historyTitle: 'Evaluation History',
            liveUpdates: 'Live Updates',
            stats: {
                total: 'Total Models',
                accuracy: 'Avg Accuracy',
                precision: 'Avg Precision',
                recall: 'Avg Recall',
                f1: 'Avg F1-Score',
                roc: 'Avg ROC AUC',
            },
            storage: {
                title: 'Server Storage',
                used: 'Used',
                available: 'Available'
            }
        },
        runsTable: {
            noEvaluationsTitle: 'No Evaluations Found',
            noEvaluationsDesc: 'Start your first evaluation to see the results here.',
            name: 'Evaluation Name',
            status: 'Status',
            accuracy: 'Accuracy',
            precision: 'Precision',
            recall: 'Recall',
            f1Score: 'F1 Score',
            rocAuc: 'ROC AUC',
            confMatrix: 'Matrix',
            action: 'Action',
            tested: 'Tested',
            evaluating: 'Evaluating...',
            failed: 'Failed',
            pending: 'Pending',
            reevaluate: 'Reevaluate',
        },
        modelDetails: {
            loading: 'Loading model data...',
            id: 'ID',
            created: 'Created',
            errorHeader: 'Execution Error:',
            createdAt: "Created at:",
            noRuns: "No runs yet",
            executionError: "Execution Error:",
            mainMetrics: "Key Metrics",
            confusionMatrix: "Confusion Matrix",
            matrix: {
                tn: "True Negative",
                fp: "False Positive",
                fn: "False Negative",
                tp: "True Positive"
            }
        },
        modelSetup: {
            step1Title: "1. Upload Assets",
            archLabel: "Architecture",
            weightsLabel: "Weights",
            selectJson: "Select JSON",
            selectH5: "Select H5",
            uploading: "Uploading...",
            step2Title: "2. Create AI Model",
            namePlaceholder: "Enter model name (e.g. Xception v1)...",
            createBtn: "Create Model",
            creating: "Creating...",
            errorUpload: "File upload failed",
            errorCreate: "Model creation failed"
        },
        modelsTable: {
            pageSubtitle: "Manage your registered AI models and architectures",
            noModels: "No models found",
            noModelsDesc: "Upload your first model to see it here.",
            name: "Name",
            description: "Description",
            createdAt: "Created At",
            actions: "Actions",
            edit: "Edit",
            delete: "Delete",
            editModel: "Edit Model",
            editSubtitle: "Update the information for your model.",
            confirmDelete: "Are you sure you want to delete the model",
            deleteSuccess: "Model deleted successfully!",
            deleteError: "An error occurred while deleting the model.",
            editSuccess: "Model updated successfully!",
            editError: "An error occurred while updating the model.",
            fetchModelError: "Failed to load model data.",
            cancel: "Cancel",
            saveChanges: "Save Changes"
        },
        evaluation: {
            title: "Evaluation",
            historySubtitle: "View and manage all your model runs and metrics.",
            allModels: "All Models",
            liveUpdates: "Live Updates",
            backToTable: "Back to table",
            pageTitle: "Start Evaluation",
            pageSubtitle: "Select a dataset and parameters to evaluate the model.",
            parametersHeader: "Evaluation Parameters",
            loadingData: "Loading data...",
            selectedModel: "Selected Model",
            unknownModel: "Unknown Model",
            selectDatasetLabel: "Select Dataset",
            selectDatasetPlaceholder: "-- Choose a dataset for testing --",
            noDatasetsText: "No datasets available. Please upload them on the Datasets page first.",
            formatLabel: "Format",
            startingTest: "Starting test...",
            fetchError: "Failed to load data from the server.",
            startError: "An error occurred while starting the evaluation.",
            fetchModelError: "Failed to load model data.",
            startTestBtn: 'Start New Test',
            allEvaluations: 'All Evaluations',
            confirmDelete: 'Are you sure you want to delete this evaluation?'
        }
    },
    uk: {
        common: {
            back: 'Назад до панелі',
            loading: 'Завантаження...',
            delete: 'Видалити',
            none: 'Нічого',
            cancel: "Скасувати",
            tested: 'Протестовано',
            evaluating: 'Оцінювання...',
            processing: 'Обробка...',
            downloading: 'Завантаження...',
            failed: 'Помилка',
            pending: 'В очікуванні',
        },
        pagination: {
            page: 'Сторінка',
        },
        header: {
            title: 'VisionMetrics Hub',
            logout: 'ВИЙТИ',
            online: 'В мережі',
            admin: 'Адміністратор',
            pages: 'Сторінки',
            overview: 'Огляд'
        },
        sidebar: {
            dashboard: 'Дашборд',
            models: 'Моделі ШІ',
            testRuns: 'Запуски тестів',
            settings: 'Налаштування',
            analytics: 'Аналітика',
            logout: 'Вийти'
        },
        auth: {
            username: 'Ім\'я користувача',
            password: 'Пароль',
            login: 'Увійти',
            invalid: 'Невірне ім\'я користувача або пароль'
        },
        dashboard: {
            title: 'Панель керування',
            subtitle: 'Моніторинг та оцінка продуктивності ваших нейромереж',
            uploading: 'Завантаження...',
            uploadBtn: 'Створити нову модель',
            historyTitle: 'Історія оцінювання',
            liveUpdates: 'Живе оновлення',
            stats: {
                total: 'Всього моделей',
                accuracy: 'Сер. Точність',
                precision: 'Сер. Precision',
                recall: 'Сер. Recall',
                f1: 'Сер. F1-Score',
                roc: 'Сер. ROC AUC',
            },
            storage: {
                title: 'Пам\'ять сервера',
                used: 'Використано',
                available: 'Вільно'
            }
        },
        runsTable: {
            noEvaluationsTitle: 'Оцінювань не знайдено',
            noEvaluationsDesc: 'Запустіть своє перше оцінювання, щоб побачити результати тут.',
            name: 'Назва оцінювання',
            status: 'Статус',
            accuracy: 'Точність (Accuracy)',
            precision: 'Влучність (Precision)',
            recall: 'Повнота (Recall)',
            f1Score: 'F1 Оцінка',
            rocAuc: 'ROC AUC',
            confMatrix: 'Матриця',
            action: 'Дія',
            tested: 'Перевірено',
            evaluating: 'Оцінюється...',
            failed: 'Помилка',
            pending: 'Очікує',
            reevaluate: 'Переоцінити'
        },
        modelDetails: {
            loading: 'Завантаження даних моделі...',
            id: 'ID',
            createdAt: "Створено:",
            errorHeader: 'Помилка виконання:',
            mainMetrics: 'Основні показники',
            noRuns: "Ще не тестувалась",
            executionError: "Помилка виконання:",
            confusionMatrix: "Матриця помилок (Confusion Matrix)",
            matrix: {
                tn: "Істинно негативні (TN)",
                fp: "Хибно позитивні (FP)",
                fn: "Хибно негативні (FN)",
                tp: "Істинно позитивні (TP)"
            }
        },
        modelSetup: {
            step1Title: "1. Завантаження файлів",
            archLabel: "Архітектура",
            weightsLabel: "Ваги",
            selectJson: "Вибрати JSON",
            selectH5: "Вибрати H5",
            uploading: "Завантаження...",
            step2Title: "2. Створення моделі",
            namePlaceholder: "Введіть назву моделі (напр. Xception v1)...",
            createBtn: "Створити модель",
            creating: "Створення...",
            errorUpload: "Помилка при завантаженні файлу",
            errorCreate: "Помилка при створенні моделі"
        },
        modelsTable: {
            pageSubtitle: "Керуйте вашими зареєстрованими ШІ моделями та архітектурами",
            noModels: "Моделей не знайдено",
            noModelsDesc: "Завантажте вашу першу модель, щоб вона з'явилася тут.",
            name: "Назва",
            description: "Опис",
            createdAt: "Дата створення",
            actions: "Дії",
            edit: "Редагувати",
            delete: "Видалити",
            editModel: "Редагування моделі",
            editSubtitle: "Оновіть інформацію про вашу модель.",
            confirmDelete: "Ви впевнені, що хочете видалити модель",
            deleteSuccess: "Модель успішно видалено!",
            deleteError: "Помилка при видаленні моделі.",
            editSuccess: "Модель успішно оновлено!",
            editError: "Помилка при оновленні моделі.",
            fetchModelError: "Не вдалося завантажити дані моделі.",
            cancel: "Скасувати",
            saveChanges: "Зберегти зміни"
        },
        evaluation: {
            title: "Оцінювання",
            historySubtitle: "Переглядайте та керуйте всіма запусками моделей та їх метриками.",
            allModels: "Всі моделі",
            liveUpdates: "Автооновлення",
            backToTable: "Назад до таблиці",
            pageTitle: "Запуск тестування",
            pageSubtitle: "Оберіть датасет та параметри для оцінки моделі.",
            parametersHeader: "Параметри оцінювання",
            loadingData: "Завантаження даних...",
            selectedModel: "Обрана модель",
            unknownModel: "Невідома модель",
            selectDatasetLabel: "Виберіть датасет",
            selectDatasetPlaceholder: "-- Оберіть датасет для перевірки --",
            noDatasetsText: "Немає доступних датасетів. Спочатку завантажте їх на сторінці Datasets.",
            formatLabel: "Формат",
            startingTest: "Запуск тесту...",
            fetchError: "Не вдалося завантажити дані з сервера.",
            startError: "Виникла помилка під час запуску тестування.",
            startTestBtn: 'Почати новий тест',
            allEvaluations: 'Всі оцінювання',
            confirmDelete: 'Ви впевнені, що хочете видалити це оцінювання?'
        },
    }
}

export const i18n = createI18n({
    legacy: false,
    locale: 'en',
    fallbackLocale: 'en',
    messages,
})
```

## `layouts/MainLayout.vue`

```vue
<template>
  <div class="flex h-screen bg-slate-50 overflow-hidden">

    <Sidebar />

    <div class="flex-1 flex flex-col h-screen overflow-hidden">

      <Header />

      <main class="flex-1 overflow-y-auto p-6 lg:p-8">
        <router-view />
      </main>

    </div>
  </div>
</template>

<script setup>
import Sidebar from '@/components/AppSidebar.vue'
import Header from '@/components/AppHeader.vue'
</script>
```

## `main.js`

```javascript
import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { i18n } from './i18n'
import axios from 'axios'
import './assets/main.css'

const token = localStorage.getItem('token')
if (token) {
    axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
}

axios.interceptors.response.use(
    response => response,
    error => {
        if (error.response && error.response.status === 401) {
            localStorage.removeItem('token')
            router.push('/login')
        }
        return Promise.reject(error)
    }
)

createApp(App).use(router).use(i18n).mount('#app')
```

## `router/index.js`

```javascript
import { createRouter, createWebHistory } from 'vue-router'
import MainLayout from '../layouts/MainLayout.vue'
import Dashboard from '../views/DashboardView.vue'
import Login from '../views/Login.vue'
import ModelsView from "@/views/ModelsView.vue"
import ModelDetails from "@/views/ModelDetails.vue";
import LoraTestView from "@/views/LoraTestView.vue";
import LoraTasksView from "@/views/LoraTasksView.vue";
import DatasetsView from "@/views/DatasetsView.vue";
import EvaluateModelView from "@/components/EvaluateModelView.vue";
import EditModelView from "@/views/EditModelView.vue";
import Evaluations from "@/views/Evaluations.vue";
import DatasetUpload from "@/components/DatasetUpload.vue";
import EvaluationDetail from "@/views/EvaluationDetail.vue";
import DatasetDetail from "@/views/DatasetDetail.vue";
import ModelUpload from "@/views/ModelUpload.vue";
import LoraTaskResultsView from "@/views/LoraTaskResultsView.vue";
import LoraAdaptersView from "@/views/LoraAdaptersView.vue";
import LoraAdapterUploadView from "@/views/LoraAdapterUploadView.vue";
import ActiveModelsView from "@/views/ActiveModelsView.vue";
import ApiDocsView from "@/views/ApiDocsView.vue";
import BaseModelTasksView from "@/views/BaseModelTasksView.vue";
import BaseModelCreateTaskView from "@/views/BaseModelCreateTaskView.vue";
import JudgesView from "@/views/JudgesView.vue";
import AddJudgeView from "@/views/AddJudgeView.vue";
import JudgeTasksView from "@/views/JudgeTasksView.vue";
import CreateJudgeView from "@/views/CreateJudgeView.vue";

const routes = [
    {
        path: '/login',
        component: Login,
        name: 'Login'
    },
    {
        path: '/',
        component: MainLayout,
        meta: { requiresAuth: true },
        children: [
            {
                path: '',
                component: Dashboard,
                name: 'Dashboard'
            },
            {
                path: 'test-lora',
                component: LoraTestView,
                name: 'TestLoRA'
            },
            {
                path: 'lora-tasks',
                component: LoraTasksView,
                name: 'LoraTasks'
            },
            {
                path: 'lora-tasks/:id/results',
                component: LoraTaskResultsView,
                name: 'LoraTaskResults',
                props: true
            },
            {
                path: 'models',
                component: ModelsView,
                name: 'Models'
            },
            {
                path: 'models/create',
                component: ModelUpload,
                name: 'ModelSetup'
            },
            {
                path: 'models/:id',
                name: 'model-details',
                component: ModelDetails,
                props: true
            },
            {
                path: 'models/:id/edit',
                name: 'EditModel',
                component: EditModelView,
                props: true
            },
            {
                path: 'datasets',
                component: DatasetsView,
                name: 'Datasets'
            },
            {
                path: 'datasets/upload',
                name: 'DatasetUpload',
                component: DatasetUpload
            },
            {
                path: 'datasets/:id',
                name: 'DatasetDetail',
                component: DatasetDetail,
                props: true
            },
            {
                path: 'base-model-tasks',
                component: BaseModelTasksView,
                name: 'BaseModelTasks'
            },
            {
                path: 'base-models-tasks/create',
                component: BaseModelCreateTaskView,
                name: 'BaseModelCreateTask'
            },
            {
                path: 'base-models-tasks/:id/results',
                component: LoraTaskResultsView,
                name: 'BaseModelCreateTaskResults',
                props: true
            },
            {
                path: 'lora-adapters',
                component: LoraAdaptersView,
                name: 'LoraAdapters'
            },
            {
                path: 'lora-adapters/upload',
                component: LoraAdapterUploadView,
                name: 'LoraAdapterUpload'
            },
            {
                path: 'evaluations',
                name: 'Evaluations',
                component: Evaluations
            },
            {
                path: 'evaluations/create',
                name: 'EvaluateModel',
                component: EvaluateModelView,
                props: true
            },
            {
                path: 'evaluations/:id',
                name: 'EvaluationDetails',
                component: EvaluationDetail,
                props: true
            },
            {
                path: 'active-models',
                component: ActiveModelsView,
                name: 'ActiveModels'
            },
            {
                path: 'api-docs',
                component: ApiDocsView,
                name: 'ApiDocs'
            },
            {
                path: 'judges',
                component: JudgesView,
                name: 'Judges'
            },
            {
                path: 'judges/create',
                component: AddJudgeView,
                name: 'AddJudge'
            },
            {
                path: 'judge-tasks',
                component: JudgeTasksView,
                name: 'JudgeTasks'
            },
            {
                path: 'judge-tasks/create',
                component: CreateJudgeView,
                name: 'CreateJudge'
            },
        ]
    }
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

router.beforeEach((to, from, next) => {
    const token = localStorage.getItem('token')

    if (to.meta.requiresAuth && !token) {
        next('/login')
    } else if (to.path === '/login' && token) {
        next('/')
    } else {
        next()
    }
})

export default router
```

## `views/ActiveModelsView.vue`

```vue
<template>
  <div class="w-full px-4 md:px-8 space-y-8 pb-20">

    <!-- Page Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-black text-slate-900 tracking-tight">Active Models</h1>
        <p class="text-slate-500 font-medium mt-1">Start, monitor, and manage your running LoRA instances.</p>
      </div>
    </div>

    <!-- Start New Active Model Card -->
    <div class="bg-white p-8 rounded-[2rem] shadow-sm border border-slate-100 flex flex-col md:flex-row gap-4 items-end">
      <div class="flex-1 w-full flex flex-col gap-2">
        <label class="text-xs font-black text-slate-400 uppercase tracking-widest">Select Adapter to Start</label>
        <div class="relative">
          <select
              v-model="selectedAdapterId"
              :disabled="isLoadingAdapters"
              class="w-full px-4 py-3 rounded-xl bg-slate-50 border border-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500 font-medium text-slate-700 appearance-none cursor-pointer disabled:opacity-50"
          >
            <option value="" disabled>-- Choose an adapter --</option>
            <option v-for="adapter in availableAdapters" :key="adapter.id" :value="adapter.id">
              {{ adapter.folder_name || `Adapter #${adapter.id}` }} {{ adapter.base_model_name_or_path ? `(${adapter.base_model_name_or_path})` : '' }}
            </option>
          </select>
          <div class="pointer-events-none absolute inset-y-0 right-0 flex items-center px-4 text-slate-400">
            <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
            </svg>
          </div>
        </div>
        <p v-if="availableAdapters.length === 0 && !isLoadingAdapters" class="text-xs text-orange-500 font-medium mt-1">
          No adapters found. Please upload one first.
        </p>
      </div>

      <button
          @click="startActiveModel"
          :disabled="!selectedAdapterId || isStarting"
          class="px-8 py-3 h-[50px] bg-blue-600 text-white rounded-xl font-black shadow-lg shadow-blue-600/20 hover:bg-blue-700 disabled:bg-slate-300 transition-all flex items-center shrink-0"
      >
        <span v-if="isStarting" class="animate-spin inline-block mr-2">⏳</span>
        {{ isStarting ? 'Starting...' : '+ Start Model' }}
      </button>
    </div>

    <!-- Active Models Table -->
    <div class="bg-white rounded-[2rem] shadow-sm border border-slate-100 overflow-hidden">
      <div class="px-8 py-6 border-b border-slate-50 flex items-center justify-between bg-slate-50/30">
        <h2 class="text-xl font-black text-slate-800 tracking-tight">Running Instances</h2>
        <button @click="fetchActiveModels" class="text-sm font-bold text-blue-500 hover:text-blue-700 transition-colors flex items-center gap-1">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" /></svg>
          Refresh
        </button>
      </div>

      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse">
          <thead>
          <tr class="bg-slate-50 text-slate-400 text-xs uppercase tracking-widest border-b border-slate-100">
            <th class="px-6 py-4 font-black">Model ID</th>
            <th class="px-6 py-4 font-black">Adapter ID</th>
            <th class="px-6 py-4 font-black">Queue Name</th>
            <th class="px-6 py-4 font-black">Status</th>
            <th class="px-6 py-4 font-black text-right">Actions</th>
          </tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
          <tr v-if="isLoadingData" class="text-center">
            <td colspan="5" class="py-8 text-slate-400 font-medium">Loading active models...</td>
          </tr>
          <tr v-else-if="activeModels.length === 0" class="text-center">
            <td colspan="5" class="py-8 text-slate-400 font-medium">No models are currently running.</td>
          </tr>
          <tr v-for="model in activeModels" :key="model.id" class="hover:bg-slate-50/50 transition-colors text-sm">
            <td class="px-6 py-4 font-mono font-bold text-slate-800">#{{ model.id }}</td>
            <td class="px-6 py-4 font-mono text-slate-500">Adapter {{ model.adapter_id }}</td>
            <td class="px-6 py-4 font-mono text-blue-600 bg-blue-50/50 rounded">{{ model.queue_name }}</td>
            <td class="px-6 py-4">
                <span
                    class="px-3 py-1 text-[10px] font-black uppercase tracking-wider rounded-full inline-flex items-center"
                    :class="{
                    'bg-green-100 text-green-700': model.status === 'running' || model.status === 'active',
                    'bg-blue-50 text-blue-600': model.status === 'starting' || model.status === 'pending',
                    'bg-red-100 text-red-700': model.status === 'failed',
                    'bg-slate-100 text-slate-600': !['running', 'active', 'starting', 'pending', 'failed'].includes(model.status)
                  }"
                >
                  <span v-if="model.status === 'starting' || model.status === 'pending'" class="inline-block animate-pulse mr-1">●</span>
                  {{ model.status }}
                </span>
            </td>
            <td class="px-6 py-4 text-right">
              <button
                  @click="stopActiveModel(model.adapter_id)"
                  class="text-red-500 hover:text-red-700 font-bold px-3 py-1.5 bg-red-50 hover:bg-red-100 rounded-lg transition-colors inline-flex items-center gap-1"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 10a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 01-1-1v-4z" /></svg>
                Stop
              </button>
            </td>
          </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useLoraAdaptersList } from '@/composables/useLoraAdaptersList'

const API_URL = import.meta.env.VITE_API_URL || ''

// Composable for dropdown data
const { availableAdapters, isLoadingAdapters, fetchAdapters } = useLoraAdaptersList(API_URL)

const activeModels = ref([])
const isLoadingData = ref(false)
const selectedAdapterId = ref('')
const isStarting = ref(false)

const getHeaders = () => {
  const token = localStorage.getItem('token')
  return token ? { 'Authorization': `Bearer ${token}` } : {}
}

const fetchActiveModels = async () => {
  isLoadingData.value = true
  try {
    const response = await axios.get(`${API_URL}/llm/lora/active-models/`, { headers: getHeaders() })
    activeModels.value = response.data
  } catch (error) {
    console.error("Failed to fetch active models:", error)
  } finally {
    isLoadingData.value = false
  }
}

const startActiveModel = async () => {
  if (!selectedAdapterId.value) return

  isStarting.value = true
  try {
    await axios.post(`${API_URL}/llm/lora/active-models/`,
        { adapter_id: selectedAdapterId.value },
        { headers: getHeaders() }
    )
    selectedAdapterId.value = '' // reset dropdown
    await fetchActiveModels()    // refresh table
  } catch (error) {
    console.error("Failed to start active model:", error)
    alert(error.response?.data?.detail || "Error starting the model.")
  } finally {
    isStarting.value = false
  }
}

const stopActiveModel = async (adapterId) => {
  if (!confirm('Are you sure you want to stop and delete this active model instance?')) return

  try {
    // Note: The FastAPI endpoint expects the adapter_id in the URL path for DELETE
    await axios.delete(`${API_URL}/llm/lora/active-models/${adapterId}`, { headers: getHeaders() })
    await fetchActiveModels() // refresh table
  } catch (error) {
    console.error("Failed to stop active model:", error)
    alert(error.response?.data?.detail || "Error stopping the model.")
  }
}

onMounted(() => {
  fetchAdapters()
  fetchActiveModels()
})
</script>
```

## `views/AddJudgeView.vue`

```vue
<template>
  <div class="max-w-4xl mx-auto space-y-8 pb-20 p-6">
    <div class="flex items-center mb-6">
      <button @click="$router.push('/judges')" class="text-sm font-bold text-slate-500 hover:text-slate-800 flex items-center gap-2">
        <span>&larr;</span> Back to Judges
      </button>
    </div>

    <div>
      <h1 class="text-3xl font-black text-slate-900 tracking-tight">Register New Judge</h1>
      <p class="text-slate-500 font-medium mt-1">Add a new LLM model to your registry of automated judges.</p>
    </div>

    <div class="bg-white p-8 rounded-[2rem] shadow-sm border border-slate-100">
      <div class="space-y-6">
        <div class="flex flex-col gap-2">
          <label class="text-xs font-black text-slate-400 uppercase tracking-widest">
            Model Name (Identifier)
          </label>
          <input
              v-model="modelName"
              type="text"
              placeholder="e.g. gpt-4-turbo"
              class="px-4 py-3 rounded-xl bg-slate-50 border focus:outline-none focus:ring-2 font-medium text-slate-700 transition-all"
              :class="errorMessage ? 'border-red-300 focus:ring-red-500' : 'border-slate-200 focus:ring-blue-500'"
              @input="errorMessage = ''"
          />
        </div>

        <div class="flex flex-col gap-2">
          <label class="text-xs font-black text-slate-400 uppercase tracking-widest">
            Display Name (Optional)
          </label>
          <input
              v-model="name"
              type="text"
              placeholder="e.g. GPT-4 Strict Evaluator"
              class="px-4 py-3 rounded-xl bg-slate-50 border border-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500 font-medium text-slate-700"
          />
        </div>

        <div class="flex flex-col gap-2">
          <label class="text-xs font-black text-slate-400 uppercase tracking-widest">
            Description (Optional)
          </label>
          <textarea
              v-model="description"
              placeholder="Short description of this judge..."
              class="px-4 py-3 rounded-xl bg-slate-50 border border-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500 font-medium text-slate-700 min-h-[100px]"
          ></textarea>
        </div>

        <div v-if="errorMessage" class="p-4 bg-red-50 text-red-700 rounded-xl font-medium text-sm border border-red-100">
          {{ errorMessage }}
        </div>

        <button
            @click="saveJudge"
            :disabled="!modelName.trim() || isSubmitting"
            class="w-full py-4 bg-blue-600 text-white rounded-2xl font-black shadow-lg shadow-blue-600/20 hover:bg-blue-700 disabled:bg-slate-300 transition-all flex items-center justify-center mt-4"
        >
          <span v-if="isSubmitting" class="animate-spin inline-block mr-2">⏳</span>
          {{ isSubmitting ? 'Saving...' : 'Add to Registry' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const API_URL = import.meta.env.VITE_API_URL || ''

const modelName = ref('')
const name = ref('')
const description = ref('')
const isSubmitting = ref(false)
const errorMessage = ref('')

const saveJudge = async () => {
  if (!modelName.value.trim()) return
  isSubmitting.value = true
  errorMessage.value = ''

  try {
    const token = localStorage.getItem('token')

    const payload = {
      model_name: modelName.value.trim(),
      name: name.value.trim() || null,
      description: description.value.trim() || null
    }

    await axios.post(`${API_URL}/llm/judges/`, payload, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    router.push('/judges')
  } catch (error) {
    errorMessage.value = error.response?.data?.detail || 'An error occurred while saving the judge.'
  } finally {
    isSubmitting.value = false
  }
}
</script>
```

## `views/ApiDocsView.vue`

```vue
<template>
  <div class="w-full px-4 md:px-8 space-y-8 pb-20">

    <!-- Page Header -->
    <div>
      <h1 class="text-3xl font-black text-slate-900 tracking-tight">API Documentation</h1>
      <p class="text-slate-500 font-medium mt-1">REST API endpoints, payloads, and usage examples for active LoRA models.</p>
    </div>

    <!-- Main Content -->
    <div class="bg-white p-8 rounded-[2rem] shadow-sm border border-slate-100">
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">

        <!-- Endpoint 1: Generate Chat -->
        <div class="bg-slate-50 p-6 rounded-3xl border border-slate-200 flex flex-col">
          <div class="flex items-center justify-between mb-4">
            <span class="px-3 py-1 bg-green-100 text-green-700 font-black text-xs rounded-lg uppercase tracking-wider shadow-sm">POST</span>
            <code class="text-sm text-blue-600 font-bold bg-white px-2 py-1 rounded-md border border-slate-200">/api/llm/lora/chat/generate</code>
          </div>
          <p class="text-sm text-slate-600 mb-4 font-medium">Generate a chat response using a specific active LoRA model.</p>

          <div class="relative bg-white rounded-2xl p-4 mt-auto border border-slate-200 shadow-inner">
            <button @click="copyToClipboard(generateJson)" class="absolute top-3 right-3 text-slate-400 hover:text-blue-600 transition-colors bg-white rounded-md p-1 border border-transparent hover:border-slate-200" title="Copy JSON">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"></path></svg>
            </button>
            <pre class="text-xs font-mono text-slate-700 overflow-x-auto whitespace-pre-wrap">{{ generateJson }}</pre>
          </div>
        </div>

        <!-- Endpoint 2: List Models -->
        <div class="bg-slate-50 p-6 rounded-3xl border border-slate-200 flex flex-col">
          <div class="flex items-center justify-between mb-4">
            <span class="px-3 py-1 bg-blue-100 text-blue-700 font-black text-xs rounded-lg uppercase tracking-wider shadow-sm">GET</span>
            <code class="text-sm text-blue-600 font-bold bg-white px-2 py-1 rounded-md border border-slate-200">/api/llm/lora/chat/models</code>
          </div>
          <p class="text-sm text-slate-600 mb-4 font-medium">Retrieve the list of available active models.</p>

          <div class="relative bg-white rounded-2xl p-4 mt-auto border border-slate-200 shadow-inner">
            <button @click="copyToClipboard(modelsJson)" class="absolute top-3 right-3 text-slate-400 hover:text-blue-600 transition-colors bg-white rounded-md p-1 border border-transparent hover:border-slate-200" title="Copy JSON">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"></path></svg>
            </button>
            <pre class="text-xs font-mono text-slate-700 overflow-x-auto whitespace-pre-wrap">{{ modelsJson }}</pre>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
const generateJson = `{
  "model": "disinfo__TinyLlama_TinyLlama_1_1B_Chat_v1_0_9f4082.zip",
  "messages": [
    {
      "role": "user",
      "content": "Test"
    }
  ],
  "generation_params": {
        "max_new_tokens": 256,
        "temperature": 0.1,
        "top_k": 40,
        "top_p": 0.9,
        "repetition_penalty": 1.15,
        "system_prompt": None
    }
}`

const modelsJson = `{
    "data": [
        {
            "id": "1",
            "name": "disinfo__TinyLlama_TinyLlama_1_1B_Chat_v1_0_9f4082.zip"
        }
    ]
}`

const copyToClipboard = async (text) => {
  try {
    await navigator.clipboard.writeText(text)
    alert('Copied to clipboard!')
  } catch (err) {
    console.error('Failed to copy text', err)
  }
}
</script>
```

## `views/BaseModelCreateTaskView.vue`

```vue
<template>
  <div class="max-w-4xl mx-auto space-y-8 pb-20 p-6">
    <div class="flex items-center mb-6">
      <button @click="$router.push('/base-model-tasks')" class="text-sm font-bold text-slate-500 hover:text-slate-800 flex items-center gap-2">
        <span>&larr;</span> Back to Base Models Table
      </button>
    </div>

    <div>
      <h1 class="text-3xl font-black text-slate-900 tracking-tight">Create Base Model Evaluation</h1>
      <p class="text-slate-500 font-medium mt-1">Configure parameters for pure base model testing.</p>
    </div>

    <div class="bg-white p-8 rounded-[2rem] shadow-sm border border-slate-100">
      <h2 class="text-xl font-black text-slate-800 mb-6 flex items-center gap-3">
        Evaluation Parameters
      </h2>

      <div v-if="isLoading" class="text-slate-500 font-medium animate-pulse">
        Loading datasets...
      </div>

      <div v-else class="space-y-6">
        <div class="flex flex-col gap-2">
          <label class="text-xs font-black text-slate-400 uppercase tracking-widest">
            Task Name
          </label>
          <input
              v-model="taskName"
              type="text"
              placeholder="e.g., Llama-2-7b base test"
              class="px-4 py-3 rounded-xl bg-slate-50 border border-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500 font-medium text-slate-700"
          />
        </div>

        <div class="flex flex-col gap-2">
          <label class="text-xs font-black text-slate-400 uppercase tracking-widest">
            Description (Optional)
          </label>
          <textarea
              v-model="taskDescription"
              placeholder="Short description of this evaluation run..."
              class="px-4 py-3 rounded-xl bg-slate-50 border border-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500 font-medium text-slate-700 min-h-[100px]"
          ></textarea>
        </div>

        <div class="flex flex-col gap-2">
          <label class="text-xs font-black text-slate-400 uppercase tracking-widest">
            Base Model ID (HuggingFace)
          </label>
          <input
              v-model="baseModelId"
              type="text"
              placeholder="e.g., gpt2, meta-llama/Llama-2-7b-hf"
              class="px-4 py-3 rounded-xl bg-slate-50 border border-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500 font-medium text-slate-700"
          />
        </div>

        <EvaluationJudgeSelector
            v-model="selectedJudgeIds"
            :apiUrl="API_URL"
        />

        <hr class="border-slate-100 my-6" />

        <div class="flex flex-col gap-2 mb-6">
          <div class="flex justify-between items-end">
            <label class="text-xs font-black text-slate-400 uppercase tracking-widest">Generation Parameters (JSON)</label>
            <span v-if="jsonError" class="text-xs font-bold text-red-500">{{ jsonError }}</span>
          </div>
          <textarea
              v-model="generationParamsStr"
              rows="8"
              class="px-4 py-4 rounded-xl bg-slate-50 border focus:outline-none focus:ring-2 resize-y font-mono text-sm text-slate-700"
              :class="jsonError ? 'border-red-300 focus:ring-red-500' : 'border-slate-200 focus:ring-blue-500'"
          ></textarea>
        </div>

        <CustomPromptTemplate
            v-model:useCustom="useCustomTemplate"
            v-model:templateText="promptTemplate"
        />

        <EvaluationModeSelector
            v-model:mode="evaluationMode"
            v-model:promptText="prompt"
            v-model:datasetId="selectedDatasetId"
            :datasets="datasets"
        />

        <div v-if="errorMessage" class="p-4 bg-red-50 text-red-700 rounded-xl font-medium text-sm border border-red-100">
          {{ errorMessage }}
        </div>

        <button
            @click="startEvaluation"
            :disabled="!isFormValid || isSubmitting"
            class="w-full py-4 bg-blue-600 text-white rounded-2xl font-black shadow-lg shadow-blue-600/20 hover:bg-blue-700 disabled:bg-slate-300 transition-all flex items-center justify-center mt-4"
        >
          <span v-if="isSubmitting" class="animate-spin inline-block mr-2">⏳</span>
          {{ isSubmitting ? 'Starting Test...' : 'Start Base Model Test' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import CustomPromptTemplate from '@/components/CustomPromptTemplate.vue'
import EvaluationModeSelector from "@/components/EvaluationModeSelector.vue"
import EvaluationJudgeSelector from '@/components/EvaluationJudgeSelector.vue'

const router = useRouter()
const API_URL = import.meta.env.VITE_API_URL || ''

const taskName = ref('')
const taskDescription = ref('')
const baseModelId = ref('')
const evaluationMode = ref('prompt')
const prompt = ref('')
const selectedDatasetId = ref('')

const selectedJudgeIds = ref([])

const useCustomTemplate = ref(false)
const promptTemplate = ref('{input_text}')

const defaultParams = {
  max_new_tokens: 128,
  temperature: 0.1,
  top_k: 40,
  top_p: 0.9,
  repetition_penalty: 1.15,
  do_sample: true,
  system_prompt: null
}

const generationParamsStr = ref(JSON.stringify(defaultParams, null, 2))
const jsonError = ref('')

const datasets = ref([])
const isLoading = ref(true)
const isSubmitting = ref(false)
const errorMessage = ref('')

watch(generationParamsStr, (newValue) => {
  try {
    JSON.parse(newValue)
    jsonError.value = ''
  } catch (e) {
    jsonError.value = 'Invalid JSON format'
  }
})

const isFormValid = computed(() => {
  if (!baseModelId.value || !taskName.value) return false
  if (jsonError.value) return false

  if (evaluationMode.value === 'dataset' && !selectedDatasetId.value) return false
  if (evaluationMode.value === 'prompt' && !prompt.value.trim()) return false

  return true
})

const fetchData = async () => {
  isLoading.value = true
  errorMessage.value = ''

  try {
    const token = localStorage.getItem('token')
    const config = { headers: { 'Authorization': `Bearer ${token}` } }

    const datasetsRes = await axios.get(`${API_URL}/datasets/`, config)
    datasets.value = datasetsRes.data

  } catch (error) {
    console.error(error)
    errorMessage.value = 'Failed to load datasets. Please check your connection.'
  } finally {
    isLoading.value = false
  }
}

const startEvaluation = async () => {
  if (!isFormValid.value) return

  isSubmitting.value = true
  errorMessage.value = ''

  try {
    const token = localStorage.getItem('token')

    const payload = {
      name: taskName.value,
      description: taskDescription.value,
      base_model_id: baseModelId.value,
      dataset_id: evaluationMode.value === 'dataset' ? selectedDatasetId.value : null,
      prompt: evaluationMode.value === 'prompt' ? prompt.value : null,
      generation_params: JSON.parse(generationParamsStr.value),
      judge_ids: selectedJudgeIds.value
    }

    if (useCustomTemplate.value && promptTemplate.value.trim() !== '') {
      payload.prompt_template = promptTemplate.value.trim()
    }

    await axios.post(
        `${API_URL}/llm/base-models/evaluations/`,
        payload,
        {
          headers: { 'Authorization': `Bearer ${token}` }
        }
    )

    router.push('/base-model-tasks')
  } catch (error) {
    errorMessage.value = error.response?.data?.detail || 'An error occurred while starting the evaluation.'
  } finally {
    isSubmitting.value = false
  }
}

onMounted(() => {
  fetchData()
})
</script>
```

## `views/BaseModelTasksView.vue`

```vue
<template>
  <div class="space-y-8 pb-12">
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <h1 class="text-3xl font-black text-slate-900 tracking-tight">Base Model Evaluations</h1>
        <p class="text-slate-500 font-medium">Manage and view evaluations for pure base models</p>
      </div>

      <router-link
          to="/base-models-tasks/create"
          class="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2.5 rounded-xl shadow-lg shadow-blue-600/20 transition-all font-bold flex items-center text-sm"
      >
        <span class="mr-2">+</span>
        New Evaluation
      </router-link>
    </div>

    <div class="bg-white rounded-[2.5rem] shadow-xl shadow-slate-200/50 border border-slate-100 overflow-hidden relative">

      <TasksTable
          :tasks="tasks"
          :is-loading="isLoading"
          :resolve-route="(id) => ({ name: 'BaseModelCreateTaskResults', params: { id: id } })"
          @delete="handleDelete"
      />

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import TasksTable from '@/components/TasksTable.vue'

const API_URL = import.meta.env.VITE_API_URL || ''
const tasks = ref([])
const isLoading = ref(false)

const fetchTasks = async () => {
  isLoading.value = true
  try {
    const token = localStorage.getItem('token')
    const response = await axios.get(`${API_URL}/llm/base-models/evaluations/`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    tasks.value = response.data.tasks || []
  } catch (error) {
    console.error('Error fetching base model tasks:', error)
  } finally {
    isLoading.value = false
  }
}

const handleDelete = async (id) => {
  if (confirm(`Are you sure you want to delete evaluation task #${id}?`)) {
    try {
      const token = localStorage.getItem('token')
      await axios.delete(`${API_URL}/llm/base-models/evaluations/${id}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      await fetchTasks()
    } catch (error) {
      alert(error.response?.data?.detail || 'Failed to delete task. It might still be running.')
      console.error(error)
    }
  }
}

onMounted(() => {
  fetchTasks()
})
</script>
```

## `views/CreateJudgeView.vue`

```vue
<template>
  <div class="max-w-4xl mx-auto space-y-8 pb-20 p-6">
    <div class="flex items-center mb-6">
      <button @click="$router.push('/judge-tasks')" class="text-sm font-bold text-slate-500 hover:text-slate-800 flex items-center gap-2">
        <span>&larr;</span> Back to Tasks
      </button>
    </div>

    <div>
      <h1 class="text-3xl font-black text-slate-900 tracking-tight">Run Judge Evaluation</h1>
      <p class="text-slate-500 font-medium mt-1">Configure parameters and start an automated judging process.</p>
    </div>

    <div class="bg-white p-8 rounded-[2rem] shadow-sm border border-slate-100">
      <div v-if="isLoadingData" class="text-slate-500 font-medium animate-pulse">
        Loading required data...
      </div>

      <div v-else class="space-y-6">

        <div class="flex flex-col gap-2">
          <label class="text-xs font-black text-slate-400 uppercase tracking-widest">
            Select Evaluation Task <span class="text-red-500">*</span>
          </label>
          <select
              v-model="selectedEvaluationTaskId"
              class="px-4 py-3 rounded-xl bg-slate-50 border border-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500 font-medium text-slate-700 cursor-pointer"
          >
            <option value="" disabled>-- Choose an evaluation task --</option>
            <option v-for="task in availableTasks" :key="task.id" :value="task.id">
              {{ task.name || `Task #${task.id}` }}
            </option>
          </select>
        </div>

        <div class="flex flex-col gap-2">
          <label class="text-xs font-black text-slate-400 uppercase tracking-widest">
            Select Judge Model <span class="text-red-500">*</span>
          </label>
          <select
              v-model="selectedJudgeId"
              class="px-4 py-3 rounded-xl bg-slate-50 border border-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500 font-medium text-slate-700 cursor-pointer"
          >
            <option value="" disabled>-- Choose a judge --</option>
            <option v-for="judge in availableJudges" :key="judge.id" :value="judge.id">
              {{ judge.model_name }}
            </option>
          </select>
        </div>

        <div class="flex flex-col gap-2">
          <label class="text-xs font-black text-slate-400 uppercase tracking-widest">Run Name (Optional)</label>
          <input
              v-model="runName"
              type="text"
              placeholder="e.g. Strict Evaluation Run"
              class="px-4 py-3 rounded-xl bg-slate-50 border border-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500 font-medium text-slate-700"
          />
        </div>

        <div class="flex flex-col gap-2">
          <label class="text-xs font-black text-slate-400 uppercase tracking-widest">Description (Optional)</label>
          <textarea
              v-model="runDescription"
              placeholder="Context or notes about this run..."
              class="px-4 py-3 rounded-xl bg-slate-50 border border-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500 font-medium text-slate-700 min-h-[100px]"
          ></textarea>
        </div>

        <div class="flex flex-col gap-2 mb-6">
          <div class="flex justify-between items-end">
            <label class="text-xs font-black text-slate-400 uppercase tracking-widest">Judge Parameters (JSON)</label>
            <span v-if="jsonError" class="text-xs font-bold text-red-500">{{ jsonError }}</span>
          </div>
          <textarea
              v-model="judgeParamsStr"
              rows="6"
              class="px-4 py-4 rounded-xl bg-slate-50 border focus:outline-none focus:ring-2 resize-y font-mono text-sm text-slate-700"
              :class="jsonError ? 'border-red-300 focus:ring-red-500' : 'border-slate-200 focus:ring-blue-500'"
          ></textarea>
        </div>

        <div v-if="errorMessage" class="p-4 bg-red-50 text-red-700 rounded-xl font-medium text-sm border border-red-100">
          {{ errorMessage }}
        </div>

        <button
            @click="startJudgeRun"
            :disabled="!isFormValid || isSubmitting"
            class="w-full py-4 bg-blue-600 text-white rounded-2xl font-black shadow-lg shadow-blue-600/20 hover:bg-blue-700 disabled:bg-slate-300 transition-all flex items-center justify-center mt-4"
        >
          <span v-if="isSubmitting" class="animate-spin inline-block mr-2">⏳</span>
          {{ isSubmitting ? 'Starting...' : 'Start Evaluation' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const route = useRoute()
const API_URL = import.meta.env.VITE_API_URL || ''

const availableJudges = ref([])
const availableTasks = ref([])
const isLoadingData = ref(false)

const selectedEvaluationTaskId = ref(route.query.taskId ? Number(route.query.taskId) : '')
const selectedJudgeId = ref('')
const runName = ref('')
const runDescription = ref('')

const defaultParams = {
  temperature: 0.0,
  max_new_tokens: 512,
  system_prompt: null
}

const judgeParamsStr = ref(JSON.stringify(defaultParams, null, 2))
const jsonError = ref('')

const isSubmitting = ref(false)
const errorMessage = ref('')

watch(judgeParamsStr, (newValue) => {
  try {
    JSON.parse(newValue)
    jsonError.value = ''
  } catch (e) {
    jsonError.value = 'Invalid JSON format'
  }
})

const isFormValid = computed(() => {
  if (!selectedEvaluationTaskId.value) return false
  if (!selectedJudgeId.value) return false
  if (jsonError.value) return false
  return true
})

const fetchFormData = async () => {
  isLoadingData.value = true
  errorMessage.value = ''

  try {
    const token = localStorage.getItem('token')
    const headers = { 'Authorization': `Bearer ${token}` }

    const params = { size: 100 }

    const [judgesRes, tasksRes] = await Promise.all([
      axios.get(`${API_URL}/llm/judges/`, { headers, params }),

      axios.get(`${API_URL}/llm/judge-runs/evaluation-tasks/`, { headers, params })
    ])

    availableJudges.value = judgesRes.data.items || []

    availableTasks.value = tasksRes.data.tasks || tasksRes.data.items || tasksRes.data || []

  } catch (error) {
    errorMessage.value = 'Failed to load form data.'
    console.error("Fetch form data error:", error)
  } finally {
    isLoadingData.value = false
  }
}

const startJudgeRun = async () => {
  if (!isFormValid.value) return

  isSubmitting.value = true
  errorMessage.value = ''

  try {
    const token = localStorage.getItem('token')

    const payload = {
      evaluation_task_id: selectedEvaluationTaskId.value,
      judge_id: selectedJudgeId.value,
      name: runName.value.trim() || null,
      description: runDescription.value.trim() || null,
      judge_params: JSON.parse(judgeParamsStr.value)
    }

    await axios.post(`${API_URL}/llm/judge-runs/`, payload, {
      headers: { 'Authorization': `Bearer ${token}` }
    })

    router.push('/judge-tasks')
  } catch (error) {
    errorMessage.value = error.response?.data?.detail || 'An error occurred while starting.'
  } finally {
    isSubmitting.value = false
  }
}

onMounted(() => {
  fetchFormData()
})
</script>
```

## `views/DashboardView.vue`

```vue
<template>
  <div class="space-y-8 pb-12">
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
      <div>
        <h1 class="text-3xl font-black text-slate-900 tracking-tight">{{ t('dashboard.title') }}</h1>
        <p class="text-slate-500 font-medium">{{ t('dashboard.subtitle') }}</p>
      </div>

    </div>

    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-6">
      <StatCard :title="t('dashboard.stats.total')" :value="totalModels" icon="📁" iconBgClass="bg-blue-50" iconTextClass="text-blue-600" />
      <StatCard :title="t('dashboard.stats.accuracy')" :value="`${averageMetrics.accuracy}%`" icon="🎯" iconBgClass="bg-orange-50" iconTextClass="text-orange-600" />
      <StatCard :title="t('dashboard.stats.precision')" :value="`${averageMetrics.precision}%`" icon="🔍" iconBgClass="bg-cyan-50" iconTextClass="text-cyan-600" />
      <StatCard :title="t('dashboard.stats.recall')" :value="`${averageMetrics.recall}%`" icon="📢" iconBgClass="bg-pink-50" iconTextClass="text-pink-600" />
      <StatCard :title="t('dashboard.stats.f1')" :value="`${averageMetrics.f1}%`" icon="📊" iconBgClass="bg-green-50" iconTextClass="text-green-600" />
      <StatCard :title="t('dashboard.stats.roc')" :value="`${averageMetrics.roc}%`" icon="📈" iconBgClass="bg-purple-50" iconTextClass="text-purple-600" />
    </div>

    <div class="max-w-md">
      <DiskUsageCard
          :used="storageData.used"
          :total="storageData.total"
          :free="storageData.free"
          :percentage="storageData.percentage"
          :unit="storageData.unit"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import axios from 'axios'
import StatCard from '@/components/StatCard.vue'
import DiskUsageCard from "@/components/DiskUsageCard.vue"

const { t } = useI18n()
const models = ref([])
const totalModels = ref(0)
const storageData = ref({ used: 0, total: 0, free: 0, percentage: 0, unit: 'GB' })
const API_URL = import.meta.env.VITE_API_URL || ''

const averageMetrics = computed(() => {
  const testedModels = models.value.filter(m => {
    if (!m.evaluations || m.evaluations.length === 0) return false;
    const lastEval = m.evaluations[m.evaluations.length - 1];
    return lastEval.metrics !== null && lastEval.metrics !== undefined;
  })

  if (testedModels.length === 0) return { accuracy: '0.0', f1: '0.0', roc: '0.0', precision: '0.0', recall: '0.0' }

  let accSum = 0, f1Sum = 0, rocSum = 0, precSum = 0, recSum = 0

  testedModels.forEach(m => {
    const lastEval = m.evaluations[m.evaluations.length - 1];
    accSum += lastEval.metrics.accuracy || 0
    f1Sum += lastEval.metrics.f1_score || 0
    rocSum += lastEval.metrics.roc_auc || 0
    precSum += lastEval.metrics.precision || 0
    recSum += lastEval.metrics.recall || 0
  })

  const count = testedModels.length
  return {
    accuracy: ((accSum / count) * 100).toFixed(1),
    f1: ((f1Sum / count) * 100).toFixed(1),
    roc: ((rocSum / count) * 100).toFixed(1),
    precision: ((precSum / count) * 100).toFixed(1),
    recall: ((recSum / count) * 100).toFixed(1),
  }
})

const fetchModels = async () => {
  try {
    const response = await axios.get(`${API_URL}/models/`, {
      params: { page: 1, size: 50 }
    })
    models.value = response.data.items
    totalModels.value = response.data.total
  } catch (error) {
    console.error("Error fetching models:", error)
  }
}

const fetchStorageInfo = async () => {
  try {
    const response = await axios.get(`${API_URL}/storage-info/`)
    storageData.value = response.data
  } catch (error) {
    console.error("Error fetching storage info:", error)
  }
}

onMounted(() => {
  fetchModels()
  fetchStorageInfo()
})
</script>
```

## `views/DatasetDetail.vue`

```vue
<template>
  <div class="max-w-5xl mx-auto p-6 space-y-8 pb-20">

    <!-- Back Button -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
      <button @click="$router.push('/datasets')" class="text-sm font-bold text-slate-500 hover:text-slate-800 flex items-center gap-2">
        <span>&larr;</span> {{ t('common.back') || 'Back to Datasets' }}
      </button>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-20 text-slate-400 font-medium animate-pulse">
      {{ t('common.loading') || 'Loading dataset details...' }}
    </div>

    <!-- Main Content -->
    <div v-else-if="dataset" class="space-y-6">

      <!-- Header Card -->
      <div class="bg-white p-6 rounded-[2rem] shadow-sm border border-slate-100 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 class="text-3xl font-black text-slate-800 tracking-tight">
            {{ dataset.name }}
          </h1>
          <p class="text-sm text-slate-500 mt-2 flex items-center gap-3">
            <span class="font-mono bg-slate-100 px-2 py-0.5 rounded text-xs">ID: {{ dataset.id }}</span>
            <span class="flex items-center gap-1.5">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
              {{ new Date(dataset.created_at).toLocaleString() }}
            </span>
          </p>
        </div>

        <span class="px-4 py-1.5 rounded-full text-xs font-black uppercase tracking-wider bg-blue-50 text-blue-600 border border-blue-100">
          {{ dataset.file_format }}
        </span>
      </div>

      <!-- Details Grid -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">

        <!-- Configuration Data -->
        <div class="bg-white p-6 rounded-[2rem] shadow-sm border border-slate-100">
          <h3 class="font-bold text-slate-700 mb-4 flex items-center gap-2">
            <span class="text-xl">⚙️</span> Configuration
          </h3>
          <ul class="space-y-3 text-sm">
            <li class="flex justify-between items-center border-b border-slate-50 pb-3">
              <span class="text-slate-500">ID Column</span>
              <span class="font-mono font-bold text-slate-800 bg-slate-50 px-2 py-1 rounded">{{ dataset.id_column || '—' }}</span>
            </li>
            <li class="flex justify-between items-center border-b border-slate-50 pb-3">
              <span class="text-slate-500">Dataset Type</span>
              <span class="font-mono font-bold text-slate-800 bg-slate-50 px-2 py-1 rounded uppercase">{{ dataset.dataset_type || '—' }}</span>
            </li>
            <li class="flex justify-between items-center border-b border-slate-50 pb-3">
              <span class="text-slate-500">File Source</span>
              <span class="font-mono font-bold text-slate-800 bg-slate-50 px-2 py-1 rounded uppercase">{{ dataset.file_source || '—' }}</span>
            </li>
            <li class="flex justify-between items-center border-b border-slate-50 pb-3">
              <span class="text-slate-500">Artifact ID</span>
              <span class="font-mono font-bold text-slate-800 bg-slate-50 px-2 py-1 rounded">{{ dataset.artifact_id || '—' }}</span>
            </li>
            <li class="flex justify-between items-center border-b border-slate-50 pb-3">
              <span class="text-slate-500">Source URL</span>
              <a v-if="dataset.source_url" :href="dataset.source_url" target="_blank" class="font-bold text-blue-600 hover:underline truncate max-w-[200px]">
                {{ dataset.source_url }}
              </a>
              <span v-else class="font-bold text-slate-800">—</span>
            </li>
            <li class="flex justify-between items-start pt-1">
              <span class="text-slate-500 mt-1">Mapping Config</span>
              <div v-if="dataset.mapping_config && Object.keys(dataset.mapping_config).length > 0" class="font-mono text-xs text-slate-800 bg-slate-50 p-2 rounded max-w-[200px] overflow-x-auto whitespace-pre-wrap">
                {{ JSON.stringify(dataset.mapping_config, null, 2) }}
              </div>
              <span v-else class="font-mono font-bold text-slate-800 bg-slate-50 px-2 py-1 rounded">—</span>
            </li>
          </ul>
        </div>

        <!-- Schema Configuration -->
        <div class="bg-white p-6 rounded-[2rem] shadow-sm border border-slate-100 flex flex-col">
          <h3 class="font-bold text-slate-700 mb-4 flex items-center gap-2">
            <span class="text-xl">📋</span> Schema Configuration
          </h3>
          <div class="flex-1 bg-slate-50 rounded-xl p-5 border border-slate-100 text-sm flex flex-col gap-5 overflow-y-auto max-h-[300px]">
            <template v-if="dataset.schema_config && Object.keys(dataset.schema_config).length > 0">

              <!-- Input Fields -->
              <div>
                <span class="block text-[10px] font-black text-slate-400 uppercase tracking-widest mb-2">Input Fields</span>
                <div class="flex flex-wrap gap-2">
                  <span v-for="field in dataset.schema_config.input_fields" :key="field" class="px-2 py-1 bg-blue-50 text-blue-700 rounded-md font-mono text-xs font-bold border border-blue-100">
                    {{ field }}
                  </span>
                  <span v-if="!dataset.schema_config.input_fields?.length" class="text-slate-400 italic text-xs">None</span>
                </div>
              </div>

              <!-- Target Fields -->
              <div>
                <span class="block text-[10px] font-black text-slate-400 uppercase tracking-widest mb-2">Target Fields</span>
                <div class="flex flex-wrap gap-2">
                  <span v-for="field in dataset.schema_config.target_fields" :key="field" class="px-2 py-1 bg-emerald-50 text-emerald-700 rounded-md font-mono text-xs font-bold border border-emerald-100">
                    {{ field }}
                  </span>
                  <span v-if="!dataset.schema_config.target_fields?.length" class="text-slate-400 italic text-xs">None</span>
                </div>
              </div>

              <!-- Metadata Fields -->
              <div>
                <span class="block text-[10px] font-black text-slate-400 uppercase tracking-widest mb-2">Metadata Fields</span>
                <div class="flex flex-wrap gap-2">
                  <span v-for="field in dataset.schema_config.metadata_fields" :key="field" class="px-2 py-1 bg-purple-50 text-purple-700 rounded-md font-mono text-xs font-bold border border-purple-100">
                    {{ field }}
                  </span>
                  <span v-if="!dataset.schema_config.metadata_fields?.length" class="text-slate-400 italic text-xs">None</span>
                </div>
              </div>

            </template>
            <template v-else>
              <div class="text-slate-400 italic text-center py-4 text-xs font-medium">No schema configuration provided for this dataset.</div>
            </template>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
const route = useRoute()

const dataset = ref(null)
const loading = ref(true)

const API_URL = import.meta.env.VITE_API_URL || ''

const fetchDatasetDetails = async () => {
  loading.value = true
  try {
    const token = localStorage.getItem('token')
    const response = await axios.get(`${API_URL}/datasets/${route.params.id}`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    dataset.value = response.data
  } catch (error) {
    console.error("Error fetching dataset details:", error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchDatasetDetails()
})
</script>
```

## `views/DatasetsView.vue`

```vue
<template>
  <div class="w-full px-4 md:px-8 space-y-8 pb-20">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-black text-slate-900 tracking-tight">Datasets</h1>
        <p class="text-slate-500 font-medium mt-1">Manage your uploaded datasets for LoRA evaluations.</p>
      </div>

      <router-link
          to="/datasets/upload"
          class="px-6 py-3 bg-blue-600 text-white rounded-xl font-black shadow-lg shadow-blue-600/20 hover:bg-blue-700 transition-all">
        + Upload New Dataset
      </router-link>
    </div>

    <DatasetsList
        :datasets="datasets"
        :is-loading="isLoadingData"
        @refresh="fetchDatasets"
        @delete="deleteDataset"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import DatasetsList from '../components/DatasetsList.vue'

const API_URL = import.meta.env.VITE_API_URL || ''

const datasets = ref([])
const isLoadingData = ref(false)

const fetchDatasets = async () => {
  isLoadingData.value = true
  try {
    const token = localStorage.getItem('token')
    const response = await axios.get(`${API_URL}/datasets/`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    datasets.value = response.data
  } catch (error) {
    console.error("Failed to fetch datasets:", error)
  } finally {
    isLoadingData.value = false
  }
}

const deleteDataset = async (id) => {
  if (!confirm('Are you sure you want to delete this dataset? This action cannot be undone.')) return

  try {
    const token = localStorage.getItem('token')
    await axios.delete(`${API_URL}/datasets/${id}`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    fetchDatasets()
  } catch (error) {
    alert('Failed to delete dataset: ' + (error.response?.data?.detail || 'Server error'))
  }
}

onMounted(() => {
  fetchDatasets()
})
</script>
```

## `views/EditModelView.vue`

```vue
<template>
  <div class="max-w-4xl mx-auto space-y-8 pb-20 p-6">

    <div class="flex items-center mb-6">
      <button @click="$router.push('/models')" class="text-sm font-bold text-slate-500 hover:text-slate-800 flex items-center gap-2">
        <span>&larr;</span> {{ t('common.back') }}
      </button>
    </div>

    <div>
      <h1 class="text-3xl font-black text-slate-900 tracking-tight">{{ t('modelsTable.editModel') }}</h1>
      <p class="text-slate-500 font-medium mt-1">{{ t('modelsTable.editSubtitle') }}</p>
    </div>

    <div v-if="isLoadingData" class="bg-white p-8 rounded-[2rem] shadow-sm border border-slate-100 flex justify-center py-20">
      <p class="text-slate-400 font-medium animate-pulse">{{ t('modelDetails.loading') }}</p>
    </div>

    <div v-else class="bg-white p-8 rounded-[2rem] shadow-sm border border-slate-100">
      <div class="space-y-6">
        <div class="flex flex-col gap-2">
          <label class="text-xs font-black text-slate-400 uppercase tracking-widest">{{ t('modelsTable.name') }}</label>
          <input
              v-model="editFormData.name"
              type="text"
              class="px-4 py-3 rounded-xl bg-slate-50 border border-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500 font-medium text-slate-700"
          />
        </div>

        <div class="flex flex-col gap-2">
          <label class="text-xs font-black text-slate-400 uppercase tracking-widest">{{ t('modelsTable.description') }}</label>
          <textarea
              v-model="editFormData.description"
              rows="4"
              class="px-4 py-3 rounded-xl bg-slate-50 border border-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500 font-medium text-slate-700 resize-none"
          ></textarea>
        </div>

        <div class="flex justify-end gap-4 mt-8 pt-6 border-t border-slate-50">
          <button
              @click="$router.push('/models')"
              class="px-8 py-3 rounded-xl font-bold text-slate-500 hover:bg-slate-100 transition-colors"
          >
            {{ t('modelsTable.cancel') }}
          </button>
          <button
              @click="submitModelEdit"
              :disabled="isSaving || !editFormData.name"
              class="px-8 py-3 bg-blue-600 text-white rounded-xl font-black shadow-lg shadow-blue-600/20 hover:bg-blue-700 disabled:bg-slate-300 transition-all flex items-center"
          >
            <span v-if="isSaving" class="animate-spin inline-block mr-2">⏳</span>
            {{ t('modelsTable.saveChanges') }}
          </button>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import axios from 'axios'
import { useModels } from '@/composables/useModels'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const API_URL = import.meta.env.VITE_API_URL || ''

const { updateModel } = useModels(API_URL)

const modelId = route.params.id
const isLoadingData = ref(true)
const isSaving = ref(false)

const editFormData = ref({
  id: null,
  name: '',
  description: ''
})

const fetchModelDetails = async () => {
  isLoadingData.value = true
  try {
    const response = await axios.get(`${API_URL}/models/${modelId}`)

    editFormData.value = {
      id: response.data.id,
      name: response.data.name,
      description: response.data.description || ''
    }
  } catch (error) {
    console.error("Error fetching model:", error)

    alert(t('modelsTable.fetchModelError'))

    router.push('/models')
  } finally {
    isLoadingData.value = false
  }
}

const submitModelEdit = async () => {
  isSaving.value = true
  try {
    await updateModel(modelId, {
      name: editFormData.value.name,
      description: editFormData.value.description
    })

    alert(t('modelsTable.editSuccess'))
    router.push('/models')
  } catch (error) {
    console.error("Error updating model:", error)
    alert(t('modelsTable.editError'))
  } finally {
    isSaving.value = false
  }
}

onMounted(() => {
  fetchModelDetails()
})
</script>
```

## `views/EvaluationDetail.vue`

```vue
<template>
  <div class="space-y-8 pb-12">

    <!-- Header Section -->
    <div class="flex flex-col md:flex-row md:items-start justify-between gap-4">
      <div>
        <button @click="$router.push('/evaluations')" class="text-sm font-bold text-slate-500 hover:text-slate-800 flex items-center gap-2 mb-4">
          <span>&larr;</span> {{ t('common.back') }}
        </button>
        <h1 class="text-3xl font-black text-slate-900 tracking-tight">
          <template v-if="evaluation">Evaluation #{{ evaluation.id }}</template>
          <template v-else>{{ t('modelDetails.loading') || 'Loading...' }}</template>
        </h1>

        <div v-if="evaluation" class="text-sm text-slate-500 mt-3 flex flex-wrap gap-6 font-medium">
          <!-- Model Link -->
          <span class="flex items-center gap-1.5">
            <strong class="text-slate-700">Model:</strong>
            <router-link v-if="evaluation.model" :to="`/models/${evaluation.model.id}`" class="text-blue-600 hover:text-blue-800 hover:underline flex items-center gap-1 transition-colors">
              {{ evaluation.model.name }}
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"></path></svg>
            </router-link>
            <span v-else>Unknown</span>
          </span>

          <!-- Dataset Link -->
          <span class="flex items-center gap-1.5">
            <strong class="text-slate-700">Dataset:</strong>
            <router-link v-if="evaluation.dataset" to="/datasets" class="text-blue-600 hover:text-blue-800 hover:underline flex items-center gap-1 transition-colors">
              {{ evaluation.dataset.name }}
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"></path></svg>
            </router-link>
            <span v-else>Unknown</span>
          </span>

          <!-- Date -->
          <span class="flex items-center gap-1.5 text-slate-400">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
            {{ new Date(evaluation.created_at).toLocaleString() }}
          </span>
        </div>
      </div>

      <div v-if="evaluation" class="mt-2 md:mt-10">
        <span class="px-6 py-2.5 rounded-xl text-sm font-black uppercase tracking-wider shadow-sm border"
              :class="{
                'bg-green-50 text-green-700 border-green-100': evaluation.status === 'completed',
                'bg-red-50 text-red-700 border-red-100': evaluation.status === 'failed',
                'bg-blue-50 text-blue-700 border-blue-100': evaluation.status === 'processing' || evaluation.status === 'pending'
              }">
          <span v-if="evaluation.status === 'processing'" class="inline-block animate-pulse mr-1">●</span>
          {{ evaluation.status }}
        </span>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-20 text-slate-400 font-medium animate-pulse"></div>

    <!-- Content Container -->
    <div v-else-if="evaluation" class="space-y-8">

      <!-- Failed Status Error Message -->
      <div v-if="evaluation.status === 'failed' && evaluation.error_message" class="bg-red-50 rounded-[2.5rem] shadow-xl shadow-red-200/20 border border-red-100 overflow-hidden">
        <div class="px-10 py-6 border-b border-red-100/50 bg-red-100/30 flex items-center gap-3">
          <h3 class="text-lg font-black text-red-800">{{ t('modelDetails.executionError') }}</h3>
        </div>
        <div class="px-10 py-8">
          <p class="text-red-600 font-mono text-sm whitespace-pre-wrap">{{ evaluation.error_message }}</p>
        </div>
      </div>

      <div v-if="evaluation.metrics" class="grid grid-cols-1 lg:grid-cols-2 gap-8">

        <!-- Main Metrics Box -->
        <div class="bg-white rounded-[2.5rem] shadow-xl shadow-slate-200/50 border border-slate-100 overflow-hidden flex flex-col">
          <div class="px-10 py-8 border-b border-slate-50 flex items-center justify-between bg-slate-50/30">
            <h2 class="text-xl font-black text-slate-800 tracking-tight">{{ t('modelDetails.mainMetrics') }}</h2>
          </div>
          <div class="p-10">
            <ul class="space-y-4 text-base">
              <!-- Original Metrics -->
              <li class="flex justify-between border-b border-slate-50 pb-3">
                <span class="text-slate-500 font-medium">Accuracy</span>
                <span class="font-bold text-slate-800">{{ formatMetric(evaluation.metrics.accuracy) }}</span>
              </li>
              <li class="flex justify-between border-b border-slate-50 pb-3">
                <span class="text-slate-500 font-medium">Precision</span>
                <span class="font-bold text-slate-800">{{ formatMetric(evaluation.metrics.precision) }}</span>
              </li>
              <li class="flex justify-between border-b border-slate-50 pb-3">
                <span class="text-slate-500 font-medium">Recall</span>
                <span class="font-bold text-slate-800">{{ formatMetric(evaluation.metrics.recall) }}</span>
              </li>
              <li class="flex justify-between border-b border-slate-50 pb-3">
                <span class="text-slate-500 font-medium">F1 Score</span>
                <span class="font-bold text-slate-800">{{ formatMetric(evaluation.metrics.f1_score) }}</span>
              </li>
              <li class="flex justify-between border-b border-slate-50 pb-3">
                <span class="text-slate-500 font-medium">ROC AUC</span>
                <span class="font-bold text-slate-800">{{ formatMetric(evaluation.metrics.roc_auc) }}</span>
              </li>
              <li class="flex justify-between border-b border-slate-50 pb-3">
                <span class="text-slate-500 font-medium">Balanced Accuracy</span>
                <span class="font-bold text-slate-800">{{ formatMetric(evaluation.metrics.balanced_accuracy) }}</span>
              </li>
              <!-- Newly Added Metrics -->
              <li class="flex justify-between border-b border-slate-50 pb-3">
                <span class="text-slate-500 font-medium">PR AUC</span>
                <span class="font-bold text-slate-800">{{ formatMetric(evaluation.metrics.pr_auc) }}</span>
              </li>
              <li class="flex justify-between border-b border-slate-50 pb-3">
                <span class="text-slate-500 font-medium">MCC (Matthews)</span>
                <span class="font-bold text-slate-800">{{ evaluation.metrics.mcc?.toFixed(4) || '—' }}</span>
              </li>
              <li class="flex justify-between border-b border-slate-50 pb-3">
                <span class="text-slate-500 font-medium">Log Loss</span>
                <span class="font-bold text-slate-800">{{ evaluation.metrics.log_loss_value?.toFixed(4) || '—' }}</span>
              </li>
              <li class="flex justify-between pb-1">
                <span class="text-slate-500 font-medium">Brier Score</span>
                <span class="font-bold text-slate-800">{{ evaluation.metrics.brier_score?.toFixed(4) || '—' }}</span>
              </li>
            </ul>
          </div>
        </div>

        <div class="space-y-8">

          <!-- Confusion Matrix Box -->
          <div class="bg-white rounded-[2.5rem] shadow-xl shadow-slate-200/50 border border-slate-100 overflow-hidden">
            <div class="px-10 py-8 border-b border-slate-50 flex items-center justify-between bg-slate-50/30">
              <h2 class="text-xl font-black text-slate-800 tracking-tight">{{ t('modelDetails.confusionMatrix') }}</h2>
            </div>
            <div class="p-10">
              <div v-if="hasConfusionMatrix(evaluation.metrics)" class="grid grid-cols-2 gap-4 text-center h-32">
                <div class="bg-slate-50 rounded-2xl flex flex-col justify-center border border-slate-100 shadow-sm">
                  <span class="text-xs text-slate-400 font-bold uppercase tracking-wider">{{ t('modelDetails.matrix.tn') || 'TN' }}</span>
                  <span class="text-3xl font-black text-slate-700 mt-1">{{ evaluation.metrics.tn }}</span>
                </div>
                <div class="bg-red-50 rounded-2xl flex flex-col justify-center border border-red-100 shadow-sm">
                  <span class="text-xs text-red-400 font-bold uppercase tracking-wider">{{ t('modelDetails.matrix.fp') || 'FP' }}</span>
                  <span class="text-3xl font-black text-red-700 mt-1">{{ evaluation.metrics.fp }}</span>
                </div>
                <div class="bg-orange-50 rounded-2xl flex flex-col justify-center border border-orange-100 shadow-sm">
                  <span class="text-xs text-orange-400 font-bold uppercase tracking-wider">{{ t('modelDetails.matrix.fn') || 'FN' }}</span>
                  <span class="text-3xl font-black text-orange-700 mt-1">{{ evaluation.metrics.fn }}</span>
                </div>
                <div class="bg-green-50 rounded-2xl flex flex-col justify-center border border-green-100 shadow-sm">
                  <span class="text-xs text-green-400 font-bold uppercase tracking-wider">{{ t('modelDetails.matrix.tp') || 'TP' }}</span>
                  <span class="text-3xl font-black text-green-700 mt-1">{{ evaluation.metrics.tp }}</span>
                </div>
              </div>
              <div v-else class="h-32 flex items-center justify-center text-slate-400 text-sm font-medium bg-slate-50 rounded-2xl border border-slate-100">
                Matrix data not available
              </div>
            </div>
          </div>

          <!-- Technical Details Box -->
          <div class="bg-white rounded-[2.5rem] shadow-xl shadow-slate-200/50 border border-slate-100 overflow-hidden">
            <div class="px-10 py-8 border-b border-slate-50 flex items-center justify-between bg-slate-50/30">
              <h2 class="text-xl font-black text-slate-800 tracking-tight">Technical Details</h2>
            </div>
            <div class="p-10">
              <ul class="space-y-4 text-base">
                <li class="flex justify-between border-b border-slate-50 pb-3">
                  <span class="text-slate-500 font-medium">Latency (ms)</span>
                  <span class="font-bold text-slate-800">{{ evaluation.metrics.mean_latency_ms?.toFixed(2) || '—' }}</span>
                </li>
                <li class="flex justify-between border-b border-slate-50 pb-3">
                  <span class="text-slate-500 font-medium">Averaging Mode</span>
                  <span class="font-bold text-slate-800 capitalize">{{ evaluation.metrics.averaging_mode || '—' }}</span>
                </li>
                <li class="flex justify-between border-b border-slate-50 pb-3">
                  <span class="text-slate-500 font-medium">Decision Threshold</span>
                  <span class="font-bold text-slate-800">{{ evaluation.metrics.decision_threshold || '0.5' }}</span>
                </li>
                <li class="flex justify-between border-b border-slate-50 pb-3">
                  <span class="text-slate-500 font-medium">Model Size</span>
                  <span class="font-bold text-slate-800">{{ formatBytes(evaluation.metrics.model_size_bytes) }}</span>
                </li>
                <li class="flex justify-between items-start pt-1">
                  <span class="text-slate-500 font-medium">Class Mapping</span>
                  <div class="font-mono text-xs text-slate-800 bg-slate-50 p-2 rounded text-right">
                    <span v-if="evaluation.metrics.class_mapping">{{ JSON.stringify(evaluation.metrics.class_mapping) }}</span>
                    <span v-else>—</span>
                  </div>
                </li>
              </ul>
            </div>
          </div>

        </div>
      </div>

      <!-- Raw JSON Data Box -->
      <div class="bg-white rounded-[2.5rem] shadow-xl shadow-slate-200/50 border border-slate-100 overflow-hidden mt-8">
        <div class="px-10 py-6 border-b border-slate-50 flex items-center justify-between bg-slate-50/30">
          <div>
            <h2 class="text-xl font-black text-slate-800 tracking-tight">Raw Evaluation Data</h2>
            <p class="text-sm text-slate-500 mt-1 font-medium">Full JSON response for this evaluation run.</p>
          </div>
          <button @click="copyToClipboard(JSON.stringify(evaluation, null, 2))" class="flex items-center gap-2 px-4 py-2 text-sm font-bold text-slate-600 hover:text-blue-600 bg-white border border-slate-200 hover:border-blue-200 rounded-xl transition-colors shadow-sm" title="Copy JSON">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"></path></svg>
            Copy JSON
          </button>
        </div>
        <div class="p-6 bg-slate-50/50">
          <pre class="text-xs font-mono text-slate-700 overflow-x-auto whitespace-pre-wrap p-4 bg-white rounded-2xl border border-slate-100 shadow-inner">{{ JSON.stringify(evaluation, null, 4) }}</pre>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
const route = useRoute()
const evaluation = ref(null)
const loading = ref(true)

const API_URL = import.meta.env.VITE_API_URL || ''

const formatMetric = (value) => {
  if (value === null || value === undefined) return '—'
  return (value * 100).toFixed(2) + '%'
}

const formatBytes = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  if (!bytes) return '—'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const hasConfusionMatrix = (metrics) => {
  return metrics.tn !== null && metrics.fp !== null && metrics.fn !== null && metrics.tp !== null
}

const copyToClipboard = async (text) => {
  try {
    await navigator.clipboard.writeText(text)
    alert('JSON copied to clipboard!')
  } catch (err) {
    console.error('Failed to copy text', err)
    alert('Failed to copy text.')
  }
}

const fetchEvaluationDetails = async () => {
  loading.value = true
  try {
    const token = localStorage.getItem('token')
    const response = await axios.get(`${API_URL}/evaluations/${route.params.id}`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    evaluation.value = response.data
  } catch (error) {
    console.error("Error fetching evaluation details:", error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchEvaluationDetails()
})
</script>
```

## `views/Evaluations.vue`

```vue
<template>
  <div class="space-y-8 pb-12">
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
      <div>
        <h1 class="text-3xl font-black text-slate-900 tracking-tight">{{ t('evaluation.title') || 'Evaluations' }}</h1>
        <p class="text-slate-500 font-medium">{{ t('evaluation.historySubtitle') || 'History of all test runs' }}</p>
      </div>

      <router-link
          to="/evaluations/create"
          class="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2.5 rounded-xl shadow-lg shadow-blue-600/20 transition-all font-bold flex items-center text-sm"
      >
        <span class="mr-2">+</span>
        {{ t('evaluation.startTestBtn') || 'Start New Test' }}
      </router-link>
    </div>

    <div class="bg-white rounded-[2.5rem] shadow-xl shadow-slate-200/50 border border-slate-100 overflow-hidden">
      <div class="px-10 py-8 border-b border-slate-50 flex items-center justify-between bg-slate-50/30">
        <h2 class="text-xl font-black text-slate-800 tracking-tight">{{ t('evaluation.allEvaluations') || 'All Evaluations' }}</h2>
        <div class="flex gap-2">
          <div class="w-3 h-3 rounded-full bg-green-500 animate-pulse"></div>
          <span class="text-xs font-bold text-slate-400 uppercase tracking-widest">{{ t('evaluation.liveUpdates') || 'Live Updates' }}</span>
        </div>
      </div>
      <RunsTable
          :evaluations="evaluations"
          :current-page="currentPage"
          :total-pages="totalPages"
          @page-change="handlePageChange"
          @reevaluate="handleReevaluate"
          @delete="handleDelete"
          @cancel="handleCancel"
      />
    </div>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import RunsTable from '@/components/RunsTable.vue'
import { useEvaluations } from '@/composables/useEvaluations'

const { t } = useI18n()

const {
  evaluations,
  currentPage,
  totalPages,
  fetchEvaluations,
  triggerReevaluate,
  deleteEvaluation,
  cancelEvaluation
} = useEvaluations()

let pollingInterval = null

const startPolling = () => {
  pollingInterval = setInterval(() => {
    fetchEvaluations(currentPage.value)
  }, 5000)
}

const stopPolling = () => {
  if (pollingInterval) {
    clearInterval(pollingInterval)
    pollingInterval = null
  }
}

const handlePageChange = (newPage) => {
  fetchEvaluations(newPage)
}

const handleReevaluate = async (id) => {
  try {
    await triggerReevaluate(id)
    await fetchEvaluations(currentPage.value)
  } catch (error) {
    console.error("Failed to re-evaluate.")
  }
}

const handleDelete = async (id) => {
  const confirmMessage = t('evaluation.confirmDelete') || 'Are you sure you want to delete this evaluation?'

  if (confirm(confirmMessage)) {
    try {
      await deleteEvaluation(id)

      if (evaluations.value?.length === 1 && currentPage.value > 1) {
        await fetchEvaluations(currentPage.value - 1)
      } else {
        await fetchEvaluations(currentPage.value)
      }
    } catch (error) {
      console.error("Failed to delete.", error)
    }
  }
}

const handleCancel = async (id) => {
  const confirmMessage = t('evaluation.confirmCancel') || 'Are you sure you want to cancel this ongoing evaluation?'

  if (confirm(confirmMessage)) {
    try {
      await cancelEvaluation(id)
      await fetchEvaluations(currentPage.value)
    } catch (error) {
      console.error("Failed to cancel evaluation.", error)
      alert("Could not cancel the evaluation. It may have already finished or failed.")
    }
  }
}

onMounted(() => {
  fetchEvaluations()
  startPolling()
})

onUnmounted(() => {
  stopPolling()
})
</script>
```

## `views/JudgeTasksView.vue`

```vue
<template>
  <div class="space-y-8 pb-12 px-4 md:px-8 mt-8">
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <h1 class="text-3xl font-black text-slate-900 tracking-tight">Judge Tasks</h1>
        <p class="text-slate-500 font-medium">Manage and monitor automated judge evaluations.</p>
      </div>

      <div class="flex flex-col sm:items-end gap-2">
        <router-link
            to="/judge-tasks/create"
            class="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2.5 rounded-xl shadow-lg shadow-blue-600/20 transition-all font-bold flex items-center justify-center text-sm w-full sm:w-auto"
        >
          <span class="mr-2">+</span>
          Create Judge Test
        </router-link>

        <button
            @click="fetchTasks"
            class="bg-slate-100 hover:bg-slate-200 text-slate-700 px-6 py-2.5 rounded-xl transition-all font-bold text-sm w-full sm:w-auto text-center"
        >
          Refresh List
        </button>
      </div>
    </div>

    <div class="bg-white rounded-[2.5rem] shadow-xl shadow-slate-200/50 border border-slate-100 overflow-hidden relative">
      <TasksTable
          :tasks="tasks"
          :is-loading="isLoading"
          :resolve-route="(id) => ({ name: 'JudgeTaskResults', params: { id: id } })"
          @delete="handleDelete"
          @cancel="handleCancel"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import axios from 'axios'
import TasksTable from '@/components/TasksTable.vue'

const API_URL = import.meta.env.VITE_API_URL || ''
const tasks = ref([])
const isLoading = ref(false)
let pollingInterval = null

const getHeaders = () => {
  const token = localStorage.getItem('token')
  return token ? { 'Authorization': `Bearer ${token}` } : {}
}

const fetchTasks = async () => {
  isLoading.value = true
  try {
    const response = await axios.get(`${API_URL}/llm/judge-runs/`, {
      headers: getHeaders()
    })

    tasks.value = response.data.items || response.data.tasks || response.data || []
  } catch (error) {
    console.error('Error fetching judge tasks:', error)
  } finally {
    isLoading.value = false
  }
}

const handleDelete = async (id) => {
  if (confirm(`Are you sure you want to delete judge task #${id}?`)) {
    try {
      await axios.delete(`${API_URL}/llm/judge-runs/${id}`, {
        headers: getHeaders()
      })
      await fetchTasks()
    } catch (error) {
      alert(error.response?.data?.detail || 'Failed to delete task. It might still be running.')
      console.error(error)
    }
  }
}

const handleCancel = async (id) => {
  if (confirm(`Are you sure you want to cancel judge task #${id}?`)) {
    try {
      await axios.post(`${API_URL}/llm/judge-runs/${id}/cancel`, {}, {
        headers: getHeaders()
      })
      await fetchTasks()
    } catch (error) {
      alert(error.response?.data?.detail || 'Failed to cancel task.')
      console.error(error)
    }
  }
}

const startPolling = () => {
  if (!pollingInterval) {
    pollingInterval = setInterval(() => {
      fetchTasks()
    }, 5000)
  }
}

const stopPolling = () => {
  if (pollingInterval) {
    clearInterval(pollingInterval)
    pollingInterval = null
  }
}

onMounted(() => {
  fetchTasks()
  startPolling()
})

onUnmounted(() => {
  stopPolling()
})
</script>
```

## `views/JudgesView.vue`

```vue
<template>
  <div class="w-full px-4 md:px-8 space-y-8 pb-20">
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <h1 class="text-3xl font-black text-slate-900 tracking-tight">Judges Management</h1>
        <p class="text-slate-500 font-medium mt-1">Manage LLM models used as automated judges for evaluation.</p>
      </div>

      <button
          @click="$router.push('/judges/create')"
          class="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2.5 rounded-xl shadow-lg shadow-blue-600/20 transition-all font-bold flex items-center text-sm"
      >
        <span class="mr-2">+</span>
        Add Judge
      </button>
    </div>

    <div class="bg-white rounded-[2.5rem] shadow-xl shadow-slate-200/50 border border-slate-100 overflow-hidden relative">
      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse">
          <thead>
          <tr class="bg-slate-50 text-slate-500 text-sm border-b border-slate-100">
            <th class="p-4 pl-8 font-semibold w-24">ID</th>
            <th class="p-4 font-semibold">Model Name</th>
            <th class="p-4 font-semibold">Created At</th>
            <th class="p-4 pr-8 font-semibold text-right">Actions</th>
          </tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
          <tr v-if="isLoading" class="text-center">
            <td colspan="4" class="py-12 text-slate-400 font-medium animate-pulse">Loading judges...</td>
          </tr>
          <tr v-else-if="judges.length === 0" class="text-center">
            <td colspan="4" class="py-12">
              <div class="text-4xl mb-3 opacity-50">⚖️</div>
              <h3 class="text-lg font-bold text-slate-700">No judges found</h3>
              <p class="text-slate-500 mt-1">Click "Add Judge" to register a new LLM evaluation model.</p>
            </td>
          </tr>
          <tr
              v-for="judge in judges"
              :key="judge.id"
              class="hover:bg-slate-50/50 transition-colors text-sm"
          >
            <td class="p-4 pl-8 font-mono font-bold text-slate-400">#{{ judge.id }}</td>
            <td class="p-4 font-bold text-slate-800">{{ judge.model_name }}</td>
            <td class="p-4 text-slate-600 font-medium">{{ formatDate(judge.created_at) }}</td>
            <td class="p-4 pr-8 text-right space-x-2">
              <button
                  @click="$router.push(`/judges/${judge.id}/edit`)"
                  class="px-3 py-1.5 text-xs font-bold text-blue-600 bg-blue-50 hover:bg-blue-100 rounded-lg transition-colors"
              >
                Edit
              </button>
              <button
                  @click="deleteJudge(judge)"
                  class="px-3 py-1.5 text-xs font-bold text-red-600 bg-red-50 hover:bg-red-100 rounded-lg transition-colors"
              >
                Delete
              </button>
            </td>
          </tr>
          </tbody>
        </table>
      </div>

      <div v-if="totalPages > 1" class="px-8 py-4 bg-slate-50/50 border-t border-slate-100 flex items-center justify-between">
        <div class="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em]">
          Page {{ currentPage }} / {{ totalPages }}
        </div>
        <div class="flex items-center gap-2">
          <button
              @click="fetchJudges(currentPage - 1)"
              :disabled="currentPage === 1"
              class="p-2 rounded-xl border border-slate-200 bg-white hover:bg-slate-50 disabled:opacity-30 disabled:cursor-not-allowed transition-all shadow-sm"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" /></svg>
          </button>

          <div class="flex items-center gap-1">
            <button
                v-for="p in visiblePages" :key="p"
                @click="fetchJudges(p)"
                class="w-8 h-8 rounded-lg text-[11px] font-black transition-all"
                :class="p === currentPage ? 'bg-blue-600 text-white shadow-lg shadow-blue-500/30' : 'bg-white border border-slate-100 text-slate-500 hover:bg-slate-50'"
            >
              {{ p }}
            </button>
          </div>

          <button
              @click="fetchJudges(currentPage + 1)"
              :disabled="currentPage === totalPages"
              class="p-2 rounded-xl border border-slate-200 bg-white hover:bg-slate-50 disabled:opacity-30 disabled:cursor-not-allowed transition-all shadow-sm"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" /></svg>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || ''

const judges = ref([])
const isLoading = ref(false)
const currentPage = ref(1)
const totalPages = ref(1)
const pageSize = 10

const getHeaders = () => {
  const token = localStorage.getItem('token')
  return token ? { 'Authorization': `Bearer ${token}` } : {}
}

const formatDate = (isoString) => {
  if (!isoString) return '—'
  const date = new Date(isoString)
  return date.toLocaleString('en-GB', {
    day: '2-digit', month: 'short', year: 'numeric',
    hour: '2-digit', minute: '2-digit'
  })
}

const visiblePages = computed(() => {
  const pages = []
  for (let i = 1; i <= totalPages.value; i++) {
    pages.push(i)
  }
  return pages
})

const fetchJudges = async (page = 1) => {
  isLoading.value = true
  try {
    const response = await axios.get(`${API_URL}/llm/judges/`, {
      params: { page, size: pageSize },
      headers: getHeaders()
    })
    judges.value = response.data.items
    currentPage.value = response.data.page
    totalPages.value = response.data.pages
  } catch (error) {
    console.error(error)
  } finally {
    isLoading.value = false
  }
}

const deleteJudge = async (judge) => {
  if (!confirm(`Are you sure you want to delete the judge "${judge.model_name}"?`)) return

  try {
    const response = await axios.delete(`${API_URL}/llm/judges/${judge.id}`, { headers: getHeaders() })

    if (response.status === 204 || response.data?.deleted === true) {
      judges.value = judges.value.filter(j => j.id !== judge.id)

      if (judges.value.length === 0 && currentPage.value > 1) {
        await fetchJudges(currentPage.value - 1)
      } else {
        await fetchJudges(currentPage.value)
      }
    } else {
      await fetchJudges(currentPage.value)
    }
  } catch (error) {
    alert(error.response?.data?.detail || "Failed to delete judge.")
  }
}

onMounted(() => {
  fetchJudges()
})
</script>
```

## `views/Login.vue`

```vue
<template>
  <div class="min-h-screen flex items-center justify-center bg-slate-50 p-4">
    <div class="bg-white p-8 rounded-[2rem] shadow-xl w-full max-w-md border border-slate-100">
      <h2 class="text-3xl font-black text-slate-800 text-center mb-8">VisionMetrics</h2>

      <form @submit.prevent="handleLogin" class="space-y-5">
        <div>
          <label class="block text-sm font-bold text-slate-700 mb-2">Username</label>
          <input v-model="username" type="text" class="w-full px-5 py-3 rounded-2xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all bg-slate-50" required />
        </div>

        <div>
          <label class="block text-sm font-bold text-slate-700 mb-2">Password</label>
          <input v-model="password" type="password" class="w-full px-5 py-3 rounded-2xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all bg-slate-50" required />
        </div>

        <p v-if="error" class="text-red-500 text-sm font-bold text-center bg-red-50 py-2 rounded-xl">{{ error }}</p>

        <button type="submit" :disabled="isLoading" class="w-full bg-blue-600 hover:bg-blue-700 text-white font-black py-4 px-4 rounded-2xl transition-all shadow-lg shadow-blue-600/20 disabled:bg-blue-400 mt-2">
          {{ isLoading ? 'Loading...' : 'Login' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const username = ref('')
const password = ref('')
const error = ref('')
const isLoading = ref(false)
const router = useRouter()
const API_URL = import.meta.env.VITE_API_URL || ''

const handleLogin = async () => {
  isLoading.value = true
  error.value = ''
  try {
    const formData = new URLSearchParams()
    formData.append('username', username.value)
    formData.append('password', password.value)

    const response = await axios.post(`${API_URL}/login`, formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    })

    localStorage.setItem('token', response.data.access_token)
    axios.defaults.headers.common['Authorization'] = `Bearer ${response.data.access_token}`
    router.push('/')
  } catch (err) {
    error.value = 'Invalid username or password'
  } finally {
    isLoading.value = false
  }
}
</script>
```

## `views/LoraAdapterUploadView.vue`

```vue
<template>
  <div class="max-w-4xl mx-auto space-y-8 pb-20 p-6">

    <div class="flex items-center mb-6">
      <button @click="$router.push('/lora-adapters')" class="text-sm font-bold text-slate-500 hover:text-slate-800 flex items-center gap-2">
        <span>&larr;</span> Back to Adapters
      </button>
    </div>

    <div>
      <h1 class="text-3xl font-black text-slate-900 tracking-tight">Upload LoRA Adapter</h1>
      <p class="text-slate-500 font-medium mt-1">Upload a new ZIP file containing your LoRA adapter weights and configs.</p>
    </div>

    <div class="bg-white p-8 rounded-[2rem] shadow-sm border border-slate-100">
      <LoraAdapterUploader @upload-success="onUploadSuccess" />
    </div>

  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import LoraAdapterUploader from '@/components/LoraAdapterUploader.vue'

const router = useRouter()

const onUploadSuccess = (newAdapter) => {
  setTimeout(() => {
    router.push('/lora-adapters')
  }, 1000)
}
</script>
```

## `views/LoraAdaptersView.vue`

```vue
<template>
  <div class="space-y-8 pb-12">

    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <h1 class="text-3xl font-black text-slate-900 tracking-tight">LoRA Adapters</h1>
        <p class="text-slate-500 font-medium">Manage your uploaded fine-tuned LoRA adapters</p>
      </div>

      <router-link
          to="/lora-adapters/upload"
          class="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2.5 rounded-xl shadow-lg shadow-blue-600/20 transition-all font-bold flex items-center text-sm"
      >
        <span class="mr-2">+</span>
        Upload Adapter
      </router-link>
    </div>

    <div class="bg-white rounded-[2.5rem] shadow-xl shadow-slate-200/50 border border-slate-100 overflow-hidden">
      <div class="relative">
        <div v-if="isLoadingAdapters" class="absolute inset-0 bg-white/50 flex items-center justify-center z-10">
          <span class="animate-pulse text-slate-500 font-bold">Loading...</span>
        </div>

        <LoraAdaptersTable
            :adapters="availableAdapters"
            @delete="handleDeleteAdapter"
        />
      </div>
    </div>

  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import axios from 'axios'
import LoraAdaptersTable from '@/components/LoraAdaptersTable.vue'
import { useLoraAdaptersList } from '@/composables/useLoraAdaptersList'

const API_URL = import.meta.env.VITE_API_URL || ''

const { availableAdapters, isLoadingAdapters, fetchAdapters } = useLoraAdaptersList(API_URL)

const handleDeleteAdapter = async (adapter) => {
  const confirmDelete = window.confirm(`Are you sure you want to delete adapter "${adapter.folder_name}"?`)

  if (confirmDelete) {
    try {
      const token = localStorage.getItem('token')
      await axios.delete(`${API_URL}/llm/lora/adapters/${adapter.id}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })

      await fetchAdapters()
      alert('Adapter deleted successfully!')
    } catch (error) {
      console.error('Delete error:', error)
      alert(error.response?.data?.detail || 'An error occurred while deleting the adapter.')
    }
  }
}

onMounted(() => {
  fetchAdapters()
})
</script>
```

## `views/LoraTaskResultsView.vue`

```vue
<template>
  <div class="space-y-8 pb-12 mt-8">

    <!-- Header Section -->
    <div class="flex items-center justify-between mb-6">
      <div>
        <button @click="$router.push('/lora-tasks')" class="text-sm font-bold text-slate-500 hover:text-slate-800 flex items-center gap-2 mb-2">
          <span>&larr;</span> Back to Tasks
        </button>

        <h1 class="text-3xl font-black text-slate-900 tracking-tight flex items-center gap-3">
          {{ taskDetails?.name || `Task #${taskId}` }}
          <span v-if="taskDetails?.name" class="text-sm font-bold text-slate-400 bg-slate-100 px-2 py-1 rounded-lg">#{{ taskId }}</span>
        </h1>

        <p class="text-slate-500 font-medium mt-2 max-w-3xl">
          {{ taskDetails?.description || 'Review the generated texts and performance metrics for this evaluation.' }}
        </p>
      </div>
    </div>

    <!-- Multi-Criteria Metrics Dashboard -->
    <div v-if="taskDetails?.metrics" class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">

      <!-- Predictive Quality Card -->
      <div class="bg-white p-6 rounded-[2rem] shadow-sm border border-slate-100 hover:shadow-md transition-shadow">
        <h3 class="text-xs font-black text-slate-400 uppercase tracking-widest mb-4 flex items-center gap-2">
          <span>🎯</span> Predictive Quality
        </h3>
        <div class="flex items-end gap-3">
          <span class="text-4xl font-black text-blue-600">{{ formatPercent(taskDetails.metrics.schema_validity_rate) }}</span>
        </div>
        <p class="text-sm font-bold text-slate-500 mt-2">Schema Validity Rate</p>
      </div>

      <!-- Operational Efficiency Card -->
      <div class="bg-white p-6 rounded-[2rem] shadow-sm border border-slate-100 hover:shadow-md transition-shadow">
        <h3 class="text-xs font-black text-slate-400 uppercase tracking-widest mb-4 flex items-center gap-2">
          <span>⚡</span> Operational Efficiency
        </h3>
        <div class="space-y-3">
          <div class="flex justify-between items-center border-b border-slate-50 pb-2">
            <span class="text-sm font-medium text-slate-500">Throughput (TPS)</span>
            <span class="font-bold text-slate-800 font-mono">{{ formatNumber(taskDetails.metrics.mean_tps) }} tok/s</span>
          </div>
          <div class="flex justify-between items-center border-b border-slate-50 pb-2">
            <span class="text-sm font-medium text-slate-500">VRAM Footprint</span>
            <span class="font-bold text-slate-800 font-mono">{{ formatNumber(taskDetails.metrics.mean_vram_mb, 0) }} MB</span>
          </div>
          <div class="flex justify-between items-center">
            <span class="text-sm font-medium text-slate-500">Avg Latency</span>
            <span class="font-bold text-slate-800 font-mono">{{ formatNumber(taskDetails.metrics.mean_latency_sec) }} s</span>
          </div>
        </div>
      </div>

      <!-- Calibration & Info Card -->
      <div class="bg-white p-6 rounded-[2rem] shadow-sm border border-slate-100 hover:shadow-md transition-shadow">
        <h3 class="text-xs font-black text-slate-400 uppercase tracking-widest mb-4 flex items-center gap-2">
          <span>⚖️</span> Calibration & Info
        </h3>
        <div class="space-y-3">
          <div class="flex justify-between items-center border-b border-slate-50 pb-2">
            <span class="text-sm font-medium text-slate-500">Mean Logprob</span>
            <span class="font-bold text-slate-800 font-mono">{{ formatNumber(taskDetails.metrics.mean_logprob, 4) }}</span>
          </div>
          <div class="flex justify-between items-center">
            <span class="text-sm font-medium text-slate-500">Total Samples</span>
            <span class="font-bold text-slate-800 font-mono">{{ taskDetails.metrics.total_samples || 'N/A' }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Per-Prompt Results Table -->
    <div class="bg-white rounded-[2rem] shadow-sm border border-slate-100 overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse">
          <thead>
          <tr class="bg-slate-50 border-b border-slate-100">
            <th class="px-6 py-4 text-xs font-black text-slate-400 uppercase tracking-widest w-[40%]">Question (Input Text)</th>
            <th class="px-6 py-4 text-xs font-black text-slate-400 uppercase tracking-widest w-[40%]">Answer (Generated Text)</th>
            <th class="px-6 py-4 text-xs font-black text-slate-400 uppercase tracking-widest w-[20%]">Metrics</th>
          </tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
          <tr v-if="isLoading">
            <td colspan="3" class="px-6 py-8 text-center text-slate-400 font-medium animate-pulse">Loading results...</td>
          </tr>
          <tr v-else-if="results.length === 0">
            <td colspan="3" class="px-6 py-8 text-center text-slate-400 font-medium">No results found for this task.</td>
          </tr>
          <tr v-for="result in results" :key="result.id" class="hover:bg-slate-50 transition-colors">
            <td class="px-6 py-4 text-sm text-slate-700 whitespace-pre-wrap align-top bg-slate-50/30 border-r border-slate-100">
              {{ result.input_text }}
            </td>
            <td class="px-6 py-4 text-sm text-slate-800 whitespace-pre-wrap align-top border-r border-slate-100">
              {{ result.generated_text }}
            </td>
            <td class="px-6 py-4 text-xs text-slate-600 align-top">
              <div class="space-y-1.5 bg-slate-50 rounded-lg p-3 border border-slate-100">
                <div v-if="result.latency_seconds != null" class="flex justify-between">
                  <span class="font-semibold text-slate-400">Latency:</span>
                  <span class="font-medium font-mono">{{ result.latency_seconds.toFixed(2) }}s</span>
                </div>
                <div v-if="result.prompt_tokens != null && result.completion_tokens != null" class="flex justify-between">
                  <span class="font-semibold text-slate-400">Tokens:</span>
                  <span class="font-medium font-mono" title="Prompt / Completion">{{ result.prompt_tokens }} / {{ result.completion_tokens }}</span>
                </div>
                <div v-if="result.peak_memory_mb != null" class="flex justify-between">
                  <span class="font-semibold text-slate-400">VRAM:</span>
                  <span class="font-medium font-mono">{{ result.peak_memory_mb.toFixed(0) }} MB</span>
                </div>
                <div v-if="result.avg_logprob != null" class="flex justify-between">
                  <span class="font-semibold text-slate-400">Logprob:</span>
                  <span class="font-medium font-mono">{{ result.avg_logprob.toFixed(3) }}</span>
                </div>
                <div v-if="result.latency_seconds == null && result.prompt_tokens == null" class="text-slate-400 italic text-center">
                  No metrics available
                </div>
              </div>
            </td>
          </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination -->
      <div v-if="totalPages > 1" class="px-6 py-4 bg-slate-50/50 border-t border-slate-100 flex items-center justify-between">
        <div class="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em]">
          Page {{ currentPage }} / {{ totalPages }} (Total: {{ totalItems }})
        </div>
        <div class="flex items-center gap-2">
          <button
              @click="fetchResults(currentPage - 1)"
              :disabled="currentPage === 1"
              class="p-2 rounded-xl border border-slate-200 bg-white hover:bg-slate-50 disabled:opacity-30 disabled:cursor-not-allowed transition-all shadow-sm"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" /></svg>
          </button>

          <button
              @click="fetchResults(currentPage + 1)"
              :disabled="currentPage === totalPages"
              class="p-2 rounded-xl border border-slate-200 bg-white hover:bg-slate-50 disabled:opacity-30 disabled:cursor-not-allowed transition-all shadow-sm"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" /></svg>
          </button>
        </div>
      </div>
    </div>

    <!-- NEW: Raw JSON Data Box -->
    <div v-if="taskDetails" class="bg-white rounded-[2.5rem] shadow-xl shadow-slate-200/50 border border-slate-100 overflow-hidden mt-8">
      <div class="px-10 py-6 border-b border-slate-50 flex items-center justify-between bg-slate-50/30">
        <div>
          <h2 class="text-xl font-black text-slate-800 tracking-tight">Raw Evaluation Data</h2>
          <p class="text-sm text-slate-500 mt-1 font-medium">Full JSON response for this evaluation run.</p>
        </div>
        <button @click="copyToClipboard(JSON.stringify(taskDetails, null, 2))" class="flex items-center gap-2 px-4 py-2 text-sm font-bold text-slate-600 hover:text-blue-600 bg-white border border-slate-200 hover:border-blue-200 rounded-xl transition-colors shadow-sm" title="Copy JSON">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"></path></svg>
          Copy JSON
        </button>
      </div>
      <div class="p-6 bg-slate-50/50">
        <pre class="text-xs font-mono text-slate-700 overflow-x-auto whitespace-pre-wrap p-4 bg-white rounded-2xl border border-slate-100 shadow-inner">{{ JSON.stringify(taskDetails, null, 4) }}</pre>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'

const route = useRoute()
const taskId = route.params.id
const API_URL = import.meta.env.VITE_API_URL || ''

const results = ref([])
const isLoading = ref(true)
const currentPage = ref(1)
const totalPages = ref(1)
const totalItems = ref(0)

const taskDetails = ref(null)

// --- Helper Functions for Formatting ---
const formatPercent = (val) => {
  if (val === null || val === undefined) return 'N/A'
  return (val * 100).toFixed(2) + '%'
}

const formatNumber = (val, decimals = 2) => {
  if (val === null || val === undefined) return 'N/A'
  return val.toFixed(decimals)
}

// --- NEW: Copy to Clipboard Function ---
const copyToClipboard = async (text) => {
  try {
    await navigator.clipboard.writeText(text)
    alert('JSON copied to clipboard!')
  } catch (err) {
    console.error('Failed to copy text', err)
    alert('Failed to copy text.')
  }
}

// --- API Calls ---
const fetchTaskDetails = async () => {
  try {
    const token = localStorage.getItem('token')
    const response = await axios.get(`${API_URL}/llm/lora/evaluations/${taskId}`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    taskDetails.value = response.data
  } catch (error) {
    console.error("Failed to fetch task details:", error)
  }
}

const fetchResults = async (page = 1) => {
  isLoading.value = true
  try {
    const token = localStorage.getItem('token')

    const response = await axios.get(`${API_URL}/llm/lora/evaluations/${taskId}/results`, {
      params: { page, size: 50 },
      headers: { 'Authorization': `Bearer ${token}` }
    })

    results.value = response.data.items
    currentPage.value = response.data.page
    totalPages.value = response.data.pages
    totalItems.value = response.data.total
  } catch (error) {
    console.error("Failed to fetch evaluation results:", error)
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  fetchTaskDetails()
  fetchResults()
})
</script>
```

## `views/LoraTasksView.vue`

```vue
<template>
  <div class="space-y-8 pb-12">
    <LoraTasksList />
  </div>
</template>

<script setup>
import LoraTasksList from '@/components/LoraTasksList.vue'
</script>
```

## `views/LoraTestView.vue`

```vue
<template>
  <div class="max-w-4xl mx-auto space-y-8 pb-20">
    <div>
      <h1 class="text-3xl font-black text-slate-900 tracking-tight">Test LoRA Adapter</h1>
      <p class="text-slate-500 font-medium mt-1">Select an existing adapter or upload a new ZIP containing one or multiple adapters.</p>
    </div>

    <LoraAdapterSetup v-model="selectedAdapter" />

    <div class="bg-white p-8 rounded-[2rem] shadow-sm border border-slate-100 transition-opacity duration-300" :class="{ 'opacity-50 pointer-events-none': !selectedAdapter }">
      <h2 class="text-xl font-black text-slate-800 mb-6 flex items-center gap-3">
        <span class="w-8 h-8 rounded-full flex items-center justify-center text-sm transition-colors" :class="selectedAdapter ? 'bg-blue-100 text-blue-600' : 'bg-slate-100 text-slate-600'">2</span>
        Generate Text
      </h2>

      <div class="flex flex-col gap-2 mb-6">
        <label class="text-xs font-black text-slate-400 uppercase tracking-widest">Test Name</label>
        <input
            v-model="testName"
            type="text"
            placeholder="e.g., Evaluation Run 1"
            class="px-4 py-3 rounded-xl bg-slate-50 border border-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500 font-medium text-slate-700 h-[50px]"
        />
      </div>

      <div class="flex flex-col gap-2 mb-6">
        <label class="text-xs font-black text-slate-400 uppercase tracking-widest">Description (Optional)</label>
        <textarea
            v-model="testDescription"
            rows="3"
            placeholder="e.g., Testing base model with higher temperature"
            class="px-4 py-3 rounded-xl bg-slate-50 border border-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500 font-medium text-slate-700 resize-none"
        ></textarea>
      </div>

      <div class="flex flex-col gap-2 mb-6">
        <label class="text-xs font-black text-slate-400 uppercase tracking-widest">
          Base Model ID <span v-if="isFetchingModel" class="text-blue-500 lowercase ml-1">(loading...)</span>
        </label>
        <input
            v-model="baseModelId"
            type="text"
            placeholder="e.g., Qwen/Qwen2.5-3B-Instruct"
            class="px-4 py-3 rounded-xl bg-slate-50 border border-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500 font-medium text-slate-700 h-[50px]"
            :disabled="isFetchingModel"
        />
      </div>

      <EvaluationJudgeSelector
          v-model="selectedJudgeIds"
          :apiUrl="API_URL"
      />

      <!-- Generation Parameters JSON -->
      <div class="flex flex-col gap-2 mb-6">
        <div class="flex justify-between items-end">
          <label class="text-xs font-black text-slate-400 uppercase tracking-widest">Generation Parameters (JSON)</label>
          <span v-if="jsonError" class="text-xs font-bold text-red-500">{{ jsonError }}</span>
        </div>
        <textarea
            v-model="generationParamsStr"
            rows="8"
            class="px-4 py-4 rounded-xl bg-slate-50 border focus:outline-none focus:ring-2 resize-y font-mono text-sm text-slate-700"
            :class="jsonError ? 'border-red-300 focus:ring-red-500' : 'border-slate-200 focus:ring-blue-500'"
        ></textarea>
      </div>

      <CustomPromptTemplate
          v-model:useCustom="useCustomTemplate"
          v-model:templateText="promptTemplate"
      />

      <EvaluationModeSelector
          v-model:mode="evaluationMode"
          v-model:promptText="prompt"
          v-model:datasetId="selectedDatasetId"
          :datasets="datasets"
      />

      <button @click="handleEvaluate" :disabled="isSubmitDisabled" class="w-full py-4 bg-slate-800 text-white rounded-2xl font-black hover:bg-slate-900 disabled:bg-slate-300 transition-all shadow-lg">
        <span v-if="isGenerating" class="flex items-center justify-center gap-2">
          <svg class="animate-spin h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          Starting background task...
        </span>
        <span v-else>Start Evaluation</span>
      </button>

      <div v-if="generateError" class="mt-6 p-4 bg-red-50 text-red-700 rounded-xl font-medium text-sm border border-red-100">
        {{ generateError }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, computed } from 'vue'
import LoraAdapterSetup from '@/components/LoraAdapterSetup.vue'
import CustomPromptTemplate from '@/components/CustomPromptTemplate.vue'
import EvaluationModeSelector from '@/components/EvaluationModeSelector.vue'
import EvaluationJudgeSelector from '@/components/EvaluationJudgeSelector.vue'

import { useDatasets } from '@/composables/useDatasets'
import { useLoraAdapter } from '@/composables/useLoraAdapter'
import { useLoraEvaluation } from '@/composables/useLoraEvaluation'

const API_URL = import.meta.env.VITE_API_URL || ''

const selectedAdapter = ref(null)
const evaluationMode = ref('prompt')
const prompt = ref('')
const selectedDatasetId = ref('')
const testName = ref('')
const testDescription = ref('')

const useCustomTemplate = ref(false)
const promptTemplate = ref('{input_text}')

const selectedJudgeIds = ref([])

const generationParamsStr = ref(JSON.stringify({
  max_new_tokens: 128,
  temperature: 0.1,
  top_k: 40,
  top_p: 0.9,
  repetition_penalty: 1.15,
  do_sample: true,
  system_prompt: null
}, null, 2))

const jsonError = ref('')

const { datasets, fetchDatasets } = useDatasets(API_URL)
const { baseModelId, isFetchingModel, fetchAdapterDetails } = useLoraAdapter(API_URL)
const { isGenerating, generateError, submitEvaluation } = useLoraEvaluation(API_URL)

onMounted(() => {
  fetchDatasets()
})

watch(selectedAdapter, (newAdapterId) => {
  fetchAdapterDetails(newAdapterId)
})

watch(generationParamsStr, (newValue) => {
  try {
    JSON.parse(newValue)
    jsonError.value = ''
  } catch (e) {
    jsonError.value = 'Invalid JSON format'
  }
})

const isSubmitDisabled = computed(() => {
  if (isGenerating.value || !selectedAdapter.value || !baseModelId.value || jsonError.value || !testName.value) return true;

  if (evaluationMode.value === 'prompt') {
    return !prompt.value;
  } else {
    return !selectedDatasetId.value;
  }
})

const handleEvaluate = async () => {
  if (isSubmitDisabled.value) return

  const parsedParams = JSON.parse(generationParamsStr.value)

  const payload = {
    name: testName.value,
    description: testDescription.value,
    adapter_id: selectedAdapter.value,
    base_model_id: baseModelId.value,
    generation_params: parsedParams,
    judge_ids: selectedJudgeIds.value
  }

  if (useCustomTemplate.value && promptTemplate.value.trim() !== '') {
    payload.prompt_template = promptTemplate.value.trim()
  }

  if (evaluationMode.value === 'prompt') {
    payload.prompt = prompt.value
  } else {
    payload.dataset_id = selectedDatasetId.value
  }

  await submitEvaluation(payload)
}
</script>
```

## `views/ModelDetails.vue`

```vue
<template>
  <div class="max-w-5xl mx-auto p-6 space-y-8 pb-20">

    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
      <button @click="$router.push('/models')" class="text-sm font-bold text-slate-500 hover:text-slate-800 flex items-center gap-2">
        <span>&larr;</span> {{ t('common.back') || 'Back to Models' }}
      </button>
    </div>

    <div v-if="loading" class="text-center py-20 text-slate-400 font-medium animate-pulse">
      {{ t('modelDetails.loading') || 'Loading model data...' }}
    </div>

    <div v-else-if="model" class="space-y-6">

      <div class="bg-white p-6 rounded-[2rem] shadow-sm border border-slate-100 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 class="text-3xl font-black text-slate-800 tracking-tight">{{ model.name }}</h1>
          <p class="text-sm text-slate-500 mt-2 flex items-center gap-3">
            <span class="font-mono bg-slate-100 px-2 py-0.5 rounded text-xs">ID: {{ model.id }}</span>
            <span class="flex items-center gap-1.5">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
              {{ new Date(model.created_at).toLocaleString() }}
            </span>
          </p>
        </div>

        <button @click="$router.push(`/models/${model.id}/edit`)" class="px-4 py-2 bg-blue-50 text-blue-600 font-bold rounded-xl hover:bg-blue-100 transition-colors text-sm">
          {{ t('modelsTable.edit') || 'Edit Model' }}
        </button>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div class="bg-white p-6 rounded-[2rem] shadow-sm border border-slate-100">
          <h3 class="font-bold text-slate-700 mb-4 flex items-center gap-2">
            <span class="text-xl">⚙️</span> Model Details
          </h3>
          <ul class="space-y-3 text-sm">
            <li class="flex justify-between items-center border-b border-slate-50 pb-3">
              <span class="text-slate-500">Architecture File ID</span>
              <span class="font-mono font-bold text-slate-800 bg-slate-50 px-2 py-1 rounded">{{ model.arch_file_id || '—' }}</span>
            </li>
            <li class="flex justify-between items-center border-b border-slate-50 pb-3">
              <span class="text-slate-500">Weights File ID</span>
              <span class="font-mono font-bold text-slate-800 bg-slate-50 px-2 py-1 rounded">{{ model.weights_file_id || '—' }}</span>
            </li>
          </ul>

          <div class="mt-4">
            <span class="text-slate-500 text-sm block mb-2">Description</span>
            <div class="bg-slate-50 rounded-xl p-4 border border-slate-100 text-sm text-slate-600 whitespace-pre-wrap">
              {{ model.description || 'No description provided.' }}
            </div>
          </div>
        </div>

        <div class="bg-white p-6 rounded-[2rem] shadow-sm border border-slate-100">
          <h3 class="font-bold text-slate-700 mb-4 flex items-center gap-2">
            <span class="text-xl">📊</span> Test Runs ({{ model.evaluations?.length || 0 }})
          </h3>

          <div v-if="model.evaluations && model.evaluations.length > 0" class="space-y-3 max-h-[300px] overflow-y-auto pr-2">
            <router-link
                v-for="evalItem in model.evaluations"
                :key="evalItem.id"
                :to="`/evaluations/${evalItem.id}`"
                class="block bg-slate-50 hover:bg-slate-100 border border-slate-100 p-3 rounded-xl transition-colors group"
            >
              <div class="flex justify-between items-center mb-1">
                <span class="font-bold text-slate-700 group-hover:text-blue-600 transition-colors">Evaluation #{{ evalItem.id }}</span>
                <span class="text-[10px] font-black uppercase px-2 py-0.5 rounded-full"
                      :class="{
                        'bg-green-100 text-green-700': evalItem.status === 'completed',
                        'bg-red-100 text-red-700': evalItem.status === 'failed',
                        'bg-blue-100 text-blue-700': evalItem.status === 'processing' || evalItem.status === 'pending'
                      }">
                  {{ evalItem.status }}
                </span>
              </div>
              <div class="text-xs text-slate-400 flex justify-between">
                <span>{{ new Date(evalItem.created_at).toLocaleDateString() }}</span>
                <span class="group-hover:translate-x-1 transition-transform">&rarr;</span>
              </div>
            </router-link>
          </div>

          <div v-else class="text-center py-10 bg-slate-50 rounded-xl text-slate-400 text-sm font-medium">
            {{ t('modelDetails.noRuns') || 'No runs yet' }}
          </div>

        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
const route = useRoute()
const model = ref(null)
const loading = ref(true)

const API_URL = import.meta.env.VITE_API_URL || ''

const fetchModelDetails = async () => {
  loading.value = true
  try {
    const token = localStorage.getItem('token')
    const response = await axios.get(`${API_URL}/models/${route.params.id}`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    model.value = response.data
  } catch (error) {
    console.error("Error fetching models:", error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchModelDetails()
})
</script>
```

## `views/ModelUpload.vue`

```vue
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
```

## `views/ModelsView.vue`

```vue
<template>
  <div class="space-y-8 pb-12">

    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <h1 class="text-3xl font-black text-slate-900 tracking-tight">{{ t('sidebar.models') }}</h1>
        <p class="text-slate-500 font-medium">{{ t('modelsTable.pageSubtitle') }}</p>
      </div>

      <router-link
          to="models/create"
          class="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2.5 rounded-xl shadow-lg shadow-blue-600/20 transition-all font-bold flex items-center text-sm"
      >
        <span class="mr-2">+</span>
        {{ t('dashboard.uploadBtn') }}
      </router-link>
    </div>

    <div class="bg-white rounded-[2.5rem] shadow-xl shadow-slate-200/50 border border-slate-100 overflow-hidden">
      <ModelsTable
          :models="models"
          :current-page="currentPage"
          :total-pages="totalPages"
          @page-change="handlePageChange"
          @edit="handleEditModel"
          @delete="handleDeleteModel"
      />
    </div>

  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import ModelsTable from '@/components/ModelsTable.vue'
import { useModels } from '@/composables/useModels'

const { t } = useI18n()
const router = useRouter()
const API_URL = import.meta.env.VITE_API_URL || ''
const pageSize = 10

const { models, currentPage, totalPages, fetchModels, deleteModelById } = useModels(API_URL)

const handlePageChange = (newPage) => {
  fetchModels(newPage, pageSize)
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

const handleEditModel = (model) => {
  router.push(`/models/${model.id}/edit`)
}

const handleDeleteModel = async (model) => {
  const confirmDelete = window.confirm(`${t('modelsTable.confirmDelete')} "${model.name}"?`)

  if (confirmDelete) {
    try {
      await deleteModelById(model.id)
      await fetchModels(currentPage.value, pageSize)
      console.log('Model deleted:', model.id)
      alert(t('modelsTable.deleteSuccess'))
    } catch (error) {
      alert(t('modelsTable.deleteError'))
    }
  }
}

onMounted(() => {
  fetchModels(1, pageSize)
})
</script>
```

