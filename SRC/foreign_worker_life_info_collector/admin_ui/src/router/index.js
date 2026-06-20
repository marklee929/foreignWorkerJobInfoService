import { createRouter, createWebHistory } from 'vue-router'
import AuthGate from '../views/AuthGate.vue'
import ContentApprovalWorkflowPage from '../views/ContentApprovalWorkflowPage.vue'
import ContentManagementPage from '../views/ContentManagementPage.vue'
import Dashboard from '../views/Dashboard.vue'
import EmploymentJobPage from '../views/EmploymentJobPage.vue'
import ImmigrationNoticePage from '../views/ImmigrationNoticePage.vue'
import JobCollectorPage from '../views/JobCollectorPage.vue'
import LifestyleInfoPage from '../views/LifestyleInfoPage.vue'
import NewsDetail from '../views/NewsDetail.vue'
import OperationLogPage from '../views/OperationLogPage.vue'
import SectionPage from '../views/SectionPage.vue'
import { checkAdminAuth } from '../services/authService'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/auth', name: 'auth', component: AuthGate },
    { path: '/', name: 'dashboard', component: Dashboard, meta: { requiresAuth: true } },
    { path: '/content', name: 'content', component: ContentManagementPage, meta: { requiresAuth: true } },
    { path: '/content-approval', name: 'content-approval', component: ContentApprovalWorkflowPage, meta: { requiresAuth: true } },
    {
      path: '/social-news',
      name: 'social-news',
      component: SectionPage,
      meta: { requiresAuth: true, title: '소셜 뉴스', description: '수집된 소셜 뉴스 후보 데이터를 확인합니다.', dataView: true },
    },
    { path: '/social-news/:id', name: 'social-news-detail', component: NewsDetail, meta: { requiresAuth: true } },
    { path: '/job-collector', redirect: '/occupation' },
    { path: '/occupation', name: 'employment-jobs', component: EmploymentJobPage, meta: { requiresAuth: true } },
    {
      path: '/lifestyle',
      name: 'lifestyle',
      component: LifestyleInfoPage,
      meta: { requiresAuth: true, title: '생활 정보', description: '생활 지원 관련 데이터를 확인합니다.', dataView: true },
    },
    { path: '/immigration', name: 'immigration', component: ImmigrationNoticePage, meta: { requiresAuth: true } },
    { path: '/labor', name: 'occupation', component: JobCollectorPage, meta: { requiresAuth: true } },
    {
      path: '/data-quality',
      name: 'data-quality',
      component: SectionPage,
      meta: { requiresAuth: true, title: '데이터 품질', description: '데이터 품질 화면은 별도 정리 예정입니다.', dataView: false },
    },
    { path: '/system-settings', redirect: '/system-settings/code-guide' },
    {
      path: '/system-settings/code-guide',
      name: 'system-settings',
      component: SectionPage,
      meta: { requiresAuth: true, title: '시스템 설정', description: '시스템 설정 화면은 별도 정리 예정입니다.', dataView: false },
    },
    { path: '/system-settings/logs', name: 'operation-logs', component: OperationLogPage, meta: { requiresAuth: true } },
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
