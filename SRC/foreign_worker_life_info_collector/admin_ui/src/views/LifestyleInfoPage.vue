<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { ExternalLink, Eye, RefreshCw, Search } from '@lucide/vue'
import Header from '../components/Header.vue'
import Sidebar from '../components/Sidebar.vue'
import StatusBadge from '../components/StatusBadge.vue'
import StatusHelp from '../components/StatusHelp.vue'
import { navItems } from '../data/defaultAdminState'
import {
  fetchLifestyleCandidateDetail,
  fetchLifestyleCandidates,
  fetchLifestyleBotStatus,
  startLifestyleBot,
  stopLifestyleBot,
} from '../services/apiClient'
import { logoutAdmin, resetDeviceId } from '../services/authService'

const rows = ref([])
const detail = ref(null)
const botStatus = ref({ status: 'STOPPED', label: '중지됨', message: '', lastErrorMessage: '' })
const loading = ref(false)
const detailLoading = ref(false)
const botBusy = ref(false)
const loadError = ref('')
const actionMessage = ref('')
const searchText = ref('')
const categoryFilter = ref('')
const statusFilter = ref('')
const page = ref(1)
const pageSize = 20
const totalCount = ref(0)

const categories = [
  { value: '', label: '전체 생활/정착' },
  { value: 'housing', label: 'Housing' },
  { value: 'banking', label: 'Finance' },
  { value: 'local_community', label: 'Telecom/Local' },
  { value: 'healthcare', label: 'Healthcare' },
  { value: 'insurance', label: 'Insurance' },
  { value: 'education', label: 'Education' },
  { value: 'korean_language', label: 'Korean Language' },
  { value: 'cost_of_living', label: 'Cost of Living' },
  { value: 'settlement_life', label: 'Settlement Life' },
  { value: 'lifestyle', label: 'Lifestyle' },
]

const pageTitle = computed(() => '생활 정보')
const totalPages = computed(() => Math.max(1, Math.ceil(totalCount.value / pageSize)))
const botActive = computed(() => botStatus.value.status === 'RUNNING' || botStatus.value.status === 'STARTING')
const cards = computed(() => [
  { label: '전체 후보', value: totalCount.value },
  { label: '표시 중', value: rows.value.length },
  { label: '고점수', value: rows.value.filter((row) => Number(row.evaluation_score || 0) >= 70).length },
  { label: '검토 필요', value: rows.value.filter((row) => row.is_sensitive || row.review_required_reason).length },
])
const selectedCandidate = computed(() => detail.value?.candidate || detail.value || null)

function formatDate(value) {
  return value ? String(value).replace('T', ' ').slice(0, 16) : '-'
}

function sourceLabel(row) {
  return row.source_name || row.publisher_name || row.source_type || '-'
}

async function loadBotStatus() {
  botStatus.value = await fetchLifestyleBotStatus()
}

async function loadRows() {
  loading.value = true
  loadError.value = ''
  try {
    const payload = await fetchLifestyleCandidates({
      page: page.value,
      size: pageSize,
      search: searchText.value.trim(),
      status: statusFilter.value,
      priority_group: categoryFilter.value ? '' : 'SECONDARY',
      content_category: categoryFilter.value,
      includeDuplicates: '0',
    })
    rows.value = payload.items || []
    totalCount.value = Number(payload.total_count || 0)
    if (!detail.value && rows.value.length) {
      await openDetail(rows.value[0])
    }
  } catch (error) {
    loadError.value = error instanceof Error ? error.message : '생활정보 데이터를 불러오지 못했습니다.'
    rows.value = []
    totalCount.value = 0
  } finally {
    loading.value = false
  }
}

async function refreshAll() {
  await Promise.allSettled([loadBotStatus(), loadRows()])
}

async function toggleBot() {
  botBusy.value = true
  actionMessage.value = ''
  loadError.value = ''
  try {
    botStatus.value = botActive.value ? await stopLifestyleBot() : await startLifestyleBot()
    actionMessage.value = botStatus.value.message || (botActive.value ? '생활정보 봇이 실행 중입니다.' : '생활정보 봇 상태를 갱신했습니다.')
  } catch (error) {
    loadError.value = error instanceof Error ? error.message : '생활정보 봇 제어에 실패했습니다.'
  } finally {
    botBusy.value = false
  }
}

async function openDetail(row) {
  if (!row?.id) {
    return
  }
  detailLoading.value = true
  try {
    detail.value = await fetchLifestyleCandidateDetail(row.id)
  } catch {
    detail.value = { candidate: row }
  } finally {
    detailLoading.value = false
  }
}

function previousPage() {
  if (page.value <= 1) {
    return
  }
  page.value -= 1
}

function nextPage() {
  if (page.value >= totalPages.value) {
    return
  }
  page.value += 1
}

async function handleLogout() {
  try {
    await logoutAdmin()
  } finally {
    resetDeviceId()
    window.location.href = '/auth'
  }
}

watch([page, categoryFilter, statusFilter], loadRows)

onMounted(refreshAll)
</script>

<template>
  <div class="min-h-screen bg-surface text-on-surface">
    <Sidebar :nav-items="navItems" @logout="handleLogout" />
    <Header :server-status="loadError ? 'error' : 'ok'" :server-message="loadError" @logout="handleLogout" />

    <main class="ml-[240px] min-w-0 space-y-lg p-lg">
      <section class="control-card p-lg">
        <div class="flex flex-wrap items-start justify-between gap-md">
          <div>
            <p class="text-label-caps text-primary">WorkConnect Admin</p>
            <h1 class="text-display-sm font-black">{{ pageTitle }}</h1>
            <p class="mt-xs text-body-sm text-on-surface-variant">생활/정착 관련 후보 데이터를 확인하고 수집 봇을 실행합니다.</p>
          </div>
          <div class="flex items-center gap-sm">
            <button class="btn-secondary" type="button" :disabled="loading" @click="refreshAll">
              <RefreshCw class="size-4" /> 새로고침
            </button>
            <button class="btn-primary" type="button" :disabled="botBusy" @click="toggleBot">
              <RefreshCw class="size-4" /> {{ botActive ? '수집 중지' : '생활정보 수집' }}
            </button>
          </div>
        </div>
      </section>

      <section v-if="actionMessage" class="rounded border border-success bg-success-container px-md py-sm text-body-sm text-success">
        {{ actionMessage }}
      </section>
      <section v-if="loadError" class="rounded border border-error bg-error-container px-md py-sm text-body-sm text-error">
        {{ loadError }}
      </section>

      <section class="grid grid-cols-5 gap-md">
        <article class="control-card p-md">
          <p class="text-label-sm text-on-surface-variant">봇 상태</p>
          <div class="mt-xs"><StatusBadge :code="botStatus.status" /></div>
          <p class="mt-xs truncate text-body-sm text-on-surface-variant">{{ botStatus.lastErrorMessage || botStatus.message || '-' }}</p>
        </article>
        <article v-for="card in cards" :key="card.label" class="control-card p-md">
          <p class="text-label-sm text-on-surface-variant">{{ card.label }}</p>
          <p class="mt-xs text-title-lg font-black">{{ card.value }}</p>
        </article>
      </section>

      <section class="grid gap-lg xl:grid-cols-[minmax(0,1fr)_420px]">
        <article class="control-card min-w-0 overflow-hidden">
          <div class="flex flex-wrap items-center gap-sm border-b border-outline-variant bg-surface-container-low px-md py-sm">
            <div class="flex min-w-[280px] flex-1 items-center gap-sm rounded border border-outline-variant bg-white px-md py-sm">
              <Search class="size-4 text-on-surface-variant" />
              <input v-model="searchText" class="min-w-0 flex-1 bg-transparent outline-none" placeholder="제목, 출처 검색" @keyup.enter="page = 1; loadRows()" />
            </div>
            <select v-model="categoryFilter" class="rounded border border-outline-variant bg-white px-md py-sm text-body-sm">
              <option v-for="item in categories" :key="item.value || 'all'" :value="item.value">{{ item.label }}</option>
            </select>
            <select v-model="statusFilter" class="rounded border border-outline-variant bg-white px-md py-sm text-body-sm">
              <option value="">전체 상태</option>
              <option value="READY_TO_PUBLISH">게시 대기</option>
              <option value="READY_TO_REVIEW">검토 대기</option>
              <option value="POSTED">게시 완료</option>
              <option value="FAILED">실패</option>
            </select>
          </div>

          <div class="overflow-x-auto">
            <table class="w-full min-w-[920px] table-fixed text-body-sm">
              <thead class="bg-surface-container-low text-label-caps text-on-surface-variant">
                <tr class="border-b border-outline-variant text-left">
                  <th class="w-[96px] px-md py-sm">
                    <span class="inline-flex items-center gap-xs">상태 <StatusHelp scope="lifestyle" title="생활정보 상태" /></span>
                  </th>
                  <th class="px-md py-sm">제목</th>
                  <th class="w-[140px] px-md py-sm">카테고리</th>
                  <th class="w-[160px] px-md py-sm">출처</th>
                  <th class="w-[92px] px-md py-sm">점수</th>
                  <th class="w-[132px] px-md py-sm">수집일</th>
                  <th class="w-[56px] px-md py-sm">보기</th>
                </tr>
              </thead>
              <tbody>
                <tr v-if="loading">
                  <td colspan="7" class="px-md py-lg text-center text-on-surface-variant">불러오는 중입니다.</td>
                </tr>
                <tr v-else-if="rows.length === 0">
                  <td colspan="7" class="px-md py-lg text-center text-on-surface-variant">생활정보 후보가 없습니다.</td>
                </tr>
                <template v-else>
                  <tr v-for="row in rows" :key="row.id" class="cursor-pointer border-t border-outline-variant hover:bg-surface-container-low" @click="openDetail(row)">
                    <td class="px-md py-sm">
                      <StatusBadge :code="row.publish_status || row.status" variant="dot" />
                    </td>
                    <td class="truncate px-md py-sm font-bold">{{ row.title || '제목 없음' }}</td>
                    <td class="px-md py-sm">{{ row.content_category || row.category || '-' }}</td>
                    <td class="truncate px-md py-sm">{{ sourceLabel(row) }}</td>
                    <td class="px-md py-sm font-mono text-success">{{ Number(row.evaluation_score || 0).toFixed(1) }}</td>
                    <td class="px-md py-sm font-mono">{{ formatDate(row.collected_at || row.last_seen_at) }}</td>
                    <td class="px-md py-sm"><Eye class="size-4 text-primary" /></td>
                  </tr>
                </template>
              </tbody>
            </table>
          </div>

          <div class="flex items-center justify-between border-t border-outline-variant px-md py-sm">
            <span class="text-body-sm text-on-surface-variant">총 {{ totalCount }}건</span>
            <div class="flex items-center gap-sm">
              <button class="btn-secondary" type="button" :disabled="page <= 1" @click="previousPage">이전</button>
              <span class="font-mono">{{ page }} / {{ totalPages }}</span>
              <button class="btn-secondary" type="button" :disabled="page >= totalPages" @click="nextPage">다음</button>
            </div>
          </div>
        </article>

        <aside class="control-card min-w-0 p-md">
          <template v-if="selectedCandidate">
            <div class="mb-md flex items-start justify-between gap-md">
              <div class="min-w-0">
                <p class="text-label-caps text-primary">{{ selectedCandidate.content_category || selectedCandidate.category || '생활정보' }}</p>
                <h2 class="mt-xs text-title font-black leading-tight">{{ selectedCandidate.title || '제목 없음' }}</h2>
              </div>
              <a v-if="selectedCandidate.source_url" class="btn-secondary shrink-0" :href="selectedCandidate.source_url" target="_blank" rel="noreferrer">
                <ExternalLink class="size-4" /> 원문
              </a>
            </div>
            <div v-if="selectedCandidate.image_url" class="mb-md aspect-video overflow-hidden rounded border border-outline-variant bg-surface-container-low">
              <img :src="selectedCandidate.image_url" :alt="selectedCandidate.title" class="h-full w-full object-cover" />
            </div>
            <dl class="mb-md grid grid-cols-2 gap-sm text-body-sm">
              <div class="rounded border border-outline-variant bg-surface-container-low p-sm">
                <dt class="text-label-sm text-on-surface-variant">출처</dt>
                <dd class="mt-xs truncate font-bold">{{ sourceLabel(selectedCandidate) }}</dd>
              </div>
              <div class="rounded border border-outline-variant bg-surface-container-low p-sm">
                <dt class="text-label-sm text-on-surface-variant">점수</dt>
                <dd class="mt-xs font-mono font-bold">{{ Number(selectedCandidate.evaluation_score || 0).toFixed(1) }}</dd>
              </div>
            </dl>
            <section class="space-y-sm">
              <div>
                <h3 class="text-title-sm font-bold">요약</h3>
                <p class="mt-xs whitespace-pre-wrap text-body-sm leading-6">{{ selectedCandidate.short_summary || selectedCandidate.generated_summary_en || selectedCandidate.summary || '요약이 없습니다.' }}</p>
              </div>
              <div>
                <h3 class="text-title-sm font-bold">검토 메모</h3>
                <p class="mt-xs whitespace-pre-wrap text-body-sm leading-6">{{ selectedCandidate.selection_reason || selectedCandidate.review_required_reason || selectedCandidate.skip_reason || '검토 메모가 없습니다.' }}</p>
              </div>
            </section>
          </template>
          <div v-else class="rounded border border-outline-variant bg-surface-container-low p-lg text-center text-body-sm text-on-surface-variant">
            {{ detailLoading ? '상세 데이터를 불러오는 중입니다.' : '왼쪽 목록에서 항목을 선택하세요.' }}
          </div>
        </aside>
      </section>
    </main>
  </div>
</template>
