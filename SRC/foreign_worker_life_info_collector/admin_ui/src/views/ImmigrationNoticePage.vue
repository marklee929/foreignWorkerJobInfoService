<script setup>
import { computed, onMounted, ref } from 'vue'
import { Check, ExternalLink, FileText, RefreshCw, Search } from '@lucide/vue'
import Header from '../components/Header.vue'
import Sidebar from '../components/Sidebar.vue'
import StatusBadge from '../components/StatusBadge.vue'
import StatusHelp from '../components/StatusHelp.vue'
import { navItems } from '../data/defaultAdminState'
import {
  approveImmigrationNotice,
  collectImmigrationNotices,
  fetchImmigrationDashboard,
  fetchImmigrationNoticeDetail,
  fetchImmigrationNotices,
  publishImmigrationNotice,
  summarizeImmigrationNotice,
} from '../services/apiClient'
import { logoutAdmin, resetDeviceId } from '../services/authService'

const dashboard = ref({})
const rows = ref([])
const detail = ref(null)
const logs = ref([])
const loading = ref(false)
const collecting = ref(false)
const actionMessage = ref('')
const errorMessage = ref('')
const keyword = ref('')
const statusFilter = ref('')
const sourceFilter = ref('')
const page = ref(1)
const pageSize = 20
const totalCount = ref(0)

const totalPages = computed(() => Math.max(1, Math.ceil(totalCount.value / pageSize)))
const sourceCounts = computed(() => dashboard.value.source_counts || [])

function formatDate(value) {
  return value ? String(value).replace('T', ' ').slice(0, 16) : '-'
}

async function loadDashboard() {
  dashboard.value = await fetchImmigrationDashboard()
  logs.value = dashboard.value.recent_logs || []
}

async function loadRows() {
  loading.value = true
  errorMessage.value = ''
  try {
    const payload = await fetchImmigrationNotices({
      page: page.value,
      size: pageSize,
      keyword: keyword.value.trim(),
      source_type: sourceFilter.value,
      content_status: statusFilter.value,
    })
    rows.value = payload.items || []
    totalCount.value = Number(payload.total_count || 0)
  } catch (error) {
    errorMessage.value = error.message
    rows.value = []
    totalCount.value = 0
  } finally {
    loading.value = false
  }
}

async function refreshAll() {
  await Promise.all([loadDashboard(), loadRows()])
}

async function runCollect() {
  collecting.value = true
  actionMessage.value = ''
  try {
    const result = await collectImmigrationNotices({ limit: 20 })
    actionMessage.value = `수집 완료: 신규 ${result.inserted_count || 0}건, 갱신 ${result.updated_count || 0}건, 실패 ${result.failed_count || 0}건`
    await refreshAll()
  } catch (error) {
    errorMessage.value = error.message
  } finally {
    collecting.value = false
  }
}

async function openDetail(row) {
  detail.value = await fetchImmigrationNoticeDetail(row.id)
}

async function summarizeSelected() {
  if (!detail.value?.id) return
  const result = await summarizeImmigrationNotice(detail.value.id)
  actionMessage.value = result.ok ? '영문 요약을 생성했습니다.' : result.message
  detail.value = await fetchImmigrationNoticeDetail(detail.value.id)
  await loadRows()
}

async function approveSelected() {
  if (!detail.value?.id) return
  await approveImmigrationNotice(detail.value.id)
  actionMessage.value = '게시 대기 상태로 전환했습니다.'
  detail.value = await fetchImmigrationNoticeDetail(detail.value.id)
  await loadRows()
}

async function publishSelected() {
  if (!detail.value?.id) return
  const result = await publishImmigrationNotice(detail.value.id)
  actionMessage.value = result.message || 'AUTO_PUBLISH_OFF'
}

function previousPage() {
  if (page.value <= 1) return
  page.value -= 1
  loadRows()
}

function nextPage() {
  if (page.value >= totalPages.value) return
  page.value += 1
  loadRows()
}

function handleLogout() {
  logoutAdmin()
  resetDeviceId()
  window.location.href = '/auth'
}

onMounted(refreshAll)
</script>

<template>
  <div class="min-h-screen bg-surface text-on-surface">
    <Sidebar :nav-items="navItems" @logout="handleLogout" />
    <Header :server-status="errorMessage ? 'error' : 'ok'" :server-message="errorMessage" @logout="handleLogout" />

    <main class="ml-[240px] min-w-0 space-y-lg p-lg">
      <section class="control-card p-lg">
        <div class="flex flex-wrap items-start justify-between gap-md">
          <div>
            <p class="text-label-caps text-primary">WorkConnect Admin</p>
            <h1 class="text-display-sm font-black">출입국 정보</h1>
            <p class="mt-xs text-body-sm text-on-surface-variant">법무부, 하이코리아, EPS 등 공식 출처의 비자/체류/외국인 정책 공지를 관리합니다.</p>
          </div>
          <div class="flex items-center gap-sm">
            <button class="btn-secondary" type="button" @click="refreshAll">
              <RefreshCw class="size-4" /> 새로고침
            </button>
            <button class="btn-primary" type="button" :disabled="collecting" @click="runCollect">
              <RefreshCw class="size-4" /> 공식 출처 수집
            </button>
          </div>
        </div>
      </section>

      <section v-if="actionMessage" class="mb-md rounded-sm border border-success bg-success-container px-md py-sm text-body-sm text-success">
        {{ actionMessage }}
      </section>
      <section v-if="errorMessage" class="mb-md rounded-sm border border-error bg-error-container px-md py-sm text-body-sm text-error">
        {{ errorMessage }}
      </section>

      <section class="grid grid-cols-5 gap-md">
        <div class="control-card p-md"><p class="text-label-sm">전체 공지</p><p class="text-title-lg">{{ dashboard.total_count || 0 }}</p></div>
        <div class="control-card p-md"><p class="text-label-sm">오늘 수집</p><p class="text-title-lg">{{ dashboard.collected_today_count || 0 }}</p></div>
        <div class="control-card p-md"><p class="text-label-sm">검토 대기</p><p class="text-title-lg">{{ dashboard.ready_to_review_count || 0 }}</p></div>
        <div class="control-card p-md"><p class="text-label-sm">고중요도</p><p class="text-title-lg">{{ dashboard.high_importance_count || 0 }}</p></div>
        <div class="control-card p-md"><p class="text-label-sm">게시 완료</p><p class="text-title-lg">{{ dashboard.posted_count || 0 }}</p></div>
      </section>

      <section class="grid grid-cols-[minmax(0,1fr)_360px] gap-md">
        <div class="control-card min-w-0 overflow-hidden">
          <div class="flex items-center gap-sm border-b border-outline-variant bg-surface-container px-md py-sm">
            <Search class="size-4 text-on-surface-variant" />
            <input v-model="keyword" class="min-w-0 flex-1 bg-transparent outline-none" placeholder="제목, 요약, 출처 검색" @keyup.enter="loadRows" />
            <select v-model="sourceFilter" class="rounded-sm border border-outline-variant bg-surface px-sm py-xs" @change="loadRows">
              <option value="">전체 출처</option>
              <option value="MINISTRY_OF_JUSTICE">법무부</option>
              <option value="HIKOREA">하이코리아</option>
              <option value="EPS">EPS</option>
              <option value="MOEL">고용노동부</option>
            </select>
            <select v-model="statusFilter" class="rounded-sm border border-outline-variant bg-surface px-sm py-xs" @change="loadRows">
              <option value="">전체 상태</option>
              <option value="READY_TO_REVIEW">검토 대기</option>
              <option value="READY_TO_PUBLISH">게시 대기</option>
              <option value="POSTED">게시 완료</option>
            </select>
          </div>
          <div class="overflow-x-auto">
            <table class="w-full min-w-[960px] table-fixed text-body-sm">
              <thead class="bg-surface-container">
                <tr class="border-b border-outline-variant text-left">
                  <th class="w-[72px] px-md py-sm text-center">
                    <span class="inline-flex items-center justify-center gap-xs">상태 <StatusHelp scope="immigration" title="출입국 상태" /></span>
                  </th>
                  <th class="px-md py-sm">제목</th>
                  <th class="w-[130px] px-md py-sm">출처</th>
                  <th class="w-[120px] px-md py-sm">비자</th>
                  <th class="w-[90px] px-md py-sm">중요도</th>
                  <th class="w-[130px] px-md py-sm">수집일</th>
                </tr>
              </thead>
              <tbody>
                <tr v-if="!loading && rows.length === 0">
                  <td colspan="6" class="px-md py-lg text-center text-on-surface-variant">수집된 공식 공지가 없습니다.</td>
                </tr>
                <tr v-for="row in rows" :key="row.id" class="cursor-pointer border-b border-outline-variant hover:bg-surface-container" @click="openDetail(row)">
                  <td class="px-md py-sm text-center">
                    <StatusBadge :code="row.content_status" variant="dot" />
                  </td>
                  <td class="truncate px-md py-sm font-bold">{{ row.title_ko }}</td>
                  <td class="px-md py-sm">{{ row.source_name }}</td>
                  <td class="px-md py-sm">{{ (row.affected_visa_types || []).join(', ') || '-' }}</td>
                  <td class="px-md py-sm font-mono text-success">{{ Number(row.importance_score || 0).toFixed(0) }}</td>
                  <td class="px-md py-sm font-mono">{{ formatDate(row.collected_at) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
          <div class="flex items-center justify-between px-md py-sm">
            <span class="text-body-sm text-on-surface-variant">총 {{ totalCount }}건</span>
            <div class="flex items-center gap-sm">
              <button class="btn-secondary" type="button" :disabled="page <= 1" @click="previousPage">이전</button>
              <span class="font-mono">{{ page }} / {{ totalPages }}</span>
              <button class="btn-secondary" type="button" :disabled="page >= totalPages" @click="nextPage">다음</button>
            </div>
          </div>
        </div>

        <aside class="space-y-md">
          <section class="control-card p-md">
            <h2 class="text-title-sm">출처별 수집 현황</h2>
            <div v-for="item in sourceCounts" :key="item.source_type" class="mt-sm flex justify-between text-body-sm">
              <span>{{ item.source_type }}</span><span class="font-mono">{{ item.count }}</span>
            </div>
          </section>
          <section class="control-card p-md">
            <h2 class="text-title-sm">최근 수집 로그</h2>
            <div v-for="log in logs" :key="`${log.collector_type}-${log.finished_at}`" class="mt-sm border-t border-outline-variant pt-sm text-body-sm">
              <p class="font-bold">{{ log.source_name }} / {{ log.status }}</p>
              <p>신규 {{ log.inserted_count }} · 갱신 {{ log.updated_count }} · 실패 {{ log.failed_count }}</p>
              <p class="font-mono text-on-surface-variant">{{ formatDate(log.finished_at) }}</p>
              <p v-if="log.error_message" class="text-error">{{ log.error_message }}</p>
            </div>
          </section>
        </aside>
      </section>

      <section v-if="detail" class="control-card p-md">
        <div class="flex items-start justify-between gap-md">
          <div>
            <p class="text-label-sm text-primary">{{ detail.source_name }} · {{ detail.notice_type }}</p>
            <h2 class="text-title-md">{{ detail.title_ko }}</h2>
          </div>
          <div class="flex gap-sm">
            <a class="btn-secondary" :href="detail.original_url" target="_blank" rel="noreferrer"><ExternalLink class="size-4" /> 원문</a>
            <button class="btn-secondary" type="button" @click="summarizeSelected"><FileText class="size-4" /> 요약 생성</button>
            <button class="btn-secondary" type="button" @click="approveSelected"><Check class="size-4" /> 검토 승인</button>
            <button class="btn-secondary" type="button" @click="publishSelected">게시 확인</button>
          </div>
        </div>
        <div class="mt-md grid grid-cols-[minmax(0,1fr)_320px] gap-md">
          <div class="space-y-md">
            <section>
              <h3 class="text-title-sm">영문 요약</h3>
              <pre class="mt-sm whitespace-pre-wrap rounded-sm bg-surface-container p-md text-body-sm">{{ detail.summary_en || '요약이 없습니다.' }}</pre>
            </section>
            <section>
              <h3 class="text-title-sm">Why it matters</h3>
              <pre class="mt-sm whitespace-pre-wrap rounded-sm bg-surface-container p-md text-body-sm">{{ detail.why_it_matters_en || '설명이 없습니다.' }}</pre>
            </section>
            <section>
              <h3 class="text-title-sm">원문 내용</h3>
              <p class="mt-sm whitespace-pre-wrap text-body-sm">{{ detail.raw_content_ko || '본문은 아직 수집되지 않았습니다.' }}</p>
            </section>
          </div>
          <aside class="space-y-md">
            <div class="control-card p-md">
              <p class="flex items-center gap-xs">
                상태:
                <StatusBadge :code="detail.content_status" />
              </p>
              <p>중요도: <b>{{ Number(detail.importance_score || 0).toFixed(0) }}</b></p>
              <p>긴급도: <b>{{ detail.urgency_level }}</b></p>
            </div>
            <div class="control-card p-md">
              <p>비자: {{ (detail.affected_visa_types || []).join(', ') || '-' }}</p>
              <p>대상: {{ (detail.affected_user_groups || []).join(', ') || '-' }}</p>
              <p>키워드: {{ (detail.policy_keywords || []).join(', ') || '-' }}</p>
            </div>
          </aside>
        </div>
      </section>
    </main>
  </div>
</template>
