<script setup lang="ts">
import { ref, provide, onMounted, onUnmounted, type HTMLAttributes } from 'vue'
import useEmblaCarousel, { type EmblaCarouselType } from 'embla-carousel-vue'
import { cn } from '@/lib/utils'

export interface CarouselProps {
  opts?: any
  plugins?: any
  orientation?: 'horizontal' | 'vertical'
  class?: HTMLAttributes['class']
}

const props = withDefaults(defineProps<CarouselProps>(), {
  orientation: 'horizontal',
})

const emits = defineEmits<{
  (e: 'init-api', api: EmblaCarouselType): void
}>()

const [emblaRef, emblaApi] = useEmblaCarousel(
  {
    ...props.opts,
    axis: props.orientation === 'horizontal' ? 'x' : 'y',
  },
  props.plugins
)

const canScrollPrev = ref(false)
const canScrollNext = ref(false)

function onSelect(api: EmblaCarouselType) {
  if (!api) return
  canScrollPrev.value = api.canScrollPrev()
  canScrollNext.value = api.canScrollNext()
}

function scrollPrev() {
  emblaApi.value?.scrollPrev()
}

function scrollNext() {
  emblaApi.value?.scrollNext()
}

function handleKeyDown(event: KeyboardEvent) {
  if (event.key === 'ArrowLeft') {
    event.preventDefault()
    scrollPrev()
  } else if (event.key === 'ArrowRight') {
    event.preventDefault()
    scrollNext()
  }
}

onMounted(() => {
  if (!emblaApi.value) return
  onSelect(emblaApi.value)
  emblaApi.value.on('reInit', onSelect)
  emblaApi.value.on('select', onSelect)
  emits('init-api', emblaApi.value)
})

onUnmounted(() => {
  emblaApi.value?.off('select', onSelect)
})

provide('carousel-context', {
  emblaRef,
  emblaApi,
  orientation: props.orientation,
  canScrollPrev,
  canScrollNext,
  scrollPrev,
  scrollNext,
})
</script>

<template>
  <div
    :class="cn('relative', props.class)"
    role="region"
    aria-roledescription="carousel"
    data-slot="carousel"
    @keydown="handleKeyDown"
  >
    <slot />
  </div>
</template>
