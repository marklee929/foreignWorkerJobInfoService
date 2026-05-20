import { createRouter, createWebHistory } from 'vue-router'
import AuthGate from '../views/AuthGate.vue'
import Dashboard from '../views/Dashboard.vue'
import SectionPage from '../views/SectionPage.vue'
import { checkAdminAuth } from '../services/authService'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/auth', name: 'auth', component: AuthGate },
    { path: '/', name: 'dashboard', component: Dashboard, meta: { requiresAuth: true } },
    {
      path: '/social-news',
      name: 'social-news',
      component: SectionPage,
      meta: { requiresAuth: true, title: '소셜 뉴스', description: '뉴스 수집, 후보 선별, 게시 승인 흐름을 기획할 화면입니다.' },
    },
    {
      path: '/lifestyle',
      name: 'lifestyle',
      component: SectionPage,
      meta: { requiresAuth: true, title: '생활 정보', description: '외국인 근로자 생활 지원 정보와 지역별 데이터를 관리할 화면입니다.' },
    },
    {
      path: '/immigration',
      name: 'immigration',
      component: SectionPage,
      meta: { requiresAuth: true, title: '출입국', description: '비자, 체류, 행정 절차 관련 정보를 관리할 화면입니다.' },
    },
    {
      path: '/labor',
      name: 'labor',
      component: SectionPage,
      meta: { requiresAuth: true, title: '노동', description: '근로 계약, 임금, 상담, 노동 정책 정보를 관리할 화면입니다.' },
    },
    {
      path: '/data-quality',
      name: 'data-quality',
      component: SectionPage,
      meta: { requiresAuth: true, title: '데이터 품질', description: '중복, 최신성, 신뢰도, 품질 점수를 검토할 화면입니다.' },
    },
    {
      path: '/bot-operations',
      name: 'bot-operations',
      component: SectionPage,
      meta: { requiresAuth: true, title: '봇 운영', description: '수집, 검증, 발행, 알림 봇의 실행 상태를 관리할 화면입니다.' },
    },
    { path: '/:pathMatch(.*)*', redirect: '/' },
  ],
})

router.beforeEach(async (to) => {
  if (!to.meta.requiresAuth) {
    return true
  }

  try {
    const result = await checkAdminAuth()
    if (result.status === 'APPROVED') {
      return true
    }
    return { name: 'auth', query: { redirect: to.fullPath, sessionId: result.sessionId } }
  } catch {
    return { name: 'auth', query: { redirect: to.fullPath, error: 'server' } }
  }
})

export default router
