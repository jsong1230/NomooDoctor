/**
 * 근태 관리 API 클라이언트
 * design.md의 API 스펙을 참조하여 구현
 */

import { apiClient } from '../api-client';
import type {
  WorkRecord,
  WorkRecordCreate,
  WorkRecordUpdate,
  MonthlySummary,
  EmployeeAnalysis,
  ImportResult,
  WorkRecordListResponse,
} from '@/types/attendance';

const ATTENDANCE_ENDPOINT = '/attendance';

/**
 * 근무 기록 생성
 * POST /api/v1/attendance/records
 */
export async function createWorkRecord(data: WorkRecordCreate): Promise<WorkRecord> {
  const response = await apiClient
    .getInstance()
    .post<{ success: boolean; data: WorkRecord }>(
      `${ATTENDANCE_ENDPOINT}/records`,
      data
    );
  return response.data.data;
}

/**
 * 근무 기록 목록 조회
 * GET /api/v1/attendance/records
 */
export async function getWorkRecords(params?: {
  employee_id?: string;
  from_date?: string;
  to_date?: string;
  year?: number;
  month?: number;
  limit?: number;
  cursor?: string;
}): Promise<WorkRecordListResponse> {
  const response = await apiClient
    .getInstance()
    .get<WorkRecordListResponse>(
      `${ATTENDANCE_ENDPOINT}/records`,
      { params }
    );
  return response.data;
}

/**
 * 근무 기록 단건 조회
 * GET /api/v1/attendance/records/{id}
 */
export async function getWorkRecord(id: string): Promise<WorkRecord> {
  const response = await apiClient
    .getInstance()
    .get<{ success: boolean; data: WorkRecord }>(
      `${ATTENDANCE_ENDPOINT}/records/${id}`
    );
  return response.data.data;
}

/**
 * 근무 기록 수정
 * PUT /api/v1/attendance/records/{id}
 */
export async function updateWorkRecord(id: string, data: WorkRecordUpdate): Promise<WorkRecord> {
  const response = await apiClient
    .getInstance()
    .put<{ success: boolean; data: WorkRecord }>(
      `${ATTENDANCE_ENDPOINT}/records/${id}`,
      data
    );
  return response.data.data;
}

/**
 * 근무 기록 삭제
 * DELETE /api/v1/attendance/records/{id}
 */
export async function deleteWorkRecord(id: string): Promise<void> {
  await apiClient
    .getInstance()
    .delete(`${ATTENDANCE_ENDPOINT}/records/${id}`);
}

/**
 * 엑셀 파일 업로드
 * POST /api/v1/attendance/import
 */
export async function importWorkRecords(file: File): Promise<ImportResult> {
  const formData = new FormData();
  formData.append('file', file);

  const response = await apiClient
    .getInstance()
    .post<{ success: boolean; data: ImportResult }>(
      `${ATTENDANCE_ENDPOINT}/import`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
  return response.data.data;
}

/**
 * 엑셀 템플릿 다운로드
 * GET /api/v1/attendance/import/template
 */
export async function downloadTemplate(): Promise<Blob> {
  const response = await apiClient
    .getInstance()
    .get(
      `${ATTENDANCE_ENDPOINT}/import/template`,
      {
        responseType: 'blob',
      }
    );
  return response.data;
}

/**
 * 월별 요약 조회
 * GET /api/v1/attendance/summary
 */
export async function getMonthlySummary(params: {
  year: number;
  month: number;
  employee_id?: string;
}): Promise<MonthlySummary> {
  const response = await apiClient
    .getInstance()
    .get<{ success: boolean; data: MonthlySummary }>(
      `${ATTENDANCE_ENDPOINT}/summary`,
      { params }
    );
  return response.data.data;
}

/**
 * 직원 패턴 분석
 * GET /api/v1/attendance/analysis
 */
export async function getEmployeeAnalysis(params: {
  employee_id: string;
  from_date?: string;
  to_date?: string;
}): Promise<EmployeeAnalysis> {
  const response = await apiClient
    .getInstance()
    .get<{ success: boolean; data: EmployeeAnalysis }>(
      `${ATTENDANCE_ENDPOINT}/analysis`,
      { params }
    );
  return response.data.data;
}

// API 함수들을 객체로 내보내기
export const attendanceApi = {
  createWorkRecord,
  getWorkRecords,
  getWorkRecord,
  updateWorkRecord,
  deleteWorkRecord,
  importWorkRecords,
  downloadTemplate,
  getMonthlySummary,
  getEmployeeAnalysis,
};
