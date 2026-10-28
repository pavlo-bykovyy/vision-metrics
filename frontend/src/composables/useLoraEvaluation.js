import { ref } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'

export function useLoraEvaluation(apiUrl) {
    const router = useRouter()
    const isGenerating = ref(false)
    const generateError = ref('')

    const submitEvaluation = async (payload) => {
        isGenerating.value = true
        generateError.value = ''

        try {
            const token = localStorage.getItem('token')
            await axios.post(`${apiUrl}/llm/lora/evaluations/`, payload, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            })
            router.push('/lora-tasks')
        } catch (err) {
            generateError.value = err.response?.data?.detail || 'Failed to start evaluation task.'
        } finally {
            isGenerating.value = false
        }
    }

    return {
        isGenerating,
        generateError,
        submitEvaluation
    }
}