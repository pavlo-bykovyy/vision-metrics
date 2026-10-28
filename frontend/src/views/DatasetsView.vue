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