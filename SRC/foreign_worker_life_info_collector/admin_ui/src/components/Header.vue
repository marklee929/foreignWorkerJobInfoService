<script setup>
import { Bell, LogOut, Settings } from '@lucide/vue'

defineProps({
  serverStatus: {
    type: String,
    default: 'ok',
  },
  serverMessage: {
    type: String,
    default: '',
  },
})

defineEmits(['logout'])
</script>

<template>
  <header class="sticky top-0 z-40 ml-[240px] flex h-14 items-center justify-end border-b border-outline-variant bg-white px-lg">
    <div class="flex items-center gap-sm">
      <span
        v-if="serverStatus !== 'ok'"
        class="rounded-sm border border-error/40 bg-error-container/40 px-sm py-xxs text-label-sm font-bold text-error"
        :title="serverMessage"
      >
        서버접속불가
      </span>
      <button class="rounded p-xs hover:bg-surface-container-low" type="button" aria-label="알림">
        <Bell :size="18" />
      </button>
      <button class="rounded p-xs hover:bg-surface-container-low" type="button" aria-label="설정">
        <Settings :size="18" />
      </button>
      <button class="rounded p-xs text-error hover:bg-error-container/30" type="button" aria-label="로그아웃" @click="$emit('logout')">
        <LogOut :size="18" />
      </button>
    </div>
  </header>
</template>
