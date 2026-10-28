import { ref } from 'vue'
import axios from 'axios'

export function useLoraAdapter(apiUrl) {
    const baseModelId = ref('')
    const isFetchingModel = ref(false)

    const fetchAdapterDetails = async (adapterId) => {
        if (!adapterId) {
            baseModelId.value = ''
            return
        }

        isFetchingModel.value = true
        try {
            const token = localStorage.getItem('token')
            const response = await axios.get(`${apiUrl}/llm/lora/adapters/${adapterId}`, {
                headers: { 'Authorization': `Bearer ${token}` }
            })
            baseModelId.value = response.data.base_model_name_or_path || ''
        } catch (error) {
            console.error("Failed to fetch adapter details from backend", error)
            baseModelId.value = ''
        } finally {
            isFetchingModel.value = false
        }
    }

    return {
        baseModelId,
        isFetchingModel,
        fetchAdapterDetails
    }
}