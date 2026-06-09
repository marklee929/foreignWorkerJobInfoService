<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { CheckCircle2, LoaderCircle, ShieldCheck, XCircle } from '@lucide/vue'
import logoUrl from '../assets/workconnect_logo.png'
import { checkAdminAuth, fetchAdminAuthStatus } from '../services/authService'

const route = useRoute()
const router = useRouter()
const status = ref('READY')
const message = ref('관리자 접속 승인을 요청해주세요.')
const sessionId = ref(route.query.sessionId || '')
const pollingTimer = ref(null)
const countdownTimer = ref(null)
const remainingSeconds = ref(0)
const approvalTimeoutSeconds = 180

const statusView = computed(() => {
  if (status.value === 'APPROVED') {
    return { icon: CheckCircle2, tone: 'text-success', title: '접속 승인 완료', body: '접속이 승인되었습니다.' }
  }
  if (status.value === 'REJECTED') {
    return { icon: XCircle, tone: 'text-error', title: '접속 거부됨', body: '접속이 거부되었습니다.' }
  }
  if (status.value === 'LOGGED_OUT') {
    return { icon: ShieldCheck, tone: 'text-primary', title: '로그아웃 완료', body: '로그아웃되었습니다.' }
  }
  if (status.value === 'ERROR') {
    return { icon: XCircle, tone: 'text-error', title: '서버 연결 실패', body: '서버 연결에 실패했습니다.' }
  }
  if (status.value === 'PENDING') {
    return { icon: LoaderCircle, tone: 'text-primary', title: 'Telegram 승인 대기 중', body: 'Telegram에서 접속 승인을 완료해주세요.' }
  }
  if (status.value === 'CHECKING') {
    return { icon: LoaderCircle, tone: 'text-primary', title: '승인 확인 중', body: '관리자 접속 확인 중입니다.' }
  }
  return { icon: ShieldCheck, tone: 'text-primary', title: '관리자 접속 승인', body: '관리자 접속 승인을 요청해주세요.' }
})

const isBusy = computed(() => status.value === 'CHECKING' || status.value === 'PENDING')
const formattedRemainingTime = computed(() => {
  const minutes = Math.floor(remainingSeconds.value / 60)
  const seconds = String(remainingSeconds.value % 60).padStart(2, '0')
  return `${minutes}:${seconds}`
})

function stopPolling() {
  if (pollingTimer.value) {
    window.clearInterval(pollingTimer.value)
    pollingTimer.value = null
  }
}

function stopCountdown() {
  if (countdownTimer.value) {
    window.clearInterval(countdownTimer.value)
    countdownTimer.value = null
  }
}

function startCountdown() {
  stopCountdown()
  remainingSeconds.value = approvalTimeoutSeconds
  countdownTimer.value = window.setInterval(() => {
    remainingSeconds.value -= 1
    if (remainingSeconds.value <= 0) {
      stopCountdown()
      stopPolling()
      status.value = 'READY'
      sessionId.value = ''
      message.value = '승인 요청 시간이 만료되었습니다. 다시 승인 요청을 눌러주세요.'
    }
  }, 1000)
}

function redirectAfterApproval() {
  const redirect = typeof route.query.redirect === 'string' ? route.query.redirect : '/'
  window.setTimeout(() => router.replace(redirect), 700)
}

async function pollStatus() {
  if (!sessionId.value) {
    return
  }
  try {
    const result = await fetchAdminAuthStatus(sessionId.value)
    status.value = result.status || 'PENDING'
    message.value = result.message || statusView.value.body
    if (result.status === 'APPROVED') {
      stopPolling()
      stopCountdown()
      redirectAfterApproval()
    }
    if (result.status === 'REJECTED' || result.status === 'LOGGED_OUT') {
      stopPolling()
      stopCountdown()
    }
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : '서버 연결에 실패했습니다.'
    if (errorMessage === '접속 아이디가 허가되지 않습니다.') {
      window.alert(errorMessage)
    }
    status.value = 'ERROR'
    message.value = errorMessage
    stopPolling()
    stopCountdown()
  }
}

async function startAuthCheck() {
  stopPolling()
  stopCountdown()
  status.value = 'CHECKING'
  message.value = '관리자 접속 확인 중입니다.'
  try {
    const result = await checkAdminAuth()
    sessionId.value = result.sessionId
    status.value = result.status || 'PENDING'
    message.value = result.message || statusView.value.body
    if (result.status === 'APPROVED') {
      redirectAfterApproval()
      return
    }
    if (result.status === 'PENDING') {
      startCountdown()
      pollingTimer.value = window.setInterval(pollStatus, 2500)
    }
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : '서버 연결에 실패했습니다.'
    if (errorMessage === '접속 아이디가 허가되지 않습니다.') {
      window.alert(errorMessage)
    }
    status.value = 'ERROR'
    message.value = errorMessage
  }
}

function initializeAuthGate() {
  if (route.query.loggedOut) {
    status.value = 'LOGGED_OUT'
    message.value = '로그아웃되었습니다.'
    return
  }
  if (sessionId.value) {
    status.value = 'PENDING'
    message.value = 'Telegram에서 접속 승인을 완료해주세요.'
    startCountdown()
    pollingTimer.value = window.setInterval(pollStatus, 2500)
    return
  }
  startAuthCheck()
}

onMounted(initializeAuthGate)
onBeforeUnmount(() => {
  stopPolling()
  stopCountdown()
})
</script>

<template>
  <main class="relative min-h-screen overflow-hidden bg-surface px-lg text-on-surface">
    <img
      class="pointer-events-none absolute left-1/2 top-1/2 h-[1382px] w-auto max-w-none -translate-x-1/2 -translate-y-1/2 object-contain opacity-95"
      :src="logoUrl"
      alt="WorkConnect"
    />
    <section class="absolute left-1/2 top-1/2 w-full max-w-[460px] -translate-x-1/2 -translate-y-1/2 rounded-md border border-white/45 bg-white/45 p-xl text-center shadow-lg backdrop-blur-sm">
      <component
        :is="statusView.icon"
        class="mx-auto mb-md"
        :class="[statusView.tone, isBusy ? 'animate-spin' : '']"
        :size="42"
      />
      <p class="mb-xs text-label-caps text-on-surface-variant">WorkConnect 관리자 승인</p>
      <h1 class="mb-sm text-display font-black">{{ statusView.title }}</h1>
      <p class="text-body-md text-on-surface-variant">{{ message || statusView.body }}</p>

      <div v-if="sessionId && status === 'PENDING'" class="mt-lg rounded border border-outline-variant bg-surface-container-low p-md text-left text-body-sm">
        <p class="font-bold text-primary">승인 요청 정보</p>
        <p class="mt-xs text-on-surface-variant">세션 ID: {{ sessionId }}</p>
      </div>

      <button
        v-if="status === 'READY' || status === 'ERROR' || status === 'REJECTED' || status === 'LOGGED_OUT' || status === 'PENDING'"
        class="mt-lg rounded bg-primary-container px-lg py-sm text-body-sm font-bold text-white disabled:cursor-not-allowed disabled:opacity-60"
        type="button"
        :disabled="status === 'PENDING'"
        @click="startAuthCheck"
      >
        {{ status === 'ERROR' || status === 'REJECTED' ? '다시 확인' : '승인 요청' }}
      </button>
      <p v-if="status === 'PENDING'" class="mt-sm text-body-sm font-bold text-primary">
        남은 승인 시간 {{ formattedRemainingTime }}
      </p>
    </section>
  </main>
</template>
