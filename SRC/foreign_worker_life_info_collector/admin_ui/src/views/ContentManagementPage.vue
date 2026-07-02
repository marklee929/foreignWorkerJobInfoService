<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { RefreshCw, Search, Send, Shuffle } from '@lucide/vue'
import Header from '../components/Header.vue'
import Sidebar from '../components/Sidebar.vue'
import StatusBadge from '../components/StatusBadge.vue'
import StatusHelp from '../components/StatusHelp.vue'
import { navItems } from '../data/defaultAdminState'
import {
  fetchContentCandidateDetail,
  fetchContentCandidates,
  fetchContentDashboard,
  fetchLivingInfoReadinessDiagnostics,
  generateContentCandidateCardPreview,
  generateLivingInfoCardPreviews,
  runLivingInfoPrepCycle,
  scoreContentCandidate,
  sendContentCandidateToTelegram,
  syncContentCandidates,
} from '../services/apiClient'
import { logoutAdmin, resetDeviceId } from '../services/authService'

const dashboard = ref({})
const rows = ref([])
const detail = ref(null)
const publishLogs = ref([])
const loading = ref(false)
const syncing = ref(false)
const livingInfoSyncing = ref(false)
const livingInfoReadinessLoading = ref(false)
const cardPreviewing = ref(false)
const bulkCardPreviewing = ref(false)
const actioningId = ref(0)
const loadError = ref('')
const actionMessage = ref('')
const livingInfoSyncResult = ref(null)
const livingInfoReadiness = ref(null)
const cardPreviewResult = ref(null)
const bulkCardPreviewResult = ref(null)
const searchText = ref('')
const statusFilter = ref('')
const sourceFilter = ref('')
const categoryFilter = ref('')
const publishableOnly = ref(true)
const page = ref(1)
const pageSize = 20
const totalCount = ref(0)

const categoryOptions = [
  'foreign_jobs',
  'work_visa',
  'immigration',
  'labor_rights',
  'employment_policy',
  'government_notice',
  'housing',
  'banking',
  'healthcare',
  'transportation',
  'insurance',
  'korean_language',
  'cost_of_living',
  'local_community',
  'education',
  'settlement_life',
  'travel',
  'lifestyle',
  'culture',
  'local_events',
  'safety',
]

const totalPages = computed(() => Math.max(1, Math.ceil(totalCount.value / pageSize)))
const rowRange = computed(() => {
  if (!totalCount.value) return '0-0'
  const start = (page.value - 1) * pageSize + 1
  return `${start}-${Math.min(start + pageSize - 1, totalCount.value)}`
})

const latestCardPreview = computed(() => {
  const log = publishLogs.value.find((item) => item.content_card_preview)
  return log?.content_card_preview || null
})

const cards = computed(() => [
  { label: '전체 콘텐츠', value: dashboard.value.total_count || 0, delta: 'TOTAL' },
  { label: '게시 가능', value: dashboard.value.ready_count || 0, delta: 'READY' },
  { label: '검토 필요', value: dashboard.value.review_count || 0, delta: 'REVIEW' },
  { label: '게시 완료', value: dashboard.value.posted_count || 0, delta: 'POSTED' },
  { label: '뉴스 연동', value: dashboard.value.social_news_count || 0, delta: 'SOCIAL_NEWS' },
  { label: '생활정보 연동', value: dashboard.value.living_info_count || 0, delta: 'LIVING_INFO' },
  { label: '출입국 연동', value: dashboard.value.immigration_count || 0, delta: 'IMMIGRATION' },
])

function formatScore(value) {
  return Number(value || 0).toFixed(2)
}

function formatDate(value) {
  return value ? String(value).replace('T', ' ').slice(0, 16) : '-'
}

function formatPayload(value) {
  if (!value) return ''
  if (typeof value === 'string') return value
  try {
    return JSON.stringify(value, null, 2)
  } catch {
    return String(value)
  }
}

function cardPreviewClass(preview) {
  if (!preview) return 'border-outline-variant bg-surface-container-low text-on-surface-variant'
  if (preview.ok || preview.status === 'CARD_PREVIEW_GENERATED') return 'border-success bg-success-container text-success'
  if (preview.status === 'CARD_NOT_REQUIRED') return 'border-outline-variant bg-surface-container-low text-on-surface-variant'
  return 'border-error bg-error-container text-error'
}

function sourceLabel(value) {
  const labels = {
    SOCIAL_NEWS: '소셜 뉴스',
    IMMIGRATION_INFO: '출입국',
    LIVING_INFO: '생활정보',
    VISA_INFO: '비자정보',
    OCCUPATION_INFO: '직업정보',
    GOVERNMENT_NOTICE: '정부 공지',
  }
  return labels[value] || value || '-'
}

function contentTypeLabel(value) {
  const labels = {
    NEWS_ARTICLE: '뉴스',
    GOVERNMENT_NOTICE: '정부 공지',
    IMMIGRATION_NOTICE: '출입국 공지',
  }
  return labels[value] || value || '-'
}

function canReview(row) {
  return ['SCORED', 'READY_TO_REVIEW', 'READY_TO_PUBLISH', 'FAILED_RETRYABLE'].includes(row.status)
}

async function loadDashboard() {
  dashboard.value = await fetchContentDashboard()
}

async function loadRows() {
  loading.value = true
  loadError.value = ''
  try {
    const payload = await fetchContentCandidates({
      page: page.value,
      size: pageSize,
      search: searchText.value.trim(),
      status: statusFilter.value,
      source_domain: sourceFilter.value,
      category: categoryFilter.value,
      publishable: publishableOnly.value ? '1' : '',
    })
    rows.value = payload.items || []
    totalCount.value = Number(payload.total_count || 0)
  } catch (error) {
    loadError.value = error instanceof Error ? error.message : '콘텐츠 후보를 불러오지 못했습니다.'
    rows.value = []
    totalCount.value = 0
  } finally {
    loading.value = false
  }
}

async function loadAll() {
  await Promise.all([loadDashboard(), loadRows(), loadLivingInfoReadiness()])
}

async function syncAll() {
  if (syncing.value) return
  syncing.value = true
  actionMessage.value = ''
  loadError.value = ''
  try {
    const result = await syncContentCandidates({ limit: 500 })
    actionMessage.value = `동기화 완료: ${result.synced_total || 0}건`
    page.value = 1
    await loadAll()
  } catch (error) {
    loadError.value = error instanceof Error ? error.message : '콘텐츠 동기화에 실패했습니다.'
  } finally {
    syncing.value = false
  }
}

async function syncLivingInfo() {
  if (livingInfoSyncing.value) return
  livingInfoSyncing.value = true
  actionMessage.value = ''
  loadError.value = ''
  livingInfoSyncResult.value = null
  try {
    const result = await runLivingInfoPrepCycle({ limit: 100, dryRun: false })
    livingInfoSyncResult.value = result
    const prepare = result.prepare || {}
    const sync = result.sync || {}
    actionMessage.value = `Living info prepared: clusters ${prepare.cluster_count || 0}, written ${prepare.written_count || 0}, synced ${sync.synced_count || 0}, skipped ${sync.skipped_count || 0}`
    sourceFilter.value = 'LIVING_INFO'
    statusFilter.value = 'READY_TO_REVIEW'
    publishableOnly.value = false
    page.value = 1
    await loadAll()
  } catch (error) {
    loadError.value = error instanceof Error ? error.message : 'Living info preparation failed.'
  } finally {
    livingInfoSyncing.value = false
  }
}

async function loadLivingInfoReadiness() {
  if (livingInfoReadinessLoading.value) return
  livingInfoReadinessLoading.value = true
  loadError.value = ''
  try {
    livingInfoReadiness.value = await fetchLivingInfoReadinessDiagnostics({ limit: 100 })
  } catch (error) {
    loadError.value = error instanceof Error ? error.message : 'Living info readiness diagnostics failed.'
  } finally {
    livingInfoReadinessLoading.value = false
  }
}

async function generateLivingInfoCardPreviewBatch() {
  if (bulkCardPreviewing.value) return
  bulkCardPreviewing.value = true
  actionMessage.value = ''
  loadError.value = ''
  bulkCardPreviewResult.value = null
  try {
    const result = await generateLivingInfoCardPreviews({ limit: 20, status: 'READY_TO_REVIEW' })
    bulkCardPreviewResult.value = result
    actionMessage.value = `Living info card preview: generated ${result.generated_count || 0}, failed ${result.failed_count || 0}, skipped ${result.skipped_count || 0}`
    sourceFilter.value = 'LIVING_INFO'
    statusFilter.value = 'READY_TO_REVIEW'
    publishableOnly.value = false
    page.value = 1
    await loadAll()
    if (detail.value?.id) {
      await openDetail(detail.value)
    }
  } catch (error) {
    loadError.value = error instanceof Error ? error.message : 'Living info card preview failed.'
  } finally {
    bulkCardPreviewing.value = false
  }
}

async function openDetail(row) {
  detail.value = null
  publishLogs.value = []
  try {
    const payload = await fetchContentCandidateDetail(row.id)
    detail.value = payload
    publishLogs.value = payload.publish_logs || []
  } catch (error) {
    loadError.value = error instanceof Error ? error.message : '상세 정보를 불러오지 못했습니다.'
  }
}

async function sendTelegramReview(row) {
  if (actioningId.value || !canReview(row)) return
  actioningId.value = row.id
  actionMessage.value = ''
  loadError.value = ''
  try {
    const result = await sendContentCandidateToTelegram(row.id, {})
    actionMessage.value = `Telegram 검토 전송: ${result.status || '-'}`
    await loadAll()
    await openDetail(row)
  } catch (error) {
    loadError.value = error instanceof Error ? error.message : 'Telegram 검토 전송에 실패했습니다.'
  } finally {
    actioningId.value = 0
  }
}

async function generateCardPreview(row) {
  const target = row || detail.value
  if (!target?.id || actioningId.value) return
  cardPreviewing.value = true
  actioningId.value = target.id
  actionMessage.value = ''
  loadError.value = ''
  cardPreviewResult.value = null
  try {
    const result = await generateContentCandidateCardPreview(target.id, {})
    cardPreviewResult.value = result
    const preview = result.content_card_preview || {}
    actionMessage.value = `Card preview: ${result.status || '-'} / ${preview.status || '-'}`
    await loadAll()
    await openDetail(target)
  } catch (error) {
    loadError.value = error instanceof Error ? error.message : 'Card preview generation failed.'
  } finally {
    actioningId.value = 0
    cardPreviewing.value = false
  }
}

async function applyScore(score) {
  if (!detail.value?.id || actioningId.value) return
  actioningId.value = detail.value.id
  actionMessage.value = ''
  loadError.value = ''
  try {
    const result = await scoreContentCandidate(detail.value.id, { score, comment: `Admin UI score ${score}` })
    actionMessage.value = `점수 반영 완료: ${score}점`
    if (result.candidate) {
      detail.value = result.candidate
    }
    await loadAll()
  } catch (error) {
    loadError.value = error instanceof Error ? error.message : '점수 반영에 실패했습니다.'
  } finally {
    actioningId.value = 0
  }
}

function nextPage() {
  if (page.value < totalPages.value) page.value += 1
}

function prevPage() {
  if (page.value > 1) page.value -= 1
}

async function handleLogout() {
  await logoutAdmin().catch(() => {})
  resetDeviceId()
  window.location.href = '/auth'
}

let searchTimer = 0
watch([searchText, statusFilter, sourceFilter, categoryFilter, publishableOnly], () => {
  page.value = 1
  window.clearTimeout(searchTimer)
  searchTimer = window.setTimeout(loadRows, 250)
})

watch(page, loadRows)
onMounted(loadAll)
</script>

<template>
  <div class="min-h-screen bg-background text-on-surface">
    <Header server-status="ok" server-message="" @logout="handleLogout" />
    <Sidebar :nav-items="navItems" @logout="handleLogout" />

    <main class="ml-[240px] min-w-0 space-y-lg p-lg">
      <section class="rounded border border-outline-variant bg-surface p-lg">
        <div class="mb-md flex flex-wrap items-start justify-between gap-md">
          <div>
            <p class="text-label-sm font-bold text-primary">WorkConnect Admin</p>
            <h1 class="text-display-sm font-black">콘텐츠 관리</h1>
            <p class="mt-xs text-body-sm text-on-surface-variant">
              Facebook에 올릴 최종 콘텐츠 후보와 게시 결과를 관리합니다. 원문 날짜와 콘텐츠 갱신일은 별도로 표시합니다.
            </p>
          </div>
          <div class="flex flex-wrap gap-sm">
            <button class="btn-secondary inline-flex items-center gap-xs" type="button" :disabled="syncing" @click="syncAll">
              <Shuffle :size="16" />
              콘텐츠 동기화
            </button>
            <button class="btn-secondary inline-flex items-center gap-xs" type="button" :disabled="livingInfoSyncing" @click="syncLivingInfo">
              <Shuffle :size="16" />
              Living info prepare
            </button>
            <button class="btn-secondary inline-flex items-center gap-xs" type="button" :disabled="livingInfoReadinessLoading" @click="loadLivingInfoReadiness">
              <RefreshCw :size="16" />
              Living readiness
            </button>
            <button class="btn-secondary inline-flex items-center gap-xs" type="button" :disabled="bulkCardPreviewing" @click="generateLivingInfoCardPreviewBatch">
              <Shuffle :size="16" />
              Living info card preview
            </button>
            <button class="btn-secondary inline-flex items-center gap-xs" type="button" :disabled="loading" @click="loadAll">
              <RefreshCw :size="16" />
              새로고침
            </button>
          </div>
        </div>

        <p v-if="loadError" class="mb-md rounded border border-error bg-error-container px-md py-sm text-body-sm text-error">{{ loadError }}</p>
        <p v-if="actionMessage" class="mb-md rounded border border-success bg-success-container px-md py-sm text-body-sm text-success">{{ actionMessage }}</p>
        <p v-if="livingInfoSyncResult" class="mb-md rounded border border-outline-variant bg-surface-container-low px-md py-sm text-body-sm">
          living_info prep-cycle:
          dryRun {{ livingInfoSyncResult.dry_run ? 'YES' : 'NO' }},
          prepared {{ livingInfoSyncResult.prepare?.seen_count || 0 }},
          clusters {{ livingInfoSyncResult.prepare?.cluster_count || 0 }},
          written {{ livingInfoSyncResult.prepare?.written_count || 0 }},
          synced {{ livingInfoSyncResult.sync?.synced_count || 0 }},
          skipped {{ livingInfoSyncResult.sync?.skipped_count || 0 }}
        </p>
        <p v-if="livingInfoReadiness" class="mb-md rounded border border-outline-variant bg-surface-container-low px-md py-sm text-body-sm">
          living_info readiness:
          sources {{ livingInfoReadiness.seen_count || 0 }},
          clusters {{ livingInfoReadiness.cluster_count || 0 }},
          publicReady {{ livingInfoReadiness.public_ready_count || 0 }},
          notReady {{ livingInfoReadiness.not_ready_count || 0 }},
          topReason {{ Object.keys(livingInfoReadiness.top_skip_reasons || {})[0] || '-' }}
        </p>
        <p v-if="bulkCardPreviewResult" class="mb-md rounded border border-outline-variant bg-surface-container-low px-md py-sm text-body-sm">
          living_info card preview dry-run:
          seen {{ bulkCardPreviewResult.seen_count || 0 }},
          generated {{ bulkCardPreviewResult.generated_count || 0 }},
          failed {{ bulkCardPreviewResult.failed_count || 0 }},
          skipped {{ bulkCardPreviewResult.skipped_count || 0 }}
        </p>

        <div class="grid gap-md md:grid-cols-3 xl:grid-cols-6">
          <article v-for="card in cards" :key="card.label" class="rounded border border-outline-variant bg-surface-container-low p-md">
            <p class="text-label-sm font-bold">{{ card.label }}</p>
            <p class="mt-sm text-display-sm font-black text-primary">{{ card.value }}</p>
            <p class="text-label-sm font-bold text-success">{{ card.delta }}</p>
          </article>
        </div>
      </section>

      <section class="rounded border border-outline-variant bg-surface">
        <div class="border-b border-outline-variant p-md">
          <div class="flex flex-wrap items-center gap-sm">
            <div class="flex min-w-[280px] flex-1 items-center gap-sm rounded border border-outline-variant bg-surface-container-low px-md py-sm">
              <Search :size="18" class="text-on-surface-variant" />
              <input v-model="searchText" class="min-w-0 flex-1 bg-transparent text-body-sm outline-none" placeholder="제목, 요약, 출처, 카테고리 검색" />
            </div>
            <select v-model="sourceFilter" class="rounded border border-outline-variant bg-surface px-md py-sm text-body-sm">
              <option value="">전체 출처</option>
              <option value="SOCIAL_NEWS">소셜 뉴스</option>
              <option value="IMMIGRATION_INFO">출입국</option>
              <option value="LIVING_INFO">생활정보</option>
              <option value="OCCUPATION_INFO">직업정보</option>
            </select>
            <select v-model="statusFilter" class="rounded border border-outline-variant bg-surface px-md py-sm text-body-sm">
              <option value="">전체 상태</option>
              <option value="READY_TO_PUBLISH">게시 가능</option>
              <option value="READY_TO_REVIEW">검토 필요</option>
              <option value="FAILED_RETRYABLE">재시도 가능</option>
              <option value="POSTED">게시 완료</option>
              <option value="SCORED">채점</option>
            </select>
            <select v-model="categoryFilter" class="rounded border border-outline-variant bg-surface px-md py-sm text-body-sm">
              <option value="">전체 분류</option>
              <option v-for="category in categoryOptions" :key="category" :value="category">{{ category }}</option>
            </select>
            <label class="inline-flex items-center gap-xs rounded border border-outline-variant px-md py-sm text-body-sm">
              <input v-model="publishableOnly" type="checkbox" />
              게시 가능만
            </label>
          </div>
        </div>

        <div class="overflow-x-auto">
          <table class="w-full min-w-[1680px] border-collapse text-left text-body-sm">
            <thead class="bg-surface-container">
              <tr>
                <th class="px-md py-sm">
                  <span class="inline-flex items-center gap-xs">상태 <StatusHelp scope="content-management" title="콘텐츠 관리 상태" /></span>
                </th>
                <th class="px-md py-sm">제목</th>
                <th class="px-md py-sm">출처 도메인</th>
                <th class="px-md py-sm">유형</th>
                <th class="px-md py-sm">분류</th>
                <th class="px-md py-sm">원출처</th>
                <th class="px-md py-sm">점수</th>
                <th class="px-md py-sm">Facebook</th>
                <th class="px-md py-sm">원문 발행일</th>
                <th class="px-md py-sm">원문 수집일</th>
                <th class="px-md py-sm">콘텐츠 갱신일</th>
                <th class="px-md py-sm">게시일</th>
                <th class="px-md py-sm">제어</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in rows" :key="row.id" class="border-t border-outline-variant hover:bg-surface-container-low">
                <td class="px-md py-sm">
                  <button class="inline-flex" type="button" @click="openDetail(row)">
                    <StatusBadge :code="row.status" />
                  </button>
                </td>
                <td class="max-w-[380px] px-md py-sm">
                  <button class="text-left font-bold hover:text-primary" type="button" @click="openDetail(row)">{{ row.title }}</button>
                  <p class="mt-xxs truncate text-label-sm text-on-surface-variant">{{ row.summary_en || '-' }}</p>
                </td>
                <td class="px-md py-sm">{{ sourceLabel(row.source_domain) }}</td>
                <td class="px-md py-sm">{{ contentTypeLabel(row.content_type) }}</td>
                <td class="px-md py-sm font-mono text-label-sm">{{ row.category || '-' }}</td>
                <td class="px-md py-sm">{{ row.original_source_name || row.source_name || '-' }}</td>
                <td class="px-md py-sm font-mono font-bold text-success">{{ formatScore(row.final_publish_score) }}</td>
                <td class="px-md py-sm">
                  <a v-if="row.facebook_post_url" class="font-bold text-primary underline" :href="row.facebook_post_url" target="_blank" rel="noreferrer">게시글</a>
                  <span v-else-if="row.status === 'FAILED_RETRYABLE'" class="text-error">실패</span>
                  <span v-else>-</span>
                </td>
                <td class="px-md py-sm font-mono text-label-sm">{{ formatDate(row.original_published_at) }}</td>
                <td class="px-md py-sm font-mono text-label-sm">{{ formatDate(row.original_collected_at) }}</td>
                <td class="px-md py-sm font-mono text-label-sm">{{ formatDate(row.content_updated_at) }}</td>
                <td class="px-md py-sm font-mono text-label-sm">{{ formatDate(row.published_at) }}</td>
                <td class="px-md py-sm">
                  <button class="btn-secondary inline-flex items-center gap-xs" type="button" :disabled="actioningId === row.id || !canReview(row)" @click="sendTelegramReview(row)">
                    <Send :size="14" />
                    Telegram 검토
                  </button>
                </td>
              </tr>
              <tr v-if="!rows.length">
                <td colspan="13" class="px-md py-xl text-center text-on-surface-variant">표시할 콘텐츠 후보가 없습니다.</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="flex items-center justify-between border-t border-outline-variant p-md text-body-sm">
          <span>{{ rowRange }} / {{ totalCount }}건</span>
          <div class="flex items-center gap-sm">
            <button class="btn-secondary" type="button" :disabled="page <= 1" @click="prevPage">이전</button>
            <span class="font-mono">{{ page }} / {{ totalPages }}</span>
            <button class="btn-secondary" type="button" :disabled="page >= totalPages" @click="nextPage">다음</button>
          </div>
        </div>
      </section>

      <section v-if="detail" class="grid gap-lg xl:grid-cols-[1fr_360px]">
        <article class="rounded border border-outline-variant bg-surface p-lg">
          <div class="mb-md flex flex-wrap items-start justify-between gap-md">
            <div>
              <p class="text-label-sm font-bold text-primary">{{ sourceLabel(detail.source_domain) }} / {{ contentTypeLabel(detail.content_type) }} / {{ detail.category || '-' }}</p>
              <h2 class="mt-xs text-headline font-black">{{ detail.title }}</h2>
            </div>
            <StatusBadge :code="detail.status" />
          </div>

          <dl class="mb-md grid gap-sm text-body-sm md:grid-cols-2">
            <div><dt class="font-bold">원출처</dt><dd>{{ detail.original_source_name || detail.source_name || '-' }}</dd></div>
            <div><dt class="font-bold">원본 참조</dt><dd>{{ detail.raw_ref_table }} #{{ detail.raw_ref_id }}</dd></div>
            <div><dt class="font-bold">원문 수집일</dt><dd>{{ formatDate(detail.original_collected_at) }}</dd></div>
            <div><dt class="font-bold">콘텐츠 갱신일</dt><dd>{{ formatDate(detail.content_updated_at) }}</dd></div>
            <div><dt class="font-bold">게시일</dt><dd>{{ formatDate(detail.published_at) }}</dd></div>
            <div><dt class="font-bold">Facebook post id</dt><dd>{{ detail.facebook_post_id || '-' }}</dd></div>
            <div class="md:col-span-2">
              <dt class="font-bold">Facebook 게시 URL</dt>
              <dd>
                <a v-if="detail.facebook_post_url" class="break-all text-primary underline" :href="detail.facebook_post_url" target="_blank" rel="noreferrer">{{ detail.facebook_post_url }}</a>
                <span v-else>-</span>
              </dd>
            </div>
            <div class="md:col-span-2">
              <dt class="font-bold">원문 링크</dt>
              <dd>
                <a class="break-all text-primary underline" :href="detail.link_url || detail.original_source_url || detail.source_url" target="_blank" rel="noreferrer">
                  {{ detail.link_url || detail.original_source_url || detail.source_url || '-' }}
                </a>
              </dd>
            </div>
          </dl>

          <h3 class="mb-xs text-title font-bold">요약</h3>
          <p class="mb-md whitespace-pre-wrap text-body-sm leading-6">{{ detail.summary_en || '요약이 없습니다.' }}</p>
          <h3 class="mb-xs text-title font-bold">Why it matters</h3>
          <p class="mb-md whitespace-pre-wrap text-body-sm leading-6">{{ detail.why_it_matters_en || '중요도 설명이 없습니다.' }}</p>
          <h3 class="mb-xs text-title font-bold">본문/게시 재료</h3>
          <p class="whitespace-pre-wrap rounded border border-outline-variant bg-surface-container-low p-md text-body-sm leading-6">{{ detail.body_en || '본문이 없습니다.' }}</p>
        </article>

        <aside class="space-y-lg">
          <article class="rounded border border-outline-variant bg-surface p-lg">
            <h3 class="mb-md text-title font-bold">평가</h3>
            <dl class="space-y-sm text-body-sm">
              <div class="flex justify-between gap-md"><dt>최종 점수</dt><dd class="font-mono font-bold text-success">{{ formatScore(detail.final_publish_score) }}</dd></div>
              <div class="flex justify-between gap-md"><dt>품질</dt><dd class="font-mono">{{ formatScore(detail.quality_score) }}</dd></div>
              <div class="flex justify-between gap-md"><dt>관련성</dt><dd class="font-mono">{{ formatScore(detail.relevance_score) }}</dd></div>
              <div class="flex justify-between gap-md"><dt>실용성</dt><dd class="font-mono">{{ formatScore(detail.practical_value_score) }}</dd></div>
              <div class="flex justify-between gap-md"><dt>긴급성</dt><dd class="font-mono">{{ formatScore(detail.urgency_score) }}</dd></div>
            </dl>
            <p v-if="detail.review_required_yn" class="mt-md rounded border border-error bg-error-container p-sm text-body-sm text-error">검토 필요: {{ detail.review_reason || '사유 없음' }}</p>
            <div class="mt-md flex flex-wrap gap-xs">
              <button class="btn-secondary" type="button" :disabled="cardPreviewing || actioningId === detail.id" @click="generateCardPreview(detail)">
                Card preview
              </button>
              <button v-for="score in [90, 75, 60, 40]" :key="score" class="btn-secondary" type="button" :disabled="actioningId === detail.id" @click="applyScore(score)">
                {{ score }}점
              </button>
            </div>
          </article>

          <article class="rounded border border-outline-variant bg-surface p-lg">
            <h3 class="mb-md text-title font-bold">검토/게시 로그</h3>
            <div v-if="latestCardPreview" class="mb-sm rounded border p-sm text-body-sm" :class="cardPreviewClass(latestCardPreview)">
              <div class="flex flex-wrap items-center justify-between gap-sm">
                <b>Latest card preview</b>
                <span class="font-mono text-label-sm">{{ latestCardPreview.status || '-' }}</span>
              </div>
              <dl class="mt-xs grid gap-xs text-label-sm">
                <div class="flex justify-between gap-md"><dt>template</dt><dd class="font-mono">{{ latestCardPreview.template_type || '-' }}</dd></div>
                <div v-if="latestCardPreview.image_name" class="flex justify-between gap-md"><dt>image</dt><dd class="font-mono">{{ latestCardPreview.image_name }}</dd></div>
              </dl>
              <p v-if="latestCardPreview.reason" class="mt-xs whitespace-pre-wrap">{{ latestCardPreview.reason }}</p>
              <p v-if="latestCardPreview.image_path" class="mt-xs break-all font-mono text-[11px]">{{ latestCardPreview.image_path }}</p>
            </div>
            <div v-for="log in publishLogs" :key="log.id" class="mb-sm rounded border border-outline-variant p-sm text-body-sm">
              <div class="flex justify-between gap-md">
                <b>{{ log.status }}</b>
                <span class="font-mono text-label-sm">{{ formatDate(log.created_at) }}</span>
              </div>
              <p v-if="log.error_message" class="mt-xs text-error">{{ log.error_message }}</p>
              <a v-if="log.facebook_post_url" class="mt-xs block break-all text-primary underline" :href="log.facebook_post_url" target="_blank" rel="noreferrer">{{ log.facebook_post_url }}</a>
              <div v-if="log.content_card_preview" class="mt-sm rounded border p-sm" :class="cardPreviewClass(log.content_card_preview)">
                <div class="flex flex-wrap items-center justify-between gap-sm">
                  <b>card preview</b>
                  <span class="font-mono text-label-sm">{{ log.content_card_preview.status || '-' }}</span>
                </div>
                <dl class="mt-xs grid gap-xs text-label-sm">
                  <div class="flex justify-between gap-md"><dt>template</dt><dd class="font-mono">{{ log.content_card_preview.template_type || '-' }}</dd></div>
                  <div class="flex justify-between gap-md"><dt>required</dt><dd class="font-mono">{{ log.content_card_preview.card_required ? 'YES' : 'NO' }}</dd></div>
                  <div v-if="log.content_card_preview.image_name" class="flex justify-between gap-md"><dt>image</dt><dd class="font-mono">{{ log.content_card_preview.image_name }}</dd></div>
                </dl>
                <p v-if="log.content_card_preview.reason" class="mt-xs whitespace-pre-wrap">{{ log.content_card_preview.reason }}</p>
                <p v-if="log.content_card_preview.image_path" class="mt-xs break-all font-mono text-[11px]">{{ log.content_card_preview.image_path }}</p>
                <details v-if="log.content_card_preview.payload && Object.keys(log.content_card_preview.payload).length" class="mt-xs">
                  <summary class="cursor-pointer font-bold">card payload</summary>
                  <pre class="mt-xs max-h-40 overflow-auto rounded bg-white/60 p-sm text-[11px] text-on-surface">{{ formatPayload(log.content_card_preview.payload) }}</pre>
                </details>
              </div>
              <details v-if="log.request_payload || log.response_payload" class="mt-xs">
                <summary class="cursor-pointer font-bold">payload</summary>
                <pre class="mt-xs max-h-48 overflow-auto rounded bg-surface-container-low p-sm text-[11px]">{{ formatPayload(log.request_payload || log.response_payload) }}</pre>
              </details>
            </div>
            <p v-if="!publishLogs.length" class="text-body-sm text-on-surface-variant">검토/게시 로그가 없습니다.</p>
          </article>
        </aside>
      </section>
    </main>
  </div>
</template>
