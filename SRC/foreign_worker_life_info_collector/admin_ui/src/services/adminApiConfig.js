export function getAdminApiBaseUrl() {
  if (import.meta.env.VITE_ADMIN_API_URL) {
    return import.meta.env.VITE_ADMIN_API_URL
  }

  const currentHost = window.location.hostname || '127.0.0.1'
  const hostname = currentHost === 'localhost' ? '127.0.0.1' : currentHost
  return `http://${hostname}:8765`
}
