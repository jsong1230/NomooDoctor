/**
 * 근태 관리 관련 타입 정의
 */

// 근무 기록
export interface WorkRecord {
  id: string;
  employee_id: string;
  employee_name: string;
  work_date: string; // YYYY-MM-DD
  scheduled_start: string; // HH:MM
  scheduled_end: string; // HH:MM
  actual_start: string | null; // HH:MM
  actual_end: string | null; // HH:MM
  break_minutes: number;
  total_work_minutes: number;
  overtime_minutes: number;
  night_minutes: number;
  holiday_minutes: number;
  is_holiday: boolean;
  memo: string | null;
  created_at: string;
  updated_at: string | null;
}

// 근무 기록 생성 요청
export interface WorkRecordCreate {
  employee_id: string;
  work_date: string;
  scheduled_start: string;
  scheduled_end: string;
  actual_start: string | null;
  actual_end: string | null;
  break_minutes: number;
  is_holiday: boolean;
  memo: string | null;
}

// 근무 기록 수정 요청
export interface WorkRecordUpdate {
  work_date?: string;
  scheduled_start?: string;
  scheduled_end?: string;
  actual_start?: string | null;
  actual_end?: string | null;
  break_minutes?: number;
  is_holiday?: boolean;
  memo?: string | null;
}

// 월별 요약 - 직원별
export interface EmployeeMonthlySummary {
  employee_id: string;
  employee_name: string;
  employment_type: string;
  total_work_days: number;
  total_work_minutes: number;
  total_overtime_minutes: number;
  total_night_minutes: number;
  total_holiday_minutes: number;
  total_break_minutes: number;
  late_count: number;
  early_leave_count: number;
  absent_count: number;
}

// 월별 요약 - 회사 전체
export interface CompanyTotalSummary {
  total_employees: number;
  avg_work_minutes_per_day: number;
  total_overtime_minutes: number;
  total_night_minutes: number;
  total_holiday_minutes: number;
}

// 월별 요약 응답
export interface MonthlySummary {
  year: number;
  month: number;
  employees: EmployeeMonthlySummary[];
  company_total: CompanyTotalSummary;
}

// 연장근무 추세
export interface OvertimeTrend {
  year: number;
  month: number;
  total_minutes: number;
}

// 패턴 분석 데이터
export interface PatternData {
  avg_start_time: string; // HH:MM
  avg_end_time: string; // HH:MM
  avg_work_minutes_per_day: number;
  avg_overtime_minutes_per_month: number;
  overtime_trend: OvertimeTrend[];
  weekday_distribution: Record<string, number>; // {"mon": 95, ...}
  weekly_hours_warning: boolean;
}

// 분석 알림
export interface AnalysisAlert {
  type: string;
  message: string;
}

// 직원 패턴 분석 응답
export interface EmployeeAnalysis {
  employee_id: string;
  employee_name: string;
  period: {
    from: string;
    to: string;
  };
  pattern: PatternData;
  alerts: AnalysisAlert[];
}

// 엑셀 업로드 결과
export interface ImportError {
  row: number;
  column?: string;
  value?: string;
  reason: string;
}

export interface ImportResult {
  total_rows: number;
  created: number;
  updated: number;
  skipped: number;
  errors: ImportError[];
}

// 목록 조회 응답
export interface WorkRecordListResponse {
  success: boolean;
  data: WorkRecord[];
  pagination: {
    cursor: string | null;
    hasNext: boolean;
    limit: number;
  };
}
