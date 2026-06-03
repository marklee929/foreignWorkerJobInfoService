import { createRouter, createWebHistory } from 'vue-router'
import AuthGate from '../views/AuthGate.vue'
import Dashboard from '../views/Dashboard.vue'
import JobCollectorPage from '../views/JobCollectorPage.vue'
import NewsDetail from '../views/NewsDetail.vue'
import SectionPage from '../views/SectionPage.vue'
import { checkAdminAuth } from '../services/authService'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/auth', name: 'auth', component: AuthGate },
    { path: '/', name: 'dashboard', component: Dashboard, meta: { requiresAuth: true } },
    {
      path: '/content',
      name: 'content',
      component: SectionPage,
      meta: { requiresAuth: true, title: '콘텐츠 관리', description: '콘텐츠 생성 기능을 연결한 뒤 데이터를 표시합니다.', dataView: false },
    },
    {
      path: '/social-news',
      name: 'social-news',
      component: SectionPage,
      meta: { requiresAuth: true, title: '소셜 뉴스', description: '수집된 소셜 뉴스 후보 데이터를 확인합니다.', dataView: true },
    },
    {
      path: '/social-news/:id',
      name: 'social-news-detail',
      component: NewsDetail,
      meta: { requiresAuth: true },
    },
    {
      path: '/job-collector',
      redirect: '/occupation',
    },
    {
      path: '/occupation',
      name: 'occupation',
      component: JobCollectorPage,
      meta: { requiresAuth: true },
    },
    {
      path: '/lifestyle',
      name: 'lifestyle',
      component: SectionPage,
      meta: { requiresAuth: true, title: '생활 정보', description: '생활 지원 관련 저장 데이터를 확인합니다.', dataView: true },
    },
    {
      path: '/immigration',
      name: 'immigration',
      component: SectionPage,
      meta: { requiresAuth: true, title: '출입국', description: '비자, 체류, 출입국 관련 저장 데이터를 확인합니다.', dataView: true },
    },
    {
      path: '/labor',
      name: 'labor',
      component: SectionPage,
      meta: { requiresAuth: true, title: '노동', description: '근로, 임금, 노동 상담 관련 저장 데이터를 확인합니다.', dataView: true },
    },
    {
      path: '/data-quality',
      name: 'data-quality',
      component: SectionPage,
      meta: { requiresAuth: true, title: '데이터 품질', description: '데이터 품질 화면은 별도 정리 예정입니다.', dataView: false },
    },
    {
      path: '/system-settings',
      name: 'system-settings',
      component: SectionPage,
      meta: { requiresAuth: true, title: '시스템 설정', description: '시스템 설정 화면은 별도 정리 예정입니다.', dataView: false },
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
