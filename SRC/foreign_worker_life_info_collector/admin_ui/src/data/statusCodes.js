const GROUP_ORDER = [
  'Source',
  'Content',
  'Review',
  'Publish',
  'Runtime',
  'Blocked',
  'System',
]

const DEFAULT_STATUS = {
  code: 'UNKNOWN',
  label: '기타',
  group: 'System',
  description: '공통 코드에 아직 등록되지 않은 상태입니다.',
  dot: 'bg-zinc-400',
  chip: 'border-zinc-200 bg-zinc-50 text-zinc-700',
}

const STATUS_GUIDE_SCOPES = {
  'social-news': [
    'NORMALIZED',
    'SUMMARIZED',
    'SCORED',
    'READY_TO_PUBLISH',
    'READY_TO_REVIEW',
    'FAILED_RETRYABLE',
    'FAILED_PERMISSION',
    'POSTED',
    'POST_EXPIRED',
    'DUPLICATE',
    'DUPLICATE_SKIPPED',
    'TEXT_INVALID',
    'SKIPPED',
    'SKIPPED_LOW_SCORE',
    'ARCHIVED',
  ],
  lifestyle: [
    'NORMALIZED',
    'SUMMARIZED',
    'SCORED',
    'READY_TO_REVIEW',
    'READY_TO_PUBLISH',
    'POSTED',
    'FAILED_RETRYABLE',
    'SKIPPED',
    'SKIPPED_LOW_SCORE',
  ],
  immigration: [
    'RAW_COLLECTED',
    'NORMALIZED',
    'SUMMARIZED',
    'READY_TO_REVIEW',
    'READY_TO_PUBLISH',
    'POSTED',
    'FAILED',
    'ARCHIVED',
  ],
  'content-management': [
    'SCORED',
    'READY_TO_REVIEW',
    'READY_TO_PUBLISH',
    'FAILED_RETRYABLE',
    'POSTED',
    'POST_EXPIRED',
    'ARCHIVED',
  ],
  'content-approval': [
    'COLLECTED',
    'GENERATED',
    'SENT_TO_TELEGRAM',
    'APPROVED',
    'REJECTED',
    'PUBLISHED',
    'FAILED',
  ],
}

export const STATUS_CODES = {
  RAW: {
    label: '원본',
    group: 'Source',
    description: '원천 데이터가 들어왔지만 아직 표준화 전입니다.',
    dot: 'bg-slate-400',
    chip: 'border-slate-300 bg-slate-50 text-slate-700',
  },
  RAW_COLLECTED: {
    label: '원문 수집',
    group: 'Source',
    description: '원문 또는 공식 공지가 수집된 상태입니다.',
    dot: 'bg-slate-400',
    chip: 'border-slate-300 bg-slate-50 text-slate-700',
  },
  COLLECTED: {
    label: '수집',
    group: 'Source',
    description: 'source item이 수집되고 보존된 상태입니다.',
    dot: 'bg-blue-500',
    chip: 'border-blue-200 bg-blue-50 text-blue-700',
  },
  CANDIDATE: {
    label: '후보',
    group: 'Source',
    description: '콘텐츠 또는 게시 후보로 올라온 원천 항목입니다.',
    dot: 'bg-blue-500',
    chip: 'border-blue-200 bg-blue-50 text-blue-700',
  },
  NORMALIZED: {
    label: '정규화',
    group: 'Source',
    description: '원천 데이터의 URL, 제목, 본문, 출처가 표준화된 상태입니다.',
    dot: 'bg-sky-500',
    chip: 'border-sky-200 bg-sky-50 text-sky-700',
  },
  SUMMARIZED: {
    label: '요약 완료',
    group: 'Content',
    description: '요약 또는 설명문 생성이 완료된 상태입니다.',
    dot: 'bg-cyan-500',
    chip: 'border-cyan-200 bg-cyan-50 text-cyan-700',
  },
  SCORED: {
    label: '점수 평가',
    group: 'Content',
    description: '품질, 관련성, 게시 적합도 점수가 계산된 상태입니다.',
    dot: 'bg-purple-500',
    chip: 'border-purple-200 bg-purple-50 text-purple-700',
  },
  GENERATED: {
    label: '생성',
    group: 'Content',
    description: 'Facebook/Telegram 검토용 콘텐츠 초안이 생성된 상태입니다.',
    dot: 'bg-cyan-500',
    chip: 'border-cyan-200 bg-cyan-50 text-cyan-700',
  },
  READY_TO_REVIEW: {
    label: '검토 대기',
    group: 'Review',
    description: '운영자 검토 또는 Telegram 점수 반영이 필요한 상태입니다.',
    dot: 'bg-amber-500',
    chip: 'border-amber-200 bg-amber-50 text-amber-800',
  },
  REVIEW_REQUIRED: {
    label: '검토 필요',
    group: 'Review',
    description: '민감도, 출처, 품질 문제로 수동 검토가 필요한 상태입니다.',
    dot: 'bg-amber-500',
    chip: 'border-amber-200 bg-amber-50 text-amber-800',
  },
  SENT_TO_TELEGRAM: {
    label: 'Telegram 전송',
    group: 'Review',
    description: '검토 메시지가 Telegram으로 전송된 상태입니다.',
    dot: 'bg-violet-500',
    chip: 'border-violet-200 bg-violet-50 text-violet-700',
  },
  APPROVED: {
    label: '승인',
    group: 'Review',
    description: '운영자가 콘텐츠를 승인한 상태입니다.',
    dot: 'bg-emerald-500',
    chip: 'border-emerald-200 bg-emerald-50 text-emerald-700',
  },
  REJECTED: {
    label: '반려',
    group: 'Review',
    description: '운영자가 콘텐츠를 반려한 상태입니다.',
    dot: 'bg-rose-500',
    chip: 'border-rose-200 bg-rose-50 text-rose-700',
  },
  READY_TO_PUBLISH: {
    label: '게시 대기',
    group: 'Publish',
    description: '게시 가능한 점수와 조건을 만족한 상태입니다.',
    dot: 'bg-emerald-500',
    chip: 'border-emerald-200 bg-emerald-50 text-emerald-700',
  },
  POSTED: {
    label: '게시 완료',
    group: 'Publish',
    description: '실제 게시가 완료된 상태입니다.',
    dot: 'bg-indigo-500',
    chip: 'border-indigo-200 bg-indigo-50 text-indigo-700',
  },
  PUBLISHED: {
    label: '게시 완료',
    group: 'Publish',
    description: '외부 채널 게시가 완료된 상태입니다.',
    dot: 'bg-indigo-500',
    chip: 'border-indigo-200 bg-indigo-50 text-indigo-700',
  },
  DRY_RUN_PUBLISHED: {
    label: '테스트 게시',
    group: 'Publish',
    description: '실제 게시 없이 게시 시뮬레이션만 완료한 상태입니다.',
    dot: 'bg-teal-500',
    chip: 'border-teal-200 bg-teal-50 text-teal-700',
  },
  POST_EXPIRED: {
    label: '게시 만료',
    group: 'Publish',
    description: '게시 후보 또는 게시 결과가 유효 기간을 지난 상태입니다.',
    dot: 'bg-orange-500',
    chip: 'border-orange-200 bg-orange-50 text-orange-700',
  },
  NOTIFIED: {
    label: '알림 완료',
    group: 'Publish',
    description: '알림 채널 전송이 완료된 상태입니다.',
    dot: 'bg-indigo-500',
    chip: 'border-indigo-200 bg-indigo-50 text-indigo-700',
  },
  DRY_RUN_NOTIFIED: {
    label: '테스트 알림',
    group: 'Publish',
    description: '실제 알림 없이 알림 시뮬레이션만 완료한 상태입니다.',
    dot: 'bg-teal-500',
    chip: 'border-teal-200 bg-teal-50 text-teal-700',
  },
  FAILED: {
    label: '실패',
    group: 'Blocked',
    description: '처리 또는 게시가 실패한 상태입니다.',
    dot: 'bg-red-500',
    chip: 'border-red-200 bg-red-50 text-red-700',
  },
  ERROR: {
    label: '오류',
    group: 'Blocked',
    description: '봇 또는 시스템 작업에 오류가 발생한 상태입니다.',
    dot: 'bg-red-500',
    chip: 'border-red-200 bg-red-50 text-red-700',
  },
  FAILED_RETRYABLE: {
    label: '재시도',
    group: 'Blocked',
    description: '오류가 있었지만 재시도 가능한 상태입니다.',
    dot: 'bg-orange-500',
    chip: 'border-orange-200 bg-orange-50 text-orange-700',
  },
  FAILED_PERMISSION: {
    label: '권한 확인',
    group: 'Blocked',
    description: '토큰, API 권한, 계정 권한 확인이 필요한 상태입니다.',
    dot: 'bg-red-500',
    chip: 'border-red-200 bg-red-50 text-red-700',
  },
  FAILED_REPOST_REQUIRED: {
    label: '재게시 필요',
    group: 'Blocked',
    description: '기존 게시 실패 후 재게시 판단이 필요한 상태입니다.',
    dot: 'bg-orange-500',
    chip: 'border-orange-200 bg-orange-50 text-orange-700',
  },
  AUTO_RETRY_BLOCKED: {
    label: '재시도 차단',
    group: 'Blocked',
    description: '자동 재시도 조건을 만족하지 못해 대기 중인 상태입니다.',
    dot: 'bg-red-500',
    chip: 'border-red-200 bg-red-50 text-red-700',
  },
  DUPLICATE: {
    label: '중복',
    group: 'Blocked',
    description: '동일 또는 유사 원천으로 중복 제외된 상태입니다.',
    dot: 'bg-orange-500',
    chip: 'border-orange-200 bg-orange-50 text-orange-700',
  },
  DUPLICATE_SKIPPED: {
    label: '중복 제외',
    group: 'Blocked',
    description: '대표 항목이 아니어서 게시/검토에서 제외된 상태입니다.',
    dot: 'bg-orange-500',
    chip: 'border-orange-200 bg-orange-50 text-orange-700',
  },
  TEXT_INVALID: {
    label: '본문 오류',
    group: 'Blocked',
    description: '본문이 너무 짧거나 유효하지 않아 제외된 상태입니다.',
    dot: 'bg-red-500',
    chip: 'border-red-200 bg-red-50 text-red-700',
  },
  SKIPPED: {
    label: '제외',
    group: 'Blocked',
    description: '게시 또는 검토 대상에서 제외된 상태입니다.',
    dot: 'bg-zinc-400',
    chip: 'border-zinc-200 bg-zinc-50 text-zinc-700',
  },
  SKIPPED_LOW_SCORE: {
    label: '점수 미달',
    group: 'Blocked',
    description: '점수가 기준보다 낮아 제외된 상태입니다.',
    dot: 'bg-zinc-400',
    chip: 'border-zinc-200 bg-zinc-50 text-zinc-700',
  },
  SKIPPED_DAILY_RESET: {
    label: '일일 만료',
    group: 'Blocked',
    description: '일일 후보 정리로 제외된 상태입니다.',
    dot: 'bg-zinc-400',
    chip: 'border-zinc-200 bg-zinc-50 text-zinc-700',
  },
  ARCHIVED: {
    label: '보관',
    group: 'Blocked',
    description: '운영 목록에서 제외하고 보관된 상태입니다.',
    dot: 'bg-zinc-400',
    chip: 'border-zinc-200 bg-zinc-50 text-zinc-700',
  },
  RUNNING: {
    label: '실행 중',
    group: 'Runtime',
    description: '봇 또는 스케줄러가 실행 중인 상태입니다.',
    dot: 'bg-emerald-500',
    chip: 'border-emerald-200 bg-emerald-50 text-emerald-700',
  },
  STARTING: {
    label: '시작 중',
    group: 'Runtime',
    description: '봇 또는 스케줄러가 시작 중인 상태입니다.',
    dot: 'bg-cyan-500',
    chip: 'border-cyan-200 bg-cyan-50 text-cyan-700',
  },
  STOPPING: {
    label: '중지 중',
    group: 'Runtime',
    description: '봇 또는 스케줄러가 중지 중인 상태입니다.',
    dot: 'bg-amber-500',
    chip: 'border-amber-200 bg-amber-50 text-amber-800',
  },
  STOPPED: {
    label: '중지',
    group: 'Runtime',
    description: '봇 또는 스케줄러가 꺼진 상태입니다.',
    dot: 'bg-slate-400',
    chip: 'border-slate-300 bg-slate-50 text-slate-700',
  },
  READY: {
    label: '준비',
    group: 'Runtime',
    description: '실행 가능한 준비 상태입니다.',
    dot: 'bg-emerald-500',
    chip: 'border-emerald-200 bg-emerald-50 text-emerald-700',
  },
  PLANNED: {
    label: '추가 예정',
    group: 'Runtime',
    description: '화면 자리만 있고 아직 실제 기능은 없는 상태입니다.',
    dot: 'bg-zinc-400',
    chip: 'border-zinc-200 bg-zinc-50 text-zinc-700',
  },
  DISABLED: {
    label: '비활성',
    group: 'Runtime',
    description: '설정 또는 운영 판단으로 비활성화된 상태입니다.',
    dot: 'bg-slate-400',
    chip: 'border-slate-300 bg-slate-50 text-slate-700',
  },
  CONNECTED: {
    label: '연결됨',
    group: 'Runtime',
    description: '외부/로컬 서비스 연결이 정상인 상태입니다.',
    dot: 'bg-emerald-500',
    chip: 'border-emerald-200 bg-emerald-50 text-emerald-700',
  },
  DISCONNECTED: {
    label: '연결 안 됨',
    group: 'Runtime',
    description: '외부/로컬 서비스 연결이 끊긴 상태입니다.',
    dot: 'bg-red-500',
    chip: 'border-red-200 bg-red-50 text-red-700',
  },
  SUCCESS: {
    label: '성공',
    group: 'System',
    description: '작업이 정상 완료된 상태입니다.',
    dot: 'bg-emerald-500',
    chip: 'border-emerald-200 bg-emerald-50 text-emerald-700',
  },
  COMPLETED: {
    label: '완료',
    group: 'System',
    description: '작업이 완료된 상태입니다.',
    dot: 'bg-emerald-500',
    chip: 'border-emerald-200 bg-emerald-50 text-emerald-700',
  },
  WAITING: {
    label: '대기',
    group: 'System',
    description: '쿨다운 또는 다음 실행을 기다리는 상태입니다.',
    dot: 'bg-amber-500',
    chip: 'border-amber-200 bg-amber-50 text-amber-800',
  },
  DRY_RUN: {
    label: 'Dry-run',
    group: 'System',
    description: '실제 외부 전송 없이 검증만 수행한 상태입니다.',
    dot: 'bg-teal-500',
    chip: 'border-teal-200 bg-teal-50 text-teal-700',
  },
  SENT: {
    label: '전송',
    group: 'System',
    description: '외부 채널로 전송된 상태입니다.',
    dot: 'bg-violet-500',
    chip: 'border-violet-200 bg-violet-50 text-violet-700',
  },
  BLOCKED: {
    label: '차단',
    group: 'Blocked',
    description: '안전 규칙 또는 운영 설정으로 차단된 상태입니다.',
    dot: 'bg-red-500',
    chip: 'border-red-200 bg-red-50 text-red-700',
  },
}

export function normalizeStatusCode(value) {
  const code = String(value || 'UNKNOWN').trim().toUpperCase()
  return code || 'UNKNOWN'
}

export function statusMeta(value) {
  const code = normalizeStatusCode(value)
  const found = STATUS_CODES[code]
  if (found) {
    return { code, ...found }
  }
  return { ...DEFAULT_STATUS, code, label: value || DEFAULT_STATUS.label }
}

export function statusLabel(value) {
  return statusMeta(value).label
}

export function statusCodeGuide() {
  const groups = new Map()
  Object.keys(STATUS_CODES).forEach((code) => {
    const meta = statusMeta(code)
    if (!groups.has(meta.group)) {
      groups.set(meta.group, [])
    }
    groups.get(meta.group).push(meta)
  })
  return [...groups.entries()]
    .sort(([left], [right]) => GROUP_ORDER.indexOf(left) - GROUP_ORDER.indexOf(right))
    .map(([group, items]) => ({
      group,
      items: items.sort((left, right) => left.code.localeCompare(right.code)),
    }))
}

export function statusGuideFor(scope, fallbackCodes = []) {
  const codes = STATUS_GUIDE_SCOPES[scope] || fallbackCodes
  return [...new Set(codes)].map((code) => statusMeta(code))
}
