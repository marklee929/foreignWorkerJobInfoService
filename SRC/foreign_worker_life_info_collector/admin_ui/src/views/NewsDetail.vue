<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowLeft, ExternalLink, RefreshCw, RotateCcw } from '@lucide/vue'
import Header from '../components/Header.vue'
import Sidebar from '../components/Sidebar.vue'
import { navItems } from '../data/defaultAdminState'
import { fetchCandidateDetail, repostCandidate } from '../services/apiClient'
import { logoutAdmin, resetDeviceId } from '../services/authService'

const route = useRoute()
const router = useRouter()
const detail = ref(null)
const loading = ref(true)
const loadError = ref('')
const reposting = ref(false)

const candidate = computed(() => detail.value?.candidate || {})
const publishLogs = computed(() => detail.value?.publishLogs || [])
const telegramLogs = computed(() => detail.value?.telegramLogs || [])
const pipelineLogs = computed(() => detail.value?.pipelineLogs || [])
const groupItems = computed(() => detail.value?.groupItems || [])
const rawItems = computed(() => detail.value?.rawItems || [])
const facebookMessage = computed(() => detail.value?.facebookMessage || '')
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
    READY_TO_PUBLISH: '게시 대기',
    POSTED: '게시 완료',
    PUBLISHED: '게시 완료',
    FAILED_PERMISSION: '권한 확인 필요',
    FAILED_REPOST_REQUIRED: '재게시 필요',
    FAILED_RETRYABLE: '재시도 대기',
    DUPLICATE: '중복 제외',
    NORMALIZED: '정규화',
    SUMMARIZED: '요약 완료',
    SCORED: '점수 평가',
    SKIPPED: '제외',
    POST_EXPIRED: '게시 만료',
  }
  return map[status] || status || '-'
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

async function handleRepost() {
  if (!candidate.value.id || reposting.value) return
  reposting.value = true
  loadError.value = ''
  try {
    const result = await repostCandidate(candidate.value.id)
    if (!result.ok) {
      const debug = result.result?.token_debug
      const debugMessage = debug
        ? ` / 토큰 확인: type=${debug.token_type || '-'}, valid=${debug.is_valid === true}, profile_id=${debug.profile_id || '-'}`
        : ''
      loadError.value = `${result.result?.error_message || result.message || '재게시 요청은 처리됐지만 Facebook 게시에 실패했습니다.'}${debugMessage}`
    }
    await loadDetail()
  } catch (error) {
    loadError.value = error instanceof Error ? error.message : '재게시 요청에 실패했습니다.'
  } finally {
    reposting.value = false
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
            :disabled="reposting || Boolean(candidate.facebook_post_url)"
            @click="handleRepost"
          >
            <RotateCcw :size="15" />
            {{ reposting ? '재게시 중' : '재게시' }}
          </button>
        </div>
      </div>

      <section v-if="loadError" class="rounded border border-error bg-error-container/30 p-sm text-body-sm text-error">
        {{ loadError }}
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
              <span class="text-on-surface-variant">{{ formatDate(candidate.collected_at) }}</span>
            </div>
            <h1 class="max-w-[1080px] text-display font-black">{{ candidate.title || '제목 없음' }}</h1>
            <div class="grid gap-xs text-body-sm">
              <div v-if="candidate.google_news_url" class="flex flex-wrap items-center gap-sm">
                <span class="w-24 font-bold text-on-surface-variant">Google URL</span>
                <a class="text-primary underline" :href="candidate.google_news_url" target="_blank" rel="noreferrer">{{ candidate.google_news_url }}</a>
              </div>
              <div v-if="candidate.source_url" class="flex flex-wrap items-center gap-sm">
                <span class="w-24 font-bold text-on-surface-variant">원문 URL</span>
                <a class="text-primary underline" :href="candidate.source_url" target="_blank" rel="noreferrer">{{ candidate.source_url }}</a>
              </div>
              <div v-if="candidate.canonical_url" class="flex flex-wrap items-center gap-sm">
                <span class="w-24 font-bold text-on-surface-variant">Canonical</span>
                <a class="text-primary underline" :href="candidate.canonical_url" target="_blank" rel="noreferrer">{{ candidate.canonical_url }}</a>
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
                  <span class="text-on-surface-variant">{{ formatDate(item.collected_at) }}</span>
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
          <article class="control-card space-y-md p-lg">
            <div>
              <h2 class="mb-xs text-headline">영문 요약</h2>
              <p class="whitespace-pre-wrap text-body-sm leading-6">{{ candidate.generated_summary_en || candidate.short_summary || candidate.summary || '저장된 영문 요약이 없습니다.' }}</p>
            </div>
            <div>
              <h2 class="mb-xs text-headline">Why it matters</h2>
              <p class="whitespace-pre-wrap text-body-sm leading-6">{{ candidate.generated_why_it_matters_en || candidate.relevance_reason || '저장된 중요도 설명이 없습니다.' }}</p>
            </div>
            <div>
              <h2 class="mb-xs text-headline">최종 Facebook 게시 본문</h2>
              <pre class="whitespace-pre-wrap rounded border border-outline-variant bg-surface-container-low p-md text-body-sm leading-6">{{ facebookMessage || '게시 본문 미리보기가 없습니다.' }}</pre>
            </div>
            <div>
              <h2 class="mb-xs text-headline">기사 원문</h2>
              <p class="whitespace-pre-wrap text-body-sm leading-7">{{ candidate.content || '저장된 기사 본문이 없습니다. 일부 RSS/검색 결과는 원문 HTML 접근이 제한될 수 있습니다.' }}</p>
            </div>
          </article>

          <aside class="space-y-md">
            <section class="control-card p-md">
              <h2 class="mb-sm text-headline">평가</h2>
              <dl class="space-y-xs text-body-sm">
                <div class="flex justify-between gap-md"><dt>중복 위험</dt><dd class="font-mono">{{ formatScore(candidate.duplicate_risk_score) }}</dd></div>
                <div class="flex justify-between gap-md"><dt>한국 관련성</dt><dd class="font-mono">{{ formatScore(candidate.korea_relevance_score) }}</dd></div>
                <div class="flex justify-between gap-md"><dt>비자/노동</dt><dd class="font-mono">{{ formatScore(candidate.visa_or_labor_policy_score) }}</dd></div>
                <div class="flex justify-between gap-md"><dt>게시 적합도</dt><dd class="font-mono">{{ formatScore(candidate.facebook_post_suitability_score) }}</dd></div>
                <div class="flex justify-between gap-md"><dt>위험도</dt><dd>{{ candidate.risk_level || '-' }}</dd></div>
              </dl>
            </section>

            <section class="control-card p-md">
              <h2 class="mb-sm text-headline">처리 사유</h2>
              <p class="whitespace-pre-wrap text-body-sm leading-6">{{ candidate.selection_reason || candidate.skip_reason || candidate.fail_reason || '저장된 사유가 없습니다.' }}</p>
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
              <pre v-if="parseJson(log.response_body)?.token_debug" class="mt-sm overflow-auto rounded bg-surface-container-low p-sm text-[11px]">{{ JSON.stringify(parseJson(log.response_body).token_debug, null, 2) }}</pre>
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
