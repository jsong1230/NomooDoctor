/**
 * 컴플라이언스 대시보드 관련 타입 정의
 */

// 리스크 레벨
export type RiskLevel = 'green' | 'yellow' | 'red';

// 이벤트 유형
export type ComplianceEventType =
  | 'contract_expiry'
  | 'payroll_date'
  | 'work_rule_due'
  | 'insurance_report';

// 이벤트 심각도
export type EventSeverity = 'info' | 'warning' | 'critical';

// 리스크 감점 항목
export interface RiskDeduction {
  category: string;
  deduction: number;
  count: number;
  message: string;
  resolution: string;
}

// 리스크 스코어 응답
export interface RiskScoreResponse {
  score: number;
  level: RiskLevel;
  details: RiskDeduction[];
  total_employees: number;
  employees_without_contract: number;
  employees_without_payslip: number;
  work_rule_required: boolean;
  work_rule_exists: boolean;
}

// 컴플라이언스 이벤트
export interface ComplianceEvent {
  id: string;
  event_type: ComplianceEventType;
  title: string;
  description: string;
  event_date: string;
  d_day: number | null;
  severity: EventSeverity;
  related_employee_id: string | null;
  related_employee_name: string | null;
}

// 이벤트 목록 응답
export interface ComplianceEventsResponse {
  events: ComplianceEvent[];
  year: number;
  month: number;
}

// 향후 이벤트 응답
export interface UpcomingEventsResponse {
  events: ComplianceEvent[];
  period_days: number;
}

// 월별 리스크 스코어
export interface MonthlyRiskScore {
  year: number;
  month: number;
  score: number;
  level: RiskLevel;
}

// 리스크 스코어 히스토리 응답
export interface RiskScoreHistoryResponse {
  history: MonthlyRiskScore[];
}

// 리스크 레벨별 색상 및 라벨
export const RISK_LEVEL_CONFIG: Record<
  RiskLevel,
  { label: string; bgClass: string; textClass: string; borderClass: string }
> = {
  green: {
    label: '양호',
    bgClass: 'bg-green-50',
    textClass: 'text-green-700',
    borderClass: 'border-green-200',
  },
  yellow: {
    label: '주의',
    bgClass: 'bg-yellow-50',
    textClass: 'text-yellow-700',
    borderClass: 'border-yellow-200',
  },
  red: {
    label: '위험',
    bgClass: 'bg-red-50',
    textClass: 'text-red-700',
    borderClass: 'border-red-200',
  },
};

// 이벤트 유형별 라벨
export const EVENT_TYPE_LABELS: Record<ComplianceEventType, string> = {
  contract_expiry: '계약 만료',
  payroll_date: '급여 지급일',
  work_rule_due: '취업규칙',
  insurance_report: '보험 신고',
};

// 심각도별 색상
export const SEVERITY_CONFIG: Record<
  EventSeverity,
  { label: string; dotClass: string; bgClass: string; textClass: string }
> = {
  info: {
    label: '정보',
    dotClass: 'bg-blue-400',
    bgClass: 'bg-blue-50',
    textClass: 'text-blue-700',
  },
  warning: {
    label: '주의',
    dotClass: 'bg-yellow-400',
    bgClass: 'bg-yellow-50',
    textClass: 'text-yellow-700',
  },
  critical: {
    label: '긴급',
    dotClass: 'bg-red-400',
    bgClass: 'bg-red-50',
    textClass: 'text-red-700',
  },
};

/**
 * 리스크 레벨 라벨 반환
 */
export function getRiskLevelLabel(level: RiskLevel): string {
  return RISK_LEVEL_CONFIG[level].label;
}

/**
 * D-Day 문자열 반환
 */
export function formatDDay(dDay: number | null): string {
  if (dDay === null) return '';
  if (dDay === 0) return 'D-Day';
  if (dDay > 0) return `D-${dDay}`;
  return `D+${Math.abs(dDay)}`;
}
