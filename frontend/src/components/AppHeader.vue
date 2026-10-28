<template>
  <header class="h-20 bg-white border-b border-slate-100 px-8 flex items-center justify-between">
    <div class="flex items-center space-x-2 text-sm">
      <span class="text-slate-400">Pages</span>
      <span class="text-slate-300">/</span>
      <span class="text-slate-900 font-medium capitalize">{{ currentRouteName }}</span>
    </div>

    <div class="flex items-center space-x-6">
      <div class="flex bg-slate-50 p-1 rounded-lg border border-slate-100">
        <button
            v-for="lang in ['en', 'uk']" :key="lang"
            @click="changeLocale(lang)"
            :class="['px-3 py-1 rounded-md text-xs font-bold transition-all',
                   locale === lang ? 'bg-white shadow-sm text-blue-600' : 'text-slate-400 hover:text-slate-600']"
        >
          {{ lang.toUpperCase() }}
        </button>
      </div>

      <div class="h-6 w-px bg-slate-100"></div>

      <div class="flex items-center space-x-3 cursor-pointer hover:opacity-80 transition">
        <div class="text-right hidden sm:block">
          <p class="text-sm font-bold text-slate-900 leading-tight">Admin User</p>
          <p class="text-xs text-green-500 font-medium">Online</p>
        </div>
        <div class="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-500 to-blue-600 flex items-center justify-center text-white shadow-md">
          JD
        </div>
      </div>
    </div>
  </header>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'

const route = useRoute()
const { locale } = useI18n()

const currentRouteName = computed(() => route.name || 'Overview')

const changeLocale = (lang) => {
  locale.value = lang
}
</script>