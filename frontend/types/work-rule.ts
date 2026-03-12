/**
 * 취업규칙 관련 타입 정의
 */

// 취업규칙 상태
export type WorkRuleStatus = 'draft' | 'under_review' | 'active' | 'superseded';

// 업종 타입 (설계서 기준)
export type IndustryType = 'manufacturing' | 'food_service' | 'service' | 'it';

// 취업규칙 섹션
export interface WorkRuleSection {
  section_number: number;
  title: string;
  content_html: string;
  is_required: boolean;
  law_reference?: string;
}

// 취업규칙 내용
export interface WorkRuleContent {
  sections: WorkRuleSection[];
}

// 취업규칙 기본 정보
export interface WorkRule {
  id: string;
  company_id: string;
  version: number;
  status: WorkRuleStatus;
  industry_type: string;
  content: WorkRuleContent;
  effective_date?: string;
  approval_date?: string;
  worker_consent_count?: number;
  total_worker_count?: number;
  revision_reason?: string;
  ai_generated: boolean;
  ai_model?: string;
  docx_url?: string;
  pdf_url?: string;
  filed_at?: string;
  created_at: string;
  updated_at: string;
}

// 취업규칙 목록 아이템 (축약된 정보)
export interface WorkRuleListItem {
  id: string;
  version: number;
  status: WorkRuleStatus;
  industry_type: string;
  effective_date?: string;
  approval_date?: string;
  worker_consent_count?: number;
  ai_generated: boolean;
  filed_at?: string;
  created_at: string;
  updated_at: string;
}

// 취업규칙 생성 요청
export interface WorkRuleCreate {
  industry_type: IndustryType;
  effective_date?: string;
}

// 취업규칙 업데이트 요청
export interface WorkRuleUpdate {
  content?: WorkRuleContent;
  effective_date?: string;
  status?: WorkRuleStatus;
  worker_consent_count?: number;
  total_worker_count?: number;
  approval_date?: string;
}

// AI 초안 생성 요청
export interface WorkRuleGenerateRequest {
  industry_type?: IndustryType;
  additional_context?: string;
}

// 취업규칙 개정 요청
export interface WorkRuleReviseRequest {
  revision_reason: string;
  effective_date?: string;
}

// 다운로드 응답
export interface DownloadResponse {
  download_url: string;
  filename: string;
  expires_at: string;
}

// 동의 절차 체크리스트 스텝
export interface ConsentChecklistStep {
  step: number;
  title: string;
  description: string;
  law_reference: string;
  is_required: boolean;
}

// 동의 절차 체크리스트 응답
export interface ConsentChecklistResponse {
  checklist: ConsentChecklistStep[];
  employee_count: number;
  consent_threshold: number;
  consent_type: string;
}

// 템플릿 섹션
export interface TemplateSection {
  section_number: number;
  title: string;
  description: string;
}

// 템플릿 응답
export interface TemplateResponse {
  industry_type: string;
  industry_name: string;
  description: string;
  sections: TemplateSection[];
}

// 업종 옵션
export const INDUSTRY_OPTIONS: Array<{ value: IndustryType; label: string }> = [
  { value: 'manufacturing', label: '제조업' },
  { value: 'food_service', label: '요식업' },
  { value: 'service', label: '서비스업' },
  { value: 'it', label: 'IT/정보통신' },
];

// 상태 라벨
export const STATUS_LABELS: Record<WorkRuleStatus, string> = {
  draft: '작성중',
  under_review: '검토중',
  active: '시행중',
  superseded: '폐지됨',
};

// 업종 라벨 변환 함수
export function getIndustryLabel(type: string): string {
  const option = INDUSTRY_OPTIONS.find(opt => opt.value === type as IndustryType);
  return option?.label || type;
}

// 상태 라벨 변환 함수
export function getStatusLabel(status: WorkRuleStatus): string {
  return STATUS_LABELS[status] || status;
}
