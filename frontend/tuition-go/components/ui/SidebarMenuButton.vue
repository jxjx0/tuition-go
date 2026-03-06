<script setup lang="ts">
import { inject, computed } from 'vue'
import { Primitive } from 'radix-vue'
import { cva } from 'class-variance-authority'
import { Tooltip, TooltipTrigger, TooltipContent } from './tooltip'
import { cn } from '@/lib/utils'

const context = inject<any>('sidebar-context')

const sidebarMenuButtonVariants = cva(
  'peer/menu-button flex w-full items-center gap-2 overflow-hidden rounded-md p-2 text-left text-sm outline-hidden ring-sidebar-ring transition-[width,height,padding] hover:bg-sidebar-accent hover:text-sidebar-accent-foreground focus-visible:ring-2 active:bg-sidebar-accent active:text-sidebar-accent-foreground disabled:pointer-events-none disabled:opacity-50 group-has-data-[sidebar=menu-action]/menu-item:pr-8 aria-disabled:pointer-events-none aria-disabled:opacity-50 data-[active=true]:bg-sidebar-accent data-[active=true]:font-medium data-[active=true]:text-sidebar-accent-foreground data-[state=open]:hover:bg-sidebar-accent data-[state=open]:hover:text-sidebar-accent-foreground group-data-[collapsible=icon]:size-8! group-data-[collapsible=icon]:p-2! [&>span:last-child]:truncate [&>svg]:size-4 [&>svg]:shrink-0',
  {
    variants: {
      variant: {
        default: 'hover:bg-sidebar-accent hover:text-sidebar-accent-foreground',
        outline:
          'bg-background shadow-[0_0_0_1px_hsl(var(--sidebar-border))] hover:bg-sidebar-accent hover:text-sidebar-accent-foreground hover:shadow-[0_0_0_1px_hsl(var(--sidebar-accent))]',
      },
      size: {
        default: 'h-8 text-sm',
        sm: 'h-7 text-xs',
        lg: 'h-12 text-sm group-data-[collapsible=icon]:p-0!',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'default',
    },
  },
)

const props = withDefaults(defineProps<{
  as?: string
  asChild?: boolean
  isActive?: boolean
  variant?: 'default' | 'outline'
  size?: 'default' | 'sm' | 'lg'
  tooltip?: string | any
  class?: string
}>(), {
  variant: 'default',
  size: 'default',
})
</script>

<template>
  <template v-if="!tooltip">
    <Primitive
      :as="as || 'button'"
      :as-child="asChild"
      data-slot="sidebar-menu-button"
      data-sidebar="menu-button"
      :data-size="size"
      :data-active="isActive"
      :class="cn(sidebarMenuButtonVariants({ variant, size }), props.class)"
    >
      <slot />
    </Primitive>
  </template>
  <template v-else>
    <Tooltip>
      <TooltipTrigger as-child>
        <Primitive
          :as="as || 'button'"
          :as-child="asChild"
          data-slot="sidebar-menu-button"
          data-sidebar="menu-button"
          :data-size="size"
          :data-active="isActive"
          :class="cn(sidebarMenuButtonVariants({ variant, size }), props.class)"
        >
          <slot />
        </Primitive>
      </TooltipTrigger>
      <TooltipContent
        side="right"
        align="center"
        :hidden="context.state.value !== 'collapsed' || context.isMobile.value"
      >
        <template v-if="typeof tooltip === 'string'">
          {{ tooltip }}
        </template>
        <template v-else>
          <component :is="tooltip" v-if="tooltip" />
        </template>
      </TooltipContent>
    </Tooltip>
  </template>
</template>
