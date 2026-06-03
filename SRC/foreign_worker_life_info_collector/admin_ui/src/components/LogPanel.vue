<script setup>
import { ref } from 'vue'

defineProps({
  logs: {
    type: Array,
    required: true,
  },
  loadingMore: {
    type: Boolean,
    default: false,
  },
  hasMore: {
    type: Boolean,
    default: true,
  },
})

const emit = defineEmits(['load-more'])
const scroller = ref(null)
const isDragging = ref(false)
let dragStartY = 0
let dragStartScrollTop = 0

function formatLogTime(value) {
  if (!value || value === '-') {
    return '-'
  }
  const date = new Date(value)
  if (!Number.isNaN(date.getTime())) {
    const parts = new Intl.DateTimeFormat('sv-SE', {
      timeZone: 'Asia/Seoul',
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: false,
    }).formatToParts(date)
    const byType = Object.fromEntries(parts.map((part) => [part.type, part.value]))
    return `${byType.year}-${byType.month}-${byType.day} ${byType.hour}:${byType.minute}:${byType.second}`
  }
  const text = String(value)
  return text.replace('T', ' ').slice(0, 19)
}

function requestMoreIfNeeded() {
  const element = scroller.value
  if (!element) {
    return
  }
  const nearBottom = element.scrollTop + element.clientHeight >= element.scrollHeight - 48
  if (nearBottom) {
    emit('load-more')
  }
}

function handlePointerDown(event) {
  const element = scroller.value
  if (!element) {
    return
  }
  isDragging.value = true
  dragStartY = event.clientY
  dragStartScrollTop = element.scrollTop
  element.setPointerCapture?.(event.pointerId)
}

function handlePointerMove(event) {
  if (!isDragging.value || !scroller.value) {
    return
  }
  event.preventDefault()
  scroller.value.scrollTop = dragStartScrollTop - (event.clientY - dragStartY)
}

function handlePointerUp(event) {
  if (!isDragging.value) {
    return
  }
  isDragging.value = false
  try {
    scroller.value?.releasePointerCapture?.(event.pointerId)
  } catch {
    // Pointer capture may already be released by the browser.
  }
  requestMoreIfNeeded()
}
</script>

<template>
  <section class="control-card overflow-hidden">
    <div class="flex items-center border-b border-outline-variant bg-white px-md py-sm">
      <div>
        <h2 class="text-headline">실시간 운영 로그</h2>
        <p class="text-body-sm text-on-surface-variant">수집, 요약, 중복 검사, 평가, 게시, 채용정보 수집 상태를 최신순으로 확인합니다.</p>
      </div>
      <span class="ml-auto rounded bg-surface-container px-sm py-xs text-label-caps text-on-surface-variant">최신 로그</span>
    </div>

    <div
      ref="scroller"
      class="scrollbar-hidden h-[292px] cursor-grab select-none overflow-y-auto divide-y divide-outline-variant font-mono text-mono-data active:cursor-grabbing"
      :class="isDragging ? 'cursor-grabbing' : ''"
      @scroll.passive="requestMoreIfNeeded"
      @pointerdown="handlePointerDown"
      @pointermove="handlePointerMove"
      @pointerup="handlePointerUp"
      @pointercancel="handlePointerUp"
      @pointerleave="handlePointerUp"
    >
      <div v-if="logs.length === 0" class="py-lg text-center text-body-sm text-on-surface-variant">데이터 없음</div>
      <div
        v-for="log in logs"
        :key="log.id"
        class="grid grid-cols-[150px_120px_72px_minmax(0,1fr)_86px] gap-md px-md py-sm"
        :class="log.level === 'ERROR' ? 'bg-error-container/30 text-error' : ''"
      >
        <span class="whitespace-nowrap">{{ formatLogTime(log.time) }}</span>
        <span class="font-bold" :class="log.level === 'ERROR' ? 'text-error' : 'text-primary'">{{ log.bot }}</span>
        <span
          class="rounded px-xs text-center text-[10px]"
          :class="log.level === 'ERROR' ? 'bg-error-container text-error' : log.level === 'WARN' ? 'bg-tertiary-container text-tertiary' : 'bg-emerald-100 text-emerald-700'"
        >
          {{ log.level }}
        </span>
        <span class="truncate">{{ log.message }}</span>
        <span class="text-right text-on-surface-variant">{{ log.latency }}</span>
      </div>
      <div v-if="loadingMore" class="px-md py-sm text-center text-body-sm text-on-surface-variant">이전 로그를 불러오는 중입니다.</div>
      <div v-else-if="!hasMore && logs.length > 0" class="px-md py-sm text-center text-body-sm text-on-surface-variant">더 불러올 로그가 없습니다.</div>
    </div>
  </section>
</template>
