import { ref, watchEffect, onMounted, onUnmounted, inject, provide, computed } from 'vue'

const SIDEBAR_COOKIE_NAME = 'sidebar_state'
const SIDEBAR_COOKIE_MAX_AGE = 60 * 60 * 24 * 7
const SIDEBAR_WIDTH = '16rem'
const SIDEBAR_WIDTH_MOBILE = '18rem'
const SIDEBAR_WIDTH_ICON = '3rem'
const SIDEBAR_KEYBOARD_SHORTCUT = 'b'

export function useIsMobile() {
    const isMobile = ref(false)

    if (typeof window !== 'undefined') {
        const checkMobile = () => {
            isMobile.value = window.innerWidth < 768
        }
        checkMobile()
        window.addEventListener('resize', checkMobile)
        onUnmounted(() => window.removeEventListener('resize', checkMobile))
    }

    return isMobile
}

export type SidebarState = 'expanded' | 'collapsed'

export function useSidebar() {
    const context = inject<any>('sidebar-context')
    if (!context) {
        throw new Error('useSidebar must be used within a SidebarProvider.')
    }
    return context
}
