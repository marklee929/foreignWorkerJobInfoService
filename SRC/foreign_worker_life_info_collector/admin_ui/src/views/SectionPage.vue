<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ChevronLeft, ChevronRight, RefreshCw, Search, Trash2, Wrench } from '@lucide/vue'
import Header from '../components/Header.vue'
import Sidebar from '../components/Sidebar.vue'
import StatusBadge from '../components/StatusBadge.vue'
import StatusHelp from '../components/StatusHelp.vue'
import { navItems } from '../data/defaultAdminState'
import { statusCodeGuide } from '../data/statusCodes'
import { cleanupCandidateLinks, deleteCandidates, fetchCandidates } from '../services/apiClient'
import { logoutAdmin, resetDeviceId } from '../services/authService'

const route = useRoute()
const router = useRouter()
const rows = ref([])
const selectedIds = ref(new Set())
const loading = ref(false)
const deleting = ref(false)
const cleaning = ref(false)
const loadError = ref('')
const actionMessage = ref('')
const searchText = ref('')
const statusFilter = ref('')
const priorityGroupFilter = ref('')
const contentCategoryFilter = ref('')
const sensitiveFilter = ref('')
const includeDuplicates = ref(false)
const page = ref(1)
const pageSize = 10
const totalCount = ref(0)

const pageTitle = computed(() => route.meta.title || '작업 화면')
const pageDescription = computed(() => route.meta.description || '저장된 데이터를 확인합니다.')
const isDataView = computed(() => route.meta.dataView === true && route.name === 'social-news')
const isSystemSettings = computed(() => route.name === 'system-settings')
const statusGuideGroups = computed(() => statusCodeGuide())

const categoryFilters = {
  content: [],
  'social-news': [],
  lifestyle: ['생활', '지원', '상담', '복지', '교육', '의료', '주거'],
  immigration: ['출입국', '체류', '비자', '사증', '외국인등록', '고용허가', 'E-9', 'H-2'],
  labor: ['노동', '근로', '임금', '퇴직', '산재', '근무', '고용', '계약'],
}

const sectionRows = computed(() => {
  const filters = categoryFilters[String(route.name || '')] || []
  if (!filters.length) {
    return rows.value
  }
  return rows.value.filter((item) => {
    const haystack = [
      item.category,
      item.title,
      item.source_name,
      item.source_type,
      item.short_summary,
      item.selection_reason,
      item.skip_reason,
      item.fail_reason,
    ]
      .filter(Boolean)
      .join(' ')
      .toLowerCase()
    return filters.some((filter) => haystack.includes(filter.toLowerCase()))
  })
})

const filteredRows = computed(() => {
  return sectionRows.value
})

const totalPages = computed(() => Math.max(1, Math.ceil(totalCount.value / pageSize)))
const startIndex = computed(() => (page.value - 1) * pageSize)
const pagedRows = computed(() => filteredRows.value)
const selectedCount = computed(() => selectedIds.value.size)
const allPageSelected = computed(() => pagedRows.value.length > 0 && pagedRows.value.every((item) => selectedIds.value.has(item.id)))
const rowRange = computed(() => {
  if (!totalCount.value) {
    return '0-0'
  }
  return `${startIndex.value + 1}-${Math.min(startIndex.value + pageSize, totalCount.value)}`
})

function formatScore(value) {
  return Number(value || 0).toFixed(2)
}

function formatDate(value) {
  if (!value) {
    return '-'
  }
  return String(value).replace('T', ' ').slice(0, 16)
}

function formatShortDate(value) {
  const formatted = formatDate(value)
  return formatted === '-' ? '-' : formatted.slice(5)
}

async function loadRows() {
  if (!isDataView.value) {
    rows.value = []
    totalCount.value = 0
    selectedIds.value = new Set()
    return
  }
  loading.value = true
  loadError.value = ''
  try {
    const payload = await fetchCandidates({
      page: page.value,
      size: pageSize,
      search: searchText.value.trim(),
      status: statusFilter.value,
      priority_group: priorityGroupFilter.value,
      content_category: contentCategoryFilter.value,
      sensitive: sensitiveFilter.value,
      includeDuplicates: includeDuplicates.value ? '1' : '0',
    })
    rows.value = payload.items || []
    totalCount.value = Number(payload.total_count ?? rows.value.length)
    const visibleIds = new Set(rows.value.map((item) => item.id))
    selectedIds.value = new Set([...selectedIds.value].filter((id) => visibleIds.has(id)))
  } catch (error) {
    loadError.value = error instanceof Error ? error.message : '데이터를 불러오지 못했습니다.'
    rows.value = []
    totalCount.value = 0
    selectedIds.value = new Set()
  } finally {
    loading.value = false
  }
}

function toggleRow(id) {
  const next = new Set(selectedIds.value)
  if (next.has(id)) {
    next.delete(id)
  } else {
    next.add(id)
  }
  selectedIds.value = next
}

function togglePageSelection() {
  const next = new Set(selectedIds.value)
  if (allPageSelected.value) {
    pagedRows.value.forEach((item) => next.delete(item.id))
  } else {
    pagedRows.value.forEach((item) => next.add(item.id))
  }
  selectedIds.value = next
}

async function handleDeleteSelected() {
  if (!selectedCount.value || deleting.value) {
    return
  }
  const count = selectedCount.value
  const ok = window.confirm(`선택한 ${count}건을 삭제할까요? 삭제한 데이터는 목록에서 제거됩니다.`)
  if (!ok) {
    return
  }
  deleting.value = true
  loadError.value = ''
  try {
    const deletedIds = new Set(selectedIds.value)
    await deleteCandidates([...deletedIds])
    selectedIds.value = new Set()
    rows.value = rows.value.filter((item) => !deletedIds.has(item.id))
    if (page.value > totalPages.value) {
      page.value = totalPages.value
    }
    if (pagedRows.value.length === 0 && page.value > 1) {
      page.value -= 1
    }
    await loadRows()
    if (page.value > totalPages.value) {
      page.value = totalPages.value
    }
  } catch (error) {
    loadError.value = error instanceof Error ? error.message : '삭제에 실패했습니다.'
  } finally {
    deleting.value = false
  }
}

async function handleCleanupLinks() {
  if (cleaning.value || loading.value) {
    return
  }
  cleaning.value = true
  loadError.value = ''
  actionMessage.value = ''
  try {
    const result = await cleanupCandidateLinks({
      ids: [...selectedIds.value],
      search: searchText.value.trim(),
      status: statusFilter.value,
      includeDuplicates: includeDuplicates.value ? '1' : '0',
      limit: selectedCount.value ? Math.min(selectedCount.value, 10) : 10,
    })
    actionMessage.value = `링크/본문 정리 완료: 대상 ${result.target || 0}건, URL ${result.resolved_url || 0}건, 본문 ${result.content_updated || 0}건, 점수 ${result.score_updated || 0}건, 대기열 ${result.queue_updated || 0}건, 실패 ${result.failed || 0}건`
    await loadRows()
  } catch (error) {
    loadError.value = error instanceof Error ? error.message : '링크/본문 정리에 실패했습니다.'
  } finally {
    cleaning.value = false
  }
}

function openDetail(item) {
  if (!item?.id || route.name !== 'social-news') {
    return
  }
  router.push({ name: 'social-news-detail', params: { id: item.id } })
}


function previousPage() {
  page.value = Math.max(1, page.value - 1)
}

function nextPage() {
  page.value = Math.min(totalPages.value, page.value + 1)
}

async function handleLogout() {
  try {
    await logoutAdmin()
  } finally {
    resetDeviceId()
    window.location.replace('/auth?loggedOut=1')
  }
}

function resetPageAndLoad() {
  if (page.value !== 1) {
    page.value = 1
    return
  }
  loadRows()
}

watch([searchText, statusFilter, priorityGroupFilter, contentCategoryFilter, sensitiveFilter, includeDuplicates], resetPageAndLoad)

watch(page, loadRows)

watch(
  () => route.name,
  () => {
    page.value = 1
    selectedIds.value = new Set()
    loadRows()
  },
)

onMounted(loadRows)
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
            <h1 class="text-display font-black">{{ pageTitle }}</h1>
            <p class="mt-xs text-body-sm text-on-surface-variant">{{ pageDescription }}</p>
          </div>
          <div v-if="isDataView" class="flex items-center gap-sm">
            <button
              class="inline-flex items-center gap-xs rounded border border-outline-variant px-md py-xs text-body-sm font-bold disabled:cursor-not-allowed disabled:opacity-40"
              type="button"
              :disabled="loading || cleaning"
              @click="handleCleanupLinks"
            >
              <Wrench :size="15" />
              {{ cleaning ? '정리 중' : selectedCount ? `링크/본문 정리 ${selectedCount}건` : '링크/본문 정리' }}
            </button>
            <button
              class="inline-flex items-center gap-xs rounded border border-error px-md py-xs text-body-sm font-bold text-error disabled:cursor-not-allowed disabled:opacity-40"
              type="button"
              :disabled="selectedCount === 0 || deleting"
              @click="handleDeleteSelected"
            >
              <Trash2 :size="15" />
              {{ deleting ? '삭제 중' : `선택 삭제${selectedCount ? ` ${selectedCount}건` : ''}` }}
            </button>
            <button
              class="inline-flex items-center gap-xs rounded border border-outline-variant px-md py-xs text-body-sm disabled:cursor-not-allowed disabled:opacity-40"
              type="button"
              :disabled="loading"
              @click="loadRows"
            >
              <RefreshCw :size="15" />
              새로고침
            </button>
          </div>
        </div>

        <template v-if="isDataView">
          <div class="mb-md flex items-center gap-md rounded border border-outline-variant bg-surface-container-low px-md py-sm">
            <Search class="text-outline" :size="18" />
            <input
              v-model="searchText"
              class="min-w-0 flex-1 bg-transparent text-body-sm outline-none"
              type="search"
              placeholder="제목, 분류, 출처, 상태로 검색"
            />
            <span class="text-body-sm text-on-surface-variant">총 {{ totalCount }}건</span>
          </div>

          <div class="mb-md flex flex-wrap items-center gap-sm text-body-sm">
            <label class="inline-flex items-center gap-xs rounded border border-outline-variant px-sm py-xs">
              <input v-model="includeDuplicates" type="checkbox" />
              중복 포함 보기
            </label>
            <select v-model="statusFilter" class="rounded border border-outline-variant bg-white px-sm py-xs">
              <option value="">전체 상태</option>
              <option value="READY_TO_PUBLISH">게시 대기</option>
              <option value="FAILED_RETRYABLE">재시도 대기</option>
              <option value="FAILED_PERMISSION">권한 확인 필요</option>
              <option value="POSTED">게시 완료</option>
              <option value="POST_EXPIRED">게시 만료</option>
              <option value="DUPLICATE">중복 제외</option>
              <option value="NORMALIZED">정규화 완료</option>
              <option value="SCORED">점수 평가</option>
            </select>
          </div>

          <section v-if="loadError" class="mb-md rounded border border-error bg-error-container/30 p-sm text-body-sm text-error">
            {{ loadError }}
          </section>
          <section v-if="actionMessage" class="mb-md rounded border border-success bg-success/10 p-sm text-body-sm text-success">
            {{ actionMessage }}
          </section>

          <div class="overflow-hidden rounded border border-outline-variant bg-white">
            <table class="w-full border-collapse text-left text-body-sm">
              <thead class="bg-surface-container-low text-label-caps text-on-surface-variant">
                <tr>
                  <th class="w-12 px-md py-sm">
                    <input
                      type="checkbox"
                      :checked="allPageSelected"
                      :disabled="pagedRows.length === 0"
                      aria-label="현재 페이지 전체 선택"
                      @change="togglePageSelection"
                    />
                  </th>
                  <th class="px-md py-sm">
                    <span class="inline-flex items-center gap-xs">상태 <StatusHelp scope="social-news" title="소스 뉴스 상태" /></span>
                  </th>
                  <th class="px-md py-sm">제목</th>
                  <th class="px-md py-sm">중복</th>
                  <th class="px-md py-sm">관련 출처</th>
                  <th class="px-md py-sm">분류</th>
                  <th class="px-md py-sm">출처</th>
                  <th class="px-md py-sm">점수</th>
                  <th class="px-md py-sm">콘텐츠</th>
                  <th class="px-md py-sm">최종 수집일</th>
                  <th class="px-md py-sm">최초 수집일</th>
                </tr>
              </thead>
              <tbody>
                <tr v-if="pagedRows.length === 0" class="h-20 border-t border-outline-variant">
                  <td class="px-md text-center text-on-surface-variant" colspan="11">
                    {{ loading ? '데이터를 불러오는 중입니다.' : '데이터 없음' }}
                  </td>
                </tr>
                <tr v-for="item in pagedRows" :key="item.id" class="h-11 cursor-pointer border-t border-outline-variant hover:bg-surface-container-low" @click="openDetail(item)">
                  <td class="px-md">
                    <input type="checkbox" :checked="selectedIds.has(item.id)" :aria-label="`${item.title} 선택`" @click.stop @change="toggleRow(item.id)" />
                  </td>
                  <td class="px-md">
                    <StatusBadge :code="item.publish_status || item.status" variant="dot" />
                  </td>
                  <td class="max-w-[420px] px-md font-bold">
                    <span class="block truncate">{{ item.title || '제목 없음' }}</span>
                  </td>
                  <td class="px-md font-mono text-on-surface-variant">{{ item.duplicate_count || 0 }}</td>
                  <td class="px-md font-mono text-on-surface-variant">{{ item.related_source_count || 1 }}</td>
                  <td class="px-md text-on-surface-variant">{{ item.content_category || item.category || '-' }}</td>
                  <td class="px-md text-on-surface-variant">{{ item.source_name || item.source_type || '-' }}</td>
                  <td class="px-md font-mono font-bold text-success">{{ formatScore(item.evaluation_score) }}</td>
                  <td class="px-md">
                    <StatusBadge v-if="item.content_candidate_id" :code="item.content_status" variant="dot" />
                    <span v-else class="text-on-surface-variant">-</span>
                  </td>
                  <td class="whitespace-nowrap px-md font-mono text-on-surface-variant">{{ formatShortDate(item.last_seen_at || item.collected_at) }}</td>
                  <td class="whitespace-nowrap px-md font-mono text-on-surface-variant">{{ formatShortDate(item.collected_at) }}</td>
                </tr>
              </tbody>
            </table>
          </div>

          <div class="mt-md flex items-center justify-between text-body-sm">
            <span class="text-on-surface-variant">{{ rowRange }} / {{ totalCount }}건</span>
            <div class="flex items-center gap-sm">
              <button class="rounded border border-outline-variant p-xs disabled:cursor-not-allowed disabled:opacity-40" type="button" :disabled="page <= 1" @click="previousPage">
                <ChevronLeft :size="16" />
              </button>
              <span class="font-mono">{{ page }} / {{ totalPages }}</span>
              <button class="rounded border border-outline-variant p-xs disabled:cursor-not-allowed disabled:opacity-40" type="button" :disabled="page >= totalPages" @click="nextPage">
                <ChevronRight :size="16" />
              </button>
            </div>
          </div>
        </template>

        <template v-else-if="isSystemSettings">
          <section class="space-y-md">
            <div class="rounded border border-outline-variant bg-surface-container-low p-md">
              <h2 class="text-headline">코드 가이드</h2>
              <p class="mt-xs text-body-sm text-on-surface-variant">목록 화면의 상태 색상은 이 공통 코드 기준을 사용합니다.</p>
            </div>
            <div class="grid gap-md xl:grid-cols-2">
              <article v-for="group in statusGuideGroups" :key="group.group" class="overflow-hidden rounded border border-outline-variant bg-white">
                <div class="border-b border-outline-variant bg-surface-container-low px-md py-sm">
                  <h3 class="text-title-sm font-bold">{{ group.group }}</h3>
                </div>
                <div class="divide-y divide-outline-variant">
                  <div v-for="item in group.items" :key="item.code" class="grid grid-cols-[120px_120px_minmax(0,1fr)] items-center gap-md px-md py-sm text-body-sm">
                    <code class="font-mono text-[11px] text-on-surface-variant">{{ item.code }}</code>
                    <StatusBadge :code="item.code" />
                    <p class="text-on-surface-variant">{{ item.description }}</p>
                  </div>
                </div>
              </article>
            </div>
          </section>
        </template>

        <template v-else>
          <div class="rounded border border-outline-variant bg-surface-container-low p-lg">
            <h2 class="mb-xs text-headline">정리 예정</h2>
            <p class="text-body-sm text-on-surface-variant">이 화면은 다음 단계에서 별도로 구성합니다.</p>
          </div>
        </template>
      </section>
    </main>
  </div>
</template>
