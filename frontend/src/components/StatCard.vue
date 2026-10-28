<template>
  <div class="bg-white rounded-lg shadow-sm p-6 border border-gray-100 flex items-center">
    <div :class="['w-12 h-12 rounded-full flex items-center justify-center mr-4 text-xl', iconBgClass, iconTextClass]">
      {{ icon }}
    </div>
    <div>
      <p class="text-xs text-gray-500 uppercase tracking-wide">{{ title }}</p>
      <p class="text-2xl font-semibold text-gray-800">{{ value }}</p>
    </div>
  </div>
</template>

<script setup>
defineProps({
  title: String,
  value: [String, Number],
  icon: String,
  iconBgClass: String,
  iconTextClass: String
})
</script>