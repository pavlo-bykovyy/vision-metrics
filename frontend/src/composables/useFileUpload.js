import { ref } from 'vue'
import axios from 'axios'
import { useI18n } from 'vue-i18n'

export function useFileUpload(apiUrl) {
    const { t } = useI18n()

    const isUploading = ref(false)
    const progress = ref(0)
    const asset = ref(null)

    const uploadFile = async (file) => {
        if (!file) return

        isUploading.value = true
        progress.value = 0
        const formData = new FormData()
        formData.append('file', file)

        try {
            const token = localStorage.getItem('token')

            const res = await axios.post(`${apiUrl}/upload-file/`, formData, {
                headers: {
                    'Authorization': `Bearer ${token}`
                },
                onUploadProgress: (progressEvent) => {
                    progress.value = Math.round((progressEvent.loaded * 100) / progressEvent.total)
                }
            })
            asset.value = res.data
        } catch (err) {
            alert(t('modelSetup.errorUpload') + ': ' + (err.response?.data?.detail || 'Server error'))
        } finally {
            isUploading.value = false
        }
    }

    return {
        isUploading,
        progress,
        asset,
        uploadFile
    }
}