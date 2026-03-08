<script setup lang="ts">
import { ref, computed, provide, onMounted, onUnmounted } from 'vue'
import { useIsMobile } from '@/hooks/use-mobile'
import { TooltipProvider } from './TooltipProvider.vue'
import { cn } from '@/lib/utils'

const SIDEBAR_COOKIE_NAME = 'sidebar_state'
const SIDEBAR_COOKIE_MAX_AGE = 60 * 60 * 24 * 7
const SIDEBAR_WIDTH = '16rem'
const SIDEBAR_WIDTH_ICON = '3rem'
const SIDEBAR_KEYBOARD_SHORTCUT = 'b'

const props = withDefaults(defineProps<{
  defaultOpen?: boolean
  open?: boolean
  class?: string
  style?: any
}>(), {
  defaultOpen: true,
})

const emits = defineEmits<{
  (e: 'update:open', value: boolean): void
}>()

const isMobile = useIsMobile()
const openMobile = ref(false)

const _open = ref(props.defaultOpen)
const open = computed({
  get: () => props.open !== undefined ? props.open : _open.value,
  set: (value: boolean) => {
    if (props.open !== undefined) {
      emits('update:open', value)
    } else {
      _open.value = value
    }
    document.cookie = `${SIDEBAR_COOKIE_NAME}=${value}; path=/; max-age=${SIDEBAR_COOKIE_MAX_AGE}`
  }
})

function toggleSidebar() {
  if (isMobile.value) {
    openMobile.value = !openMobile.value
  } else {
    open.value = !open.value
  }
}

function handleKeyDown(event: KeyboardEvent) {
  if (event.key === SIDEBAR_KEYBOARD_SHORTCUT && (event.metaKey || event.ctrlKey)) {
    event.preventDefault()
    toggleSidebar()
  }
}

onMounted(() => {
  window.addEventListener('keydown', handleKeyDown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeyDown)
})

const state = computed(() => open.value ? 'expanded' : 'collapsed')

provide('sidebar-context', {
  state,
  open,
  setOpen: (val: boolean) => open.value = val,
  isMobile,
  openMobile,
  setOpenMobile: (val: boolean) => openMobile.value = val,
  toggleSidebar,
})
</script>

<template>
  <TooltipProvider :delay-duration="0">
    <div
      data-slot="sidebar-wrapper"
      :style="{
        '--sidebar-width': SIDEBAR_WIDTH,
        '--sidebar-width-icon': SIDEBAR_WIDTH_ICON,
        ...props.style,
      }"
      :class="cn(
        'group/sidebar-wrapper has-data-[variant=inset]:bg-sidebar flex min-h-svh w-full',
        props.class
      )"
    >
      <slot />
    </div>
  </TooltipProvider>
</template>
