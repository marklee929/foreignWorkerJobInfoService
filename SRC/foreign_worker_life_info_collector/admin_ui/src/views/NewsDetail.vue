<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowLeft, ExternalLink, RefreshCw, Wrench } from '@lucide/vue'
import Header from '../components/Header.vue'
import Sidebar from '../components/Sidebar.vue'
import { navItems } from '../data/defaultAdminState'
import { cleanupCandidateLinks, fetchCandidateDetail } from '../services/apiClient'
import { logoutAdmin, resetDeviceId } from '../services/authService'

const route = useRoute()
const router = useRouter()
const detail = ref(null)
const loading = ref(true)
const loadError = ref('')
const actionMessage = ref('')
const cleaning = ref(false)

const candidate = computed(() => detail.value?.candidate || {})
const publishLogs = computed(() => detail.value?.publishLogs || [])
const telegramLogs = computed(() => detail.value?.telegramLogs || [])
const pipelineLogs = computed(() => detail.value?.pipelineLogs || [])
const groupItems = computed(() => detail.value?.groupItems || [])
const rawItems = computed(() => detail.value?.rawItems || [])
const facebookMessage = computed(() => detail.value?.facebookMessage || '')
const summaryText = computed(() => candidate.value.generated_summary_en || candidate.value.short_summary || candidate.value.summary || '저장된 영문 요약이 없습니다.')
const whyText = computed(() => candidate.value.generated_why_it_matters_en || candidate.value.relevance_reason || '저장된 중요도 설명이 없습니다.')
const imageUrls = computed(() => {
  const raw = candidate.value.image_urls_json || candidate.value.image_urls || []
  const list = Array.isArray(raw) ? raw : parseJson(raw) || []
  const urls = [candidate.value.image_url, ...list].filter(Boolean)
  return [...new Set(urls)]
})

function formatDate(value) {
  if (!value) return '-'
  return String(value).replace('T', ' ').slice(0, 19)
}

function formatScore(value) {
  return Number(value || 0).toFixed(2)
}

function statusLabel(status) {
  const map = {
    RAW: '원본',
    CANDIDATE: '후보',
    COLLECTED: '수집',
    NORMALIZED: '정규화',
    SUMMARIZED: '요약완료',
    SCORED: '점수평가',
    READY_TO_PUBLISH: '게시대기',
    READY_TO_REVIEW: '검토대기',
    REVIEW_REQUIRED: '검토필요',
    AUTO_RETRY_BLOCKED: '재시막힘',
    FAILED_REPOST_REQUIRED: '재게시',
    FAILED_PERMISSION: '권한확인',
    FAILED_RETRYABLE: '재시도',
    FAILED: '실패',
    PUBLISHED: '게시완료',
    DRY_RUN_PUBLISHED: '테스트',
    NOTIFIED: '알림완료',
    DRY_RUN_NOTIFIED: '테스트',
    DUPLICATE: '중복제외',
    DUPLICATE_SKIPPED: '중복제외',
    TEXT_INVALID: '본문오류',
    SKIPPED: '제외',
    SKIPPED_LOW_SCORE: '점수미달',
    POSTED: '게시완료',
    POST_EXPIRED: '게시만료',
    SKIPPED_DAILY_RESET: '일일만료',
    ARCHIVED: '보관',
  }
  return map[status] || (status ? '기타상태' : '-')
}

function parseJson(value) {
  if (!value) return null
  if (typeof value === 'object') return value
  try {
    return JSON.parse(value)
  } catch {
    return null
  }
}

async function loadDetail() {
  loading.value = true
  loadError.value = ''
  try {
    detail.value = await fetchCandidateDetail(route.params.id)
  } catch (error) {
    loadError.value = error instanceof Error ? error.message : '뉴스 상세 데이터를 불러오지 못했습니다.'
  } finally {
    loading.value = false
  }
}

async function handleCleanupLinks() {
  if (!candidate.value.id || cleaning.value) return
  cleaning.value = true
  loadError.value = ''
  actionMessage.value = ''
  try {
    const result = await cleanupCandidateLinks({
      ids: [candidate.value.id],
      limit: 1,
      forceResummarize: false,
    })
    actionMessage.value = `링크/본문 정리 완료: URL ${result.resolved_url || 0}건, 본문 ${result.content_updated || 0}건, 요약 ${result.summary_updated || 0}건, 점수 ${result.score_updated || 0}건, 대기열 ${result.queue_updated || 0}건, 실패 ${result.failed || 0}건`
    await loadDetail()
  } catch (error) {
    loadError.value = error instanceof Error ? error.message : '링크/본문 정리에 실패했습니다.'
  } finally {
    cleaning.value = false
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

onMounted(loadDetail)
</script>

<template>
  <div class="min-h-screen bg-surface text-on-surface">
    <Sidebar :nav-items="navItems" @logout="handleLogout" />
    <Header @logout="handleLogout" />

    <main class="ml-[240px] space-y-md p-lg">
      <div class="flex items-center justify-between gap-md">
        <button class="inline-flex items-center gap-xs rounded border border-outline-variant px-md py-xs text-body-sm" type="button" @click="router.back()">
          <ArrowLeft :size="16" />
          목록으로
        </button>
        <div class="flex items-center gap-sm">
          <button class="inline-flex items-center gap-xs rounded border border-outline-variant px-md py-xs text-body-sm" type="button" :disabled="loading" @click="loadDetail">
            <RefreshCw :size="15" />
            새로고침
          </button>
          <button
            class="inline-flex items-center gap-xs rounded border border-outline-variant px-md py-xs text-body-sm font-bold disabled:cursor-not-allowed disabled:opacity-40"
            type="button"
            :disabled="loading || cleaning"
            @click="handleCleanupLinks"
          >
            <Wrench :size="15" />
            {{ cleaning ? '재생성 중' : '링크/본문 재생성' }}
          </button>
        </div>
      </div>

      <section v-if="loadError" class="rounded border border-error bg-error-container/30 p-sm text-body-sm text-error">
        {{ loadError }}
      </section>
      <section v-if="actionMessage" class="rounded border border-success bg-success/10 p-sm text-body-sm text-success">
        {{ actionMessage }}
      </section>

      <section v-if="loading" class="control-card p-lg text-body-sm text-on-surface-variant">
        상세 데이터를 불러오는 중입니다.
      </section>

      <template v-else>
        <section class="control-card overflow-hidden">
          <img v-if="imageUrls.length" class="h-[280px] w-full object-cover" :src="imageUrls[0]" alt="" />
          <div class="space-y-md p-lg">
            <div class="flex flex-wrap items-center gap-sm text-body-sm">
              <span class="rounded bg-surface-container px-sm py-[2px] font-bold">{{ statusLabel(candidate.publish_status || candidate.status) }}</span>
              <span class="font-mono text-success">점수 {{ formatScore(candidate.evaluation_score) }}</span>
              <span class="text-on-surface-variant">{{ candidate.publisher_name || candidate.source_name || candidate.source_type || '-' }}</span>
              <span class="text-on-surface-variant">최종 수집 {{ formatDate(candidate.last_seen_at || candidate.collected_at) }}</span>
              <span class="text-on-surface-variant">최초 수집 {{ formatDate(candidate.collected_at) }}</span>
            </div>
            <h1 class="max-w-[1080px] text-display font-black">{{ candidate.title || '제목 없음' }}</h1>
            <div class="grid gap-xs text-body-sm">
              <div v-if="candidate.google_news_url" class="flex flex-wrap items-center gap-sm">
                <span class="w-24 font-bold text-on-surface-variant">Google URL</span>
                <a class="min-w-0 break-all text-primary underline" :href="candidate.google_news_url" target="_blank" rel="noreferrer">{{ candidate.google_news_url }}</a>
              </div>
              <div v-if="candidate.source_url" class="flex flex-wrap items-center gap-sm">
                <span class="w-24 font-bold text-on-surface-variant">원문 URL</span>
                <a class="min-w-0 break-all text-primary underline" :href="candidate.source_url" target="_blank" rel="noreferrer">{{ candidate.source_url }}</a>
              </div>
              <div v-if="candidate.canonical_url" class="flex flex-wrap items-center gap-sm">
                <span class="w-24 font-bold text-on-surface-variant">Canonical</span>
                <a class="min-w-0 break-all text-primary underline" :href="candidate.canonical_url" target="_blank" rel="noreferrer">{{ candidate.canonical_url }}</a>
              </div>
            </div>
            <div class="flex flex-wrap gap-sm">
              <a v-if="candidate.source_url" class="inline-flex items-center gap-xs rounded border border-outline-variant px-md py-xs text-body-sm font-bold text-primary" :href="candidate.source_url" target="_blank" rel="noreferrer">
                원문 기사
                <ExternalLink :size="14" />
              </a>
              <a v-if="candidate.facebook_post_url" class="inline-flex items-center gap-xs rounded border border-outline-variant px-md py-xs text-body-sm font-bold text-primary" :href="candidate.facebook_post_url" target="_blank" rel="noreferrer">
                Facebook 게시글
                <ExternalLink :size="14" />
              </a>
            </div>
          </div>
        </section>

        <section v-if="imageUrls.length > 1" class="control-card p-md">
          <h2 class="mb-sm text-headline">이미지</h2>
          <div class="flex gap-sm overflow-x-auto">
            <img v-for="url in imageUrls" :key="url" class="h-28 w-44 rounded border border-outline-variant object-cover" :src="url" alt="" />
          </div>
        </section>

        <section class="grid grid-cols-2 gap-md">
          <section class="control-card p-md">
            <div class="mb-sm flex items-center justify-between gap-md">
              <h2 class="text-headline">그룹 내부 기사</h2>
              <span class="text-body-sm text-on-surface-variant">{{ candidate.group_item_count || groupItems.length }}건</span>
            </div>
            <div class="max-h-[260px] space-y-sm overflow-y-auto">
              <div v-for="item in groupItems" :key="item.id" class="rounded border border-outline-variant p-sm text-body-sm">
                <div class="mb-xs flex flex-wrap items-center gap-sm">
                  <span v-if="item.is_representative" class="rounded bg-primary-container px-sm py-[2px] font-bold text-primary">대표</span>
                  <span class="rounded bg-surface-container px-sm py-[2px] font-bold">{{ statusLabel(item.publish_status || item.status) }}</span>
                  <span class="font-mono text-success">{{ formatScore(item.evaluation_score) }}</span>
                  <span class="text-on-surface-variant">최종 {{ formatDate(item.last_seen_at || item.collected_at) }}</span>
                  <span class="text-on-surface-variant">최초 {{ formatDate(item.collected_at) }}</span>
                </div>
                <p class="font-bold">{{ item.title }}</p>
                <div class="mt-xs flex flex-wrap gap-sm text-on-surface-variant">
                  <span>{{ item.source_name || item.source_type || '-' }}</span>
                  <a v-if="item.source_url" class="text-primary underline" :href="item.source_url" target="_blank" rel="noreferrer">원문</a>
                  <a v-if="item.google_news_url" class="text-primary underline" :href="item.google_news_url" target="_blank" rel="noreferrer">Google</a>
                </div>
              </div>
              <p v-if="!groupItems.length" class="text-body-sm text-on-surface-variant">그룹 내부 기사가 없습니다.</p>
            </div>
          </section>

          <section class="control-card p-md">
            <div class="mb-sm flex items-center justify-between gap-md">
              <h2 class="text-headline">원천 수집 기록</h2>
              <span class="text-body-sm text-on-surface-variant">{{ rawItems.length }}건</span>
            </div>
            <div class="max-h-[260px] space-y-sm overflow-y-auto">
              <div v-for="item in rawItems" :key="item.id" class="rounded border border-outline-variant p-sm text-body-sm">
                <div class="mb-xs flex flex-wrap items-center gap-sm">
                  <span v-if="item.is_duplicate" class="rounded bg-surface-container px-sm py-[2px] font-bold">중복 수집</span>
                  <span>{{ item.publisher_name || item.source_name || item.source_type || '-' }}</span>
                  <span class="font-mono text-on-surface-variant">{{ formatDate(item.collected_at) }}</span>
                </div>
                <p class="font-bold">{{ item.title }}</p>
                <div class="mt-xs flex flex-wrap gap-sm text-on-surface-variant">
                  <a v-if="item.source_url" class="text-primary underline" :href="item.source_url" target="_blank" rel="noreferrer">원문</a>
                  <a v-if="item.google_news_url" class="text-primary underline" :href="item.google_news_url" target="_blank" rel="noreferrer">Google</a>
                  <span v-if="item.duplicate_reason">{{ item.duplicate_reason }}</span>
                </div>
              </div>
              <p v-if="!rawItems.length" class="text-body-sm text-on-surface-variant">원천 수집 기록이 없습니다.</p>
            </div>
          </section>
        </section>

        <section class="grid grid-cols-[minmax(0,1fr)_420px] gap-md">
          <article class="control-card min-w-0 space-y-md p-lg">
            <div>
              <h2 class="mb-xs text-headline">영문 요약</h2>
              <p class="whitespace-pre-wrap text-body-sm leading-6">{{ summaryText }}</p>
            </div>
            <div>
              <h2 class="mb-xs text-headline">Why it matters</h2>
              <p class="whitespace-pre-wrap text-body-sm leading-6">{{ whyText }}</p>
            </div>
            <div>
              <h2 class="mb-xs text-headline">최종 Facebook 게시 본문</h2>
              <pre class="max-w-full whitespace-pre-wrap break-words rounded border border-outline-variant bg-surface-container-low p-md text-body-sm leading-6">{{ facebookMessage || '게시 본문 미리보기가 없습니다.' }}</pre>
            </div>
            <div>
              <h2 class="mb-xs text-headline">기사 원문</h2>
              <p class="whitespace-pre-wrap break-words text-body-sm leading-7">{{ candidate.content || '저장된 기사 본문이 없습니다. 일부 RSS/검색 결과는 원문 HTML 접근이 제한될 수 있습니다.' }}</p>
            </div>
          </article>

          <aside class="min-w-0 space-y-md">
            <section class="control-card p-md">
              <h2 class="mb-sm text-headline">평가</h2>
              <dl class="space-y-xs text-body-sm">
                <div class="flex justify-between gap-md"><dt>중복 위험</dt><dd class="font-mono">{{ formatScore(candidate.duplicate_risk_score) }}</dd></div>
                <div class="flex justify-between gap-md"><dt>한국 관련성</dt><dd class="font-mono">{{ formatScore(candidate.korea_relevance_score) }}</dd></div>
                <div class="flex justify-between gap-md"><dt>카테고리</dt><dd>{{ candidate.content_priority_group || '-' }} / {{ candidate.content_category || candidate.category || '-' }}</dd></div>
                <div class="flex justify-between gap-md"><dt>정착 관련성</dt><dd class="font-mono">{{ formatScore(candidate.settlement_relevance_score) }}</dd></div>
                <div class="flex justify-between gap-md"><dt>실용 가치</dt><dd class="font-mono">{{ formatScore(candidate.practical_value_score) }}</dd></div>
                <div class="flex justify-between gap-md"><dt>순환 점수</dt><dd class="font-mono">{{ formatScore(candidate.category_rotation_score) }}</dd></div>
                <div class="flex justify-between gap-md"><dt>비자/노동</dt><dd class="font-mono">{{ formatScore(candidate.visa_or_labor_policy_score) }}</dd></div>
                <div class="flex justify-between gap-md"><dt>게시 적합도</dt><dd class="font-mono">{{ formatScore(candidate.facebook_post_suitability_score) }}</dd></div>
                <div class="flex justify-between gap-md"><dt>위험도</dt><dd>{{ candidate.risk_level || '-' }}</dd></div>
              </dl>
            </section>

            <section class="control-card p-md">
              <h2 class="mb-sm text-headline">처리 사유</h2>
              <p class="whitespace-pre-wrap text-body-sm leading-6">{{ candidate.category_selection_reason || candidate.review_required_reason || candidate.selection_reason || candidate.skip_reason || candidate.fail_reason || '저장된 사유가 없습니다.' }}</p>
            </section>
          </aside>
        </section>

        <section class="control-card p-md">
          <h2 class="mb-sm text-headline">Facebook 게시 로그</h2>
          <div class="space-y-sm">
            <div v-for="log in publishLogs" :key="log.id" class="rounded border border-outline-variant p-sm text-body-sm">
              <div class="mb-xs flex flex-wrap items-center gap-sm font-bold">
                <span>{{ log.status }}</span>
                <span class="font-mono text-on-surface-variant">{{ formatDate(log.published_at) }}</span>
                <span v-if="log.error_code" class="text-error">{{ log.error_code }}</span>
              </div>
              <p v-if="log.error_message" class="whitespace-pre-wrap text-error">{{ log.error_message }}</p>
              <details v-if="log.final_message" class="mt-sm">
                <summary class="cursor-pointer font-bold">final_message</summary>
                <pre class="mt-xs max-w-full whitespace-pre-wrap break-words rounded bg-surface-container-low p-sm text-[11px]">{{ log.final_message }}</pre>
              </details>
              <details v-if="log.payload_preview" class="mt-sm">
                <summary class="cursor-pointer font-bold">payload preview</summary>
                <pre class="mt-xs max-w-full overflow-auto rounded bg-surface-container-low p-sm text-[11px]">{{ JSON.stringify(parseJson(log.payload_preview) || log.payload_preview, null, 2) }}</pre>
              </details>
              <details v-if="log.response_body" class="mt-sm">
                <summary class="cursor-pointer font-bold">Facebook response</summary>
                <pre class="mt-xs max-w-full overflow-auto rounded bg-surface-container-low p-sm text-[11px]">{{ JSON.stringify(parseJson(log.response_body) || log.response_body, null, 2) }}</pre>
              </details>
            </div>
            <p v-if="!publishLogs.length" class="text-body-sm text-on-surface-variant">게시 로그가 없습니다.</p>
          </div>
        </section>

        <section class="grid grid-cols-2 gap-md">
          <section class="control-card p-md">
            <h2 class="mb-sm text-headline">Telegram 알림 로그</h2>
            <div class="space-y-sm">
              <div v-for="log in telegramLogs" :key="log.id" class="rounded border border-outline-variant p-sm text-body-sm">
                <div class="mb-xs flex items-center justify-between gap-md font-bold">
                  <span>{{ log.status }}</span>
                  <span class="font-mono text-on-surface-variant">{{ formatDate(log.sent_at) }}</span>
                </div>
                <p class="whitespace-pre-wrap">{{ log.message }}</p>
                <p v-if="log.error_message" class="mt-xs text-error">{{ log.error_message }}</p>
              </div>
              <p v-if="!telegramLogs.length" class="text-body-sm text-on-surface-variant">알림 로그가 없습니다.</p>
            </div>
          </section>

          <section class="control-card p-md">
            <h2 class="mb-sm text-headline">처리 로그</h2>
            <div class="max-h-[420px] space-y-sm overflow-y-auto">
              <div v-for="log in pipelineLogs" :key="log.id" class="rounded border border-outline-variant p-sm text-body-sm">
                <div class="mb-xs flex items-center justify-between gap-md font-bold">
                  <span>{{ log.step_name }} / {{ log.status }}</span>
                  <span class="font-mono text-on-surface-variant">{{ formatDate(log.created_at) }}</span>
                </div>
                <p class="whitespace-pre-wrap">{{ log.message }}</p>
              </div>
              <p v-if="!pipelineLogs.length" class="text-body-sm text-on-surface-variant">처리 로그가 없습니다.</p>
            </div>
          </section>
        </section>
      </template>
    </main>
  </div>
</template>
