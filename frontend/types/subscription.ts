/**
 * 구독 및 결제 관련 타입 정의
 */

// 플랜 기능
export interface PlanFeature {
  chat_limit: number | null;
  contract_limit: number | null;
  payroll: boolean;
  payslip_send_limit: number | null;
  attorney_consult: boolean;
  attorney_consult_limit: number | null;
}

// 플랜 정보
export interface PlanInfo {
  id: string;
  name: string;
  price: number;
  features: PlanFeature;
}

// 구독 정보
export interface Subscription {
  id: string;
  plan: string;
  status: string;
  starts_at: string;
  expires_at: string | null;
  monthly_amount: number;
  has_billing_key: boolean;
  cancelled_at: string | null;
}

// 사용량 정보
export interface UsageInfo {
  month: string;
  chat_count: number;
  contract_count: number;
  payslip_send_count: number;
  chat_limit: number | null;
  contract_limit: number | null;
  payslip_send_limit: number | null;
}

// 내 구독 응답
export interface MySubscriptionData {
  subscription: Subscription | null;
  usage: UsageInfo;
}

// 구독 생성 결과
export interface SubscriptionResult {
  subscription_id: string;
  toss_order_id: string;
  status: string;
  starts_at: string;
  expires_at: string;
}

// 플랜 변경 결과
export interface PlanChangeResult {
  subscription_id: string;
  old_plan: string;
  new_plan: string;
  proration_amount: number;
  proration_description: string;
  next_billing_amount: number;
  effective_at: string;
}

// 구독 해지 결과
export interface CancelResult {
  subscription_id: string;
  status: string;
  cancelled_at: string;
  access_until: string;
  message: string;
}

// 결제 이력 항목
export interface PaymentHistoryItem {
  id: string;
  toss_payment_id: string | null;
  amount: number;
  status: string;
  payment_method: string | null;
  paid_at: string | null;
}

// 페이지네이션
export interface PaginationMeta {
  cursor: string | null;
  has_next: boolean;
  limit: number;
  total_count: number;
}

// 결제 이력 응답
export interface PaymentHistoryData {
  payments: PaymentHistoryItem[];
  pagination: PaginationMeta;
}
