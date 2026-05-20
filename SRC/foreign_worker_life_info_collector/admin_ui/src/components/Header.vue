<script setup>
import { Bell, LogOut, Search, Settings } from '@lucide/vue'

defineProps({
  runtimeConfig: {
    type: Object,
    required: true,
  },
})

defineEmits(['logout'])
</script>

<template>
  <header class="sticky top-0 z-40 ml-[240px] flex h-14 items-center justify-between border-b border-outline-variant bg-white px-lg">
    <div class="relative">
      <Search class="absolute left-md top-1/2 -translate-y-1/2 text-outline" :size="17" />
      <input
        class="w-[300px] rounded border border-outline-variant bg-surface-container-low py-xs pl-10 pr-md text-body-sm focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
        type="text"
        :value="runtimeConfig.defaultKeyword"
        readonly
      />
    </div>

    <div class="flex items-center gap-lg">
      <div v-if="runtimeConfig.apiConnected" class="flex items-center gap-xs rounded border border-primary/20 bg-primary-container/10 px-md py-xs">
        <span class="h-2 w-2 rounded-full" :class="runtimeConfig.apiConnected ? 'bg-success' : 'bg-tertiary'"></span>
        <span class="text-label-caps text-primary">
          API: 연결됨 | DB: {{ runtimeConfig.database }} | 테스트 우선
        </span>
      </div>
      <div class="flex items-center gap-sm">
        <button class="rounded p-xs hover:bg-surface-container-low" aria-label="알림">
          <Bell :size="18" />
        </button>
        <button class="rounded p-xs hover:bg-surface-container-low" aria-label="설정">
          <Settings :size="18" />
        </button>
        <button class="rounded p-xs text-error hover:bg-error-container/30" type="button" aria-label="로그아웃" @click="$emit('logout')">
          <LogOut :size="18" />
        </button>
      </div>
    </div>
  </header>
</template>
