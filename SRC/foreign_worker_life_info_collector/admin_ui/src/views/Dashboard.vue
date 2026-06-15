<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { Cpu } from '@lucide/vue'
import Sidebar from '../components/Sidebar.vue'
import Header from '../components/Header.vue'
import StatusCard from '../components/StatusCard.vue'
import LogPanel from '../components/LogPanel.vue'
import { emptySummary, navItems, runtimeConfig as baseRuntimeConfig } from '../data/defaultAdminState'
import {
  fetchBotStatus,
  fetchCandidates,
  fetchDashboardSummary,
  fetchFacebookStatus,
  fetchImmigrationBotStatus,
  fetchJobCollectorLogs,
  fetchJobCollectorStatus,
  fetchLifestyleBotStatus,
  fetchLlamaStatus,
  fetchLogs,
  fetchModules,
  fetchOccupationDashboard,
  reconnectLlama,
  resetBotError,
  startBot,
  startImmigrationBot,
  startJobCollectorScheduler,
  startLifestyleBot,
  startLlama,
  stopBot,
  stopImmigrationBot,
  stopJobCollectorScheduler,
  stopLifestyleBot,
  stopLlama,
} from '../services/apiClient'
import { logoutAdmin, resetDeviceId } from '../services/authService'

const runtimeConfig = ref({ ...baseRuntimeConfig })
const summary = ref({ ...emptySummary })
const modules = ref([])
const candidates = ref([])
const logs = ref([])
const jobLogs = ref([])
const botStatus = ref({ status: 'STOPPED', label: '중지됨', lastErrorMessage: '' })
const lifestyleBotStatus = ref({ status: 'STOPPED', label: '중지됨', lastErrorMessage: '' })
const immigrationBotStatus = ref({ status: 'STOPPED', label: '중지됨', lastErrorMessage: '' })
const facebookStatus = ref({ page_id: '', page_token_fingerprint: '', page_token_masked: '', page_token_env_key: 'FACEBOOK_PAGE_ACCESS_TOKEN' })
const jobCollectorStatus = ref({ status: 'STOPPED', schedulerEnabled: false, latest: null, settings: {} })
const occupationDashboard = ref({ job_count: 0, occupation_count: 0, latest_status: null })
const llamaStatus = ref({ enabled: false, connected: false, endpoint: '-', model: '-', status: 'DISABLED', message: '로컬 LLaMA 비활성' })
const loadError = ref('')
const loading = ref(true)
const botBusy = ref(false)
const lifestyleBotBusy = ref(false)
const immigrationBotBusy = ref(false)
const jobBusy = ref(false)
const llamaBusy = ref(false)
const dashboardLoaded = ref(false)
const loadingMoreLogs = ref(false)
const hasMoreLogs = ref(true)
const visibleLogCount = ref(10)
const LOG_PAGE_SIZE = 10
const DASHBOARD_TTL_MS = 30000
let refreshTimer = null
let lastDashboardLoadAt = 0

const statusCards = computed(() => [
  { label: '전체 뉴스', value: String(summary.value.candidate_count || 0), delta: '누적', tone: 'primary' },
  { label: '자동 후보', value: String(summary.value.today_ready_count || 0), delta: '24H READY', tone: 'secondary' },
  { label: '누적 게시', value: String(summary.value.published_count || 0), delta: '누적', tone: 'neutral' },
  { label: '전날 만료', value: String(summary.value.previous_post_expired_count || 0), delta: 'POST_EXPIRED', tone: 'tertiary' },
  { label: '게시 만료', value: String(summary.value.post_expired_count || 0), delta: '누적', tone: 'neutral' },
  { label: '실패', value: String(summary.value.failed_count || 0), delta: '오류', tone: 'error' },
])

const publishStatusItems = computed(() => [
  { label: '24h 수집/갱신', value: summary.value.today_article_count || 0 },
  { label: '평균 점수', value: Number(summary.value.avg_score || 0).toFixed(2) },
  { label: '현재 threshold', value: summary.value.current_threshold || 50 },
  { label: '자동 후보', value: summary.value.ready_count || summary.value.today_ready_count || 0 },
  { label: '재시도 후보', value: summary.value.retryable_count || 0 },
  { label: '24h 게시 완료', value: summary.value.posted_today_count || 0 },
  { label: 'COOLDOWN', value: summary.value.cooldown_active ? '대기 중' : '게시 가능' },
  { label: '다음 게시 가능', value: summary.value.next_publish_at || '-' },
])

const recentCandidates = computed(() =>
  candidates.value.slice(0, 8).map((candidate) => ({
    id: candidate.id || candidate.title,
    category: candidate.category || '소셜 뉴스',
    title: candidate.title || '제목 없음',
    source: candidate.source_name || candidate.source_type || '-',
    score: Number(candidate.evaluation_score || 0).toFixed(2),
    status: candidate.status || '대기',
    facebookUrl: candidate.facebook_post_url || '',
  })),
)

const combinedLogRows = computed(() => {
  const socialRows = logs.value.map((log) => ({
    time: log.time || '-',
    bot: log.bot || '소셜 뉴스 봇',
    level: log.level || 'INFO',
    message: log.message || '',
    id: `social-${log.id || log.time || log.message}`,
    latency: log.latency || '-',
  }))
  const jobRows = jobLogs.value.map((log) => {
    const failed = Number(log.failedCount || 0)
    const message = [
      `채용정보 수집 ${log.status}`,
      `수신 ${log.totalReceived || 0}건`,
      `신규 ${log.insertedCount || 0}건`,
      `업데이트 ${log.updatedCount || 0}건`,
      `스킵 ${log.skippedCount || 0}건`,
      failed ? `실패 ${failed}건` : '',
      log.errorMessage || '',
    ]
      .filter(Boolean)
      .join(' / ')
    return {
      time: log.endedAt || log.startedAt || '-',
      bot: '채용정보 봇',
      level: failed ? 'ERROR' : 'INFO',
      message,
      id: `job-${log.id}`,
      latency: `${log.pageFrom || 1}-${log.pageTo || 1}`,
    }
  })
  return [...socialRows, ...jobRows]
    .sort((a, b) => String(b.time).localeCompare(String(a.time)))
})

const logRows = computed(() => combinedLogRows.value.slice(0, visibleLogCount.value))
const llamaActive = computed(() => llamaStatus.value.status === 'CONNECTED' || llamaStatus.value.status === 'STARTING')
const llamaToggleLabel = computed(() => (llamaActive.value ? 'LLaMA 끄기' : 'LLaMA 켜기'))
const llamaServerTypeLabel = computed(() => (llamaStatus.value.managed === false ? '외부 서버' : '동일 서버'))

const botCards = computed(() => [
  {
    key: 'social-news',
    name: '소셜 뉴스 봇',
    description: '뉴스 수집, 요약, 게시',
    status: botStatus.value.status,
    active: botStatus.value.status === 'RUNNING' || botStatus.value.status === 'STARTING',
    error: botStatus.value.status === 'ERROR',
    busy: botBusy.value,
    toggle: handleToggleBot,
    detail: botStatus.value.lastErrorMessage || `Facebook token fp=${facebookStatus.value.page_token_fingerprint || '-'} / page=${facebookStatus.value.page_id || '-'}`,
  },
  {
    key: 'occupation-dictionary',
    name: '직업정보 봇',
    description: '고용24 직업/직무 사전',
    status: occupationDashboard.value.latest_status || 'READY',
    active: Number(occupationDashboard.value.occupation_count || 0) > 0 || Number(occupationDashboard.value.job_count || 0) > 0,
    readonly: true,
    detail: `직업정보 ${occupationDashboard.value.occupation_count || 0}건 / 직무정보 ${occupationDashboard.value.job_count || 0}건`,
  },
  { key: 'content-bot', name: '콘텐츠 생성 봇', description: '추가 예정', status: 'PLANNED', active: false, planned: true },
  {
    key: 'lifestyle-bot',
    name: '생활정보 봇',
    description: '생활/정착 후보 수집',
    status: lifestyleBotStatus.value.status,
    active: lifestyleBotStatus.value.status === 'RUNNING' || lifestyleBotStatus.value.status === 'STARTING',
    error: lifestyleBotStatus.value.status === 'ERROR',
    busy: lifestyleBotBusy.value,
    toggle: handleToggleLifestyleBot,
    detail: lifestyleBotStatus.value.lastErrorMessage || lifestyleBotStatus.value.message || '생활정보 카테고리 수집 대기',
  },
  {
    key: 'immigration-bot',
    name: '출입국 봇',
    description: '법무부/하이코리아 공식 공지 수집',
    status: immigrationBotStatus.value.status,
    active: immigrationBotStatus.value.status === 'RUNNING' || immigrationBotStatus.value.status === 'STARTING',
    error: immigrationBotStatus.value.status === 'ERROR',
    busy: immigrationBotBusy.value,
    toggle: handleToggleImmigrationBot,
    detail: immigrationBotStatus.value.lastErrorMessage || immigrationBotStatus.value.message || '공식 출처 수집 대기',
  },
  {
    key: 'job-collector',
    name: '채용정보 봇',
    description: '고용24 채용공고 수집 - 점검중',
    status: 'PLANNED',
    active: false,
    planned: true,
    detail: jobCollectorStatus.value.lastErrorMessage || '기업회원 API 권한 확인 후 다시 활성화',
  },
])

function normalizeBotPayload(payload) {
  const labelMap = {
    RUNNING: '실행 중',
    STOPPED: '중지됨',
    ERROR: '장애',
    STARTING: '시작 중',
    STOPPING: '종료 중',
  }
  const status = payload?.status || 'STOPPED'
  return {
    ...payload,
    status,
    label: labelMap[status] || payload?.label || status,
  }
}

function llamaStatusLabel(status) {
  const map = {
    CONNECTED: '연결됨',
    DISCONNECTED: '연결 안 됨',
    STARTING: '시작 중',
    STOPPING: '종료 중',
    ERROR: '오류',
    DISABLED: '꺼짐',
  }
  return map[status] || status || '확인 중'
}

function uniqueLogKey(log) {
  return log.id || `${log.time || log.startedAt}-${log.message || log.status || ''}`
}

function mergeUniqueLogs(target, nextItems, prepend = false) {
  const seen = new Set()
  const merged = prepend ? [...nextItems, ...target.value] : [...target.value, ...nextItems]
  target.value = merged.filter((item) => {
    const key = uniqueLogKey(item)
    if (seen.has(key)) {
      return false
    }
    seen.add(key)
    return true
  }).slice(0, 120)
}

async function loadOperationalLogs({ reset = false } = {}) {
  if (loadingMoreLogs.value) {
    return
  }
  loadingMoreLogs.value = true
  try {
    if (reset) {
      logs.value = []
      jobLogs.value = []
      visibleLogCount.value = LOG_PAGE_SIZE
      hasMoreLogs.value = true
    }
    const [socialResult, jobResult] = await Promise.allSettled([
      fetchLogs({ limit: LOG_PAGE_SIZE, offset: logs.value.length }),
      fetchJobCollectorLogs({ limit: LOG_PAGE_SIZE, offset: jobLogs.value.length }),
    ])
    const socialPage = socialResult.status === 'fulfilled' ? socialResult.value : []
    const jobPage = jobResult.status === 'fulfilled' ? jobResult.value : []
    mergeUniqueLogs(logs, socialPage)
    mergeUniqueLogs(jobLogs, jobPage)
    hasMoreLogs.value = socialPage.length === LOG_PAGE_SIZE || jobPage.length === LOG_PAGE_SIZE
  } finally {
    loadingMoreLogs.value = false
  }
}

async function refreshLatestLogs() {
  const [socialResult, jobResult] = await Promise.allSettled([
    fetchLogs({ limit: LOG_PAGE_SIZE, offset: 0 }),
    fetchJobCollectorLogs({ limit: LOG_PAGE_SIZE, offset: 0 }),
  ])
  const socialPage = socialResult.status === 'fulfilled' ? socialResult.value : []
  const jobPage = jobResult.status === 'fulfilled' ? jobResult.value : []
  mergeUniqueLogs(logs, socialPage, true)
  mergeUniqueLogs(jobLogs, jobPage, true)
}

async function handleLoadMoreLogs() {
  if (loadingMoreLogs.value) {
    return
  }
  if (!hasMoreLogs.value && visibleLogCount.value >= combinedLogRows.value.length) {
    return
  }
  visibleLogCount.value += LOG_PAGE_SIZE
  if (visibleLogCount.value >= combinedLogRows.value.length - 2 && hasMoreLogs.value) {
    await loadOperationalLogs()
  }
}

async function loadDashboard({ silent = false } = {}) {
  const now = Date.now()
  if (silent && dashboardLoaded.value && now - lastDashboardLoadAt < DASHBOARD_TTL_MS) {
    return
  }
  if (silent && document.hidden) {
    return
  }
  if (!silent) {
    loading.value = true
  }
  loadError.value = ''
  const requests = [
    ['summary', fetchDashboardSummary],
    ['modules', fetchModules],
    ['candidates', fetchCandidates],
    ['bot', fetchBotStatus],
    ['lifestyleBot', fetchLifestyleBotStatus],
    ['immigrationBot', fetchImmigrationBotStatus],
    ['llama', fetchLlamaStatus],
    ['jobCollector', fetchJobCollectorStatus],
    ['occupation', fetchOccupationDashboard],
    ['facebook', fetchFacebookStatus],
  ]
  try {
    const settled = await Promise.allSettled(requests.map(([, request]) => request()))
    const failed = settled
      .map((result, index) => ({ result, key: requests[index][0] }))
      .filter((item) => item.result.status === 'rejected')
    if (failed.length) {
      const firstError = failed[0].result.reason
      const message = firstError instanceof Error ? firstError.message : String(firstError)
      if (message.includes('관리자 승인') || message.includes('접속 승인') || message.includes('unauthorized')) {
        window.location.replace('/auth')
        return
      }
      loadError.value = `서버접속불가: ${failed.map((item) => item.key).join(', ')}`
      console.warn('[dashboard] API request failed', failed.map((item) => ({ key: item.key, reason: item.result.reason?.message || String(item.result.reason) })))
      runtimeConfig.value = { ...runtimeConfig.value, apiConnected: false }
    } else {
      runtimeConfig.value = { ...runtimeConfig.value, apiConnected: true }
    }

    const value = (key, fallback) => {
      const index = requests.findIndex((item) => item[0] === key)
      return settled[index]?.status === 'fulfilled' ? settled[index].value : fallback
    }
    const summaryPayload = value('summary', summary.value)
    const modulePayload = value('modules', modules.value)
    const candidatePayload = value('candidates', { items: candidates.value })
    const botPayload = value('bot', botStatus.value)
    const lifestyleBotPayload = value('lifestyleBot', lifestyleBotStatus.value)
    const immigrationBotPayload = value('immigrationBot', immigrationBotStatus.value)
    const llamaPayload = value('llama', llamaStatus.value)
    const jobPayload = value('jobCollector', jobCollectorStatus.value)
    const occupationPayload = value('occupation', occupationDashboard.value)
    const facebookPayload = value('facebook', facebookStatus.value)

    summary.value = { ...emptySummary, ...summaryPayload }
    runtimeConfig.value = {
      ...runtimeConfig.value,
      database: summaryPayload.database || runtimeConfig.value.database,
    }
    modules.value = modulePayload
    candidates.value = candidatePayload.items || candidatePayload
    botStatus.value = normalizeBotPayload(botPayload)
    lifestyleBotStatus.value = normalizeBotPayload(lifestyleBotPayload)
    immigrationBotStatus.value = normalizeBotPayload(immigrationBotPayload)
    llamaStatus.value = llamaPayload
    jobCollectorStatus.value = jobPayload
    occupationDashboard.value = occupationPayload
    facebookStatus.value = facebookPayload
    if (!dashboardLoaded.value) {
      await loadOperationalLogs({ reset: true })
    } else {
      await refreshLatestLogs()
    }
    dashboardLoaded.value = true
    lastDashboardLoadAt = Date.now()
  } catch (error) {
    loadError.value = `서버접속불가: ${error instanceof Error ? error.message : String(error)}`
    runtimeConfig.value = { ...runtimeConfig.value, apiConnected: false }
  } finally {
    loading.value = false
  }
}

async function handleToggleBot() {
  botBusy.value = true
  try {
    if (botStatus.value.status === 'ERROR') {
      botStatus.value = normalizeBotPayload(await resetBotError())
    }
    const payload = botStatus.value.status === 'RUNNING' || botStatus.value.status === 'STARTING' ? await stopBot() : await startBot()
    botStatus.value = normalizeBotPayload(payload)
    await loadDashboard({ silent: true })
  } finally {
    botBusy.value = false
  }
}

async function handleToggleLifestyleBot() {
  lifestyleBotBusy.value = true
  try {
    const active = lifestyleBotStatus.value.status === 'RUNNING' || lifestyleBotStatus.value.status === 'STARTING'
    const payload = active ? await stopLifestyleBot() : await startLifestyleBot()
    lifestyleBotStatus.value = normalizeBotPayload(payload)
    await loadDashboard({ silent: true })
  } finally {
    lifestyleBotBusy.value = false
  }
}

async function handleToggleImmigrationBot() {
  immigrationBotBusy.value = true
  try {
    const active = immigrationBotStatus.value.status === 'RUNNING' || immigrationBotStatus.value.status === 'STARTING'
    const payload = active ? await stopImmigrationBot() : await startImmigrationBot()
    immigrationBotStatus.value = normalizeBotPayload(payload)
    await loadDashboard({ silent: true })
  } finally {
    immigrationBotBusy.value = false
  }
}

async function handleToggleJobCollector() {
  jobBusy.value = true
  try {
    if (jobCollectorStatus.value.schedulerEnabled) {
      await stopJobCollectorScheduler()
    } else {
      await startJobCollectorScheduler()
    }
    await loadDashboard({ silent: true })
  } finally {
    jobBusy.value = false
  }
}

async function handleReconnectLlama() {
  llamaBusy.value = true
  try {
    llamaStatus.value = await reconnectLlama()
  } finally {
    llamaBusy.value = false
  }
}

async function handleToggleLlama() {
  llamaBusy.value = true
  try {
    llamaStatus.value = llamaActive.value ? await stopLlama() : await startLlama()
    await loadDashboard({ silent: true })
  } finally {
    llamaBusy.value = false
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

onMounted(() => {
  loadDashboard()
  refreshTimer = window.setInterval(() => loadDashboard({ silent: true }), DASHBOARD_TTL_MS)
  document.addEventListener('visibilitychange', handleVisibilityChange)
})

onBeforeUnmount(() => {
  if (refreshTimer) {
    window.clearInterval(refreshTimer)
  }
  document.removeEventListener('visibilitychange', handleVisibilityChange)
})

function handleVisibilityChange() {
  if (!document.hidden) {
    loadDashboard({ silent: true })
  }
}
</script>

<template>
  <div class="min-h-screen bg-surface text-on-surface">
    <Sidebar :nav-items="navItems" @logout="handleLogout" />
    <Header :server-status="loadError ? 'error' : 'ok'" :server-message="loadError" @logout="handleLogout" />

    <main class="ml-[240px] space-y-lg p-lg">
      <section class="grid grid-cols-6 gap-gutter">
        <StatusCard v-for="card in statusCards" :key="card.label" :card="card" />
      </section>

      <section class="control-card overflow-hidden">
        <div class="flex items-center border-b border-outline-variant bg-white px-md py-sm">
          <div>
            <h2 class="text-headline">게시기 상태</h2>
            <p class="text-body-sm text-on-surface-variant">오늘 수집된 미게시 기사 전체를 기준으로 1시간마다 1건을 선택합니다.</p>
          </div>
        </div>
        <div class="grid grid-cols-9 gap-sm p-md">
          <div v-for="item in publishStatusItems" :key="item.label" class="rounded border border-outline-variant bg-surface-container-low p-sm">
            <p class="text-label-caps text-on-surface-variant">{{ item.label }}</p>
            <p class="mt-xs truncate text-body-md font-black">{{ item.value }}</p>
          </div>
        </div>
      </section>

      <section class="control-card overflow-hidden">
        <div class="flex items-center border-b border-outline-variant bg-white px-md py-sm">
          <div>
            <h2 class="text-headline">봇 상태</h2>
            <p class="text-body-sm text-on-surface-variant">운영 봇은 ON/OFF만 제어하고, 아직 미구현 봇은 자리만 표시합니다.</p>
          </div>
          <span class="ml-auto rounded bg-surface-container px-sm py-xs text-label-caps text-on-surface-variant">
            {{ botCards.filter((bot) => bot.active).length }}개 활동 중
          </span>
        </div>

        <div class="max-h-[220px] overflow-y-auto">
          <div class="flex min-w-full gap-gutter overflow-x-auto p-md">
            <article
              v-for="bot in botCards"
              :key="bot.key"
              class="min-w-[260px] rounded border border-outline-variant bg-surface-container-low p-sm"
            >
              <div class="flex items-start justify-between gap-md">
                <div class="min-w-0">
                  <h3 class="truncate text-body-md font-black">{{ bot.name }}</h3>
                  <p class="mt-xs truncate text-body-sm text-on-surface-variant">{{ bot.description }}</p>
                </div>
                <span
                  class="shrink-0 rounded px-sm py-[2px] text-[10px] font-bold"
                  :class="bot.error ? 'bg-error-container text-error' : bot.active ? 'bg-emerald-100 text-emerald-700' : 'bg-white text-on-surface-variant'"
                >
                  {{ bot.planned ? '추가 예정' : bot.active ? '활동 중' : '활동 안 함' }}
                </span>
              </div>

              <div class="mt-md flex items-center justify-between">
                <p class="min-w-0 truncate text-body-sm" :class="bot.error ? 'text-error' : 'text-on-surface-variant'">{{ bot.detail }}</p>
                <button
                  v-if="!bot.planned && bot.toggle"
                  class="relative h-8 w-16 shrink-0 rounded-full transition disabled:cursor-not-allowed disabled:opacity-60"
                  :class="bot.active ? 'bg-success' : 'bg-outline'"
                  type="button"
                  :disabled="bot.busy"
                  :aria-label="`${bot.name} 켜기 또는 끄기`"
                  @click="bot.toggle"
                >
                  <span class="absolute top-1 h-6 w-6 rounded-full bg-white transition" :class="bot.active ? 'left-9' : 'left-1'"></span>
                </button>
              </div>
            </article>
          </div>
        </div>
      </section>

      <section class="grid grid-cols-12 gap-gutter">
        <section class="control-card col-span-4 self-start p-md">
          <div class="mb-md flex items-start justify-between gap-md">
            <div class="flex min-w-0 items-center gap-sm">
              <Cpu class="text-primary" :size="20" />
              <div class="min-w-0">
                <h2 class="text-headline">로컬 LLaMA</h2>
                <p class="mt-xs truncate text-body-sm text-on-surface-variant">{{ llamaStatus.message }}</p>
              </div>
            </div>
            <button
              class="relative h-8 w-16 shrink-0 rounded-full transition disabled:cursor-not-allowed disabled:opacity-60"
              :class="llamaActive ? 'bg-success' : 'bg-outline'"
              type="button"
              :disabled="llamaBusy"
              :aria-label="llamaToggleLabel"
              @click="handleToggleLlama"
            >
              <span class="absolute top-1 h-6 w-6 rounded-full bg-white transition" :class="llamaActive ? 'left-9' : 'left-1'"></span>
            </button>
          </div>

          <div class="mb-md flex items-center justify-between rounded border border-outline-variant bg-surface-container-low px-sm py-xs">
            <span class="text-label-caps text-on-surface-variant">전원</span>
            <span class="text-body-sm font-black" :class="llamaActive ? 'text-success' : 'text-on-surface-variant'">
              {{ llamaBusy ? '처리 중' : llamaActive ? 'ON' : 'OFF' }}
            </span>
          </div>

          <dl class="space-y-xs text-body-sm">
            <div class="flex items-center justify-between gap-md rounded border border-outline-variant px-sm py-xs">
              <dt class="text-on-surface-variant">상태</dt>
              <dd class="font-bold">{{ llamaStatusLabel(llamaStatus.status) }}</dd>
            </div>
            <div class="flex items-center justify-between gap-md rounded border border-outline-variant px-sm py-xs">
              <dt class="text-on-surface-variant">모델</dt>
              <dd class="truncate font-mono">{{ llamaStatus.model }}</dd>
            </div>
            <div class="rounded border border-outline-variant px-sm py-xs">
              <dt class="text-on-surface-variant">엔드포인트</dt>
              <dd class="mt-xs truncate font-mono">{{ llamaStatus.endpoint }}</dd>
            </div>
            <div class="flex items-center justify-between gap-md rounded border border-outline-variant px-sm py-xs">
              <dt class="text-on-surface-variant">서버 유형</dt>
              <dd class="font-bold">{{ llamaServerTypeLabel }}</dd>
            </div>
          </dl>

          <div class="mt-md flex items-center gap-sm">
            <button
              class="rounded border border-outline-variant px-md py-xs text-body-sm disabled:cursor-not-allowed disabled:opacity-50"
              type="button"
              :disabled="llamaBusy"
              @click="handleReconnectLlama"
            >
              재연결
            </button>
            <span class="text-body-sm text-on-surface-variant">OFF 시 모델 메모리 해제 요청</span>
          </div>
        </section>

        <div class="col-span-8">
          <LogPanel :logs="logRows" :has-more="hasMoreLogs" :loading-more="loadingMoreLogs" @load-more="handleLoadMoreLogs" />
        </div>
      </section>

      <section class="control-card overflow-hidden">
        <div class="flex items-center border-b border-outline-variant bg-white px-md py-sm">
          <div>
            <h2 class="text-headline">최근 후보 기사</h2>
            <p class="text-body-sm text-on-surface-variant">수집된 후보의 제목, 출처, 평가 점수, 처리 상태를 확인합니다.</p>
          </div>
          <button class="ml-auto rounded border border-outline-variant px-md py-xs text-body-sm" type="button" :disabled="loading" @click="loadDashboard()">
            새로고침
          </button>
        </div>

        <table class="w-full border-collapse text-left text-body-sm">
          <thead class="bg-white text-label-caps text-on-surface-variant">
            <tr>
              <th class="px-md py-sm">분류</th>
              <th class="px-md py-sm">제목</th>
              <th class="px-md py-sm">출처</th>
              <th class="px-md py-sm">점수</th>
              <th class="px-md py-sm">Facebook</th>
              <th class="px-md py-sm">상태</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="recentCandidates.length === 0" class="h-14 border-t border-outline-variant">
              <td class="px-md text-center text-on-surface-variant" colspan="6">데이터 없음</td>
            </tr>
            <tr v-for="candidate in recentCandidates" :key="candidate.id" class="h-10 border-t border-outline-variant hover:bg-surface-container-low">
              <td class="px-md">{{ candidate.category }}</td>
              <td class="px-md font-bold">{{ candidate.title }}</td>
              <td class="px-md text-on-surface-variant">{{ candidate.source }}</td>
              <td class="px-md font-mono font-bold text-success">{{ candidate.score }}</td>
              <td class="px-md">
                <a v-if="candidate.facebookUrl" class="font-bold text-primary" :href="candidate.facebookUrl" target="_blank" rel="noreferrer">게시글</a>
                <span v-else class="text-on-surface-variant">-</span>
              </td>
              <td class="px-md text-on-surface-variant">{{ candidate.status }}</td>
            </tr>
          </tbody>
        </table>
      </section>
    </main>
  </div>
</template>
