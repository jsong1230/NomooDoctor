/**
 * 사업장 관련 타입 정의
 */

// 업종 타입
export type IndustryType =
  | 'manufacturing'   // 제조업
  | 'food_service'    // 요식업
  | 'retail'          // 소매업
  | 'service'         // 서비스업
  | 'it'              // IT/정보통신
  | 'construction'    // 건설업
  | 'healthcare'      // 의료업
  | 'other';          // 기타

// 사업장 정보
export interface Company {
  id: string;
  owner_id: string;
  business_name: string;
  business_number: string;
  representative_name: string;
  industry_type: IndustryType;
  employee_count: number;
  address?: string;
  postal_code?: string;
  phone?: string;
  work_rule_required: boolean;
  created_at: string;
  updated_at: string;
}

// 사업장 등록 요청
export interface CreateCompanyRequest {
  business_name: string;
  business_number: string;
  representative_name: string;
  industry_type: IndustryType;
  employee_count: number;
  address?: string;
  postal_code?: string;
  phone?: string;
}

// 사업장 수정 요청
export interface UpdateCompanyRequest {
  business_name: string;
  representative_name: string;
  industry_type: IndustryType;
  employee_count: number;
  address?: string;
  postal_code?: string;
  phone?: string;
}

// 사업장 삭제 요청
export interface DeleteCompanyRequest {
  confirmation: string;
}

// 사업장 목록 응답
export interface CompanyListResponse {
  companies: Company[];
  pagination: {
    cursor: string | null;
    hasNext: boolean;
    limit: number;
    totalCount: number;
  };
}

// 사업장 선택 응답
export interface SelectCompanyResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  company: {
    id: string;
    business_name: string;
  };
}

// 업종 옵션
export const INDUSTRY_OPTIONS: Array<{ value: IndustryType; label: string }> = [
  { value: 'manufacturing', label: '제조업' },
  { value: 'food_service', label: '요식업' },
  { value: 'retail', label: '소매업' },
  { value: 'service', label: '서비스업' },
  { value: 'it', label: 'IT/정보통신' },
  { value: 'construction', label: '건설업' },
  { value: 'healthcare', label: '의료업' },
  { value: 'other', label: '기타' },
];

// 업종 라벨 변환 함수
export function getIndustryLabel(type: IndustryType): string {
  const option = INDUSTRY_OPTIONS.find(opt => opt.value === type);
  return option?.label || type;
}
