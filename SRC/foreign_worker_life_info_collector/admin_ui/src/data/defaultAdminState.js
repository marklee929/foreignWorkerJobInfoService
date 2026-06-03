import {
  Activity,
  BriefcaseBusiness,
  Database,
  FileText,
  Globe2,
  Network,
  Settings,
  TrendingUp,
} from '@lucide/vue'

export const navItems = [
  { label: '대시보드', icon: Activity, path: '/' },
  { label: '콘텐츠 관리', icon: Database, path: '/content' },
  { label: '소셜 뉴스', icon: Network, path: '/social-news' },
  { label: '직업정보', icon: BriefcaseBusiness, path: '/occupation' },
  { label: '생활 정보', icon: FileText, path: '/lifestyle' },
  { label: '출입국', icon: Globe2, path: '/immigration' },
  { label: '노동', icon: BriefcaseBusiness, path: '/labor' },
  { label: '데이터 품질', icon: TrendingUp, path: '/data-quality' },
  { label: '시스템 설정', icon: Settings, path: '/system-settings' },
]

export const runtimeConfig = {
  dryRun: true,
  apiConnected: false,
  database: 'foreign_worker_job_info',
  schemas: ['admin', 'social_news'],
}

export const emptySummary = {
  candidate_count: 0,
  today_ready_count: 0,
  previous_post_expired_count: 0,
  published_count: 0,
  post_expired_count: 0,
  duplicate_count: 0,
  failed_count: 0,
  module_count: 0,
  enabled_module_count: 0,
  disabled_module_count: 0,
  latest_cycle: null,
  api_connected: false,
  database: 'foreign_worker_job_info',
}
