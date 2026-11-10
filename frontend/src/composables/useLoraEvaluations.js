import { ref } from 'vue'
import { useRouter } from 'vue-router'
import http from '@/shared/http'

export function useLoraEvaluations() {
    const router = useRouter()

    const tasks = ref([])
    const isLoadingTasks = ref(false)
    const listError = ref('')

    const isGenerating = ref(false)
    const generateError = ref('')

    const fetchTasks = async () => {
        isLoadingTasks.value = true
        listError.value = ''
        try {
            const { data } = await http.get('/llm/lora/evaluations/')
            tasks.value = data.tasks
        } catch (err) {
            listError.value = err.response?.data?.detail || 'Failed to load evaluation tasks.'
        } finally {
            isLoadingTasks.value = false
        }
    }

    const submitEvaluation = async (payload) => {
        isGenerating.value = true
        generateError.value = ''
        try {
            await http.post('/llm/lora/evaluations/', payload)
            router.push('/lora-tasks')
        } catch (err) {
            generateError.value = err.response?.data?.detail || 'Failed to start evaluation task.'
        } finally {
            isGenerating.value = false
        }
    }

    return {
        tasks, isLoadingTasks, listError, fetchTasks,
        isGenerating, generateError, submitEvaluation
    }
}