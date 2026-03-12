/**
 * 급여명세서 관련 타입 정의
 */

// 발송 방법 타입
export type SendMethod = 'email' | 'kakao' | 'both';

// 발송 상태 타입
export type SendStatus = 'pending' | 'sent' | 'failed';

// 급여명세서 엔티티
export interface Payslip {
  id: string;
  employee_id: string;
  employee_name: string;
  company_name: string;
  year: number;
  month: number;
  payment_date: string | null;

  // 지급 항목
  base_salary: number;
  weekly_allowance: number;
  overtime_pay: number;
  night_pay: number;
  holiday_pay: number;
  meal_allowance: number;
  transport_allowance: number;
  total_payment: number;

  // 공제 항목
  national_pension: number;
  health_insurance: number;
  long_term_care: number;
  employment_insurance: number;
  income_tax: number;
  local_income_tax: number;
  total_deduction: number;

  // 실수령액
  net_salary: number;

  // 발송 정보
  send_status: SendStatus;
  sent_at: string | null;
  sent_via: string | null;
  created_at: string;
}

// 급여명세서 생성 요청
export interface CreatePayslipRequest {
  employee_id: string;
  year: number;
  month: number;
  payment_date: string;
  base_salary: number;
  weekly_allowance?: number;
  overtime_pay?: number;
  night_pay?: number;
  holiday_pay?: number;
  meal_allowance?: number;
  transport_allowance?: number;
  national_pension?: number;
  health_insurance?: number;
  long_term_care?: number;
  employment_insurance?: number;
  income_tax?: number;
  local_income_tax?: number;
}

// 급여명세서 발송 요청
export interface SendPayslipRequest {
  method: SendMethod;
  email?: string;
}

/**
 * 금액을 한국 원화 형식으로 포맷
 * @param amount 포맷할 금액 (숫자)
 * @returns 콤마 구분 + '원' 단위 문자열 (예: 3,000,000원)
 */
export function formatCurrency(amount: number): string {
  return new Intl.NumberFormat('ko-KR').format(amount) + '원';
}

/**
 * 발송 상태 한국어 라벨 반환
 * @param status 발송 상태
 * @returns 한국어 라벨 문자열
 */
export function getSendStatusLabel(status: SendStatus): string {
  const labels: Record<SendStatus, string> = {
    pending: '미발송',
    sent: '발송완료',
    failed: '발송실패',
  };
  return labels[status];
}

/**
 * 발송 상태에 따른 Tailwind CSS 텍스트 색상 클래스 반환
 * @param status 발송 상태
 * @returns Tailwind CSS 클래스 문자열
 */
export function getSendStatusColor(status: SendStatus): string {
  const colors: Record<SendStatus, string> = {
    pending: 'text-slate-500',
    sent: 'text-green-600',
    failed: 'text-red-600',
  };
  return colors[status];
}
