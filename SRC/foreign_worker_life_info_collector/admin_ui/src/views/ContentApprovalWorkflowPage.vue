<script setup>
import { computed, onMounted, ref } from 'vue'
import { AlertCircle, Check, Database, Eye, FileClock, ListChecks, PlayCircle, RefreshCw, Send, X } from '@lucide/vue'
import Header from '../components/Header.vue'
import Sidebar from '../components/Sidebar.vue'
import StatusBadge from '../components/StatusBadge.vue'
import StatusHelp from '../components/StatusHelp.vue'
import { navItems } from '../data/defaultAdminState'
import {
  approveGeneratedContent,
  collectContentSources,
  fetchContentApprovalDashboard,
  fetchGeneratedContentDetail,
  fetchGeneratedContents,
  fetchPublishTargets,
  fetchReviewLogs,
  fetchSourceCatalog,
  fetchSourceItems,
  generateContentDrafts,
  rejectGeneratedContent,
  sendContentToTelegram,
} from '../services/apiClient'
import { logoutAdmin, resetDeviceId } from '../services/authService'

const tabs = [
  { key: 'generated', label: 'GENERATED', icon: ListChecks, status: 'GENERATED' },
  { key: 'sent', label: 'SENT_TO_TELEGRAM', icon: Send, status: 'SENT_TO_TELEGRAM' },
  { key: 'approved', label: 'APPROVED', icon: Check, status: 'APPROVED' },
  { key: 'rejected', label: 'REJECTED', icon: X, status: 'REJECTED' },
  { key: 'sources', label: 'Source Registry', icon: Database },
  { key: 'publish', label: 'Publish Log', icon: FileClock },
]

const statusTabMap = {
  generated: 'GENERATED',
  sent: 'SENT_TO_TELEGRAM',
  approved: 'APPROVED',
  rejected: 'REJECTED',
}

const dashboard = ref({})
const activeTab = ref('generated')
const generatedRows = ref([])
const sourceRows = ref([])
const sourceCatalog = ref([])
const publishRows = ref([])
const reviewLogs = ref([])
const selectedDetail = ref(null)
const loading = ref(false)
const actioningId = ref(0)
const errorMessage = ref('')
const actionMessage = ref('')
const statusFilter = ref('GENERATED')
const categoryFilter = ref('')
const sourceLimit = ref(10)

const sourceForm = ref({
  sourceDomain: 'EMPLOYMENT',
  sourcePlatform: 'work24',
  sourceName: 'Work24',
  sourceUrl: '',
  title: '',
  summaryText: '',
  language: 'ko',
  countryCode: 'KR',
  category: 'employment',
  sourceRiskLevel: 'LOW',
  accessRestriction: 'PUBLIC',
  copyrightRiskLevel: 'LOW',
  piiCheckedYn: true,
  usableForContentYn: true,
})

const cards = computed(() => [
  { label: 'Total', value: dashboard.value.total || 0, tone: 'text-primary' },
  { label: 'Generated', value: dashboard.value.generated || 0, tone: 'text-success' },
  { label: 'Telegram', value: dashboard.value.sentToTelegram || 0, tone: 'text-primary' },
  { label: 'Approved', value: dashboard.value.approved || 0, tone: 'text-success' },
  { label: 'Rejected', value: dashboard.value.rejected || 0, tone: 'text-error' },
  { label: 'Published', value: dashboard.value.published || 0, tone: 'text-on-surface' },
])

const currentSourceCatalog = computed(() => {
  return sourceCatalog.value.find((item) => item.sourcePlatform === sourceForm.value.sourcePlatform)
})

function formatDate(value) {
  return value ? String(value).replace('T', ' ').slice(0, 19) : '-'
}

function sourceLabel(domain) {
  const labels = {
    EMPLOYMENT: 'Employment',
    VISA_IMMIGRATION: 'Visa',
    LIVING_INFO: 'Living Info',
    COMMUNITY: 'Community Signal',
    SOCIAL_NEWS: 'Social News',
    OCCUPATION_INFO: 'Occupation',
    GOVERNMENT_NOTICE: 'Government Notice',
  }
  return labels[domain] || domain || '-'
}

function contentTypeFor(row) {
  if (row.sourceDomain === 'EMPLOYMENT') return 'JOB_GUIDE'
  if (row.sourceDomain === 'VISA_IMMIGRATION') return 'VISA_GUIDE'
  if (row.sourceDomain === 'LIVING_INFO') return 'LIVING_TIP'
  if (row.sourceDomain === 'COMMUNITY') return 'COMMUNITY_FAQ'
  return 'NEWS_EXPLAINER'
}

async function loadDashboard() {
  dashboard.value = await fetchContentApprovalDashboard()
}

async function loadGenerated() {
  generatedRows.value = await fetchGeneratedContents({
    status: statusFilter.value || statusTabMap[activeTab.value] || '',
    category: categoryFilter.value,
    limit: 100,
  })
}

async function loadSources() {
  sourceRows.value = await fetchSourceItems({ limit: 100 })
}

async function loadSourceCatalog() {
  sourceCatalog.value = await fetchSourceCatalog()
  if (!sourceForm.value.sourcePlatform && sourceCatalog.value.length > 0) {
    sourceForm.value.sourcePlatform = sourceCatalog.value[0].sourcePlatform
    applySourceCatalog()
  }
}

async function loadPublishRows() {
  publishRows.value = await fetchPublishTargets({ limit: 100 })
}

async function loadReviewLogs(contentId = '') {
  reviewLogs.value = await fetchReviewLogs({ contentId, limit: 100 })
}

async function loadAll() {
  loading.value = true
  errorMessage.value = ''
  try {
    await Promise.all([loadDashboard(), loadGenerated(), loadSources(), loadSourceCatalog(), loadPublishRows(), loadReviewLogs()])
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : 'Failed to load data.'
  } finally {
    loading.value = false
  }
}

async function changeTab(tab) {
  activeTab.value = tab.key
  statusFilter.value = tab.status || ''
  selectedDetail.value = null
  if (tab.status) await loadGenerated()
  if (tab.key === 'sources') await Promise.all([loadSources(), loadSourceCatalog()])
  if (tab.key === 'publish') await Promise.all([loadPublishRows(), loadReviewLogs()])
}

function applySourceCatalog() {
  const selected = currentSourceCatalog.value
  if (!selected) return
  sourceForm.value.sourceDomain = selected.sourceDomain
  sourceForm.value.sourceName = selected.sourceName
  sourceForm.value.category = selected.category
  sourceForm.value.usableForContentYn = selected.sourceDomain !== 'COMMUNITY'
  sourceForm.value.sourceRiskLevel = selected.sourceDomain === 'COMMUNITY' || selected.sourceDomain === 'VISA_IMMIGRATION' ? 'MEDIUM' : 'LOW'
}

async function openDetail(row) {
  selectedDetail.value = await fetchGeneratedContentDetail(row.id)
  reviewLogs.value = selectedDetail.value.reviewLogs || []
}

async function runCollector() {
  actionMessage.value = ''
  errorMessage.value = ''
  try {
    const result = await collectContentSources({
      domain: sourceForm.value.sourceDomain,
      sourcePlatform: sourceForm.value.sourcePlatform,
      category: sourceForm.value.category,
      limit: sourceLimit.value,
      dryRun: false,
    })
    actionMessage.value = `Collector completed. created=${result.created || 0}, updated=${result.updated || 0}, blocked=${result.blocked || 0}`
    await Promise.all([loadDashboard(), loadSources()])
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : 'Collector failed.'
  }
}

async function saveManualSource() {
  actionMessage.value = ''
  errorMessage.value = ''
  if (!sourceForm.value.title && !sourceForm.value.sourceUrl) {
    errorMessage.value = 'Manual source requires a title or URL.'
    return
  }
  try {
    const result = await collectContentSources({
      domain: sourceForm.value.sourceDomain,
      sourcePlatform: sourceForm.value.sourcePlatform,
      category: sourceForm.value.category,
      dryRun: false,
      items: [{ ...sourceForm.value, bodyText: sourceForm.value.summaryText }],
    })
    actionMessage.value = `Manual source saved. created=${result.created || 0}, updated=${result.updated || 0}`
    await Promise.all([loadDashboard(), loadSources()])
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : 'Manual source save failed.'
  }
}

async function generateFromSource(row) {
  if (actioningId.value) return
  actioningId.value = row.id
  actionMessage.value = ''
  errorMessage.value = ''
  try {
    const result = await generateContentDrafts({
      sourceItemIds: [row.id],
      contentType: contentTypeFor(row),
      language: 'en',
      sendToTelegram: false,
    })
    actionMessage.value = `Generated ${result.length || 0} content item(s).`
    await Promise.all([loadDashboard(), loadGenerated()])
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : 'Content generation failed.'
  } finally {
    actioningId.value = 0
  }
}

async function sendTelegram(row) {
  if (actioningId.value) return
  actioningId.value = row.id
  actionMessage.value = ''
  errorMessage.value = ''
  try {
    await sendContentToTelegram(row.id, { dryRun: true, comment: 'Admin UI dry-run delivery.' })
    actionMessage.value = 'Telegram dry-run delivery completed.'
    await Promise.all([loadDashboard(), loadGenerated()])
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : 'Telegram delivery failed.'
  } finally {
    actioningId.value = 0
  }
}

async function reviewRow(row, action) {
  if (actioningId.value) return
  actioningId.value = row.id
  actionMessage.value = ''
  errorMessage.value = ''
  try {
    if (action === 'approve') {
      await approveGeneratedContent(row.id, { reviewerId: 'admin', reviewerName: 'Admin', comment: 'Approved in admin UI.' })
      actionMessage.value = 'Approved.'
    } else {
      await rejectGeneratedContent(row.id, { reviewerId: 'admin', reviewerName: 'Admin', comment: 'Rejected in admin UI.' })
      actionMessage.value = 'Rejected.'
    }
    await Promise.all([loadDashboard(), loadGenerated(), loadReviewLogs(row.id)])
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : 'Review action failed.'
  } finally {
    actioningId.value = 0
  }
}

async function handleLogout() {
  await logoutAdmin().catch(() => {})
  resetDeviceId()
  window.location.href = '/auth'
}

onMounted(loadAll)
</script>

<template>
  <div class="min-h-screen bg-background text-on-surface">
    <Header server-status="ok" server-message="" @logout="handleLogout" />
    <Sidebar :nav-items="navItems" @logout="handleLogout" />

    <main class="ml-[240px] min-w-0 space-y-lg p-lg">
      <section class="control-card p-lg">
        <div class="mb-md flex flex-wrap items-center justify-between gap-md">
          <div>
            <p class="text-label-sm font-bold text-primary">WorkConnect Admin</p>
            <h1 class="text-display-sm font-black">Content Approval Workflow</h1>
          </div>
          <button class="btn-secondary inline-flex items-center gap-xs" type="button" :disabled="loading" @click="loadAll">
            <RefreshCw :size="16" />
            Refresh
          </button>
        </div>

        <p v-if="errorMessage" class="mb-md flex items-center gap-xs rounded border border-error bg-error-container px-md py-sm text-body-sm text-error">
          <AlertCircle :size="16" /> {{ errorMessage }}
        </p>
        <p v-if="actionMessage" class="mb-md rounded border border-success bg-success-container px-md py-sm text-body-sm text-success">{{ actionMessage }}</p>

        <div class="grid gap-md md:grid-cols-3 xl:grid-cols-6">
          <article v-for="card in cards" :key="card.label" class="rounded-md border border-outline-variant bg-surface-container-low p-md">
            <p class="text-label-sm font-bold">{{ card.label }}</p>
            <p class="mt-xs text-display-sm font-black" :class="card.tone">{{ card.value }}</p>
          </article>
        </div>
      </section>

      <nav class="flex flex-wrap gap-sm border-b border-outline-variant">
        <button
          v-for="tab in tabs"
          :key="tab.key"
          class="inline-flex items-center gap-xs border-b-2 px-md py-sm text-body-sm font-bold"
          :class="activeTab === tab.key ? 'border-primary text-primary' : 'border-transparent text-on-surface-variant'"
          type="button"
          @click="changeTab(tab)"
        >
          <component :is="tab.icon" :size="16" />
          {{ tab.label }}
        </button>
      </nav>

      <section v-if="statusTabMap[activeTab]" class="control-card overflow-hidden">
        <div class="flex flex-wrap items-center gap-sm border-b border-outline-variant p-md">
          <select v-model="statusFilter" class="rounded border border-outline-variant bg-white px-sm py-xs text-body-sm" @change="loadGenerated">
            <option value="">All Status</option>
            <option value="GENERATED">GENERATED</option>
            <option value="SENT_TO_TELEGRAM">SENT_TO_TELEGRAM</option>
            <option value="APPROVED">APPROVED</option>
            <option value="REJECTED">REJECTED</option>
          </select>
          <input v-model="categoryFilter" class="rounded border border-outline-variant px-sm py-xs text-body-sm" placeholder="Category" @keyup.enter="loadGenerated" />
          <button class="btn-secondary" type="button" @click="loadGenerated">Search</button>
        </div>

        <div class="overflow-x-auto">
          <table class="w-full min-w-[1180px] border-collapse text-left text-body-sm">
            <thead class="bg-surface-container-low text-label-caps">
              <tr>
                <th class="px-md py-sm">
                  <span class="inline-flex items-center gap-xs">Status <StatusHelp scope="content-approval" title="콘텐츠 승인 상태" /></span>
                </th>
                <th class="px-md py-sm">Title</th>
                <th class="px-md py-sm">Category</th>
                <th class="px-md py-sm">Language</th>
                <th class="px-md py-sm">Generated</th>
                <th class="px-md py-sm">Telegram</th>
                <th class="px-md py-sm">Approved</th>
                <th class="px-md py-sm">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in generatedRows" :key="row.id" class="border-t border-outline-variant hover:bg-surface-container-low">
                <td class="px-md py-sm"><StatusBadge :code="row.status" /></td>
                <td class="max-w-[420px] px-md py-sm">
                  <button class="truncate text-left font-bold hover:text-primary" type="button" @click="openDetail(row)">{{ row.title }}</button>
                  <p class="truncate text-label-sm text-on-surface-variant">{{ row.shortSummary || '-' }}</p>
                </td>
                <td class="px-md py-sm">{{ row.category || '-' }}</td>
                <td class="px-md py-sm font-mono">{{ row.language || '-' }}</td>
                <td class="px-md py-sm font-mono text-label-sm">{{ formatDate(row.generatedAt) }}</td>
                <td class="px-md py-sm font-mono">{{ row.telegramMessageId || '-' }}</td>
                <td class="px-md py-sm font-mono text-label-sm">{{ formatDate(row.approvedAt) }}</td>
                <td class="px-md py-sm">
                  <div class="flex flex-wrap gap-xs">
                    <button class="btn-secondary inline-flex items-center gap-xs" type="button" :disabled="row.status !== 'GENERATED' || actioningId === row.id" @click="sendTelegram(row)">
                      <Send :size="14" /> Send
                    </button>
                    <button class="btn-secondary inline-flex items-center gap-xs" type="button" :disabled="row.status !== 'SENT_TO_TELEGRAM' || actioningId === row.id" @click="reviewRow(row, 'approve')">
                      <Check :size="14" /> Approve
                    </button>
                    <button class="btn-secondary inline-flex items-center gap-xs" type="button" :disabled="row.status !== 'SENT_TO_TELEGRAM' || actioningId === row.id" @click="reviewRow(row, 'reject')">
                      <X :size="14" /> Reject
                    </button>
                    <button class="btn-secondary inline-flex items-center gap-xs" type="button" @click="openDetail(row)">
                      <Eye :size="14" /> Detail
                    </button>
                  </div>
                </td>
              </tr>
              <tr v-if="generatedRows.length === 0">
                <td class="px-md py-xl text-center text-on-surface-variant" colspan="8">No content in this queue.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <section v-if="activeTab === 'sources'" class="grid gap-lg xl:grid-cols-[360px_1fr]">
        <form class="control-card space-y-sm p-md" @submit.prevent="saveManualSource">
          <h2 class="text-title font-bold">Source Registry</h2>
          <select v-model="sourceForm.sourcePlatform" class="w-full rounded border border-outline-variant px-sm py-xs text-body-sm" @change="applySourceCatalog">
            <option value="manual">Manual</option>
            <option v-for="item in sourceCatalog" :key="item.sourcePlatform" :value="item.sourcePlatform">
              {{ item.group }} / {{ item.sourceName }} / {{ item.allowedUse }}
            </option>
          </select>
          <select v-model="sourceForm.sourceDomain" class="w-full rounded border border-outline-variant px-sm py-xs text-body-sm">
            <option value="EMPLOYMENT">Employment</option>
            <option value="VISA_IMMIGRATION">Visa</option>
            <option value="LIVING_INFO">Living Info</option>
            <option value="COMMUNITY">Community Signal</option>
            <option value="SOCIAL_NEWS">Social News</option>
            <option value="OCCUPATION_INFO">Occupation</option>
          </select>
          <input v-model.number="sourceLimit" class="w-full rounded border border-outline-variant px-sm py-xs text-body-sm" min="1" max="100" type="number" placeholder="Collector limit" />
          <button class="btn-secondary inline-flex w-full items-center justify-center gap-xs" type="button" :disabled="loading" @click="runCollector">
            <PlayCircle :size="16" /> Run Collector
          </button>
          <div class="border-t border-outline-variant pt-sm">
            <input v-model="sourceForm.sourceName" class="mb-sm w-full rounded border border-outline-variant px-sm py-xs text-body-sm" placeholder="Source name" />
            <input v-model="sourceForm.sourceUrl" class="mb-sm w-full rounded border border-outline-variant px-sm py-xs text-body-sm" placeholder="URL" />
            <input v-model="sourceForm.title" class="mb-sm w-full rounded border border-outline-variant px-sm py-xs text-body-sm" placeholder="Manual title" />
            <textarea v-model="sourceForm.summaryText" class="mb-sm h-28 w-full rounded border border-outline-variant px-sm py-xs text-body-sm" placeholder="Manual summary"></textarea>
            <input v-model="sourceForm.category" class="mb-sm w-full rounded border border-outline-variant px-sm py-xs text-body-sm" placeholder="Category" />
            <button class="btn-secondary inline-flex w-full items-center justify-center gap-xs" type="submit">
              <Database :size="16" /> Save Manual Source
            </button>
          </div>
        </form>

        <article class="control-card overflow-hidden">
          <div class="flex justify-between border-b border-outline-variant p-md">
            <h2 class="text-title font-bold">Collected Sources</h2>
            <button class="btn-secondary" type="button" @click="loadSources">Search</button>
          </div>
          <div class="overflow-x-auto">
            <table class="w-full min-w-[920px] text-left text-body-sm">
              <thead class="bg-surface-container-low text-label-caps">
                <tr>
                  <th class="px-md py-sm">Domain</th>
                  <th class="px-md py-sm">Title</th>
                  <th class="px-md py-sm">Source</th>
                  <th class="px-md py-sm">Risk</th>
                  <th class="px-md py-sm">Usable</th>
                  <th class="px-md py-sm">Collected</th>
                  <th class="px-md py-sm">Action</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="row in sourceRows" :key="row.id" class="border-t border-outline-variant">
                  <td class="px-md py-sm">{{ sourceLabel(row.sourceDomain) }}</td>
                  <td class="max-w-[360px] truncate px-md py-sm font-bold">{{ row.title }}</td>
                  <td class="px-md py-sm">{{ row.sourceName || row.sourcePlatform || '-' }}</td>
                  <td class="px-md py-sm">{{ row.sourceRiskLevel || '-' }}</td>
                  <td class="px-md py-sm">{{ row.usableForContentYn ? 'Y' : 'N' }}</td>
                  <td class="px-md py-sm font-mono text-label-sm">{{ formatDate(row.collectedAt) }}</td>
                  <td class="px-md py-sm">
                    <button class="btn-secondary" type="button" :disabled="!row.usableForContentYn || actioningId === row.id" @click="generateFromSource(row)">Generate</button>
                  </td>
                </tr>
                <tr v-if="sourceRows.length === 0">
                  <td class="px-md py-xl text-center text-on-surface-variant" colspan="7">No collected sources.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </article>
      </section>

      <section v-if="activeTab === 'publish'" class="grid gap-lg xl:grid-cols-[1fr_420px]">
        <article class="control-card overflow-hidden">
          <div class="flex justify-between border-b border-outline-variant p-md">
            <h2 class="text-title font-bold">Publish Log</h2>
            <button class="btn-secondary" type="button" @click="loadPublishRows">Search</button>
          </div>
          <div class="overflow-x-auto">
            <table class="w-full min-w-[780px] text-left text-body-sm">
              <thead class="bg-surface-container-low text-label-caps">
                <tr>
                  <th class="px-md py-sm">Content</th>
                  <th class="px-md py-sm">Channel</th>
                  <th class="px-md py-sm">
                    <span class="inline-flex items-center gap-xs">Status <StatusHelp scope="content-approval" title="게시 로그 상태" /></span>
                  </th>
                  <th class="px-md py-sm">External ID</th>
                  <th class="px-md py-sm">Created</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="row in publishRows" :key="row.id" class="border-t border-outline-variant">
                  <td class="px-md py-sm font-mono">#{{ row.generatedContentId }}</td>
                  <td class="px-md py-sm">{{ row.targetChannel }}</td>
                  <td class="px-md py-sm"><StatusBadge :code="row.publishStatus" /></td>
                  <td class="px-md py-sm">{{ row.externalPostId || '-' }}</td>
                  <td class="px-md py-sm font-mono text-label-sm">{{ formatDate(row.createdAt) }}</td>
                </tr>
                <tr v-if="publishRows.length === 0">
                  <td class="px-md py-xl text-center text-on-surface-variant" colspan="5">No publish log rows.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </article>

        <article class="control-card p-md">
          <h2 class="mb-sm text-title font-bold">Review Log</h2>
          <div v-for="log in reviewLogs" :key="log.id" class="mb-sm rounded-md border border-outline-variant p-sm text-body-sm">
            <div class="flex items-center justify-between gap-sm">
              <b>{{ log.action }}</b>
              <span class="font-mono text-label-sm">{{ formatDate(log.reviewedAt) }}</span>
            </div>
            <p class="mt-xs text-on-surface-variant">{{ log.reviewerName || log.reviewerId || '-' }}</p>
            <p class="mt-xs">{{ log.comment || '-' }}</p>
          </div>
          <p v-if="reviewLogs.length === 0" class="text-body-sm text-on-surface-variant">No review logs.</p>
        </article>
      </section>

      <section v-if="selectedDetail" class="control-card p-lg">
        <div class="mb-md flex flex-wrap items-start justify-between gap-md">
          <div>
            <div class="flex items-center gap-sm">
              <p class="text-label-sm font-bold text-primary">#{{ selectedDetail.id }}</p>
              <StatusBadge :code="selectedDetail.status" />
            </div>
            <h2 class="text-headline font-black">{{ selectedDetail.title }}</h2>
          </div>
          <div class="flex flex-wrap gap-xs">
            <button class="btn-secondary inline-flex items-center gap-xs" type="button" :disabled="selectedDetail.status !== 'GENERATED'" @click="sendTelegram(selectedDetail)">
              <Send :size="14" /> Send
            </button>
            <button class="btn-secondary inline-flex items-center gap-xs" type="button" :disabled="selectedDetail.status !== 'SENT_TO_TELEGRAM'" @click="reviewRow(selectedDetail, 'approve')">
              <Check :size="14" /> Approve
            </button>
            <button class="btn-secondary inline-flex items-center gap-xs" type="button" :disabled="selectedDetail.status !== 'SENT_TO_TELEGRAM'" @click="reviewRow(selectedDetail, 'reject')">
              <X :size="14" /> Reject
            </button>
          </div>
        </div>
        <div class="grid gap-lg xl:grid-cols-2">
          <div class="space-y-md">
            <div>
              <h3 class="mb-xs text-title font-bold">Original Source</h3>
              <p class="whitespace-pre-wrap rounded-md border border-outline-variant bg-surface-container-low p-md text-body-sm leading-6">
                {{ selectedDetail.sourceItem?.bodyText || selectedDetail.sourceItem?.summaryText || '-' }}
              </p>
            </div>
            <div>
              <h3 class="mb-xs text-title font-bold">Generated Content</h3>
              <p class="whitespace-pre-wrap rounded-md border border-outline-variant bg-surface-container-low p-md text-body-sm leading-6">{{ selectedDetail.writtenContent || '-' }}</p>
            </div>
          </div>
          <div>
            <h3 class="mb-xs text-title font-bold">Image</h3>
            <div class="mb-md aspect-video overflow-hidden rounded-md border border-outline-variant bg-surface-container-low">
              <img v-if="selectedDetail.imageUrl" class="h-full w-full object-cover" :src="selectedDetail.imageUrl" alt="content image" />
              <div v-else class="flex h-full items-center justify-center p-md text-center text-body-sm text-on-surface-variant">
                {{ selectedDetail.imagePrompt || 'No image generated.' }}
              </div>
            </div>
            <dl class="space-y-sm text-body-sm">
              <div><dt class="font-bold">Status</dt><dd><StatusBadge :code="selectedDetail.status" /></dd></div>
              <div><dt class="font-bold">Original Link</dt><dd class="break-all">{{ selectedDetail.originalLink || '-' }}</dd></div>
              <div><dt class="font-bold">Why It Matters</dt><dd>{{ selectedDetail.whyItMatters || '-' }}</dd></div>
              <div><dt class="font-bold">Check Next</dt><dd class="whitespace-pre-wrap">{{ selectedDetail.checkNext || '-' }}</dd></div>
              <div><dt class="font-bold">Disclaimer</dt><dd>{{ selectedDetail.sourceDisclaimer || '-' }}</dd></div>
            </dl>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>
