<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { statusGuideFor, statusMeta } from '../data/statusCodes'

const props = defineProps({
  scope: {
    type: String,
    default: '',
  },
  codes: {
    type: Array,
    default: () => [],
  },
  title: {
    type: String,
    default: '상태 코드',
  },
})

const items = computed(() => {
  const scoped = statusGuideFor(props.scope, props.codes)
  return scoped.length ? scoped : props.codes.map((code) => statusMeta(code))
})

const root = ref(null)
const hovering = ref(false)
const pinned = ref(false)
const open = computed(() => hovering.value || pinned.value)

function togglePinned() {
  if (pinned.value) {
    close()
    return
  }
  pinned.value = true
  hovering.value = true
}

function close() {
  pinned.value = false
  hovering.value = false
}

function handlePointerDown(event) {
  if (!pinned.value || root.value?.contains(event.target)) {
    return
  }
  close()
}

function handleKeydown(event) {
  if (event.key === 'Escape' && pinned.value) {
    close()
  }
}

onMounted(() => {
  document.addEventListener('pointerdown', handlePointerDown)
  document.addEventListener('keydown', handleKeydown)
})

onBeforeUnmount(() => {
  document.removeEventListener('pointerdown', handlePointerDown)
  document.removeEventListener('keydown', handleKeydown)
})
</script>

<template>
  <span
    ref="root"
    class="relative inline-flex align-middle"
    @mouseenter="hovering = true"
    @mouseleave="hovering = false"
  >
    <button
      class="inline-flex h-5 w-5 items-center justify-center rounded-full border border-outline-variant bg-white text-[11px] font-black text-on-surface-variant shadow-sm transition hover:border-primary hover:text-primary focus:border-primary focus:outline-none"
      :class="pinned ? 'border-primary text-primary' : ''"
      type="button"
      :aria-label="`${title} 보기`"
      :aria-expanded="open"
      @click.stop="togglePinned"
    >
      ?
    </button>
    <span
      class="absolute left-0 top-6 z-50 w-[340px] rounded-md border border-outline-variant bg-white p-sm text-left text-body-sm font-normal text-on-surface shadow-lg transition"
      :class="open ? 'pointer-events-auto opacity-100' : 'pointer-events-none opacity-0'"
      role="tooltip"
      @click.stop
    >
      <span class="mb-xs flex items-center justify-between gap-sm">
        <span class="block text-label-caps text-primary">{{ title }}</span>
        <button v-if="pinned" class="rounded border border-outline-variant px-xs py-[1px] text-[10px] font-bold text-on-surface-variant" type="button" @click="close">
          닫기
        </button>
      </span>
      <span class="grid max-h-[360px] gap-xs overflow-y-auto">
        <span v-for="item in items" :key="item.code" class="grid grid-cols-[18px_92px_minmax(0,1fr)] gap-xs">
          <span class="mt-[5px] h-2.5 w-2.5 rounded-full" :class="item.dot"></span>
          <code class="font-mono text-[10px] text-on-surface-variant">{{ item.code }}</code>
          <span>
            <b>{{ item.label }}</b>
            <span class="block text-[11px] leading-4 text-on-surface-variant">{{ item.description }}</span>
          </span>
        </span>
      </span>
    </span>
  </span>
</template>
