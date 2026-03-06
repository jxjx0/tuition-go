<script setup lang="ts">
import { 
  NavigationMenuRoot, 
  type NavigationMenuRootEmits, 
  type NavigationMenuRootProps, 
  useForwardPropsEmits 
} from 'radix-vue'
import NavigationMenuViewport from './NavigationMenuViewport.vue'
import { cn } from '@/lib/utils'

const props = withDefaults(defineProps<NavigationMenuRootProps & { class?: string; viewport?: boolean }>(), {
  viewport: true,
})
const emits = defineEmits<NavigationMenuRootEmits>()

const forwarded = useForwardPropsEmits(props, emits)
</script>

<template>
  <NavigationMenuRoot
    v-bind="forwarded"
    data-slot="navigation-menu"
    :data-viewport="viewport"
    :class="cn(
      'group/navigation-menu relative flex max-w-max flex-1 items-center justify-center',
      props.class
    )"
  >
    <slot />
    <NavigationMenuViewport v-if="viewport" />
  </NavigationMenuRoot>
</template>
