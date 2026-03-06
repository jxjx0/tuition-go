import { ref } from 'vue'
// ToastProps defined locally to avoid import issues with .vue files
export interface ToastProps {
    variant?: 'default' | 'destructive'
    class?: string
}

const TOAST_LIMIT = 1
const TOAST_REMOVE_DELAY = 1000000

type ToasterToast = ToastProps & {
    id: string
    title?: string
    description?: string
    action?: {
        altText: string
        onClick?: () => void
        [key: string]: any
    }
    open?: boolean
    onOpenChange?: (open: boolean) => void
}

const count = ref(0)
const toasts = ref<ToasterToast[]>([])

function genId() {
    count.value = (count.value + 1) % Number.MAX_SAFE_INTEGER
    return count.value.toString()
}

const toastTimeouts = new Map<string, ReturnType<typeof setTimeout>>()

const addToRemoveQueue = (toastId: string) => {
    if (toastTimeouts.has(toastId)) {
        return
    }

    const timeout = setTimeout(() => {
        toastTimeouts.delete(toastId)
        toasts.value = toasts.value.filter((t: ToasterToast) => t.id !== toastId)
    }, TOAST_REMOVE_DELAY)

    toastTimeouts.set(toastId, timeout)
}

function toast(props: Omit<ToasterToast, 'id'>) {
    const id = genId()

    const update = (newProps: Partial<ToasterToast>) => {
        const index = toasts.value.findIndex((t: ToasterToast) => t.id === id)
        if (index !== -1) {
            toasts.value[index] = { ...toasts.value[index], ...newProps }
        }
    }

    const dismiss = () => {
        const index = toasts.value.findIndex((t: ToasterToast) => t.id === id)
        if (index !== -1) {
            toasts.value[index] = { ...toasts.value[index], open: false }
            addToRemoveQueue(id)
        }
    }

    toasts.value = [
        {
            ...props,
            id,
            open: true,
            onOpenChange: (open: boolean) => {
                if (!open) dismiss()
            },
        },
        ...toasts.value,
    ].slice(0, TOAST_LIMIT)

    return {
        id,
        dismiss,
        update,
    }
}

function useToast() {
    return {
        toasts,
        toast,
        dismiss: (toastId?: string) => {
            if (toastId) {
                const index = toasts.value.findIndex((t: ToasterToast) => t.id === toastId)
                if (index !== -1) {
                    toasts.value[index] = { ...toasts.value[index], open: false }
                    addToRemoveQueue(toastId)
                }
            } else {
                toasts.value.forEach((t: ToasterToast) => {
                    t.open = false
                    addToRemoveQueue(t.id)
                })
            }
        },
    }
}

export { useToast, toast }
