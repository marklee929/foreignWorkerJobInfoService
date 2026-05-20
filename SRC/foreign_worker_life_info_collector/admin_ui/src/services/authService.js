import { getAdminApiBaseUrl } from './adminApiConfig'

const API_BASE_URL = getAdminApiBaseUrl()
const DEVICE_ID_KEY = 'workconnect.admin.deviceId'

function createDeviceId() {
  if (globalThis.crypto?.randomUUID) {
    return globalThis.crypto.randomUUID()
  }
  const random = new Uint8Array(16)
  globalThis.crypto?.getRandomValues?.(random)
  return Array.from(random, (value) => value.toString(16).padStart(2, '0')).join('')
}

export function getDeviceId() {
  const saved = localStorage.getItem(DEVICE_ID_KEY)
  if (saved) {
    return saved
  }
  const deviceId = createDeviceId()
  localStorage.setItem(DEVICE_ID_KEY, deviceId)
  return deviceId
}

export function resetDeviceId() {
  localStorage.removeItem(DEVICE_ID_KEY)
}

async function requestJson(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    credentials: 'include',
    headers: {
      Accept: 'application/json',
      'Content-Type': 'application/json',
      'X-Device-Id': getDeviceId(),
      ...(options.headers || {}),
    },
    ...options,
  })
  const payload = await response.json().catch(() => ({}))
  if (!response.ok) {
    throw new Error(payload.message || '서버 연결에 실패했습니다.')
  }
  return payload
}

export function checkAdminAuth(options = {}) {
  return requestJson('/api/admin/auth/check', {
    method: 'POST',
    body: JSON.stringify({
      deviceId: getDeviceId(),
      userAgent: navigator.userAgent,
      forceApprovalRequest: Boolean(options.forceApprovalRequest),
    }),
  }).catch((error) => {
    throw new Error(error.message === 'Failed to fetch' ? '서버 연결에 실패했습니다.' : error.message)
  })
}

export function fetchAdminAuthStatus(sessionId) {
  return requestJson(`/api/admin/auth/status/${sessionId}`).catch((error) => {
    throw new Error(error.message === 'Failed to fetch' ? '서버 연결에 실패했습니다.' : error.message)
  })
}

export function logoutAdmin() {
  return requestJson('/api/admin/auth/logout', {
    method: 'POST',
    body: JSON.stringify({
      deviceId: getDeviceId(),
      userAgent: navigator.userAgent,
    }),
  }).catch((error) => {
    throw new Error(error.message === 'Failed to fetch' ? '서버 연결에 실패했습니다.' : error.message)
  })
}
