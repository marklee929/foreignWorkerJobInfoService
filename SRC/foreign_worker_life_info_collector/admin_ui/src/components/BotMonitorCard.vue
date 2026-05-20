<script setup>
import { Cpu, FileStack } from '@lucide/vue'

defineProps({
  pipelineMetrics: {
    type: Array,
    required: true,
  },
  runtimeConfig: {
    type: Object,
    required: true,
  },
})
</script>

<template>
  <section class="grid grid-cols-12 gap-gutter">
    <div class="control-card col-span-4 p-md">
      <div class="mb-md flex items-center gap-sm">
        <Cpu class="text-primary" :size="20" />
        <h2 class="text-headline">로컬 LLaMA</h2>
        <span class="ml-auto rounded bg-surface-container px-sm py-xs text-[10px] font-bold text-on-surface-variant">설정 기반</span>
      </div>
      <dl class="space-y-sm text-body-sm">
        <div class="flex justify-between"><dt>모듈</dt><dd class="font-mono font-bold">step.llama_check</dd></div>
        <div class="flex justify-between"><dt>엔드포인트</dt><dd class="font-mono">LOCAL_LLAMA_ENDPOINT</dd></div>
        <div class="flex justify-between"><dt>정책</dt><dd class="font-mono text-primary">비활성 시 호출 안 함</dd></div>
        <div class="flex justify-between"><dt>모드</dt><dd class="rounded bg-surface-container px-xs">{{ runtimeConfig.dryRun ? '테스트 실행' : '실행' }}</dd></div>
      </dl>
      <div class="mt-md border-t border-outline-variant pt-md">
        <p class="rounded border border-secondary-fixed-dim bg-secondary-fixed/30 px-sm py-xs text-body-sm text-secondary">
          백엔드에서 해당 모듈을 활성화하기 전까지 외부 호출은 꺼져 있습니다.
        </p>
      </div>
    </div>

    <div class="control-card col-span-8 p-md">
      <div class="mb-md flex items-center gap-sm">
        <FileStack class="text-secondary" :size="20" />
        <h2 class="text-headline">소셜 뉴스 파이프라인</h2>
        <a class="ml-auto text-body-sm text-primary" href="#">읽기 전용 상태</a>
      </div>
      <div class="grid grid-cols-3 gap-gutter">
        <div class="flex h-[88px] items-center justify-center rounded border border-outline-variant bg-surface-container-low text-center text-body-md">
          수집 -> 정규화 -> 요약<br />-> 중복 검사 -> 평가 -> 게시
        </div>
        <div class="col-span-2 grid grid-cols-2 gap-gutter">
          <div v-for="metric in pipelineMetrics" :key="metric.label" class="rounded border border-outline-variant p-sm">
            <p class="mb-sm text-label-caps text-on-surface-variant">{{ metric.label }}</p>
            <div class="flex items-center gap-sm">
              <div class="h-2 flex-1 rounded-full bg-surface-container">
                <div class="h-2 rounded-full" :class="metric.tone === 'error' ? 'bg-error' : metric.tone === 'primary' ? 'bg-primary-container' : 'bg-success'" :style="{ width: metric.percent + '%' }"></div>
              </div>
              <span class="font-mono text-mono-data font-bold" :class="metric.tone === 'error' ? 'text-error' : 'text-success'">{{ metric.value }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>
