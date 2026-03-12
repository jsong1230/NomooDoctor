/**
 * 사업장 API 클라이언트
 * design.md의 API 스펙을 참조하여 구현
 */

import { axiosInstance } from '../api-client';
import type {
  Company,
  CreateCompanyRequest,
  UpdateCompanyRequest,
  DeleteCompanyRequest,
  CompanyListResponse,
  SelectCompanyResponse,
} from '@/types/company';

const COMPANY_ENDPOINT = '/companies';

/**
 * 사업장 등록
 * POST /api/v1/companies
 */
export async function createCompany(data: CreateCompanyRequest): Promise<Company> {
  const response = await axiosInstance.post<{ success: boolean; data: Company; message: string }>(
    COMPANY_ENDPOINT,
    data
  );
  return response.data.data;
}

/**
 * 사업장 목록 조회
 * GET /api/v1/companies
 */
export async function getCompanies(params?: {
  limit?: number;
  cursor?: string;
  is_deleted?: boolean;
}): Promise<CompanyListResponse> {
  const response = await axiosInstance.get<{ success: boolean; data: Company[]; pagination: CompanyListResponse['pagination'] }>(
    COMPANY_ENDPOINT,
    { params }
  );
  return {
    companies: response.data.data,
    pagination: response.data.pagination,
  };
}

/**
 * 사업장 상세 조회
 * GET /api/v1/companies/{id}
 */
export async function getCompany(id: string): Promise<Company> {
  const response = await axiosInstance.get<{ success: boolean; data: Company }>(
    `${COMPANY_ENDPOINT}/${id}`
  );
  return response.data.data;
}

/**
 * 사업장 정보 수정
 * PUT /api/v1/companies/{id}
 */
export async function updateCompany(id: string, data: UpdateCompanyRequest): Promise<Company> {
  const response = await axiosInstance.put<{ success: boolean; data: Company; message: string }>(
    `${COMPANY_ENDPOINT}/${id}`,
    data
  );
  return response.data.data;
}

/**
 * 사업장 삭제 (Soft Delete)
 * DELETE /api/v1/companies/{id}
 */
export async function deleteCompany(id: string, data: DeleteCompanyRequest): Promise<void> {
  await axiosInstance.delete<{ success: boolean; data: null; message: string }>(
    `${COMPANY_ENDPOINT}/${id}`,
    { data }
  );
}

/**
 * 현재 사업장 선택 (컨텍스트 변경)
 * POST /api/v1/companies/{id}/select
 */
export async function selectCompany(id: string): Promise<SelectCompanyResponse> {
  const response = await axiosInstance.post<{ success: boolean; data: SelectCompanyResponse; message: string }>(
    `${COMPANY_ENDPOINT}/${id}/select`
  );
  return response.data.data;
}

// API 함수들을 객체로 내보내기
export const companyApi = {
  createCompany,
  getCompanies,
  getCompany,
  updateCompany,
  deleteCompany,
  selectCompany,
};
