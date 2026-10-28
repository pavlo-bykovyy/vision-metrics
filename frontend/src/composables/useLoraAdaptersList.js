import { ref } from 'vue'
import axios from 'axios'

export function useLoraAdaptersList(apiUrl) {
    const availableAdapters = ref([])
    const isLoadingAdapters = ref(false)

    const fetchAdapters = async () => {
        isLoadingAdapters.value = true
        try {
            const response = await axios.get(`${apiUrl}/llm/lora/adapters/`)
            availableAdapters.value = response.data.adapters
        } catch (error) {
            console.error('Failed to fetch adapters:', error)
        } finally {
            isLoadingAdapters.value = false
        }
    }

    return {
        availableAdapters,
        isLoadingAdapters,
        fetchAdapters
    }
}