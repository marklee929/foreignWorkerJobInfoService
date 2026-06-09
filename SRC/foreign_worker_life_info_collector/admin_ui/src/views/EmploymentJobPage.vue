<script setup>
import { computed, onMounted, ref } from 'vue'
import { AlertTriangle, RefreshCw } from '@lucide/vue'
import Header from '../components/Header.vue'
import Sidebar from '../components/Sidebar.vue'
import { navItems } from '../data/defaultAdminState'
import { fetchJobCollectorLogs, fetchJobCollectorStatus, fetchJobPostings, stopJobCollectorScheduler } from '../services/apiClient'
import { logoutAdmin, resetDeviceId } from '../services/authService'

const loading = ref(false)
const stopping = ref(false)
const loadError = ref('')
const actionMessage = ref('')
const status = ref({ status: 'STOPPED', schedulerEnabled: false, authKeyConfigured: false, latest: null, settings: {} })
const postings = ref([])
const logs = ref([])

const latestError = computed(() => status.value.lastErrorMessage || status.value.latest?.errorMessage || '')
const statusLabel = computed(() => {
  if (latestError.value) return '점검중'
  if (status.value.schedulerEnabled) return '스케줄러 켜짐'
  return '추가 예정'
})

function formatDate(value) {
  return value ? String(value).replace('T', ' ').slice(0, 19) : '-'
}

async function loadPage() {
  loading.value = true
  loadError.value = ''
  try {
    const [nextStatus, nextPostings, nextLogs] = await Promise.all([
      fetchJobCollectorStatus(),
      fetchJobPostings(),
      fetchJobCollectorLogs({ limit: 20 }),
    ])
    status.value = nextStatus
    postings.value = nextPostings
    logs.value = nextLogs
  } catch (error) {
    loadError.value = error instanceof Error ? error.message : '채용정보 데이터를 불러오지 못했습니다.'
  } finally {
    loading.value = false
  }
}

async function handleStopScheduler() {
  stopping.value = true
  actionMessage.value = ''
  loadError.value = ''
  try {
    status.value = await stopJobCollectorScheduler()
    actionMessage.value = '채용정보 수집 스케줄러를 중지했습니다.'
    await loadPage()
  } catch (error) {
    loadError.value = error instanceof Error ? error.message : '스케줄러 중지에 실패했습니다.'
  } finally {
    stopping.value = false
  }
}

async function handleLogout() {
  try {
    await logoutAdmin()
  } finally {
    resetDeviceId()
    window.location.replace('/auth?loggedOut=1')
  }
}

onMounted(loadPage)
</script>

<template>
  <div class="min-h-screen bg-surface text-on-surface">
    <Sidebar :nav-items="navItems" @logout="handleLogout" />
    <Header @logout="handleLogout" />

    <main class="ml-[240px] space-y-lg p-lg">
      <section class="control-card p-md">
        <div class="mb-md flex items-start justify-between gap-lg">
          <div>
            <p class="mb-xs text-label-caps text-primary">WorkConnect Admin</p>
            <h1 class="text-display font-black">채용정보</h1>
            <p class="mt-xs text-body-sm text-on-surface-variant">고용24 채용공고 수집기는 API 권한 확인 전까지 점검중으로 유지합니다.</p>
          </div>
          <div class="flex items-center gap-sm">
            <button
              v-if="status.schedulerEnabled"
              class="inline-flex items-center gap-xs rounded border border-error px-md py-xs text-body-sm font-bold text-error disabled:opacity-40"
              type="button"
              :disabled="stopping"
              @click="handleStopScheduler"
            >
              <AlertTriangle :size="15" />
              {{ stopping ? '중지 중' : '스케줄러 중지' }}
            </button>
            <button class="inline-flex items-center gap-xs rounded border border-outline-variant px-md py-xs text-body-sm font-bold disabled:opacity-40" type="button" :disabled="loading" @click="loadPage">
              <RefreshCw :size="15" />
              새로고침
            </button>
          </div>
        </div>

        <section v-if="loadError" class="mb-md rounded border border-error bg-error-container/30 p-sm text-body-sm text-error">{{ loadError }}</section>
        <section v-if="actionMessage" class="mb-md rounded border border-success bg-success/10 p-sm text-body-sm text-success">{{ actionMessage }}</section>

        <div class="mb-md grid grid-cols-4 gap-md">
          <div class="rounded border border-outline-variant bg-white p-md">
            <p class="text-label-caps text-on-surface-variant">상태</p>
            <p class="mt-sm text-headline font-black">{{ statusLabel }}</p>
          </div>
          <div class="rounded border border-outline-variant bg-white p-md">
            <p class="text-label-caps text-on-surface-variant">저장된 채용공고</p>
            <p class="mt-sm text-headline font-black">{{ postings.length }}</p>
          </div>
          <div class="rounded border border-outline-variant bg-white p-md">
            <p class="text-label-caps text-on-surface-variant">API 키</p>
            <p class="mt-sm text-headline font-black">{{ status.authKeyConfigured ? '설정됨' : '미설정' }}</p>
          </div>
          <div class="rounded border border-outline-variant bg-white p-md">
            <p class="text-label-caps text-on-surface-variant">최근 실행</p>
            <p class="mt-sm truncate font-mono text-body-sm">{{ formatDate(status.lastRunAt) }}</p>
          </div>
        </div>

        <div v-if="latestError" class="mb-md rounded border border-tertiary bg-tertiary-container/30 p-md text-body-sm">
          <p class="font-bold text-tertiary">점검 사유</p>
          <p class="mt-xs">{{ latestError }}</p>
        </div>

        <section class="mb-md overflow-hidden rounded border border-outline-variant bg-white">
          <div class="border-b border-outline-variant bg-surface-container-low px-md py-sm">
            <h2 class="text-headline">저장된 채용공고</h2>
          </div>
          <table class="w-full border-collapse text-left text-body-sm">
            <thead class="bg-white text-label-caps text-on-surface-variant">
              <tr>
                <th class="px-md py-sm">공고번호</th>
                <th class="px-md py-sm">회사</th>
                <th class="px-md py-sm">제목</th>
                <th class="px-md py-sm">지역</th>
                <th class="px-md py-sm">마감일</th>
                <th class="px-md py-sm">수집일</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="!postings.length" class="h-16 border-t border-outline-variant">
                <td colspan="6" class="px-md text-center text-on-surface-variant">{{ loading ? '불러오는 중' : '데이터 없음' }}</td>
              </tr>
              <tr v-for="item in postings" :key="item.wanted_auth_no" class="border-t border-outline-variant hover:bg-surface-container-low">
                <td class="px-md py-sm font-mono">{{ item.wanted_auth_no }}</td>
                <td class="px-md py-sm">{{ item.company || '-' }}</td>
                <td class="px-md py-sm font-bold">{{ item.title || '-' }}</td>
                <td class="px-md py-sm">{{ item.region || '-' }}</td>
                <td class="px-md py-sm font-mono">{{ item.close_dt || '-' }}</td>
                <td class="px-md py-sm font-mono">{{ formatDate(item.collected_at) }}</td>
              </tr>
            </tbody>
          </table>
        </section>

        <section class="space-y-sm">
          <h2 class="text-headline">최근 수집 로그</h2>
          <div v-for="log in logs" :key="log.id" class="rounded border border-outline-variant bg-white p-md text-body-sm">
            <div class="flex flex-wrap items-center justify-between gap-md">
              <p class="font-bold">{{ log.status }}</p>
              <p class="font-mono text-on-surface-variant">{{ formatDate(log.startedAt) }} - {{ formatDate(log.endedAt) }}</p>
            </div>
            <p class="mt-xs text-on-surface-variant">수신 {{ log.totalReceived || 0 }} / 신규 {{ log.insertedCount || 0 }} / 갱신 {{ log.updatedCount || 0 }} / 실패 {{ log.failedCount || 0 }}</p>
            <p v-if="log.errorMessage" class="mt-xs text-error">{{ log.errorMessage }}</p>
          </div>
          <p v-if="!logs.length" class="rounded border border-outline-variant bg-white p-md text-center text-body-sm text-on-surface-variant">수집 로그가 없습니다.</p>
        </section>
      </section>
    </main>
  </div>
</template>
