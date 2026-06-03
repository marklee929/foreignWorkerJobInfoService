<script setup>
import { computed } from 'vue'
import { Cpu, Power, RotateCw } from '@lucide/vue'

const props = defineProps({
  botStatus: {
    type: Object,
    required: true,
  },
  llamaStatus: {
    type: Object,
    required: true,
  },
  busy: {
    type: Boolean,
    default: false,
  },
})

defineEmits(['toggle-bot', 'reset-bot-error', 'reconnect-llama'])

const llamaLabelMap = {
  CONNECTED: '연결됨',
  DISCONNECTED: '연결 안 됨',
  STARTING: '시작 중',
  ERROR: '오류',
  DISABLED: '비활성',
}

const llamaStatusLabel = computed(() => llamaLabelMap[props.llamaStatus.status] || props.llamaStatus.status || '확인 중')
const botIsRunning = computed(() => props.botStatus.status === 'RUNNING' || props.botStatus.status === 'STARTING')
const botIsChanging = computed(() => props.busy || props.botStatus.status === 'STARTING' || props.botStatus.status === 'STOPPING')
</script>

<template>
  <section class="grid grid-cols-12 gap-gutter">
    <div class="control-card col-span-5 p-md">
      <div class="mb-md flex items-center gap-sm">
        <Power class="text-primary" :size="20" />
        <h2 class="text-headline">소셜 뉴스 봇 상태</h2>
        <span
          class="ml-auto rounded px-sm py-xs text-[10px] font-bold"
          :class="botStatus.status === 'ERROR' ? 'bg-error-container text-error' : botIsRunning ? 'bg-emerald-100 text-emerald-700' : 'bg-surface-container text-on-surface-variant'"
        >
          {{ botStatus.status === 'ERROR' ? '장애 발생' : botStatus.label }}
        </span>
      </div>

      <div class="flex items-center justify-between rounded border border-outline-variant bg-surface-container-low p-md">
        <div>
          <p class="text-body-sm text-on-surface-variant">소셜 뉴스 봇</p>
          <p class="text-display font-black">{{ botStatus.label }}</p>
        </div>
        <button
          class="relative h-8 w-16 rounded-full transition disabled:cursor-not-allowed disabled:opacity-60"
          :class="botIsRunning ? 'bg-success' : 'bg-outline'"
          type="button"
          :disabled="botIsChanging"
          @click="$emit('toggle-bot')"
          aria-label="소셜 뉴스 봇 시작 또는 종료"
        >
          <span class="absolute top-1 h-6 w-6 rounded-full bg-white transition" :class="botIsRunning ? 'left-9' : 'left-1'"></span>
        </button>
      </div>

      <p v-if="botStatus.lastErrorMessage" class="mt-md rounded border border-error bg-error-container/30 p-sm text-body-sm text-error">
        마지막 오류: {{ botStatus.lastErrorMessage }}
      </p>
      <button v-if="botStatus.status === 'ERROR'" class="mt-md rounded border border-outline-variant px-md py-xs text-body-sm" type="button" @click="$emit('reset-bot-error')">
        장애 초기화
      </button>
    </div>

    <div class="control-card col-span-7 p-md">
      <div class="mb-md flex items-center gap-sm">
        <Cpu class="text-primary" :size="20" />
        <h2 class="text-headline">로컬 LLaMA</h2>
        <span class="ml-auto rounded bg-surface-container px-sm py-xs text-[10px] font-bold text-on-surface-variant">
          {{ llamaStatus.message }}
        </span>
      </div>
      <dl class="grid grid-cols-2 gap-gutter text-body-sm">
        <div class="rounded border border-outline-variant p-sm">
          <dt class="text-on-surface-variant">상태</dt>
          <dd class="font-bold">{{ llamaStatusLabel }}</dd>
        </div>
        <div class="rounded border border-outline-variant p-sm">
          <dt class="text-on-surface-variant">모델</dt>
          <dd class="font-mono">{{ llamaStatus.model }}</dd>
        </div>
        <div class="col-span-2 rounded border border-outline-variant p-sm">
          <dt class="text-on-surface-variant">엔드포인트</dt>
          <dd class="font-mono">{{ llamaStatus.endpoint }}</dd>
        </div>
      </dl>
      <button class="mt-md inline-flex items-center gap-xs rounded border border-outline-variant px-md py-xs text-body-sm" type="button" @click="$emit('reconnect-llama')">
        <RotateCw :size="14" />
        LLaMA 재연결
      </button>
    </div>
  </section>
</template>
