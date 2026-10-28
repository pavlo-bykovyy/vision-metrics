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