<script setup>
import { computed, ref } from 'vue'
import { useRoute } from 'vue-router'
import Header from '../components/Header.vue'
import Sidebar from '../components/Sidebar.vue'
import { navItems, runtimeConfig as baseRuntimeConfig } from '../data/defaultAdminState'
import { logoutAdmin, resetDeviceId } from '../services/authService'

const route = useRoute()
const runtimeConfig = ref({ ...baseRuntimeConfig, apiConnected: true })

const pageTitle = computed(() => route.meta.title || '작업 화면')
const pageDescription = computed(() => route.meta.description || '이 화면은 기획 정리 후 기능을 연결할 예정입니다.')

async function handleLogout() {
  try {
    await logoutAdmin()
  } finally {
    resetDeviceId()
    window.location.replace('/auth?loggedOut=1')
  }
}
</script>

<template>
  <div class="min-h-screen bg-surface text-on-surface">
    <Sidebar :nav-items="navItems" @logout="handleLogout" />
    <Header :runtime-config="runtimeConfig" @logout="handleLogout" />

    <main class="ml-[240px] p-lg">
      <section class="control-card min-h-[calc(100vh-104px)] p-xl">
        <p class="mb-xs text-label-caps text-primary">WorkConnect Admin</p>
        <h1 class="mb-sm text-display font-black">{{ pageTitle }}</h1>
        <p class="max-w-[680px] text-body-md text-on-surface-variant">{{ pageDescription }}</p>

        <div class="mt-xl grid grid-cols-3 gap-gutter">
          <div class="rounded border border-outline-variant bg-surface-container-low p-md">
            <h2 class="mb-xs text-headline">기획 대기</h2>
            <p class="text-body-sm text-on-surface-variant">화면 구조와 주요 액션을 정의할 영역입니다.</p>
          </div>
          <div class="rounded border border-outline-variant bg-surface-container-low p-md">
            <h2 class="mb-xs text-headline">데이터 연결 대기</h2>
            <p class="text-body-sm text-on-surface-variant">API와 DB 테이블을 확정한 뒤 연결합니다.</p>
          </div>
          <div class="rounded border border-outline-variant bg-surface-container-low p-md">
            <h2 class="mb-xs text-headline">운영 정책 대기</h2>
            <p class="text-body-sm text-on-surface-variant">권한, 실행 조건, 알림 정책을 정리합니다.</p>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>
