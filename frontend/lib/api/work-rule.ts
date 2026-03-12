/**
 * 취업규칙 API 클라이언트
 * design.md의 API 스펙을 참조하여 구현
 */

import { apiClient } from '../api-client';
import type {
  WorkRule,
  WorkRuleListItem,
  WorkRuleCreate,
  WorkRuleUpdate,
  WorkRuleGenerateRequest,
  WorkRuleReviseRequest,
  DownloadResponse,
  ConsentChecklistResponse,
  TemplateResponse,
} from '@/types/work-rule';

const WORK_RULE_ENDPOINT = '/work-rules';

/**
 * 업종별 템플릿 조회
 * GET /api/v1/work-rules/templates
 */
export async function getTemplates(industryType?: string): Promise<TemplateResponse[]> {
  const response = await apiClient.getInstance().get<{
    success: boolean;
    data: TemplateResponse[];
  }>(`${WORK_RULE_ENDPOINT}/templates`, {
    params: industryType ? { industry_type: industryType } : {},
  });
  return response.data.data;
}

/**
 * 취업규칙 생성
 * POST /api/v1/work-rules
 */
export async function createWorkRule(data: WorkRuleCreate): Promise<WorkRule> {
  const response = await apiClient.getInstance().post<{
    success: boolean;
    data: WorkRule;
    meta?: { message: string };
  }>(WORK_RULE_ENDPOINT, data);
  return response.data.data;
}

/**
 * 취업규칙 목록 조회
 * GET /api/v1/work-rules
 */
export async function getWorkRules(params?: {
  status?: string;
  page?: number;
  per_page?: number;
}): Promise<WorkRuleListItem[]> {
  const response = await apiClient.getInstance().get<{
    success: boolean;
    data: WorkRuleListItem[];
  }>(WORK_RULE_ENDPOINT, { params });
  return response.data.data;
}

/**
 * 취업규칙 상세 조회
 * GET /api/v1/work-rules/{id}
 */
export async function getWorkRule(id: string): Promise<WorkRule> {
  const response = await apiClient.getInstance().get<{
    success: boolean;
    data: WorkRule;
  }>(`${WORK_RULE_ENDPOINT}/${id}`);
  return response.data.data;
}

/**
 * 취업규칙 수정
 * PUT /api/v1/work-rules/{id}
 */
export async function updateWorkRule(id: string, data: WorkRuleUpdate): Promise<WorkRule> {
  const response = await apiClient.getInstance().put<{
    success: boolean;
    data: WorkRule;
    meta?: { message: string };
  }>(`${WORK_RULE_ENDPOINT}/${id}`, data);
  return response.data.data;
}

/**
 * 취업규칙 삭제
 * DELETE /api/v1/work-rules/{id}
 */
export async function deleteWorkRule(id: string): Promise<void> {
  await apiClient.getInstance().delete<{
    success: boolean;
    data: null;
    meta?: { message: string };
  }>(`${WORK_RULE_ENDPOINT}/${id}`);
}

/**
 * AI 초안 생성
 * POST /api/v1/work-rules/{id}/generate
 */
export async function generateAiDraft(
  id: string,
  data: WorkRuleGenerateRequest
): Promise<WorkRule> {
  const response = await apiClient.getInstance().post<{
    success: boolean;
    data: WorkRule;
    meta?: { message: string };
  }>(`${WORK_RULE_ENDPOINT}/${id}/generate`, data);
  return response.data.data;
}

/**
 * 취업규칙 개정 (새 버전 생성)
 * POST /api/v1/work-rules/{id}/revise
 */
export async function reviseWorkRule(
  id: string,
  data: WorkRuleReviseRequest
): Promise<WorkRule> {
  const response = await apiClient.getInstance().post<{
    success: boolean;
    data: WorkRule;
    meta?: { message: string };
  }>(`${WORK_RULE_ENDPOINT}/${id}/revise`, data);
  return response.data.data;
}

/**
 * 취업규칙 다운로드 (Word/PDF)
 * GET /api/v1/work-rules/{id}/download/{type}
 */
export async function downloadWorkRule(
  id: string,
  type: 'docx' | 'pdf'
): Promise<DownloadResponse> {
  const response = await apiClient.getInstance().get<{
    success: boolean;
    data: DownloadResponse;
  }>(`${WORK_RULE_ENDPOINT}/${id}/download/${type}`);
  return response.data.data;
}

/**
 * 고용노동부 신고서류 생성
 * POST /api/v1/work-rules/{id}/file
 */
export async function generateFilingDocument(id: string): Promise<DownloadResponse> {
  const response = await apiClient.getInstance().post<{
    success: boolean;
    data: DownloadResponse;
  }>(`${WORK_RULE_ENDPOINT}/${id}/file`);
  return response.data.data;
}

/**
 * 동의 절차 체크리스트 조회
 * GET /api/v1/work-rules/consent-checklist
 */
export async function getConsentChecklist(): Promise<ConsentChecklistResponse> {
  const response = await apiClient.getInstance().get<{
    success: boolean;
    data: ConsentChecklistResponse;
  }>(`${WORK_RULE_ENDPOINT}/consent-checklist`);
  return response.data.data;
}

// API 함수들을 객체로 내보내기
export const workRuleApi = {
  getTemplates,
  createWorkRule,
  getWorkRules,
  getWorkRule,
  updateWorkRule,
  deleteWorkRule,
  generateAiDraft,
  reviseWorkRule,
  downloadWorkRule,
  generateFilingDocument,
  getConsentChecklist,
};
