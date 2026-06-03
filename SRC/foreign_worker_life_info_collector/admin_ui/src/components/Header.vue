<script setup>
import { Bell, LogOut, Settings } from '@lucide/vue'

defineEmits(['logout'])
</script>

<template>
  <header class="sticky top-0 z-40 ml-[240px] flex h-14 items-center justify-end border-b border-outline-variant bg-white px-lg">
    <div class="flex items-center gap-sm">
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
