/**
 * 구독 및 결제 API 클라이언트
 */

import { apiClient } from '../api-client';
import { axiosInstance } from '../api-client';
import type {
  PlanInfo,
  MySubscriptionData,
  SubscriptionResult,
  PlanChangeResult,
  CancelResult,
  PaymentHistoryData,
} from '@/types/subscription';

const ENDPOINT = '/subscriptions';

/** 플랜 목록 조회 (비인증) */
export async function getPlans(): Promise<PlanInfo[]> {
  const response = await axiosInstance.get<{
    success: boolean;
    data: { plans: PlanInfo[] };
  }>(`${ENDPOINT}/plans`);
  return response.data.data.plans;
}

/** 내 구독 정보 조회 */
export async function getMySubscription(): Promise<MySubscriptionData> {
  const client = apiClient.getInstance();
  const response = await client.get<{
    success: boolean;
    data: MySubscriptionData;
  }>(`${ENDPOINT}/me`);
  return response.data.data;
}

/** 구독 생성 */
export async function createSubscription(
  plan: string,
  billingKey: string
): Promise<SubscriptionResult> {
  const client = apiClient.getInstance();
  const response = await client.post<{
    success: boolean;
    data: SubscriptionResult;
  }>(ENDPOINT, { plan, billing_key: billingKey });
  return response.data.data;
}

/** 플랜 변경 */
export async function changePlan(plan: string): Promise<PlanChangeResult> {
  const client = apiClient.getInstance();
  const response = await client.put<{
    success: boolean;
    data: PlanChangeResult;
  }>(ENDPOINT, { plan });
  return response.data.data;
}

/** 구독 해지 */
export async function cancelSubscription(
  reason?: string,
  feedback?: string
): Promise<CancelResult> {
  const client = apiClient.getInstance();
  const response = await client.delete<{
    success: boolean;
    data: CancelResult;
  }>(ENDPOINT, { data: { reason, feedback } });
  return response.data.data;
}

/** 결제 내역 조회 */
export async function getPaymentHistory(params?: {
  limit?: number;
  cursor?: string;
}): Promise<PaymentHistoryData> {
  const client = apiClient.getInstance();
  const response = await client.get<{
    success: boolean;
    data: PaymentHistoryData;
  }>(`${ENDPOINT}/history`, { params });
  return response.data.data;
}

export const subscriptionApi = {
  getPlans,
  getMySubscription,
  createSubscription,
  changePlan,
  cancelSubscription,
  getPaymentHistory,
};
