<script setup>
/**
 * src/views/attacks/CreateAttackView.vue
 *
 * Page view for creating and generating dynamic attack datasets (Dataset in models.py).
 */

import CreateAttack from '@/components/attacks/CreateAttack.vue'

const API_URL = import.meta.env.VITE_API_URL || '/api'
</script>

<template>
  <CreateAttack :api-url="API_URL" />
</template>