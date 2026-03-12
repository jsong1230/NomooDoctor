/**
 * 노무사 마켓플레이스 API 클라이언트
 */

import { apiClient } from '../api-client';
import { axiosInstance } from '../api-client';
import type {
  AttorneyListData,
  AttorneyDetail,
  CreateCaseRequest,
  CreateCaseResult,
  CaseListData,
  AttorneyCase,
  CreateReviewRequest,
  ReviewListData,
} from '@/types/attorney';

/** 노무사 목록 조회 (비인증) */
export async function listAttorneys(params?: {
  specialty?: string;
  region?: string;
  sort?: string;
  limit?: number;
  offset?: number;
}): Promise<AttorneyListData> {
  const response = await axiosInstance.get<{
    success: boolean;
    data: AttorneyListData;
  }>('/attorneys', { params });
  return response.data.data;
}

/** 노무사 상세 조회 (비인증) */
export async function getAttorney(id: string): Promise<AttorneyDetail> {
  const response = await axiosInstance.get<{
    success: boolean;
    data: AttorneyDetail;
  }>(`/attorneys/${id}`);
  return response.data.data;
}

/** 상담 신청 */
export async function createCase(data: CreateCaseRequest): Promise<CreateCaseResult> {
  const client = apiClient.getInstance();
  const response = await client.post<{
    success: boolean;
    data: CreateCaseResult;
  }>('/attorney-cases', data);
  return response.data.data;
}

/** 내 케이스 목록 */
export async function listMyCases(params?: {
  status?: string;
  limit?: number;
  offset?: number;
}): Promise<CaseListData> {
  const client = apiClient.getInstance();
  const response = await client.get<{
    success: boolean;
    data: CaseListData;
  }>('/attorney-cases', { params });
  return response.data.data;
}

/** 케이스 상세 */
export async function getCase(id: string): Promise<AttorneyCase> {
  const client = apiClient.getInstance();
  const response = await client.get<{
    success: boolean;
    data: AttorneyCase;
  }>(`/attorney-cases/${id}`);
  return response.data.data;
}

/** 케이스 취소 */
export async function cancelCase(id: string): Promise<{ status: string }> {
  const client = apiClient.getInstance();
  const response = await client.put<{
    success: boolean;
    data: { status: string };
  }>(`/attorney-cases/${id}/cancel`);
  return response.data.data;
}

/** 리뷰 작성 */
export async function createReview(
  caseId: string,
  data: CreateReviewRequest
): Promise<{ review_id: string }> {
  const client = apiClient.getInstance();
  const response = await client.post<{
    success: boolean;
    data: { review_id: string };
  }>(`/attorney-cases/${caseId}/review`, data);
  return response.data.data;
}

/** 노무사 리뷰 목록 (비인증) */
export async function listReviews(
  attorneyId: string,
  params?: { limit?: number; offset?: number }
): Promise<ReviewListData> {
  const response = await axiosInstance.get<{
    success: boolean;
    data: ReviewListData;
  }>(`/attorneys/${attorneyId}/reviews`, { params });
  return response.data.data;
}

export const attorneyApi = {
  listAttorneys,
  getAttorney,
  createCase,
  listMyCases,
  getCase,
  cancelCase,
  createReview,
  listReviews,
};
