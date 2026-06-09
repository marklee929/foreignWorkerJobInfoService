<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { Database, FileSearch, KeyRound, ListChecks, RefreshCw, Search, TableProperties, X } from '@lucide/vue'
import Header from '../components/Header.vue'
import Sidebar from '../components/Sidebar.vue'
import { navItems } from '../data/defaultAdminState'
import {
  collectOccupationJobs,
  collectOccupations,
  fetchKeywordMappings,
  fetchOccupationCollectLogs,
  fetchOccupationDashboard,
  fetchOccupationJobs,
  fetchOccupations,
  generateKeywordMappings,
} from '../services/apiClient'
import { logoutAdmin, resetDeviceId } from '../services/authService'

const PAGE_SIZE = 100

const activeTab = ref('dashboard')
const loading = ref(false)
const actionBusy = ref('')
const loadError = ref('')
const actionMessage = ref('')
const dashboard = ref({})
const jobs = ref({ items: [], total_count: 0, page: 1, size: PAGE_SIZE })
const occupations = ref({ items: [], total_count: 0, page: 1, size: PAGE_SIZE })
const mappings = ref({ items: [], total_count: 0, page: 1, size: PAGE_SIZE })
const logs = ref([])
const detail = ref(null)
const filters = reactive({ keyword: '', active_yn: '', language_code: '' })

const tabs = [
  { key: 'dashboard', label: '대시보드', icon: Database },
  { key: 'jobs', label: '직무정보', icon: TableProperties },
  { key: 'occupations', label: '직업정보', icon: FileSearch },
  { key: 'mappings', label: '검색어 매핑', icon: KeyRound },
  { key: 'logs', label: '수집 로그', icon: ListChecks },
]

const cards = computed(() => [
  { label: '직무정보', value: dashboard.value.job_count || 0 },
  { label: '직업정보', value: dashboard.value.occupation_count || 0 },
  { label: '검색어 매핑', value: dashboard.value.keyword_mapping_count || 0 },
  { label: '실패 로그', value: dashboard.value.failed_count || 0 },
])

const latestJobLog = computed(() => logs.value.find((log) => log.collector_type === 'JOB') || null)
const jobMissingReason = computed(() => {
  if (Number(dashboard.value.job_count || 0) > 0) return ''
  if (latestJobLog.value?.error_message) return latestJobLog.value.error_message
  if (latestJobLog.value) return `최근 직무정보 수집 결과가 ${latestJobLog.value.status}이고 저장된 항목이 없습니다.`
  return '직무정보 수집 로그가 없습니다. 현재 직업정보 492건은 고용24 직업정보 API에서 수집됐고, 직무정보는 별도 API 키/서비스 권한 또는 엔드포인트 확인이 필요합니다.'
})

const visibleRows = computed(() => {
  if (activeTab.value === 'jobs') return jobs.value.items || []
  if (activeTab.value === 'occupations') return occupations.value.items || []
  if (activeTab.value === 'mappings') return mappings.value.items || []
  if (activeTab.value === 'logs') return logs.value || []
  return []
})

const visibleTotal = computed(() => {
  if (activeTab.value === 'jobs') return Number(jobs.value.total_count || 0)
  if (activeTab.value === 'occupations') return Number(occupations.value.total_count || 0)
  if (activeTab.value === 'mappings') return Number(mappings.value.total_count || 0)
  if (activeTab.value === 'logs') return visibleRows.value.length
  return 0
})

const currentPage = computed(() => {
  if (activeTab.value === 'jobs') return Number(jobs.value.page || 1)
  if (activeTab.value === 'occupations') return Number(occupations.value.page || 1)
  if (activeTab.value === 'mappings') return Number(mappings.value.page || 1)
  return 1
})

const currentSize = computed(() => {
  if (activeTab.value === 'jobs') return Number(jobs.value.size || PAGE_SIZE)
  if (activeTab.value === 'occupations') return Number(occupations.value.size || PAGE_SIZE)
  if (activeTab.value === 'mappings') return Number(mappings.value.size || PAGE_SIZE)
  return PAGE_SIZE
})

const totalPages = computed(() => Math.max(1, Math.ceil(visibleTotal.value / Math.max(1, currentSize.value))))
const rowStart = computed(() => (currentPage.value - 1) * currentSize.value)
const currentRangeText = computed(() => {
  if (!visibleTotal.value) return '0-0'
  return `${rowStart.value + 1}-${Math.min(rowStart.value + visibleRows.value.length, visibleTotal.value)}`
})

function formatDate(value) {
  return value ? String(value).replace('T', ' ').slice(0, 19) : '-'
}

function rawPreview(value, limit = 3000) {
  if (!value) return '{}'
  if (typeof value === 'string') return value.slice(0, limit)
  return JSON.stringify(value, null, 2).slice(0, limit)
}

function openDetail(type, item, index = null) {
  detail.value = { type, item, index }
}

function closeDetail() {
  detail.value = null
}

async function loadDashboard() {
  dashboard.value = await fetchOccupationDashboard()
}

async function loadJobs(page = jobs.value.page || 1) {
  jobs.value = await fetchOccupationJobs({ page, size: PAGE_SIZE, keyword: filters.keyword, active_yn: filters.active_yn })
}

async function loadOccupations(page = occupations.value.page || 1) {
  occupations.value = await fetchOccupations({ page, size: PAGE_SIZE, keyword: filters.keyword, active_yn: filters.active_yn })
}

async function loadMappings(page = mappings.value.page || 1) {
  mappings.value = await fetchKeywordMappings({ page, size: PAGE_SIZE, keyword: filters.keyword, language_code: filters.language_code })
}

async function loadLogs() {
  logs.value = await fetchOccupationCollectLogs({ limit: 200 })
}

async function loadCurrent() {
  loading.value = true
  loadError.value = ''
  closeDetail()
  try {
    await loadDashboard()
    if (activeTab.value === 'dashboard') await loadLogs()
    if (activeTab.value === 'jobs') await loadJobs()
    if (activeTab.value === 'occupations') await loadOccupations()
    if (activeTab.value === 'mappings') await loadMappings()
    if (activeTab.value === 'logs') await loadLogs()
  } catch (error) {
    loadError.value = error instanceof Error ? error.message : '직업정보 데이터를 불러오지 못했습니다.'
  } finally {
    loading.value = false
  }
}

async function switchTab(tab) {
  activeTab.value = tab
  filters.keyword = ''
  filters.active_yn = ''
  filters.language_code = ''
  jobs.value.page = 1
  occupations.value.page = 1
  mappings.value.page = 1
  await loadCurrent()
}

async function searchCurrent() {
  jobs.value.page = 1
  occupations.value.page = 1
  mappings.value.page = 1
  await loadCurrent()
}

async function goPage(page) {
  const nextPage = Math.max(1, Math.min(totalPages.value, page))
  loading.value = true
  loadError.value = ''
  closeDetail()
  try {
    if (activeTab.value === 'jobs') await loadJobs(nextPage)
    if (activeTab.value === 'occupations') await loadOccupations(nextPage)
    if (activeTab.value === 'mappings') await loadMappings(nextPage)
  } catch (error) {
    loadError.value = error instanceof Error ? error.message : '페이지를 불러오지 못했습니다.'
  } finally {
    loading.value = false
  }
}

async function runCollect(type) {
  actionBusy.value = type
  actionMessage.value = ''
  loadError.value = ''
  try {
    const result = type === 'jobs'
      ? await collectOccupationJobs({ pageFrom: 1, pageTo: 1, size: 100 })
      : await collectOccupations({ pageFrom: 1, pageTo: 1, size: 100 })
    actionMessage.value = `${type === 'jobs' ? '직무정보' : '직업정보'} 수집 완료: ${result.status}, 신규 ${result.insertedCount || 0}건, 갱신 ${result.updatedCount || 0}건, 실패 ${result.failedCount || 0}건`
    await searchCurrent()
  } catch (error) {
    loadError.value = error instanceof Error ? error.message : '수집 실행에 실패했습니다.'
  } finally {
    actionBusy.value = ''
  }
}

async function runGenerateMappings() {
  actionBusy.value = 'mappings'
  actionMessage.value = ''
  loadError.value = ''
  try {
    const result = await generateKeywordMappings()
    actionMessage.value = `검색어 매핑 생성 완료: ${result.inserted_count || 0}건 추가`
    await searchCurrent()
  } catch (error) {
    loadError.value = error instanceof Error ? error.message : '검색어 매핑 생성에 실패했습니다.'
  } finally {
    actionBusy.value = ''
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

onMounted(loadCurrent)
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
            <h1 class="text-display font-black">직업정보</h1>
            <p class="mt-xs text-body-sm text-on-surface-variant">고용24 직업정보와 직무정보를 수집하고 외국인 사용자의 검색어 매핑을 관리합니다.</p>
          </div>
          <div class="flex items-center gap-sm">
            <button class="inline-flex items-center gap-xs rounded border border-outline-variant px-md py-xs text-body-sm font-bold disabled:opacity-40" type="button" :disabled="actionBusy === 'jobs'" @click="runCollect('jobs')">
              <RefreshCw :size="15" />
              {{ actionBusy === 'jobs' ? '직무 수집 중' : '직무정보 수집' }}
            </button>
            <button class="inline-flex items-center gap-xs rounded border border-outline-variant px-md py-xs text-body-sm font-bold disabled:opacity-40" type="button" :disabled="actionBusy === 'occupations'" @click="runCollect('occupations')">
              <RefreshCw :size="15" />
              {{ actionBusy === 'occupations' ? '직업 수집 중' : '직업정보 수집' }}
            </button>
            <button class="inline-flex items-center gap-xs rounded border border-outline-variant px-md py-xs text-body-sm" type="button" :disabled="loading" @click="loadCurrent">
              <RefreshCw :size="15" />
              새로고침
            </button>
          </div>
        </div>

        <div class="mb-md flex flex-wrap gap-sm">
          <button
            v-for="tab in tabs"
            :key="tab.key"
            class="inline-flex items-center gap-xs rounded border px-md py-xs text-body-sm font-bold"
            :class="activeTab === tab.key ? 'border-primary bg-primary-container text-white' : 'border-outline-variant text-on-surface-variant'"
            type="button"
            @click="switchTab(tab.key)"
          >
            <component :is="tab.icon" :size="15" />
            {{ tab.label }}
          </button>
        </div>

        <section v-if="loadError" class="mb-md rounded border border-error bg-error-container/30 p-sm text-body-sm text-error">{{ loadError }}</section>
        <section v-if="actionMessage" class="mb-md rounded border border-success bg-success/10 p-sm text-body-sm text-success">{{ actionMessage }}</section>

        <section v-if="activeTab === 'dashboard'" class="space-y-md">
          <div class="grid grid-cols-4 gap-md">
            <div v-for="card in cards" :key="card.label" class="rounded border border-outline-variant bg-white p-md">
              <p class="text-label-caps text-on-surface-variant">{{ card.label }}</p>
              <p class="mt-sm text-display font-black">{{ card.value }}</p>
            </div>
          </div>

          <div v-if="jobMissingReason" class="rounded border border-tertiary bg-tertiary-container/30 p-md text-body-sm">
            <p class="font-bold text-tertiary">직무정보 수집 안 된 이유</p>
            <p class="mt-xs">{{ jobMissingReason }}</p>
          </div>

          <div class="rounded border border-outline-variant bg-white p-md text-body-sm">
            <p>최근 수집 시간: <span class="font-mono">{{ formatDate(dashboard.latest_collected_at) }}</span></p>
            <p>최근 수집 상태: <span class="font-bold">{{ dashboard.latest_status || '-' }}</span></p>
          </div>

          <div class="rounded border border-outline-variant bg-white p-md">
            <h2 class="text-headline">검색어 매핑이 필요한 이유</h2>
            <p class="mt-xs text-body-sm text-on-surface-variant">외국인 사용자는 직업명을 고용24 표준명 그대로 검색하지 않습니다. 매핑은 사용자 표현을 표준 직업/직무 코드로 연결해서 검색, 추천, 콘텐츠 분류가 같은 기준을 쓰게 만듭니다.</p>
            <div class="mt-md grid grid-cols-[1fr_40px_1fr_40px_1fr_40px_1fr] items-stretch gap-sm text-body-sm">
              <div class="rounded border border-outline-variant bg-surface-container-low p-sm"><p class="font-bold">사용자 표현</p><p class="mt-xs text-on-surface-variant">welder, 용접, factory job</p></div>
              <div class="flex items-center justify-center font-black text-primary">→</div>
              <div class="rounded border border-outline-variant bg-surface-container-low p-sm"><p class="font-bold">정규화</p><p class="mt-xs text-on-surface-variant">소문자화, 공백 정리, 동의어 처리</p></div>
              <div class="flex items-center justify-center font-black text-primary">→</div>
              <div class="rounded border border-outline-variant bg-surface-container-low p-sm"><p class="font-bold">표준 코드 연결</p><p class="mt-xs text-on-surface-variant">job_code 또는 occupation_code</p></div>
              <div class="flex items-center justify-center font-black text-primary">→</div>
              <div class="rounded border border-outline-variant bg-surface-container-low p-sm"><p class="font-bold">서비스 사용</p><p class="mt-xs text-on-surface-variant">검색, 추천, 콘텐츠 분류</p></div>
            </div>
          </div>
        </section>

        <section v-else class="space-y-md">
          <div class="flex items-center gap-md rounded border border-outline-variant bg-surface-container-low px-md py-sm">
            <Search class="text-outline" :size="18" />
            <input v-model="filters.keyword" class="min-w-0 flex-1 bg-transparent text-body-sm outline-none" type="search" placeholder="코드, 이름, 설명, raw response 검색" @keydown.enter="searchCurrent" />
            <select v-if="activeTab !== 'mappings' && activeTab !== 'logs'" v-model="filters.active_yn" class="rounded border border-outline-variant bg-white px-sm py-xs text-body-sm" @change="searchCurrent">
              <option value="">전체</option>
              <option value="Y">활성</option>
              <option value="N">비활성</option>
            </select>
            <select v-if="activeTab === 'mappings'" v-model="filters.language_code" class="rounded border border-outline-variant bg-white px-sm py-xs text-body-sm" @change="searchCurrent">
              <option value="">전체 언어</option>
              <option value="ko">ko</option>
              <option value="en">en</option>
            </select>
            <button class="rounded border border-outline-variant px-md py-xs text-body-sm font-bold" type="button" @click="searchCurrent">검색</button>
            <button v-if="activeTab === 'mappings'" class="rounded border border-outline-variant px-md py-xs text-body-sm font-bold" type="button" :disabled="actionBusy === 'mappings'" @click="runGenerateMappings">
              자동 생성
            </button>
          </div>

          <div class="flex items-center justify-between rounded border border-outline-variant bg-white px-md py-sm text-body-sm">
            <span class="font-bold">{{ tabs.find((tab) => tab.key === activeTab)?.label }} 전체 {{ visibleTotal }}건 / 현재 {{ currentRangeText }} / {{ currentPage }}쪽</span>
            <span class="text-on-surface-variant">행을 클릭하면 상세정보를 확인합니다.</span>
          </div>

          <div v-if="activeTab === 'jobs' && jobMissingReason" class="rounded border border-tertiary bg-tertiary-container/30 p-sm text-body-sm">
            <span class="font-bold text-tertiary">미수집 사유: </span>{{ jobMissingReason }}
          </div>

          <div v-if="activeTab === 'mappings'" class="rounded border border-outline-variant bg-white p-md text-body-sm">
            <p class="font-bold">매핑 상세정보</p>
            <p class="mt-xs text-on-surface-variant">각 매핑 행은 외부 검색어, 정규화된 검색어, 연결된 직무/직업 코드, 매핑 출처, 우선순위, 점수를 저장합니다.</p>
          </div>

          <div v-if="activeTab === 'jobs'" class="overflow-hidden rounded border border-outline-variant bg-white">
            <table class="w-full border-collapse text-left text-body-sm">
              <thead class="bg-surface-container-low text-label-caps text-on-surface-variant">
                <tr><th class="px-md py-sm">#</th><th class="px-md py-sm">job_code</th><th class="px-md py-sm">job_name_ko</th><th class="px-md py-sm">job_name_en</th><th class="px-md py-sm">category</th><th class="px-md py-sm">active</th><th class="px-md py-sm">updated_at</th></tr>
              </thead>
              <tbody>
                <tr v-if="!jobs.items.length" class="h-16 border-t border-outline-variant"><td colspan="7" class="px-md text-center text-on-surface-variant">{{ loading ? '불러오는 중' : '데이터 없음' }}</td></tr>
                <tr v-for="(item, index) in jobs.items" :key="item.id" class="cursor-pointer border-t border-outline-variant align-top hover:bg-surface-container-low" @click="openDetail('직무정보', item, rowStart + index + 1)">
                  <td class="px-md py-sm font-mono text-on-surface-variant">{{ rowStart + index + 1 }}</td>
                  <td class="px-md py-sm font-mono">{{ item.job_code }}</td>
                  <td class="px-md py-sm font-bold">{{ item.job_name_ko }}</td>
                  <td class="px-md py-sm">{{ item.job_name_en || '-' }}</td>
                  <td class="px-md py-sm">{{ item.job_category_name || item.job_category_code || '-' }}</td>
                  <td class="px-md py-sm">{{ item.active_yn }}</td>
                  <td class="px-md py-sm font-mono">{{ formatDate(item.updated_at) }}</td>
                </tr>
              </tbody>
            </table>
          </div>

          <div v-if="activeTab === 'occupations'" class="overflow-hidden rounded border border-outline-variant bg-white">
            <table class="w-full border-collapse text-left text-body-sm">
              <thead class="bg-surface-container-low text-label-caps text-on-surface-variant">
                <tr><th class="px-md py-sm">#</th><th class="px-md py-sm">occupation_code</th><th class="px-md py-sm">occupation_name_ko</th><th class="px-md py-sm">category</th><th class="px-md py-sm">related_jobs</th><th class="px-md py-sm">active</th><th class="px-md py-sm">updated_at</th></tr>
              </thead>
              <tbody>
                <tr v-if="!occupations.items.length" class="h-16 border-t border-outline-variant"><td colspan="7" class="px-md text-center text-on-surface-variant">{{ loading ? '불러오는 중' : '데이터 없음' }}</td></tr>
                <tr v-for="(item, index) in occupations.items" :key="item.id" class="cursor-pointer border-t border-outline-variant align-top hover:bg-surface-container-low" @click="openDetail('직업정보', item, rowStart + index + 1)">
                  <td class="px-md py-sm font-mono text-on-surface-variant">{{ rowStart + index + 1 }}</td>
                  <td class="px-md py-sm font-mono">{{ item.occupation_code }}</td>
                  <td class="px-md py-sm font-bold">{{ item.occupation_name_ko }}</td>
                  <td class="px-md py-sm">{{ item.occupation_category_name || item.occupation_category_code || '-' }}</td>
                  <td class="max-w-[360px] truncate px-md py-sm">{{ item.related_jobs || '-' }}</td>
                  <td class="px-md py-sm">{{ item.active_yn }}</td>
                  <td class="px-md py-sm font-mono">{{ formatDate(item.updated_at) }}</td>
                </tr>
              </tbody>
            </table>
          </div>

          <div v-if="activeTab === 'mappings'" class="overflow-hidden rounded border border-outline-variant bg-white">
            <table class="w-full border-collapse text-left text-body-sm">
              <thead class="bg-surface-container-low text-label-caps text-on-surface-variant">
                <tr><th class="px-md py-sm">#</th><th class="px-md py-sm">language</th><th class="px-md py-sm">external_keyword</th><th class="px-md py-sm">normalized</th><th class="px-md py-sm">mapped_name</th><th class="px-md py-sm">job</th><th class="px-md py-sm">occupation</th><th class="px-md py-sm">score</th><th class="px-md py-sm">active</th></tr>
              </thead>
              <tbody>
                <tr v-if="!mappings.items.length" class="h-16 border-t border-outline-variant"><td colspan="9" class="px-md text-center text-on-surface-variant">{{ loading ? '불러오는 중' : '데이터 없음' }}</td></tr>
                <tr v-for="(item, index) in mappings.items" :key="item.id" class="cursor-pointer border-t border-outline-variant hover:bg-surface-container-low" @click="openDetail('검색어 매핑', item, rowStart + index + 1)">
                  <td class="px-md py-sm font-mono text-on-surface-variant">{{ rowStart + index + 1 }}</td>
                  <td class="px-md py-sm font-mono">{{ item.language_code }}</td>
                  <td class="px-md py-sm font-bold">{{ item.external_keyword }}</td>
                  <td class="px-md py-sm">{{ item.normalized_keyword }}</td>
                  <td class="px-md py-sm">{{ item.mapped_name_ko || item.mapped_name_en || '-' }}</td>
                  <td class="px-md py-sm font-mono">{{ item.job_code || '-' }}</td>
                  <td class="px-md py-sm font-mono">{{ item.occupation_code || '-' }}</td>
                  <td class="px-md py-sm font-mono">{{ Number(item.match_score || 0).toFixed(2) }}</td>
                  <td class="px-md py-sm">{{ item.active_yn }}</td>
                </tr>
              </tbody>
            </table>
          </div>

          <div v-if="['jobs', 'occupations', 'mappings'].includes(activeTab)" class="flex items-center justify-end gap-sm text-body-sm">
            <button class="rounded border border-outline-variant px-md py-xs disabled:opacity-40" type="button" :disabled="currentPage <= 1 || loading" @click="goPage(1)">처음</button>
            <button class="rounded border border-outline-variant px-md py-xs disabled:opacity-40" type="button" :disabled="currentPage <= 1 || loading" @click="goPage(currentPage - 1)">이전</button>
            <span class="font-mono">{{ currentPage }} / {{ totalPages }}</span>
            <button class="rounded border border-outline-variant px-md py-xs disabled:opacity-40" type="button" :disabled="currentPage >= totalPages || loading" @click="goPage(currentPage + 1)">다음</button>
            <button class="rounded border border-outline-variant px-md py-xs disabled:opacity-40" type="button" :disabled="currentPage >= totalPages || loading" @click="goPage(totalPages)">끝</button>
          </div>

          <div v-if="activeTab === 'logs'" class="space-y-sm">
            <div v-for="log in logs" :key="log.id" class="cursor-pointer rounded border border-outline-variant bg-white p-md text-body-sm hover:bg-surface-container-low" @click="openDetail('수집 로그', log)">
              <div class="flex flex-wrap items-center justify-between gap-md">
                <p class="font-bold">{{ log.collector_type }} / {{ log.status }}</p>
                <p class="font-mono text-on-surface-variant">{{ formatDate(log.started_at) }} - {{ formatDate(log.finished_at) }}</p>
              </div>
              <p class="mt-xs text-on-surface-variant">requested {{ log.requested_count }} / inserted {{ log.inserted_count }} / updated {{ log.updated_count }} / skipped {{ log.skipped_count }} / failed {{ log.failed_count }}</p>
              <p v-if="log.error_message" class="mt-xs text-error">{{ log.error_message }}</p>
            </div>
            <p v-if="!logs.length" class="rounded border border-outline-variant bg-white p-md text-center text-body-sm text-on-surface-variant">수집 로그가 없습니다.</p>
          </div>
        </section>
      </section>
    </main>

    <aside v-if="detail" class="fixed right-0 top-0 z-[70] h-screen w-[520px] overflow-y-auto border-l border-outline-variant bg-white p-lg shadow-xl">
      <div class="mb-md flex items-start justify-between gap-md">
        <div>
          <p class="text-label-caps text-primary">상세정보</p>
          <h2 class="mt-xs text-headline">{{ detail.type }} <span v-if="detail.index" class="font-mono text-body-sm text-on-surface-variant">#{{ detail.index }}</span></h2>
        </div>
        <button class="rounded border border-outline-variant p-xs" type="button" @click="closeDetail">
          <X :size="18" />
        </button>
      </div>

      <dl class="space-y-xs text-body-sm">
        <div v-for="[key, value] in Object.entries(detail.item)" :key="key" class="rounded border border-outline-variant p-sm">
          <dt class="mb-xs font-mono text-[11px] text-on-surface-variant">{{ key }}</dt>
          <dd v-if="typeof value === 'object'" class="max-h-56 overflow-auto whitespace-pre-wrap break-words font-mono text-[11px]">{{ rawPreview(value) }}</dd>
          <dd v-else class="whitespace-pre-wrap break-words">{{ value || '-' }}</dd>
        </div>
      </dl>
    </aside>
  </div>
</template>
