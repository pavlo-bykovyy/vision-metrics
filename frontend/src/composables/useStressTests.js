/**
 * src/composables/useStressTests.js
 *
 * API client for the statistical stress test (/stress-tests): Monte Carlo simulation of
 * controlled classifier failure modes, reviewer analyses, figures and the results archive.
 */
import { ref } from 'vue'
import http from '@/shared/http'

function toMessage(error) {
    const res = error.response
    if (!res) return 'Server is unreachable'
    const detail = res.data?.detail
    if (!detail) return `${res.status} ${res.statusText}`
    if (typeof detail === 'string') return detail
    if (Array.isArray(detail)) {
        return detail
            .map((d) => `${(d.loc || []).filter((p) => p !== 'body').join('.')}: ${d.msg}`)
            .join('\n')
    }
    return JSON.stringify(detail)
}

const call = async (promise) => {
    try {
        return (await promise).data
    } catch (e) {
        throw new Error(toMessage(e))
    }
}

const encodePath = (path) => path.split('/').map(encodeURIComponent).join('/')

export const stressTestsApi = {
    getDefaults: () => call(http.get('/stress-tests/defaults')),
    list: (page = 1, size = 10) => call(http.get('/stress-tests/', { params: { page, size } })),
    create: (payload) => call(http.post('/stress-tests/', payload)),
    get: (id) => call(http.get(`/stress-tests/${id}`)),
    remove: (id) => call(http.delete(`/stress-tests/${id}`)),
    cancel: (id) => call(http.post(`/stress-tests/${id}/cancel`)),
    rerun: (id) => call(http.post(`/stress-tests/${id}/re-run`)),
    listFiles: (id) => call(http.get(`/stress-tests/${id}/files`)),
    getTable: (id, name, limit = 500) => call(http.get(`/stress-tests/${id}/tables`, { params: { name, limit } })),

    // Files need the Bearer token, so they are fetched as blobs instead of plain <img src>/<a href>.
    fetchFileBlob: (id, path) =>
        call(http.get(`/stress-tests/${id}/files/${encodePath(path)}`, { responseType: 'blob' })),
    fetchArchiveBlob: (id) => call(http.get(`/stress-tests/${id}/archive`, { responseType: 'blob' })),
}

export function saveBlob(blob, filename) {
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    document.body.appendChild(a)
    a.click()
    a.remove()
    URL.revokeObjectURL(url)
}

export function useStressTests() {
    const runs = ref([])
    const currentPage = ref(1)
    const totalPages = ref(1)
    const total = ref(0)
    const isLoading = ref(false)
    const error = ref('')

    const fetchRuns = async (page = currentPage.value, { silent = false } = {}) => {
        if (!silent) isLoading.value = true
        try {
            const data = await stressTestsApi.list(page, 10)
            runs.value = data.items
            totalPages.value = data.pages
            currentPage.value = data.page
            total.value = data.total
            error.value = ''
        } catch (e) {
            error.value = e.message
        } finally {
            isLoading.value = false
        }
    }

    return { runs, currentPage, totalPages, total, isLoading, error, fetchRuns }
}
