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