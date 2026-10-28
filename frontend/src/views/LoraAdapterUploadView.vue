<template>
  <div class="max-w-4xl mx-auto space-y-8 pb-20 p-6">

    <div class="flex items-center mb-6">
      <button @click="$router.push('/lora-adapters')" class="text-sm font-bold text-slate-500 hover:text-slate-800 flex items-center gap-2">
        <span>&larr;</span> Back to Adapters
      </button>
    </div>

    <div>
      <h1 class="text-3xl font-black text-slate-900 tracking-tight">Upload LoRA Adapter</h1>
      <p class="text-slate-500 font-medium mt-1">Upload a new ZIP file containing your LoRA adapter weights and configs.</p>
    </div>

    <div class="bg-white p-8 rounded-[2rem] shadow-sm border border-slate-100">
      <LoraAdapterUploader @upload-success="onUploadSuccess" />
    </div>

  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import LoraAdapterUploader from '@/components/LoraAdapterUploader.vue'

const router = useRouter()

const onUploadSuccess = (newAdapter) => {
  setTimeout(() => {
    router.push('/lora-adapters')
  }, 1000)
}
</script>