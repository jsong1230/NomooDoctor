/**
 * 직원 관련 타입 정의
 */

// 직원 정보
export interface Employee {
  id: string;
  name: string;
  email?: string;
  phone?: string;
  employment_type: 'regular' | 'contract' | 'part_time' | 'temporary';
  position?: string;
  department?: string;
  start_date: string;
  end_date?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

// 직원 등록 요청
export interface CreateEmployeeRequest {
  name: string;
  email?: string;
  phone?: string;
  employment_type: 'regular' | 'contract' | 'part_time' | 'temporary';
  position?: string;
  department?: string;
  start_date: string;
  end_date?: string;
}

// 직원 수정 요청
export interface UpdateEmployeeRequest {
  name?: string;
  email?: string;
  phone?: string;
  employment_type?: 'regular' | 'contract' | 'part_time' | 'temporary';
  position?: string;
  department?: string;
  end_date?: string;
}

// 직원 목록 응답
export interface EmployeeListResponse {
  data: Employee[];
  pagination?: {
    cursor: string | null;
    hasNext: boolean;
    limit: number;
  };
}
