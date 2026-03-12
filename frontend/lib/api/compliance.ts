/**
 * 컴플라이언스 API 클라이언트
 */

import { apiClient } from '../api-client';
import type {
  RiskScoreResponse,
  ComplianceEventsResponse,
  UpcomingEventsResponse,
  RiskScoreHistoryResponse,
} from '@/types/compliance';

const COMPLIANCE_ENDPOINT = '/compliance';

/**
 * 리스크 스코어 조회
 * GET /api/v1/compliance/score
 */
export async function getRiskScore(): Promise<RiskScoreResponse> {
  const response = await apiClient.getInstance().get<{
    success: boolean;
    data: RiskScoreResponse;
  }>(`${COMPLIANCE_ENDPOINT}/score`);
  return response.data.data;
}

/**
 * 리스크 상세 항목 조회
 * GET /api/v1/compliance/details
 */
export async function getRiskDetails(): Promise<{
  score: number;
  level: string;
  details: RiskScoreResponse['details'];
}> {
  const response = await apiClient.getInstance().get<{
    success: boolean;
    data: { score: number; level: string; details: RiskScoreResponse['details'] };
  }>(`${COMPLIANCE_ENDPOINT}/details`);
  return response.data.data;
}

/**
 * 노무 이벤트 목록 조회 (캘린더용)
 * GET /api/v1/compliance/events
 */
export async function getComplianceEvents(params?: {
  year?: number;
  month?: number;
}): Promise<ComplianceEventsResponse> {
  const response = await apiClient.getInstance().get<{
    success: boolean;
    data: ComplianceEventsResponse;
  }>(`${COMPLIANCE_ENDPOINT}/events`, { params });
  return response.data.data;
}

/**
 * 향후 이벤트 조회
 * GET /api/v1/compliance/events/upcoming
 */
export async function getUpcomingEvents(params?: {
  days?: number;
}): Promise<UpcomingEventsResponse> {
  const response = await apiClient.getInstance().get<{
    success: boolean;
    data: UpcomingEventsResponse;
  }>(`${COMPLIANCE_ENDPOINT}/events/upcoming`, { params });
  return response.data.data;
}

/**
 * 월별 리스크 스코어 변화 조회
 * GET /api/v1/compliance/score/history
 */
export async function getRiskScoreHistory(params?: {
  months?: number;
}): Promise<RiskScoreHistoryResponse> {
  const response = await apiClient.getInstance().get<{
    success: boolean;
    data: RiskScoreHistoryResponse;
  }>(`${COMPLIANCE_ENDPOINT}/score/history`, { params });
  return response.data.data;
}

// API 함수들을 객체로 내보내기
export const complianceApi = {
  getRiskScore,
  getRiskDetails,
  getComplianceEvents,
  getUpcomingEvents,
  getRiskScoreHistory,
};
