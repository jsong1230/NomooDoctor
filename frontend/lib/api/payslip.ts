/**
 * 급여명세서 API 클라이언트
 * F-07-payslip 설계서의 API 스펙을 참조하여 구현
 */

import { apiClient } from '../api-client';
import type {
  Payslip,
  CreatePayslipRequest,
  SendPayslipRequest,
} from '@/types/payslip';

const PAYSLIP_ENDPOINT = '/payslips';

/**
 * 급여명세서 생성
 * POST /api/v1/payslips
 */
async function createPayslip(data: CreatePayslipRequest): Promise<Payslip> {
  const response = await apiClient.getInstance().post<{
    success: boolean;
    data: Payslip;
    message: string;
  }>(PAYSLIP_ENDPOINT, data);
  return response.data.data;
}

/**
 * 급여명세서 목록 조회
 * GET /api/v1/payslips
 */
async function listPayslips(params?: {
  year?: number;
  month?: number;
  employee_id?: string;
  page?: number;
  per_page?: number;
}): Promise<Payslip[]> {
  const response = await apiClient.getInstance().get<{
    success: boolean;
    data: Payslip[];
    message: string;
  }>(PAYSLIP_ENDPOINT, { params });
  return response.data.data;
}

/**
 * 급여명세서 상세 조회
 * GET /api/v1/payslips/{id}
 */
async function getPayslip(id: string): Promise<Payslip> {
  const response = await apiClient.getInstance().get<{
    success: boolean;
    data: Payslip;
    message: string;
  }>(`${PAYSLIP_ENDPOINT}/${id}`);
  return response.data.data;
}

/**
 * 급여명세서 PDF 다운로드
 * GET /api/v1/payslips/{id}/pdf
 */
async function downloadPayslipPdf(id: string): Promise<Blob> {
  const response = await apiClient.getInstance().get<Blob>(
    `${PAYSLIP_ENDPOINT}/${id}/pdf`,
    { responseType: 'blob' }
  );
  return response.data;
}

/**
 * 급여명세서 발송 (이메일/카카오톡)
 * POST /api/v1/payslips/{id}/send
 */
async function sendPayslip(id: string, data: SendPayslipRequest): Promise<Payslip> {
  const response = await apiClient.getInstance().post<{
    success: boolean;
    data: Payslip;
    message: string;
  }>(`${PAYSLIP_ENDPOINT}/${id}/send`, data);
  return response.data.data;
}

/**
 * 직원별 급여명세서 목록 조회
 * GET /api/v1/employees/{employeeId}/payslips
 */
async function getEmployeePayslips(employeeId: string): Promise<Payslip[]> {
  const response = await apiClient.getInstance().get<{
    success: boolean;
    data: Payslip[];
    message: string;
  }>(`/employees/${employeeId}/payslips`);
  return response.data.data;
}

// API 함수들을 객체로 내보내기
export const payslipApi = {
  createPayslip,
  listPayslips,
  getPayslip,
  downloadPayslipPdf,
  sendPayslip,
  getEmployeePayslips,
};
