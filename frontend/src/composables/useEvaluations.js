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