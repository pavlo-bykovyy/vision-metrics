import { ref } from 'vue'
import axios from 'axios'

export function useLoraUpload(apiUrl) {
    const zipFile = ref(null)
    const isUploading = ref(false)
    const uploadMessage = ref('')
    const isUploadError = ref(false)

    const handleFileSelection = (event) => {
        const file = event.target.files[0]
        if (file && file.name.endsWith('.zip')) {
            zipFile.value = file
            uploadMessage.value = ''
            isUploadError.value = false
        } else {
            zipFile.value = null
            isUploadError.value = true
            uploadMessage.value = 'Please select a valid .zip file.'
        }
    }

    const uploadZipFile = async () => {
        if (!zipFile.value) return null

        isUploading.value = true
        uploadMessage.value = ''
        isUploadError.value = false

        const formData = new FormData()
        formData.append('file', zipFile.value)

        try {
            const token = localStorage.getItem('token')

            const response = await axios.post(`${apiUrl}/llm/lora/adapters/upload`, formData, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            })

            isUploadError.value = false
            uploadMessage.value = 'ZIP uploaded and extracted successfully!'
            const uploadedData = response.data

            zipFile.value = null

            return uploadedData

        } catch (err) {
            isUploadError.value = true
            uploadMessage.value = err.response?.data?.detail || 'Failed to upload and extract ZIP file.'
            return null
        } finally {
            isUploading.value = false
        }
    }

    return {
        zipFile,
        isUploading,
        uploadMessage,
        isUploadError,
        handleFileSelection,
        uploadZipFile
    }
}