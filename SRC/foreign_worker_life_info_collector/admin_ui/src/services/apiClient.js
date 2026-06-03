import { getDeviceId } from './authService'
import { getAdminApiBaseUrl } from './adminApiConfig'

const API_BASE_URL = getAdminApiBaseUrl()

async function requestJson(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    credentials: 'include',
    ...options,
    headers: {
      Accept: 'application/json',
      'X-Device-Id': getDeviceId(),
      ...(options.body ? { 'Content-Type': 'application/json' } : {}),
      ...(options.headers || {}),
    },
  }).catch(() => {
    throw new Error('서버 연결에 실패했습니다.')
  })

  const payload = await response.json().catch(() => ({}))
  if (!response.ok) {
    throw new Error(payload.message || 'API 요청에 실패했습니다.')
  }
  return payload
}

function getJson(path) {
  return requestJson(path)
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

function postJson(path, body = {}) {
  return requestJson(path, {
    method: 'POST',
    body: JSON.stringify(body),
  })
}

export async function fetchDashboardSummary() {
  return getJson('/api/dashboard/summary')
}

export async function fetchModules() {
  const payload = await getJson('/api/admin/modules')
  return payload.items || []
}

export async function fetchCandidates(params = {}) {
  return getJson(withQuery('/api/social/news/candidates', params))
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
  return postJson('/api/social/news/candidates/cleanup-links', payload)
}

export async function fetchLogs(params = {}) {
  const payload = await getJson(withQuery('/api/logs/recent', params))
  return payload.items || []
}

export function fetchBotStatus() {
  return getJson('/api/admin/bot/status')
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

export async function fetchJobCollectorLogs(params = {}) {
  const payload = await getJson(withQuery('/api/admin/job-collector/logs', params))
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
