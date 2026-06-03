<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { ChevronLeft, ChevronRight, RefreshCw, Search } from '@lucide/vue'
import Header from '../components/Header.vue'
import Sidebar from '../components/Sidebar.vue'
import { navItems } from '../data/defaultAdminState'
import { fetchJobPostings } from '../services/apiClient'
import { logoutAdmin, resetDeviceId } from '../services/authService'

const rows = ref([])
const loading = ref(false)
const loadError = ref('')
const searchText = ref('')
const page = ref(1)
const pageSize = 12

const filteredRows = computed(() => {
  const keyword = searchText.value.trim().toLowerCase()
  if (!keyword) {
    return rows.value
  }
  return rows.value.filter((item) => {
    const haystack = [item.title, item.company, item.region, item.sal, item.sal_tp_nm, item.career, item.close_dt]
      .filter(Boolean)
      .join(' ')
      .toLowerCase()
    return haystack.includes(keyword)
  })
})

const totalPages = computed(() => Math.max(1, Math.ceil(filteredRows.value.length / pageSize)))
const startIndex = computed(() => (page.value - 1) * pageSize)
const pagedRows = computed(() => filteredRows.value.slice(startIndex.value, startIndex.value + pageSize))
const rowRange = computed(() => {
  if (!filteredRows.value.length) {
    return '0-0'
  }
  return `${startIndex.value + 1}-${Math.min(startIndex.value + pageSize, filteredRows.value.length)}`
})

function formatDate(value) {
  if (!value) {
    return '-'
  }
  return String(value).replace('T', ' ').slice(0, 16)
}

async function loadRows() {
  loading.value = true
  loadError.value = ''
  try {
    rows.value = await fetchJobPostings()
    if (page.value > totalPages.value) {
      page.value = totalPages.value
    }
  } catch (error) {
    loadError.value = error instanceof Error ? error.message : '채용정보를 불러오지 못했습니다.'
    rows.value = []
  } finally {
    loading.value = false
  }
}

function previousPage() {
  page.value = Math.max(1, page.value - 1)
}

function nextPage() {
  page.value = Math.min(totalPages.value, page.value + 1)
}

async function handleLogout() {
  try {
    await logoutAdmin()
  } finally {
    resetDeviceId()
    window.location.replace('/auth?loggedOut=1')
  }
}

watch(searchText, () => {
  page.value = 1
})

onMounted(loadRows)
</script>

<template>
  <div class="min-h-screen bg-surface text-on-surface">
    <Sidebar :nav-items="navItems" @logout="handleLogout" />
    <Header @logout="handleLogout" />

    <main class="ml-[240px] space-y-lg p-lg">
      <section class="control-card p-md">
        <div class="mb-md flex items-start justify-between gap-lg">
          <div>
            <p class="mb-xs text-label-caps text-primary">WorkConnect Admin</p>
            <h1 class="text-display font-black">채용정보</h1>
            <p class="mt-xs text-body-sm text-on-surface-variant">고용24/워크넷 Open API로 수집된 채용공고 데이터를 확인합니다.</p>
          </div>
          <button class="inline-flex items-center gap-xs rounded border border-outline-variant px-md py-xs text-body-sm" type="button" :disabled="loading" @click="loadRows">
            <RefreshCw :size="15" />
            새로고침
          </button>
        </div>

        <div class="mb-md flex items-center gap-md rounded border border-outline-variant bg-surface-container-low px-md py-sm">
          <Search class="text-outline" :size="18" />
          <input v-model="searchText" class="min-w-0 flex-1 bg-transparent text-body-sm outline-none" type="search" placeholder="제목, 회사, 지역, 급여, 마감일로 검색" />
          <span class="text-body-sm text-on-surface-variant">총 {{ filteredRows.length }}건</span>
        </div>

        <section v-if="loadError" class="mb-md rounded border border-error bg-error-container/30 p-sm text-body-sm text-error">
          {{ loadError }}
        </section>

        <div class="overflow-hidden rounded border border-outline-variant bg-white">
          <table class="w-full border-collapse text-left text-body-sm">
            <thead class="bg-surface-container-low text-label-caps text-on-surface-variant">
              <tr>
                <th class="px-md py-sm">공고번호</th>
                <th class="px-md py-sm">제목</th>
                <th class="px-md py-sm">회사</th>
                <th class="px-md py-sm">지역</th>
                <th class="px-md py-sm">급여</th>
                <th class="px-md py-sm">경력</th>
                <th class="px-md py-sm">등록일</th>
                <th class="px-md py-sm">마감일</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="pagedRows.length === 0" class="h-20 border-t border-outline-variant">
                <td class="px-md text-center text-on-surface-variant" colspan="8">
                  {{ loading ? '데이터를 불러오는 중입니다.' : '데이터 없음' }}
                </td>
              </tr>
              <tr v-for="item in pagedRows" :key="item.wanted_auth_no" class="h-11 border-t border-outline-variant hover:bg-surface-container-low">
                <td class="px-md font-mono">{{ item.wanted_auth_no }}</td>
                <td class="max-w-[520px] px-md font-bold">
                  <a v-if="item.wanted_info_url" class="block truncate text-primary" :href="item.wanted_info_url" target="_blank" rel="noreferrer">{{ item.title || '제목 없음' }}</a>
                  <span v-else class="block truncate">{{ item.title || '제목 없음' }}</span>
                </td>
                <td class="px-md">{{ item.company || '-' }}</td>
                <td class="px-md text-on-surface-variant">{{ item.region || item.basic_addr || '-' }}</td>
                <td class="px-md text-on-surface-variant">{{ item.sal || item.sal_tp_nm || '-' }}</td>
                <td class="px-md text-on-surface-variant">{{ item.career || '-' }}</td>
                <td class="px-md font-mono text-on-surface-variant">{{ item.reg_dt || '-' }}</td>
                <td class="px-md font-mono text-on-surface-variant">{{ item.close_dt || '-' }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="mt-md flex items-center justify-between text-body-sm">
          <span class="text-on-surface-variant">{{ rowRange }} / {{ filteredRows.length }}건</span>
          <div class="flex items-center gap-sm">
            <button class="rounded border border-outline-variant p-xs disabled:cursor-not-allowed disabled:opacity-40" type="button" :disabled="page <= 1" @click="previousPage">
              <ChevronLeft :size="16" />
            </button>
            <span class="font-mono">{{ page }} / {{ totalPages }}</span>
            <button class="rounded border border-outline-variant p-xs disabled:cursor-not-allowed disabled:opacity-40" type="button" :disabled="page >= totalPages" @click="nextPage">
              <ChevronRight :size="16" />
            </button>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>
