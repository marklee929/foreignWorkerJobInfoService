import { getDeviceId } from './authService'
import { getAdminApiBaseUrl } from './adminApiConfig'

const API_BASE_URL = getAdminApiBaseUrl()

async function getJson(path) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    credentials: 'include',
    headers: {
      Accept: 'application/json',
      'X-Device-Id': getDeviceId(),
    },
  }).catch(() => {
    throw new Error('서버 연결에 실패했습니다.')
  })

  if (!response.ok) {
    let message = 'API 요청에 실패했습니다.'
    try {
      const payload = await response.json()
      message = payload.message || message
    } catch {
      message = '서버 연결에 실패했습니다.'
    }
    throw new Error(message)
  }

  return response.json()
}

export async function fetchDashboardSummary() {
  return getJson('/api/dashboard/summary')
}

export async function fetchModules() {
  const payload = await getJson('/api/admin/modules')
  return payload.items || []
}

export async function fetchCandidates() {
  const payload = await getJson('/api/social/news/candidates')
  return payload.items || []
}

export async function fetchLogs() {
  const payload = await getJson('/api/logs/recent')
  return payload.items || []
}
