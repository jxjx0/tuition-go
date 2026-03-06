<script setup lang="ts">
import { NavigationMenuLink, type NavigationMenuLinkEmits, type NavigationMenuLinkProps, useForwardPropsEmits } from 'radix-vue'
import { cn } from '@/lib/utils'

const props = defineProps<NavigationMenuLinkProps & { class?: string }>()
const emits = defineEmits<NavigationMenuLinkEmits>()

const forwarded = useForwardPropsEmits(props, emits)
</script>

<template>
  <NavigationMenuLink
    v-bind="forwarded"
    data-slot="navigation-menu-link"
    :class="cn(
      'data-[active=true]:focus:bg-accent data-[active=true]:hover:bg-accent data-[active=true]:bg-accent/50 data-[active=true]:text-accent-foreground hover:bg-accent hover:text-accent-foreground focus:bg-accent focus:text-accent-foreground focus-visible:ring-ring/50 [&_svg:not([class*=\'text-\'])]:text-muted-foreground flex flex-col gap-1 rounded-sm p-2 text-sm transition-all outline-none focus-visible:ring-[3px] focus-visible:outline-1 [&_svg:not([class*=\'size-\'])]:size-4',
      props.class
    )"
  >
    <slot />
  </NavigationMenuLink>
</template>
