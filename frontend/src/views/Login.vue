<template>
  <div class="min-h-screen flex items-center justify-center bg-slate-50 p-4">
    <div class="bg-white p-8 rounded-[2rem] shadow-xl w-full max-w-md border border-slate-100">
      <h2 class="text-3xl font-black text-slate-800 text-center mb-8">VisionMetrics</h2>

      <form @submit.prevent="handleLogin" class="space-y-5">
        <div>
          <label class="block text-sm font-bold text-slate-700 mb-2">Username</label>
          <input v-model="username" type="text" class="w-full px-5 py-3 rounded-2xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all bg-slate-50" required />
        </div>

        <div>
          <label class="block text-sm font-bold text-slate-700 mb-2">Password</label>
          <input v-model="password" type="password" class="w-full px-5 py-3 rounded-2xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all bg-slate-50" required />
        </div>

        <p v-if="error" class="text-red-500 text-sm font-bold text-center bg-red-50 py-2 rounded-xl">{{ error }}</p>

        <button type="submit" :disabled="isLoading" class="w-full bg-blue-600 hover:bg-blue-700 text-white font-black py-4 px-4 rounded-2xl transition-all shadow-lg shadow-blue-600/20 disabled:bg-blue-400 mt-2">
          {{ isLoading ? 'Loading...' : 'Login' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const username = ref('')
const password = ref('')
const error = ref('')
const isLoading = ref(false)
const router = useRouter()
const API_URL = import.meta.env.VITE_API_URL || ''

const handleLogin = async () => {
  isLoading.value = true
  error.value = ''
  try {
    const formData = new URLSearchParams()
    formData.append('username', username.value)
    formData.append('password', password.value)

    const response = await axios.post(`${API_URL}/login`, formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    })

    localStorage.setItem('token', response.data.access_token)
    axios.defaults.headers.common['Authorization'] = `Bearer ${response.data.access_token}`
    router.push('/')
  } catch (err) {
    error.value = 'Invalid username or password'
  } finally {
    isLoading.value = false
  }
}
</script>