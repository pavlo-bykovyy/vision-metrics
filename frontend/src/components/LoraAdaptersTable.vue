<template>
  <div>
    <div v-if="adapters.length === 0" class="py-12 flex flex-col items-center justify-center text-center">
      <div class="text-6xl mb-4 opacity-50">🔌</div>
      <h3 class="text-lg font-bold text-slate-700">No LoRA adapters found</h3>
      <p class="text-slate-500 mt-1">Upload your first adapter ZIP to see it here.</p>
    </div>

    <div v-else class="overflow-x-auto border border-slate-100 rounded-2xl overflow-hidden">
      <table class="w-full text-left border-collapse">
        <thead>
        <tr class="bg-slate-50 text-slate-500 text-sm border-b border-slate-100">
          <th class="p-4 font-semibold w-16">ID</th>
          <th class="p-4 font-semibold">Folder Name</th>
          <th class="p-4 font-semibold">Base Model</th>
          <th class="p-4 font-semibold text-right">Actions</th>
        </tr>
        </thead>
        <tbody>
        <tr
            v-for="(adapter, index) in adapters"
            :key="adapter.id"
            class="hover:bg-slate-50/50 transition-colors text-sm"
            :class="index !== adapters.length - 1 ? 'border-b border-slate-50' : ''"
        >
          <td class="p-4 font-mono font-bold text-slate-400">#{{ adapter.id }}</td>

          <td class="p-4 font-bold text-slate-800">
            {{ adapter.folder_name }}
          </td>

          <td class="p-4 text-slate-500 max-w-xs truncate" :title="adapter.base_model_name_or_path">
            {{ adapter.base_model_name_or_path || '—' }}
          </td>

          <td class="p-4 text-right space-x-2">
            <button
                @click="$emit('delete', adapter)"
                class="px-3 py-1.5 text-xs font-bold text-red-600 bg-red-50 hover:bg-red-100 rounded-lg transition-colors"
            >
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
const props = defineProps({
  adapters: {
    type: Array,
    required: true
  }
})

const emit = defineEmits(['delete'])
</script>