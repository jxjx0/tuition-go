import { ref, onMounted, onUnmounted } from 'vue'

const MOBILE_BREAKPOINT = 768

export function useIsMobile() {
    const isMobile = ref<boolean>(false)

    const checkMobile = () => {
        isMobile.value = window.innerWidth < MOBILE_BREAKPOINT
    }

    onMounted(() => {
        checkMobile()
        window.addEventListener('resize', checkMobile)
    })

    onUnmounted(() => {
        window.removeEventListener('resize', checkMobile)
    })

    return isMobile
}
