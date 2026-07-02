import { getDeviceId } from './authService'
import { getAdminApiBaseUrl } from './adminApiConfig'

const API_BASE_URL = getAdminApiBaseUrl()
const DEFAULT_TIMEOUT_MS = 8000

async function requestJson(path, options = {}) {
  const timeoutMs = options.timeoutMs || DEFAULT_TIMEOUT_MS
  const controller = new AbortController()
  const timeout = window.setTimeout(() => controller.abort(), timeoutMs)
  const { timeoutMs: _timeoutMs, ...fetchOptions } = options
  let response
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      credentials: 'include',
      ...fetchOptions,
      signal: controller.signal,
      headers: {
        Accept: 'application/json',
        'X-Device-Id': getDeviceId(),
        ...(options.body ? { 'Content-Type': 'application/json' } : {}),
        ...(options.headers || {}),
      },
    })
  } catch (error) {
    if (error?.name === 'AbortError') {
      throw new Error(`API timeout after ${Math.round(timeoutMs / 1000)}s: ${path}`)
    }
    throw new Error('서버 연결에 실패했습니다.')
  } finally {
    window.clearTimeout(timeout)
  }

  const payload = await response.json().catch(() => ({}))
  if (!response.ok) {
    throw new Error(payload.message || 'API 요청에 실패했습니다.')
  }
  return payload
}

function getJson(path) {
  return requestJson(path)
}

function getJsonWithTimeout(path, timeoutMs) {
  return requestJson(path, { timeoutMs })
}

function withQuery(path, params = {}) {
  const search = new URLSearchParams()
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      search.set(key, String(value))
    }
  })
  const query = search.toString()
  return query ? `${path}?${query}` : path
}

function postJson(path, body = {}, options = {}) {
  return requestJson(path, {
    method: 'POST',
    body: JSON.stringify(body),
    ...options,
  })
}

export async function fetchDashboardSummary() {
  return getJsonWithTimeout('/api/dashboard/summary', 30000)
}

export async function fetchModules() {
  const payload = await getJson('/api/admin/modules')
  return payload.items || []
}

export async function fetchCandidates(params = {}) {
  return getJson(withQuery('/api/social/news/candidates', params))
}

export function fetchLifestyleCandidates(params = {}) {
  return getJson(withQuery('/api/admin/lifestyle/candidates', params))
}

export function fetchLifestyleCandidateDetail(id) {
  return getJson(`/api/admin/lifestyle/candidates/${id}`)
}

export function fetchContentDashboard() {
  return getJson('/api/admin/content/dashboard')
}

export function fetchContentApprovalDashboard() {
  return getJson('/api/admin/content-review/dashboard')
}

export function fetchGeneratedContents(params = {}) {
  return getJson(withQuery('/api/admin/content/generated', params))
}

export function fetchGeneratedContentDetail(id) {
  return getJson(`/api/admin/content/generated/${id}`)
}

export function collectContentSources(payload = {}) {
  return postJson('/api/admin/sources/collect', payload)
}

export function generateContentDrafts(payload = {}) {
  return postJson('/api/admin/content/generate', payload)
}

export function runContentE2eDryRun() {
  return postJson('/api/admin/content/e2e-dry-run')
}

export function sendContentToTelegram(id, payload = {}) {
  return postJson(`/api/admin/content/${id}/send-telegram`, payload)
}

export function approveGeneratedContent(id, payload = {}) {
  return postJson(`/api/admin/content/${id}/approve`, payload)
}

export function rejectGeneratedContent(id, payload = {}) {
  return postJson(`/api/admin/content/${id}/reject`, payload)
}

export function fetchSourceItems(params = {}) {
  return getJson(withQuery('/api/admin/source-items', params))
}

export function fetchSourceCatalog() {
  return getJson('/api/admin/source-catalog')
}

export function fetchReviewLogs(params = {}) {
  return getJson(withQuery('/api/admin/review-logs', params))
}

export function fetchPublishTargets(params = {}) {
  return getJson(withQuery('/api/admin/content/publish-targets', params))
}

export function createCommunitySignal(payload = {}) {
  return postJson('/api/admin/community-signals', payload)
}

export function fetchContentCandidates(params = {}) {
  return getJson(withQuery('/api/admin/content/candidates', params))
}

export function fetchContentCandidateDetail(id) {
  return getJson(`/api/admin/content/candidates/${id}`)
}

export function syncContentCandidates(payload = {}) {
  return postJson('/api/admin/content/sync', payload)
}

export function syncLivingInfoContentCandidates(payload = {}) {
  return postJson('/api/admin/content/living-info/sync', payload)
}

export function runLivingInfoPrepCycle(payload = {}) {
  return postJson('/api/admin/content/living-info/prep-cycle', payload, { timeoutMs: 60000 })
}

export function fetchLivingInfoReadinessDiagnostics(params = {}) {
  return getJson(withQuery('/api/admin/content/living-info/readiness-diagnostics', params))
}

export function generateLivingInfoCardPreviews(payload = {}) {
  return postJson('/api/admin/content/living-info/card-preview-dry-run', payload, { timeoutMs: 60000 })
}

export function publishContentCandidate(id, payload = {}) {
  return postJson(`/api/admin/content/candidates/${id}/publish`, payload)
}

export function generateContentCandidateCardPreview(id, payload = {}) {
  return postJson(`/api/admin/content/candidates/${id}/card-preview-dry-run`, payload, { timeoutMs: 60000 })
}

export function sendContentCandidateToTelegram(id, payload = {}) {
  return postJson(`/api/admin/content/candidates/${id}/send-telegram-review`, payload)
}

export function scoreContentCandidate(id, payload = {}) {
  return postJson(`/api/admin/content/candidates/${id}/score`, payload)
}

export function fetchCandidateDetail(id) {
  return getJson(`/api/social/news/candidates/${id}`)
}

export async function deleteCandidates(ids) {
  return postJson('/api/social/news/candidates/delete', { ids })
}

export async function repostCandidate(id) {
  return postJson('/api/social/news/candidates/repost', { id })
}

export async function cleanupCandidateLinks(payload = {}) {
  return postJson('/api/social/news/candidates/cleanup-links', payload, { timeoutMs: 60000 })
}

export async function fetchLogs(params = {}) {
  const payload = await getJsonWithTimeout(withQuery('/api/logs/recent', params), 5000)
  return payload.items || []
}

export function fetchBotStatus() {
  return getJson('/api/admin/bot/status')
}

export function fetchContentBotStatus() {
  return getJson('/api/admin/content-bot/status')
}

export function startContentBot() {
  return postJson('/api/admin/content-bot/start')
}

export function stopContentBot() {
  return postJson('/api/admin/content-bot/stop')
}

export function runContentBotOnce() {
  return postJson('/api/admin/content-bot/run-once')
}

export function fetchLifestyleBotStatus() {
  return getJson('/api/admin/lifestyle-bot/status')
}

export function startLifestyleBot() {
  return postJson('/api/admin/lifestyle-bot/start')
}

export function stopLifestyleBot() {
  return postJson('/api/admin/lifestyle-bot/stop')
}

export function fetchImmigrationBotStatus() {
  return getJson('/api/admin/immigration-bot/status')
}

export function startImmigrationBot() {
  return postJson('/api/admin/immigration-bot/start')
}

export function stopImmigrationBot() {
  return postJson('/api/admin/immigration-bot/stop')
}

export function fetchFacebookStatus() {
  return getJson('/api/admin/facebook/status')
}

export function startBot() {
  return postJson('/api/admin/bot/start')
}

export function stopBot() {
  return postJson('/api/admin/bot/stop')
}

export function resetBotError() {
  return postJson('/api/admin/bot/reset-error')
}

export function fetchLlamaStatus() {
  return getJson('/api/admin/llama/status')
}

export function reconnectLlama() {
  return postJson('/api/admin/llama/reconnect')
}

export function startLlama() {
  return postJson('/api/admin/llama/start')
}

export function stopLlama() {
  return postJson('/api/admin/llama/stop')
}

export function fetchJobCollectorStatus() {
  return getJson('/api/admin/job-collector/status')
}

export async function fetchJobPostings() {
  const payload = await getJson('/api/admin/job-postings')
  return payload.items || []
}

export function fetchOccupationDashboard() {
  return getJson('/api/admin/occupation/dashboard')
}

export function fetchOccupationJobs(params = {}) {
  return getJson(withQuery('/api/admin/occupation/jobs', params))
}

export function fetchOccupationJobDetail(id) {
  return getJson(`/api/admin/occupation/jobs/${id}`)
}

export function collectOccupationJobs(payload = {}) {
  return postJson('/api/admin/occupation/jobs/collect', payload)
}

export function fetchOccupations(params = {}) {
  return getJson(withQuery('/api/admin/occupation/occupations', params))
}

export function fetchOccupationDetail(id) {
  return getJson(`/api/admin/occupation/occupations/${id}`)
}

export function collectOccupations(payload = {}) {
  return postJson('/api/admin/occupation/occupations/collect', payload)
}

export function fetchKeywordMappings(params = {}) {
  return getJson(withQuery('/api/admin/occupation/keyword-mappings', params))
}

export function createKeywordMapping(payload = {}) {
  return postJson('/api/admin/occupation/keyword-mappings', payload)
}

export function updateKeywordMapping(id, payload = {}) {
  return requestJson(`/api/admin/occupation/keyword-mappings/${id}`, {
    method: 'PUT',
    body: JSON.stringify(payload),
  })
}

export function generateKeywordMappings() {
  return postJson('/api/admin/occupation/keyword-mappings/generate')
}

export async function fetchOccupationCollectLogs(params = {}) {
  const payload = await getJson(withQuery('/api/admin/occupation/collect-logs', params))
  return payload.items || []
}

export function fetchImmigrationDashboard() {
  return getJson('/api/admin/immigration/dashboard')
}

export function fetchImmigrationNotices(params = {}) {
  return getJson(withQuery('/api/admin/immigration/notices', params))
}

export function fetchImmigrationNoticeDetail(id) {
  return getJson(`/api/admin/immigration/notices/${id}`)
}

export function collectImmigrationNotices(payload = {}) {
  return postJson('/api/admin/immigration/collect', payload)
}

export function summarizeImmigrationNotice(id) {
  return postJson(`/api/admin/immigration/notices/${id}/summarize`)
}

export function approveImmigrationNotice(id) {
  return postJson(`/api/admin/immigration/notices/${id}/approve`)
}

export function publishImmigrationNotice(id) {
  return postJson(`/api/admin/immigration/notices/${id}/publish`)
}

export async function fetchJobCollectorLogs(params = {}) {
  const payload = await getJsonWithTimeout(withQuery('/api/admin/job-collector/logs', params), 5000)
  return payload.items || []
}

export function runJobCollector() {
  return postJson('/api/admin/job-collector/run')
}

export function runJobCollectorSmokeTest() {
  return postJson('/api/admin/job-collector/smoke-test')
}

export function startJobCollectorScheduler() {
  return postJson('/api/admin/job-collector/scheduler/start')
}

export function stopJobCollectorScheduler() {
  return postJson('/api/admin/job-collector/scheduler/stop')
}

export function updateJobCollectorSettings(settings) {
  return requestJson('/api/admin/job-collector/settings', {
    method: 'PUT',
    body: JSON.stringify(settings),
  })
}
