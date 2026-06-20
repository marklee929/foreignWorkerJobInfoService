<script setup>
import { computed, onMounted, ref } from 'vue'
import { RefreshCw, Search } from '@lucide/vue'
import Header from '../components/Header.vue'
import Sidebar from '../components/Sidebar.vue'
import { navItems } from '../data/defaultAdminState'
import { fetchLogs } from '../services/apiClient'
import { logoutAdmin, resetDeviceId } from '../services/authService'

const pageSize = 50
const logs = ref([])
const loading = ref(false)
const loadingMore = ref(false)
const loadError = ref('')
const offset = ref(0)
const hasMore = ref(true)
const filters = ref({
  search: '',
  level: '',
  status: '',
  module: '',
  date_from: '',
  date_to: '',
})

const visibleCount = computed(() => logs.value.length)

function formatLogTime(value) {
  if (!value) return '-'
  const date = new Date(value)
  if (!Number.isNaN(date.getTime())) {
    const parts = new Intl.DateTimeFormat('sv-SE', {
      timeZone: 'Asia/Seoul',
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: false,
    }).formatToParts(date)
    const byType = Object.fromEntries(parts.map((part) => [part.type, part.value]))
    return `${byType.year}-${byType.month}-${byType.day} ${byType.hour}:${byType.minute}:${byType.second}`
  }
  return String(value).replace('T', ' ').slice(0, 19)
}

function levelClass(level) {
  if (level === 'ERROR') return 'bg-error-container text-error'
  if (level === 'WARN') return 'bg-tertiary-container text-tertiary'
  return 'bg-emerald-100 text-emerald-700'
}

function buildParams(nextOffset = 0) {
  return {
    limit: pageSize,
    offset: nextOffset,
    search: filters.value.search.trim(),
    level: filters.value.level,
    status: filters.value.status.trim(),
    module: filters.value.module.trim(),
    date_from: filters.value.date_from,
    date_to: filters.value.date_to,
  }
}

async function loadLogs(reset = true) {
  if (reset) {
    loading.value = true
    offset.value = 0
  } else {
    loadingMore.value = true
  }
  loadError.value = ''
  try {
    const nextOffset = reset ? 0 : offset.value
    const nextRows = await fetchLogs(buildParams(nextOffset))
    logs.value = reset ? nextRows : [...logs.value, ...nextRows]
    offset.value = nextOffset + nextRows.length
    hasMore.value = nextRows.length === pageSize
  } catch (error) {
    loadError.value = error instanceof Error ? error.message : '운영 로그를 불러오지 못했습니다.'
    if (reset) {
      logs.value = []
      hasMore.value = false
    }
  } finally {
    loading.value = false
    loadingMore.value = false
  }
}

async function handleLogout() {
  await logoutAdmin().catch(() => {})
  resetDeviceId()
  window.location.href = '/auth'
}

onMounted(() => loadLogs(true))
</script>

<template>
  <div class="min-h-screen bg-background text-on-surface">
    <Header server-status="ok" server-message="" @logout="handleLogout" />
    <Sidebar :nav-items="navItems" @logout="handleLogout" />

    <main class="ml-[240px] min-w-0 space-y-lg p-lg">
      <section class="rounded border border-outline-variant bg-surface p-lg">
        <div class="flex flex-wrap items-start justify-between gap-md">
          <div>
            <p class="text-label-sm font-bold text-primary">System Settings</p>
            <h1 class="text-display-sm font-black">운영 로그</h1>
            <p class="mt-xs text-body-sm text-on-surface-variant">
              social_news.pipeline_step_log 기준으로 운영 로그를 조회합니다. content.publish_log는 아직 통합하지 않습니다.
            </p>
          </div>
          <button class="btn-secondary inline-flex items-center gap-xs" type="button" :disabled="loading" @click="loadLogs(true)">
            <RefreshCw :size="16" />
            새로고침
          </button>
        </div>
      </section>

      <section class="rounded border border-outline-variant bg-surface">
        <form class="grid gap-sm border-b border-outline-variant p-md xl:grid-cols-[minmax(240px,1fr)_160px_160px_180px_180px_180px_auto]" @submit.prevent="loadLogs(true)">
          <label class="flex items-center gap-sm rounded border border-outline-variant bg-surface-container-low px-md py-sm">
            <Search :size="18" class="text-on-surface-variant" />
            <input v-model="filters.search" class="min-w-0 flex-1 bg-transparent text-body-sm outline-none" placeholder="message / module / step / payload 검색" />
          </label>
          <select v-model="filters.level" class="rounded border border-outline-variant bg-surface px-md py-sm text-body-sm">
            <option value="">ALL level</option>
            <option value="INFO">INFO</option>
            <option value="WARN">WARN</option>
            <option value="ERROR">ERROR</option>
          </select>
          <input v-model="filters.status" class="rounded border border-outline-variant bg-surface px-md py-sm text-body-sm" placeholder="status" />
          <input v-model="filters.module" class="rounded border border-outline-variant bg-surface px-md py-sm text-body-sm" placeholder="module / step" />
          <input v-model="filters.date_from" class="rounded border border-outline-variant bg-surface px-md py-sm text-body-sm" type="datetime-local" />
          <input v-model="filters.date_to" class="rounded border border-outline-variant bg-surface px-md py-sm text-body-sm" type="datetime-local" />
          <button class="btn-primary" type="submit" :disabled="loading">검색</button>
        </form>

        <p v-if="loadError" class="m-md rounded border border-error bg-error-container px-md py-sm text-body-sm text-error">{{ loadError }}</p>

        <div class="overflow-x-auto">
          <table class="w-full min-w-[1240px] border-collapse text-left text-body-sm">
            <thead class="bg-surface-container">
              <tr>
                <th class="px-md py-sm">시간</th>
                <th class="px-md py-sm">module</th>
                <th class="px-md py-sm">level</th>
                <th class="px-md py-sm">status</th>
                <th class="px-md py-sm">step</th>
                <th class="px-md py-sm">candidate_id</th>
                <th class="px-md py-sm">message</th>
                <th class="px-md py-sm">payload</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="loading">
                <td colspan="8" class="px-md py-xl text-center text-on-surface-variant">운영 로그를 불러오는 중입니다.</td>
              </tr>
              <tr v-for="log in logs" v-else :key="log.id" class="border-t border-outline-variant hover:bg-surface-container-low">
                <td class="whitespace-nowrap px-md py-sm font-mono text-label-sm">{{ formatLogTime(log.time) }}</td>
                <td class="px-md py-sm font-mono text-label-sm">{{ log.module || log.bot || '-' }}</td>
                <td class="px-md py-sm">
                  <span class="rounded px-xs py-xxs text-[10px] font-bold" :class="levelClass(log.level)">{{ log.level || '-' }}</span>
                </td>
                <td class="px-md py-sm font-mono text-label-sm">{{ log.status || '-' }}</td>
                <td class="px-md py-sm font-mono text-label-sm">{{ log.step || log.latency || '-' }}</td>
                <td class="px-md py-sm font-mono text-label-sm">{{ log.candidate_id || '-' }}</td>
                <td class="max-w-[420px] px-md py-sm">{{ log.message || '-' }}</td>
                <td class="px-md py-sm">
                  <details v-if="log.payload_json && log.payload_json !== '{}'">
                    <summary class="cursor-pointer text-primary">payload</summary>
                    <pre class="mt-xs max-h-36 max-w-[360px] overflow-auto rounded bg-surface-container-low p-sm text-[11px]">{{ log.payload_json }}</pre>
                  </details>
                  <span v-else>-</span>
                </td>
              </tr>
              <tr v-if="!loading && !logs.length">
                <td colspan="8" class="px-md py-xl text-center text-on-surface-variant">조건에 맞는 운영 로그가 없습니다.</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="flex flex-wrap items-center justify-between gap-sm border-t border-outline-variant p-md text-body-sm">
          <span>{{ visibleCount }}건 표시 중</span>
          <button class="btn-secondary" type="button" :disabled="loadingMore || loading || !hasMore" @click="loadLogs(false)">
            {{ loadingMore ? '불러오는 중' : hasMore ? '더 보기' : '마지막 로그' }}
          </button>
        </div>
      </section>
    </main>
  </div>
</template>
