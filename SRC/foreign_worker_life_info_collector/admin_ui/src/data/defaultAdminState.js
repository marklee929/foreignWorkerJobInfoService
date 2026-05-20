import {
  Activity,
  Bot,
  BriefcaseBusiness,
  Database,
  FileText,
  Globe2,
  Network,
  Settings,
  ShieldCheck,
  TrendingUp,
} from '@lucide/vue'

export const navItems = [
  { label: '소셜 뉴스', icon: Network, path: '/social-news' },
  { label: '생활 정보', icon: FileText, path: '/lifestyle' },
  { label: '출입국', icon: Globe2, path: '/immigration' },
  { label: '노동', icon: BriefcaseBusiness, path: '/labor' },
  { label: '데이터 품질', icon: TrendingUp, path: '/data-quality' },
  { label: '봇 운영', icon: Bot, path: '/bot-operations' },
]

export const runtimeConfig = {
  defaultKeyword: 'foreign worker visa korea',
  defaultLimit: 1,
  dryRun: true,
  apiConnected: false,
  database: 'foreign_worker_job_info',
  schemas: ['admin', 'social_news'],
}

export const emptySummary = {
  candidate_count: 0,
  published_count: 0,
  duplicate_count: 0,
  failed_count: 0,
  module_count: 0,
  enabled_module_count: 0,
  disabled_module_count: 0,
  latest_cycle: null,
  api_connected: false,
  database: 'foreign_worker_job_info',
}

export const categoryMix = [
  { label: '수집기', value: 30, color: 'bg-primary-container' },
  { label: '파이프라인 단계', value: 50, color: 'bg-secondary-container' },
  { label: '게시', value: 10, color: 'bg-tertiary-container' },
  { label: '알림', value: 10, color: 'bg-[#b4c5ff]' },
]

export const utilityActions = [
  { label: '설정', icon: Settings },
  { label: '감사', icon: ShieldCheck },
  { label: '데이터', icon: Database },
  { label: '상태', icon: Activity },
]
