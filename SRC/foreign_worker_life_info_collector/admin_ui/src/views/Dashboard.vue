<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { Map, X } from '@lucide/vue'
import Sidebar from '../components/Sidebar.vue'
import Header from '../components/Header.vue'
import StatusCard from '../components/StatusCard.vue'
import BotMonitorCard from '../components/BotMonitorCard.vue'
import DataTable from '../components/DataTable.vue'
import LogPanel from '../components/LogPanel.vue'
import { categoryMix, emptySummary, navItems, runtimeConfig as baseRuntimeConfig } from '../data/defaultAdminState'
import { fetchCandidates, fetchDashboardSummary, fetchLogs, fetchModules } from '../services/apiClient'
import { logoutAdmin, resetDeviceId } from '../services/authService'

const router = useRouter()
const runtimeConfig = ref({ ...baseRuntimeConfig })
const summary = ref({ ...emptySummary })
const modules = ref([])
const candidates = ref([])
const logs = ref([])
const loadError = ref('')
const loading = ref(true)
const dashboardLoaded = ref(false)

const enabledModules = computed(() => modules.value.filter((module) => module.enabled))
const disabledModules = computed(() => modules.value.filter((module) => !module.enabled))

const statusCards = computed(() => [
  { label: '오늘 후보', value: String(summary.value.candidate_count || 0), delta: 'DB', tone: 'primary' },
  { label: '게시 완료', value: String(summary.value.published_count || 0), delta: '테스트 우선', tone: 'neutral' },
  { label: '중복', value: String(summary.value.duplicate_count || 0), delta: '검사됨', tone: 'neutral' },
  { label: '활성 모듈', value: String(summary.value.enabled_module_count || 0), delta: `/${summary.value.module_count || 0}`, tone: 'secondary' },
  { label: '비활성 모듈', value: String(summary.value.disabled_module_count || 0), delta: '호출 안 함', tone: 'tertiary' },
  { label: '실패', value: String(summary.value.failed_count || 0), delta: '현재', tone: 'error' },
  { label: 'DB 상태', value: runtimeConfig.value.apiConnected ? '준비됨' : '확인 중', delta: 'PostgreSQL', tone: 'neutral' },
  { label: 'API', value: runtimeConfig.value.apiConnected ? '켜짐' : '확인 중', delta: loading.value ? '로딩 중' : '읽기 전용', tone: 'ai' },
])

const pipelineMetrics = computed(() => {
  const required = modules.value.filter((module) => module.required)
  const requiredEnabled = required.filter((module) => module.enabled)
  const collectors = modules.value.filter((module) => module.group === 'collector')
  const collectorsEnabled = collectors.filter((module) => module.enabled)
  const publishEnabled = modules.value.some((module) => module.key === 'publish.facebook' && module.enabled)
  const notifyEnabled = modules.value.some((module) => module.key === 'notify.telegram' && module.enabled)

  return [
    {
      label: '필수 단계',
      value: `${requiredEnabled.length}/${required.length}`,
      percent: required.length ? Math.round((requiredEnabled.length / required.length) * 100) : 0,
      tone: 'success',
    },
    {
      label: '활성 수집기',
      value: `${collectorsEnabled.length}/${collectors.length}`,
      percent: collectors.length ? Math.round((collectorsEnabled.length / collectors.length) * 100) : 0,
      tone: 'primary',
    },
    { label: 'Facebook 게시', value: publishEnabled ? '켜짐' : '꺼짐', percent: publishEnabled ? 100 : 0, tone: publishEnabled ? 'success' : 'error' },
    { label: 'Telegram 알림', value: notifyEnabled ? '켜짐' : '꺼짐', percent: notifyEnabled ? 100 : 0, tone: notifyEnabled ? 'success' : 'info' },
  ]
})

const moduleRows = computed(() =>
  modules.value.map((module) => ({
    name: module.name,
    domain: module.group,
    status: module.enabled ? '활성' : '비활성',
    job: module.description || '-',
    count: module.enabled ? '준비됨' : '호출 안 함',
    success: module.required ? '필수' : '선택',
    fail: '0',
    enabled: module.enabled,
    required: module.required,
  })),
)

const candidateRows = computed(() =>
  candidates.value.map((candidate) => ({
    category: candidate.category || '소셜 뉴스',
    region: candidate.region || 'KR',
    title: candidate.title,
    source: candidate.source_name || candidate.source_type || '-',
    score: Number(candidate.evaluation_score || 0).toFixed(2),
    duplicate: candidate.status || '-',
    llama: candidate.duplicate_risk_score ? Number(candidate.duplicate_risk_score).toFixed(2) : '꺼짐',
  })),
)

const logRows = computed(() =>
  logs.value.map((log) => ({
    time: log.time || '-',
    bot: log.bot || '파이프라인',
    level: log.level || 'INFO',
    message: log.message || '',
    id: log.id || '-',
    latency: log.latency || '-',
  })),
)

async function loadDashboard() {
  loading.value = true
  loadError.value = ''
  try {
    const [summaryPayload, modulePayload, candidatePayload, logPayload] = await Promise.all([
      fetchDashboardSummary(),
      fetchModules(),
      fetchCandidates(),
      fetchLogs(),
    ])
    summary.value = { ...emptySummary, ...summaryPayload }
    runtimeConfig.value = {
      ...runtimeConfig.value,
      apiConnected: true,
      database: summaryPayload.database || runtimeConfig.value.database,
    }
    modules.value = modulePayload.map((module) => ({
      key: module.module_key,
      group: module.module_group,
      name: module.module_name,
      description: module.description,
      enabled: Boolean(module.is_enabled),
      required: Boolean(module.is_required),
    }))
    candidates.value = candidatePayload
    logs.value = logPayload
    dashboardLoaded.value = true
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error)
    if (message.includes('관리자 승인이 필요') || message.includes('접속 아이디가 허가')) {
      router.replace('/auth')
      return
    }
    loadError.value = message
    summary.value = { ...emptySummary }
    modules.value = []
    candidates.value = []
    logs.value = []
    runtimeConfig.value = { ...runtimeConfig.value, apiConnected: false }
  } finally {
    loading.value = false
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

onMounted(loadDashboard)
</script>

<template>
  <div class="min-h-screen bg-surface text-on-surface">
    <Sidebar :nav-items="navItems" @logout="handleLogout" />
    <Header :runtime-config="runtimeConfig" @logout="handleLogout" />

    <main class="ml-[240px] space-y-lg p-lg">
      <section v-if="loadError && dashboardLoaded" class="control-card border-error bg-error-container/30 p-md text-body-sm text-error">
        서버 연결이 끊겼습니다. `run.bat` 실행 상태를 확인한 뒤 새로고침해주세요. {{ loadError }}
      </section>

      <section class="grid grid-cols-8 gap-gutter">
        <StatusCard v-for="card in statusCards" :key="card.label" :card="card" />
      </section>

      <BotMonitorCard :pipeline-metrics="pipelineMetrics" :runtime-config="runtimeConfig" />

      <section class="grid grid-cols-12 gap-gutter">
        <div class="control-card col-span-8 p-md">
          <div class="mb-md flex items-center">
            <div>
              <h2 class="text-headline">모듈 실행 정책</h2>
              <p class="text-body-sm text-on-surface-variant">
                화면은 `admin.module_config`를 읽고, 비활성 모듈은 백엔드 실행에서 호출하지 않습니다.
              </p>
            </div>
            <span class="ml-auto rounded bg-primary-fixed px-sm py-xs text-label-caps text-primary">
              {{ enabledModules.length }}개 활성 / 전체 {{ modules.length }}개
            </span>
          </div>

          <div class="grid grid-cols-2 gap-gutter">
            <div class="rounded border border-outline-variant p-md">
              <h3 class="mb-sm text-label-caps text-success">활성 모듈</h3>
              <ul v-if="enabledModules.length" class="space-y-xs text-body-sm">
                <li v-for="module in enabledModules" :key="module.key" class="flex justify-between gap-md">
                  <span class="font-bold">{{ module.key }}</span>
                  <span class="text-on-surface-variant">{{ module.group }}</span>
                </li>
              </ul>
              <p v-else class="text-body-sm text-on-surface-variant">데이터 없음</p>
            </div>
            <div class="rounded border border-outline-variant p-md">
              <h3 class="mb-sm text-label-caps text-error">비활성 모듈</h3>
              <ul v-if="disabledModules.length" class="space-y-xs text-body-sm">
                <li v-for="module in disabledModules" :key="module.key" class="flex justify-between gap-md">
                  <span class="font-bold">{{ module.key }}</span>
                  <span class="text-on-surface-variant">호출 안 함</span>
                </li>
              </ul>
              <p v-else class="text-body-sm text-on-surface-variant">데이터 없음</p>
            </div>
          </div>
        </div>

        <aside class="control-card col-span-4 p-md">
          <h2 class="mb-md text-headline">연결 상태</h2>
          <dl class="space-y-sm text-body-sm">
            <div class="flex justify-between"><dt>데이터베이스</dt><dd class="font-mono font-bold">{{ runtimeConfig.database }}</dd></div>
            <div class="flex justify-between"><dt>스키마</dt><dd class="font-mono">{{ runtimeConfig.schemas.join(', ') }}</dd></div>
            <div class="flex justify-between"><dt>API 어댑터</dt><dd :class="runtimeConfig.apiConnected ? 'text-success' : 'text-on-surface-variant'">{{ runtimeConfig.apiConnected ? '연결됨' : '확인 중' }}</dd></div>
            <div class="flex justify-between"><dt>모드</dt><dd class="rounded bg-surface-container px-xs">{{ runtimeConfig.dryRun ? '테스트 실행' : '실행' }}</dd></div>
          </dl>
          <button class="mt-md rounded border border-outline-variant px-md py-xs text-body-sm" type="button" @click="loadDashboard">
            새로고침
          </button>
        </aside>
      </section>

      <DataTable title="DB 모듈 상태" :rows="moduleRows" type="module" />

      <LogPanel :logs="logRows" />

      <section class="grid grid-cols-12 gap-gutter">
        <div class="control-card col-span-9 overflow-hidden">
          <div class="flex gap-gutter border-b border-outline-variant bg-white p-md">
            <label class="flex flex-col gap-xs text-label-caps text-on-surface-variant">
              카테고리
              <select class="w-36 rounded border border-outline-variant bg-white px-sm py-xs text-body-sm text-on-surface" disabled>
                <option>소셜 뉴스</option>
              </select>
            </label>
            <label class="flex flex-col gap-xs text-label-caps text-on-surface-variant">
              지역
              <select class="w-36 rounded border border-outline-variant bg-white px-sm py-xs text-body-sm text-on-surface" disabled>
                <option>KR</option>
              </select>
            </label>
            <label class="flex flex-col gap-xs text-label-caps text-on-surface-variant">
              최소 점수
              <select class="w-36 rounded border border-outline-variant bg-white px-sm py-xs text-body-sm text-on-surface" disabled>
                <option>API 필터 대기</option>
              </select>
            </label>
            <button class="mt-5 rounded bg-primary-fixed px-md py-xs text-body-sm font-bold text-primary opacity-60" disabled>필터</button>
            <button class="mt-5 rounded bg-primary-container px-md py-xs text-body-sm font-bold text-white opacity-60" disabled>내보내기</button>
          </div>
          <DataTable :rows="candidateRows" />
        </div>

        <aside class="control-card col-span-3 p-md">
          <div class="mb-md flex items-center">
            <h2 class="text-headline">선택된 후보</h2>
            <X class="ml-auto" :size="20" />
          </div>
          <p class="mb-sm text-label-caps">데이터 출처</p>
          <div class="mb-md h-36 overflow-hidden rounded border border-outline-variant bg-surface-container-low p-md text-body-sm text-on-surface-variant">
            행은 `social_news.candidate`에서 불러옵니다. 테이블이 비어 있으면 후보 목록에 데이터 없음이 표시됩니다.
          </div>
          <p class="mb-sm text-label-caps">현재 상태</p>
          <a class="mb-md block truncate text-body-sm font-bold text-primary" href="#">읽기 전용 API 연결됨</a>
          <div class="rounded border border-secondary-fixed-dim bg-secondary-fixed/30 p-md text-body-sm text-secondary">
            <p class="mb-xs font-bold">백엔드 보호</p>
            <p>비활성 모듈은 UI뿐 아니라 백엔드에서도 차단해야 합니다.</p>
          </div>
          <button class="mt-lg w-full rounded bg-primary-container px-md py-sm text-body-sm font-bold text-white opacity-60" disabled>게시 결과 대기</button>
        </aside>
      </section>

      <section class="grid grid-cols-12 gap-gutter">
        <div class="control-card col-span-8 p-lg">
          <div class="mb-md flex items-center">
            <h2 class="text-headline">지역 데이터 분포</h2>
            <div class="ml-auto flex gap-md text-[11px]">
              <span><i class="mr-xs inline-block h-2 w-2 rounded-full bg-primary-container"></i>수집기</span>
              <span><i class="mr-xs inline-block h-2 w-2 rounded-full bg-secondary-container"></i>파이프라인</span>
              <span><i class="mr-xs inline-block h-2 w-2 rounded-full bg-tertiary-container"></i>채널</span>
            </div>
          </div>
          <div class="flex h-[300px] items-center justify-center rounded border border-dashed border-outline-variant bg-surface-container-low text-center text-on-surface-variant">
            <div>
              <Map class="mx-auto mb-md text-outline" :size="72" />
              <p class="text-headline">지역 후보 데이터가 아직 없습니다</p>
              <p class="text-body-sm">파이프라인 행이 생성될 때까지 패널은 비어 있습니다.</p>
            </div>
          </div>
        </div>

        <div class="control-card col-span-4 p-lg">
          <h2 class="mb-lg text-headline">모듈 구성</h2>
          <div class="space-y-md">
            <div v-for="item in categoryMix" :key="item.label">
              <div class="mb-xs flex justify-between text-body-sm font-bold">
                <span>{{ item.label }}</span>
                <span>{{ item.value }}%</span>
              </div>
              <div class="h-3 rounded-full bg-surface-container">
                <div class="h-3 rounded-full" :class="item.color" :style="{ width: item.value + '%' }"></div>
              </div>
            </div>
          </div>
          <div class="mt-lg border-t border-outline-variant pt-lg text-body-md text-on-surface-variant">
            기본 운영 모드는 읽기 전용이며 테스트 실행을 우선합니다.
          </div>
        </div>
      </section>
    </main>
  </div>
</template>
