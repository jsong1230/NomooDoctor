/**
 * 퇴직금/해고 계산기 관련 타입 정의
 */

// 월별 급여 입력
export interface MonthlyWageInput {
  year: number;
  month: number;
  total_wage: number;
  days_in_month: number;
}

// 퇴직금 계산 요청
export interface SeveranceCalculateRequest {
  employee_id: string;
  resign_date: string; // YYYY-MM-DD
  annual_bonus?: number;
  unused_annual_leave_days?: number;
  monthly_wages?: MonthlyWageInput[];
}

// 계산 상세 내역
export interface CalculationDetail {
  last_3_months_total_wage: number;
  last_3_months_total_days: number;
  bonus_3_months_share: number;
  average_daily_wage: number;
  severance_formula: string;
  unused_leave_formula: string;
}

// 퇴직금 계산 결과
export interface SeveranceResult {
  employee_id: string;
  employee_name: string;
  hire_date: string; // YYYY-MM-DD
  resign_date: string; // YYYY-MM-DD
  total_service_days: number;
  average_daily_wage: number;
  severance_pay: number;
  unused_leave_pay: number;
  bonus_included: number;
  total_payment: number;
  payment_deadline: string; // YYYY-MM-DD
  eligible: boolean;
  calculation_detail: CalculationDetail;
}

// 저장된 퇴직금 기록
export interface SeveranceRecord extends SeveranceResult {
  id: string;
  status: 'calculated' | 'paid' | 'overdue';
  created_at: string; // ISO datetime
}

// 퇴직금 목록 요약
export interface SeveranceSummary {
  id: string;
  employee_id: string;
  employee_name: string;
  resign_date: string;
  total_payment: number;
  status: 'calculated' | 'paid' | 'overdue';
  payment_deadline: string;
  created_at: string;
}

// 위험 요소
export interface RiskFactors {
  is_pregnant?: boolean;
  is_on_parental_leave?: boolean;
  is_union_member?: boolean;
  is_workplace_injury?: boolean;
  is_whistleblower?: boolean;
}

// 해고 절차 요청
export interface TerminationGuideRequest {
  employee_id: string;
  termination_type: 'resignation' | 'mutual_agreement' | 'dismissal' | 'contract_expiry' | 'retirement';
  reason: string;
  risk_factors?: RiskFactors;
}

// 체크리스트 항목
export interface ChecklistItem {
  step: number;
  title: string;
  description: string;
  required: boolean;
  completed?: boolean;
}

// 해고 예고 정보
export interface AdvanceNotice {
  required: boolean;
  notice_days: number;
  notice_pay_amount: number;
  description: string;
}

// 위험 경고
export interface RiskWarning {
  type: string;
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'EMERGENCY';
  message: string;
  recommendation: string;
}

// 서류 정보
export interface DocumentInfo {
  type: string;
  name: string;
  available: boolean;
}

// 실업급여 가이드
export interface UnemploymentGuide {
  eligible: boolean;
  conditions: string;
  required_documents: string[];
}

// 법률 참조
export interface LawReference {
  law_name: string;
  article: string;
  content: string;
}

// 해고 절차 가이드
export interface TerminationGuide {
  termination_type: 'resignation' | 'mutual_agreement' | 'dismissal' | 'contract_expiry' | 'retirement';
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH' | 'EMERGENCY';
  checklist: ChecklistItem[];
  advance_notice: AdvanceNotice;
  risk_warnings: RiskWarning[];
  documents: DocumentInfo[];
  unemployment_benefit_guide: UnemploymentGuide;
  ai_guide: string;
  law_references: LawReference[];
  disclaimer: string;
}

// 서류 생성 요청
export interface DocumentGenerateRequest {
  employee_id: string;
  document_type: 'dismissal_notice' | 'resignation_agreement';
  termination_date: string; // YYYY-MM-DD
  reason: string;
  format?: 'pdf' | 'docx';
}

// 서류 생성 결과
export interface DocumentGenerateResult {
  download_url: string;
  expires_at: string; // ISO datetime
  filename: string;
  document_type: string;
}

// 해고 유형 옵션
export const TERMINATION_TYPE_OPTIONS = [
  { value: 'resignation', label: '자발적 퇴사' },
  { value: 'mutual_agreement', label: '권고사직' },
  { value: 'dismissal', label: '해고' },
  { value: 'contract_expiry', label: '계약만료' },
  { value: 'retirement', label: '정년퇴직' },
];

// 해고 유형 라벨 변환
export function getTerminationType(type: string): string {
  const option = TERMINATION_TYPE_OPTIONS.find(opt => opt.value === type);
  return option?.label || type;
}

// 위험도 레벨 색상 맵
export const RISK_LEVEL_COLOR_MAP: Record<string, string> = {
  LOW: 'bg-green-100 text-green-800 border-green-300',
  MEDIUM: 'bg-yellow-100 text-yellow-800 border-yellow-300',
  HIGH: 'bg-orange-100 text-orange-800 border-orange-300',
  EMERGENCY: 'bg-red-100 text-red-800 border-red-300',
};

// 위험도 레벨 아이콘
export const RISK_LEVEL_ICON_MAP: Record<string, string> = {
  LOW: 'circle',
  MEDIUM: 'alert-circle',
  HIGH: 'alert-triangle',
  EMERGENCY: 'alert-circle',
};

// 위험 경고 심각도 색상 맵
export const WARNING_SEVERITY_COLOR_MAP: Record<string, string> = {
  LOW: 'bg-green-50 border-green-200 text-green-800',
  MEDIUM: 'bg-yellow-50 border-yellow-200 text-yellow-800',
  HIGH: 'bg-orange-50 border-orange-200 text-orange-800',
  EMERGENCY: 'bg-red-50 border-red-200 text-red-800',
};
