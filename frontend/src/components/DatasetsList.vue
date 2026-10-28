<template>
  <div class="bg-white rounded-[2rem] shadow-sm border border-slate-100 overflow-hidden">
    <div class="px-8 py-6 border-b border-slate-50 flex items-center justify-between bg-slate-50/30">
      <h2 class="text-xl font-black text-slate-800 tracking-tight">Available Datasets</h2>
      <button @click="$emit('refresh')" class="text-sm font-bold text-blue-500 hover:text-blue-700 transition-colors">
        Refresh
      </button>
    </div>

    <div class="overflow-x-auto">
      <table class="w-full text-left border-collapse">
        <thead>
        <tr class="bg-slate-50 text-slate-400 text-xs uppercase tracking-widest border-b border-slate-100">
          <th class="px-6 py-4 font-black">ID</th>
          <th class="px-6 py-4 font-black">Name</th>
          <th class="px-6 py-4 font-black">Format</th>
          <th class="px-6 py-4 font-black text-right">Actions</th>
        </tr>
        </thead>
        <tbody class="divide-y divide-slate-100">
        <tr v-if="isLoading" class="text-center">
          <td colspan="5" class="py-8 text-slate-400 font-medium">Loading datasets...</td>
        </tr>
        <tr v-else-if="datasets.length === 0" class="text-center">
          <td colspan="5" class="py-8 text-slate-400 font-medium">No datasets found. Please upload one.</td>
        </tr>
        <tr v-for="dataset in datasets" :key="dataset.id" class="hover:bg-slate-50/50 transition-colors text-sm">
          <td class="px-6 py-4 font-mono font-bold text-slate-400">#{{ dataset.id }}</td>
          <td class="px-6 py-4 font-bold text-slate-800">
            <router-link
                :to="`/datasets/${dataset.id}`"
                class="hover:text-blue-600 hover:underline flex items-center gap-1.5 transition-colors w-fit group"
            >
              {{ dataset.name }}
              <svg class="w-3.5 h-3.5 text-slate-300 group-hover:text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
              </svg>
            </router-link>
          </td>
          <td class="px-6 py-4 font-bold text-blue-600 uppercase">{{ dataset.file_format }}</td>
          <td class="px-6 py-4 text-right">
            <button @click="$emit('delete', dataset.id)" class="text-red-500 hover:text-red-700 font-bold px-3 py-1 bg-red-50 hover:bg-red-100 rounded-lg transition-colors">
              Delete
            </button>
          </td>
        </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
defineProps({
  datasets: {
    type: Array,
    required: true
  },
  isLoading: {
    type: Boolean,
    default: false
  }
})

defineEmits(['refresh', 'delete'])
</script>