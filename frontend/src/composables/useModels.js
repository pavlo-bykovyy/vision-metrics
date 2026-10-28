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