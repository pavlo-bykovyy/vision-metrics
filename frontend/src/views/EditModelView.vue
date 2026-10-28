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