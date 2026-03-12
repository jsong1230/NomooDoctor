/**
 * 퇴직금/해고 계산기 API 클라이언트
 * design.md의 API 스펙을 참조하여 구현
 */

import { apiClient } from '../api-client';
import type {
  SeveranceCalculateRequest,
  SeveranceResult,
  SeveranceRecord,
  SeveranceSummary,
  TerminationGuideRequest,
  TerminationGuide,
  DocumentGenerateRequest,
  DocumentGenerateResult,
} from '@/types/retirement';

const RETIREMENT_ENDPOINT = '/retirement';

/**
 * 퇴직금 시뮬레이션 (미리보기, DB 저장 안 함)
 * POST /api/v1/retirement/calculate
 */
export async function calculateSeverance(data: SeveranceCalculateRequest): Promise<SeveranceResult> {
  const response = await apiClient.getInstance().post<{ success: boolean; data: SeveranceResult }>(
    `${RETIREMENT_ENDPOINT}/calculate`,
    data
  );
  return response.data.data;
}

/**
 * 퇴직금 확정 저장
 * POST /api/v1/retirement/severance
 */
export async function createSeverance(data: SeveranceCalculateRequest): Promise<SeveranceRecord> {
  const response = await apiClient.getInstance().post<{ success: boolean; data: SeveranceRecord }>(
    `${RETIREMENT_ENDPOINT}/severance`,
    data
  );
  return response.data.data;
}

/**
 * 저장된 퇴직금 상세 조회
 * GET /api/v1/retirement/severance/{id}
 */
export async function getSeverance(id: string): Promise<SeveranceRecord> {
  const response = await apiClient.getInstance().get<{ success: boolean; data: SeveranceRecord }>(
    `${RETIREMENT_ENDPOINT}/severance/${id}`
  );
  return response.data.data;
}

/**
 * 사업장 퇴직금 기록 목록 조회
 * GET /api/v1/retirement/severance
 */
export async function listSeverances(params?: {
  employee_id?: string;
  status?: 'calculated' | 'paid' | 'overdue';
  limit?: number;
  offset?: number;
}): Promise<{ data: SeveranceSummary[]; pagination?: { limit: number; offset: number; total?: number } }> {
  const response = await apiClient.getInstance().get<{
    success: boolean;
    data: SeveranceSummary[];
    pagination?: { limit: number; offset: number; total?: number };
  }>(`${RETIREMENT_ENDPOINT}/severance`, { params });
  return {
    data: response.data.data,
    pagination: response.data.pagination,
  };
}

/**
 * 해고/퇴직 절차 가이드 생성 (Claude API 활용)
 * POST /api/v1/retirement/termination-guide
 */
export async function generateTerminationGuide(data: TerminationGuideRequest): Promise<TerminationGuide> {
  const response = await apiClient.getInstance().post<{ success: boolean; data: TerminationGuide }>(
    `${RETIREMENT_ENDPOINT}/termination-guide`,
    data
  );
  return response.data.data;
}

/**
 * 해고 관련 서류 생성 (PDF/DOCX)
 * POST /api/v1/retirement/documents/generate
 */
export async function generateDocument(data: DocumentGenerateRequest): Promise<DocumentGenerateResult> {
  const response = await apiClient.getInstance().post<{ success: boolean; data: DocumentGenerateResult }>(
    `${RETIREMENT_ENDPOINT}/documents/generate`,
    data
  );
  return response.data.data;
}

// API 함수들을 객체로 내보내기
export const retirementApi = {
  calculateSeverance,
  createSeverance,
  getSeverance,
  listSeverances,
  generateTerminationGuide,
  generateDocument,
};
