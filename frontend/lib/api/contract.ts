/**
 * 계약서 및 전자서명 API 클라이언트
 */

import { apiClient } from '../api-client';
import type {
  Contract,
  SignRequestData,
  SignRequestResult,
  SignStatusResult,
} from '@/types/contract';

const ENDPOINT = '/contracts';

/** 계약서 목록 조회 */
export async function listContracts(params?: {
  employee_id?: string;
  status?: string;
  page?: number;
  per_page?: number;
}): Promise<Contract[]> {
  const client = apiClient.getInstance();
  const response = await client.get<{
    success: boolean;
    data: Contract[];
  }>(ENDPOINT, { params });
  return response.data.data;
}

/** 계약서 상세 조회 */
export async function getContract(id: string): Promise<Contract> {
  const client = apiClient.getInstance();
  const response = await client.get<{
    success: boolean;
    data: Contract;
  }>(`${ENDPOINT}/${id}`);
  return response.data.data;
}

/** 전자서명 요청 */
export async function sendSignRequest(
  contractId: string,
  data: SignRequestData
): Promise<SignRequestResult> {
  const client = apiClient.getInstance();
  const response = await client.post<{
    success: boolean;
    data: SignRequestResult;
  }>(`${ENDPOINT}/${contractId}/sign-request`, data);
  return response.data.data;
}

/** 서명 상태 조회 */
export async function getSignStatus(contractId: string): Promise<SignStatusResult> {
  const client = apiClient.getInstance();
  const response = await client.get<{
    success: boolean;
    data: SignStatusResult;
  }>(`${ENDPOINT}/${contractId}/sign-status`);
  return response.data.data;
}

/** 서명된 PDF 다운로드 */
export async function downloadSignedPdf(contractId: string): Promise<Blob> {
  const client = apiClient.getInstance();
  const response = await client.get(`${ENDPOINT}/${contractId}/signed-pdf`, {
    responseType: 'blob',
  });
  return response.data;
}

export const contractApi = {
  listContracts,
  getContract,
  sendSignRequest,
  getSignStatus,
  downloadSignedPdf,
};
