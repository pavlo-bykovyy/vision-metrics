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