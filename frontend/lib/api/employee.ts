/**
 * 직원 API 클라이언트
 */

import { apiClient } from '../api-client';
import type {
  Employee,
  EmployeeListResponse,
  CreateEmployeeRequest,
  UpdateEmployeeRequest,
} from '@/types/employee';

const EMPLOYEE_ENDPOINT = '/employees';

/**
 * 직원 목록 조회
 * GET /api/v1/employees
 */
export async function getEmployees(params?: {
  limit?: number;
  cursor?: string;
  is_active?: boolean;
}): Promise<EmployeeListResponse> {
  const response = await apiClient
    .getInstance()
    .get<{ success: boolean; data: Employee[]; pagination: any }>(
      EMPLOYEE_ENDPOINT,
      { params }
    );
  return {
    data: response.data.data,
    pagination: response.data.pagination,
  };
}

/**
 * 직원 상세 조회
 * GET /api/v1/employees/{id}
 */
export async function getEmployee(id: string): Promise<Employee> {
  const response = await apiClient
    .getInstance()
    .get<{ success: boolean; data: Employee }>(
      `${EMPLOYEE_ENDPOINT}/${id}`
    );
  return response.data.data;
}

/**
 * 직원 등록
 * POST /api/v1/employees
 */
export async function createEmployee(data: CreateEmployeeRequest): Promise<Employee> {
  const response = await apiClient
    .getInstance()
    .post<{ success: boolean; data: Employee }>(
      EMPLOYEE_ENDPOINT,
      data
    );
  return response.data.data;
}

/**
 * 직원 수정
 * PUT /api/v1/employees/{id}
 */
export async function updateEmployee(
  id: string,
  data: UpdateEmployeeRequest
): Promise<Employee> {
  const response = await apiClient
    .getInstance()
    .put<{ success: boolean; data: Employee }>(
      `${EMPLOYEE_ENDPOINT}/${id}`,
      data
    );
  return response.data.data;
}

/**
 * 직원 삭제
 * DELETE /api/v1/employees/{id}
 */
export async function deleteEmployee(id: string): Promise<void> {
  await apiClient
    .getInstance()
    .delete(`${EMPLOYEE_ENDPOINT}/${id}`);
}

// API 함수들을 객체로 내보내기
export const employeeApi = {
  getEmployees,
  getEmployee,
  createEmployee,
  updateEmployee,
  deleteEmployee,
};
