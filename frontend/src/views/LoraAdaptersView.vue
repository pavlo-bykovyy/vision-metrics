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