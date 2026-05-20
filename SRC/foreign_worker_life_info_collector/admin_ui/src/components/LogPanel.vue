<script setup>
defineProps({
  logs: {
    type: Array,
    required: true,
  },
})
</script>

<template>
  <section class="control-card p-md">
    <div class="mb-sm flex items-center">
      <h2 class="text-body-md font-semibold">최근 로그</h2>
      <span class="ml-auto text-body-sm text-on-surface-variant">DB에서 불러옴</span>
    </div>
    <div class="divide-y divide-outline-variant font-mono text-mono-data">
      <div v-if="logs.length === 0" class="py-md text-center text-body-sm text-on-surface-variant">데이터 없음</div>
      <div v-for="log in logs" :key="log.id" class="grid grid-cols-[140px_140px_64px_1fr_88px_70px] gap-md py-sm" :class="log.level === 'ERROR' ? 'bg-error-container/30 text-error' : ''">
        <span>{{ log.time }}</span>
        <span class="font-bold" :class="log.level === 'ERROR' ? 'text-error' : 'text-primary'">{{ log.bot }}</span>
        <span class="rounded px-xs text-[10px]" :class="log.level === 'ERROR' ? 'bg-error-container' : log.level === 'WARN' ? 'bg-tertiary-container text-tertiary' : 'bg-emerald-100 text-emerald-700'">{{ log.level }}</span>
        <span>{{ log.message }}</span>
        <span>ID: {{ log.id }}</span>
        <span class="text-right text-on-surface-variant">{{ log.latency }}</span>
      </div>
    </div>
  </section>
</template>
