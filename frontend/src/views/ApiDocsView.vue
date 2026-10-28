<template>
  <div class="w-full px-4 md:px-8 space-y-8 pb-20">

    <!-- Page Header -->
    <div>
      <h1 class="text-3xl font-black text-slate-900 tracking-tight">API Documentation</h1>
      <p class="text-slate-500 font-medium mt-1">REST API endpoints, payloads, and usage examples for active LoRA models.</p>
    </div>

    <!-- Main Content -->
    <div class="bg-white p-8 rounded-[2rem] shadow-sm border border-slate-100">
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">

        <!-- Endpoint 1: Generate Chat -->
        <div class="bg-slate-50 p-6 rounded-3xl border border-slate-200 flex flex-col">
          <div class="flex items-center justify-between mb-4">
            <span class="px-3 py-1 bg-green-100 text-green-700 font-black text-xs rounded-lg uppercase tracking-wider shadow-sm">POST</span>
            <code class="text-sm text-blue-600 font-bold bg-white px-2 py-1 rounded-md border border-slate-200">/api/llm/lora/chat/generate</code>
          </div>
          <p class="text-sm text-slate-600 mb-4 font-medium">Generate a chat response using a specific active LoRA model.</p>

          <div class="relative bg-white rounded-2xl p-4 mt-auto border border-slate-200 shadow-inner">
            <button @click="copyToClipboard(generateJson)" class="absolute top-3 right-3 text-slate-400 hover:text-blue-600 transition-colors bg-white rounded-md p-1 border border-transparent hover:border-slate-200" title="Copy JSON">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"></path></svg>
            </button>
            <pre class="text-xs font-mono text-slate-700 overflow-x-auto whitespace-pre-wrap">{{ generateJson }}</pre>
          </div>
        </div>

        <!-- Endpoint 2: List Models -->
        <div class="bg-slate-50 p-6 rounded-3xl border border-slate-200 flex flex-col">
          <div class="flex items-center justify-between mb-4">
            <span class="px-3 py-1 bg-blue-100 text-blue-700 font-black text-xs rounded-lg uppercase tracking-wider shadow-sm">GET</span>
            <code class="text-sm text-blue-600 font-bold bg-white px-2 py-1 rounded-md border border-slate-200">/api/llm/lora/chat/models</code>
          </div>
          <p class="text-sm text-slate-600 mb-4 font-medium">Retrieve the list of available active models.</p>

          <div class="relative bg-white rounded-2xl p-4 mt-auto border border-slate-200 shadow-inner">
            <button @click="copyToClipboard(modelsJson)" class="absolute top-3 right-3 text-slate-400 hover:text-blue-600 transition-colors bg-white rounded-md p-1 border border-transparent hover:border-slate-200" title="Copy JSON">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"></path></svg>
            </button>
            <pre class="text-xs font-mono text-slate-700 overflow-x-auto whitespace-pre-wrap">{{ modelsJson }}</pre>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
const generateJson = `{
  "model": "disinfo__TinyLlama_TinyLlama_1_1B_Chat_v1_0_9f4082.zip",
  "messages": [
    {
      "role": "user",
      "content": "Test"
    }
  ],
  "generation_params": {
        "max_new_tokens": 256,
        "temperature": 0.1,
        "top_k": 40,
        "top_p": 0.9,
        "repetition_penalty": 1.15,
        "system_prompt": None
    }
}`

const modelsJson = `{
    "data": [
        {
            "id": "1",
            "name": "disinfo__TinyLlama_TinyLlama_1_1B_Chat_v1_0_9f4082.zip"
        }
    ]
}`

const copyToClipboard = async (text) => {
  try {
    await navigator.clipboard.writeText(text)
    alert('Copied to clipboard!')
  } catch (err) {
    console.error('Failed to copy text', err)
  }
}
</script>