<script setup lang="ts">
import { ref } from 'vue'

const props = defineProps({
  modelValue: { type: Number, default: 0 },
  interactive: { type: Boolean, default: false },
  size: { type: String, default: 'md' },
  showValue: { type: Boolean, default: false },
})

const emit = defineEmits(['update:modelValue'])

const hoverVal = ref(0)
</script>

<template>
  <div class="flex items-center" :class="size==='sm'?'gap-0.5':size==='lg'?'gap-1':'gap-0.5'">
    <template v-for="i in 5" :key="i">
      <button v-if="interactive" @click="emit('update:modelValue', i)" @mouseenter="hoverVal=i" @mouseleave="hoverVal=0" class="transition-transform duration-150 hover:scale-110 focus:outline-none">
        <svg :class="size==='sm'?'w-4 h-4':size==='lg'?'w-7 h-7':'w-5 h-5'" viewBox="0 0 24 24" :fill="i<=(hoverVal||modelValue)?'#F59E0B':'#E5E7EB'" stroke="none">
          <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
        </svg>
      </button>
      <svg v-else :class="size==='sm'?'w-4 h-4':size==='lg'?'w-7 h-7':'w-5 h-5'" viewBox="0 0 24 24" :fill="i<=Math.round(modelValue)?'#F59E0B':'#E5E7EB'" stroke="none">
        <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
      </svg>
    </template>
    <span v-if="showValue" class="ml-1.5 font-semibold" style="color:#1B3A5C">{{ modelValue.toFixed(1) }}</span>
  </div>
</template>
