import { ref, onMounted, onUnmounted } from 'vue'
import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || ''

const authHeaders = () => {
    const token = localStorage.getItem('token')
    return token ? { Authorization: `Bearer ${token}` } : {}
}

/**
 * Shared logic for any page that renders a TasksTable.
 *
 * Fetches the task list, polls it periodically and exposes delete and cancel
 * handlers. The backend is expected to respond with `{ items: TaskListItem[], total: number }`.
 * Must be called inside `setup()` because it registers lifecycle hooks.
 *
 * @param {string} basePath - API path without a trailing slash, e.g. '/llm/judge-runs'.
 * @param {Object} [options] - Optional settings.
 * @param {string} [options.label='task'] - Entity name used in confirmation and error messages.
 * @param {number} [options.pollMs=5000] - Polling interval in milliseconds.
 * @returns {{
 *   tasks: import('vue').Ref<Array>,
 *   isLoading: import('vue').Ref<boolean>,
 *   fetchTasks: () => Promise<void>,
 *   handleDelete: (id: number) => Promise<void>,
 *   handleCancel: (id: number) => Promise<void>
 * }} Reactive state and action handlers for the page.
 */
export function useTaskList(basePath, { label = 'task', pollMs = 5000 } = {}) {
    const tasks = ref([])
    const isLoading = ref(false)
    let timer = null
    let inFlight = false

    const fetchTasks = async () => {
        if (inFlight) return
        inFlight = true
        isLoading.value = true
        try {
            const { data } = await axios.get(`${API_URL}${basePath}/`, { headers: authHeaders() })
            tasks.value = data.items ?? []
        } catch (error) {
            console.error(`Error fetching ${label}s:`, error)
        } finally {
            isLoading.value = false
            inFlight = false
        }
    }

    const act = async (confirmText, request, fallbackError) => {
        if (!confirm(confirmText)) return
        try {
            await request()
            await fetchTasks()
        } catch (error) {
            alert(error.response?.data?.detail || fallbackError)
            console.error(error)
        }
    }

    const handleDelete = (id) =>
        act(
            `Are you sure you want to delete ${label} #${id}?`,
            () => axios.delete(`${API_URL}${basePath}/${id}`, { headers: authHeaders() }),
            `Failed to delete ${label}. It might still be running.`
        )

    const handleCancel = (id) =>
        act(
            `Are you sure you want to cancel ${label} #${id}?`,
            () => axios.post(`${API_URL}${basePath}/${id}/cancel`, {}, { headers: authHeaders() }),
            `Failed to cancel ${label}.`
        )

    onMounted(() => {
        fetchTasks()
        timer = setInterval(fetchTasks, pollMs)
    })

    onUnmounted(() => clearInterval(timer))

    return { tasks, isLoading, fetchTasks, handleDelete, handleCancel }
}