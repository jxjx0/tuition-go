<script setup lang="ts">
const props = defineProps<{
  class?: string
}>()
</script>

<template>
  <li data-slot="pagination-item" :class="props.class">
    <slot />
  </li>
</template>
