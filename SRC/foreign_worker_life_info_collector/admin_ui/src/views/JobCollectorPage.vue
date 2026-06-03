<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { Database, FileSearch, KeyRound, ListChecks, RefreshCw, Search, TableProperties } from '@lucide/vue'
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

const activeTab = ref('dashboard')
const loading = ref(false)
const actionBusy = ref('')
const loadError = ref('')
const actionMessage = ref('')
const dashboard = ref({})
const jobs = ref({ items: [], total_count: 0, page: 1, size: 20 })
const occupations = ref({ items: [], total_count: 0, page: 1, size: 20 })
const mappings = ref({ items: [], total_count: 0, page: 1, size: 50 })
const logs = ref([])
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

function formatDate(value) {
  return value ? String(value).replace('T', ' ').slice(0, 19) : '-'
}

function rawPreview(value) {
  if (!value) return '{}'
  if (typeof value === 'string') return value.slice(0, 500)
  return JSON.stringify(value, null, 2).slice(0, 700)
}

async function loadDashboard() {
  dashboard.value = await fetchOccupationDashboard()
}

async function loadJobs(page = 1) {
  jobs.value = await fetchOccupationJobs({ page, size: jobs.value.size || 20, keyword: filters.keyword, active_yn: filters.active_yn })
}

async function loadOccupations(page = 1) {
  occupations.value = await fetchOccupations({ page, size: occupations.value.size || 20, keyword: filters.keyword, active_yn: filters.active_yn })
}

async function loadMappings(page = 1) {
  mappings.value = await fetchKeywordMappings({ page, size: mappings.value.size || 50, keyword: filters.keyword, language_code: filters.language_code })
}

async function loadLogs() {
  logs.value = await fetchOccupationCollectLogs({ limit: 80 })
}

async function loadCurrent() {
  loading.value = true
  loadError.value = ''
  try {
    await loadDashboard()
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
  await loadCurrent()
}

async function runCollect(type) {
  actionBusy.value = type
  actionMessage.value = ''
  loadError.value = ''
  try {
    const result = type === 'jobs' ? await collectOccupationJobs({ pageFrom: 1, pageTo: 1, size: 100 }) : await collectOccupations({ pageFrom: 1, pageTo: 1, size: 100 })
    actionMessage.value = `${type === 'jobs' ? '직무정보' : '직업정보'} 수집 완료: ${result.status}, 신규 ${result.insertedCount || 0}건, 갱신 ${result.updatedCount || 0}건, 실패 ${result.failedCount || 0}건`
    await loadCurrent()
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
    await loadCurrent()
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
            <p class="mt-xs text-body-sm text-on-surface-variant">고용24 직무정보와 직업정보를 수집하고 외국인 사용자의 검색어 매핑을 관리합니다.</p>
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
          <div class="rounded border border-outline-variant bg-white p-md text-body-sm">
            <p>최근 수집 시간: <span class="font-mono">{{ formatDate(dashboard.latest_collected_at) }}</span></p>
            <p>최근 수집 상태: <span class="font-bold">{{ dashboard.latest_status || '-' }}</span></p>
          </div>
        </section>

        <section v-else class="space-y-md">
          <div class="flex items-center gap-md rounded border border-outline-variant bg-surface-container-low px-md py-sm">
            <Search class="text-outline" :size="18" />
            <input v-model="filters.keyword" class="min-w-0 flex-1 bg-transparent text-body-sm outline-none" type="search" placeholder="코드, 이름, 설명, raw response 검색" @keydown.enter="loadCurrent" />
            <select v-if="activeTab !== 'mappings' && activeTab !== 'logs'" v-model="filters.active_yn" class="rounded border border-outline-variant bg-white px-sm py-xs text-body-sm" @change="loadCurrent">
              <option value="">전체</option>
              <option value="Y">활성</option>
              <option value="N">비활성</option>
            </select>
            <select v-if="activeTab === 'mappings'" v-model="filters.language_code" class="rounded border border-outline-variant bg-white px-sm py-xs text-body-sm" @change="loadCurrent">
              <option value="">전체 언어</option>
              <option value="ko">ko</option>
              <option value="en">en</option>
            </select>
            <button class="rounded border border-outline-variant px-md py-xs text-body-sm font-bold" type="button" @click="loadCurrent">검색</button>
            <button v-if="activeTab === 'mappings'" class="rounded border border-outline-variant px-md py-xs text-body-sm font-bold" type="button" :disabled="actionBusy === 'mappings'" @click="runGenerateMappings">
              자동 생성
            </button>
          </div>

          <div v-if="activeTab === 'jobs'" class="overflow-hidden rounded border border-outline-variant bg-white">
            <table class="w-full border-collapse text-left text-body-sm">
              <thead class="bg-surface-container-low text-label-caps text-on-surface-variant">
                <tr><th class="px-md py-sm">job_code</th><th class="px-md py-sm">job_name_ko</th><th class="px-md py-sm">job_name_en</th><th class="px-md py-sm">category</th><th class="px-md py-sm">active</th><th class="px-md py-sm">updated_at</th></tr>
              </thead>
              <tbody>
                <tr v-if="!jobs.items.length" class="h-16 border-t border-outline-variant"><td colspan="6" class="px-md text-center text-on-surface-variant">{{ loading ? '불러오는 중' : '데이터 없음' }}</td></tr>
                <tr v-for="item in jobs.items" :key="item.id" class="border-t border-outline-variant align-top hover:bg-surface-container-low">
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
                <tr><th class="px-md py-sm">occupation_code</th><th class="px-md py-sm">occupation_name_ko</th><th class="px-md py-sm">category</th><th class="px-md py-sm">related_jobs</th><th class="px-md py-sm">active</th><th class="px-md py-sm">updated_at</th></tr>
              </thead>
              <tbody>
                <tr v-if="!occupations.items.length" class="h-16 border-t border-outline-variant"><td colspan="6" class="px-md text-center text-on-surface-variant">{{ loading ? '불러오는 중' : '데이터 없음' }}</td></tr>
                <tr v-for="item in occupations.items" :key="item.id" class="border-t border-outline-variant align-top hover:bg-surface-container-low">
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
                <tr><th class="px-md py-sm">language</th><th class="px-md py-sm">external_keyword</th><th class="px-md py-sm">normalized</th><th class="px-md py-sm">mapped_name</th><th class="px-md py-sm">job</th><th class="px-md py-sm">occupation</th><th class="px-md py-sm">score</th><th class="px-md py-sm">active</th></tr>
              </thead>
              <tbody>
                <tr v-if="!mappings.items.length" class="h-16 border-t border-outline-variant"><td colspan="8" class="px-md text-center text-on-surface-variant">{{ loading ? '불러오는 중' : '데이터 없음' }}</td></tr>
                <tr v-for="item in mappings.items" :key="item.id" class="border-t border-outline-variant hover:bg-surface-container-low">
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

          <div v-if="activeTab === 'logs'" class="space-y-sm">
            <div v-for="log in logs" :key="log.id" class="rounded border border-outline-variant bg-white p-md text-body-sm">
              <div class="flex flex-wrap items-center justify-between gap-md">
                <p class="font-bold">{{ log.collector_type }} / {{ log.status }}</p>
                <p class="font-mono text-on-surface-variant">{{ formatDate(log.started_at) }} - {{ formatDate(log.finished_at) }}</p>
              </div>
              <p class="mt-xs text-on-surface-variant">requested {{ log.requested_count }} / inserted {{ log.inserted_count }} / updated {{ log.updated_count }} / skipped {{ log.skipped_count }} / failed {{ log.failed_count }}</p>
              <p v-if="log.error_message" class="mt-xs text-error">{{ log.error_message }}</p>
              <pre class="mt-sm max-h-32 overflow-auto rounded bg-surface-container-low p-sm text-[11px]">{{ rawPreview(log.request_params) }}</pre>
            </div>
            <p v-if="!logs.length" class="rounded border border-outline-variant bg-white p-md text-center text-body-sm text-on-surface-variant">수집 로그가 없습니다.</p>
          </div>
        </section>
      </section>
    </main>
  </div>
</template>
