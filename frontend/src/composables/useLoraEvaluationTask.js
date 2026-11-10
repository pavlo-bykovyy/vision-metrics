import { ref, watch, unref, isRef } from 'vue'
import http from '@/shared/http'

export function useLoraEvaluationTask(taskId) {
    const taskDetails = ref(null)
    const isLoadingDetails = ref(false)
    const detailsError = ref('')

    const results = ref([])
    const isLoadingResults = ref(false)
    const resultsError = ref('')
    const currentPage = ref(1)
    const totalPages = ref(1)
    const totalItems = ref(0)

    const isCancelling = ref(false)
    const isDeleting = ref(false)

    const fetchTaskDetails = async () => {
        isLoadingDetails.value = true
        detailsError.value = ''
        try {
            const { data } = await http.get(`/llm/lora/evaluations/${unref(taskId)}`)
            taskDetails.value = data
        } catch (err) {
            detailsError.value = err.response?.status === 404
                ? 'Task not found.'
                : err.response?.data?.detail || 'Failed to load task details.'
        } finally {
            isLoadingDetails.value = false
        }
    }

    const fetchResults = async (page = 1, size = 50) => {
        isLoadingResults.value = true
        resultsError.value = ''
        try {
            const { data } = await http.get(`/llm/lora/evaluations/${unref(taskId)}/results`, {
                params: { page, size }
            })
            results.value = data.items
            currentPage.value = data.page
            totalPages.value = data.pages
            totalItems.value = data.total
        } catch (err) {
            resultsError.value = err.response?.data?.detail || 'Failed to load evaluation results.'
        } finally {
            isLoadingResults.value = false
        }
    }

    const cancelTask = async () => {
        isCancelling.value = true
        try {
            await http.post(`/llm/lora/evaluations/${unref(taskId)}/cancel`)
            await fetchTaskDetails()
        } catch (err) {
            detailsError.value = err.response?.data?.detail || 'Failed to cancel task.'
            throw err
        } finally {
            isCancelling.value = false
        }
    }

    const deleteTask = async () => {
        isDeleting.value = true
        try {
            await http.delete(`/llm/lora/evaluations/${unref(taskId)}`)
        } catch (err) {
            detailsError.value = err.response?.data?.detail || 'Failed to delete task.'
            throw err
        } finally {
            isDeleting.value = false
        }
    }

    const loadAll = () => {
        fetchTaskDetails()
        fetchResults(1)
    }

    if (isRef(taskId)) {
        watch(taskId, loadAll)
    }

    return {
        taskDetails, isLoadingDetails, detailsError, fetchTaskDetails,
        results, isLoadingResults, resultsError, currentPage, totalPages, totalItems, fetchResults,
        isCancelling, cancelTask,
        isDeleting, deleteTask,
        loadAll
    }
}