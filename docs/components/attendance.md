# 근태 관리 (Attendance) 컴포넌트 문서

## 개요

근태 관리 모듈은 직원의 근무 기록, 월별 요약, 근무 패턴 분석을 통합적으로 관리하는 프론트엔드 컴포넌트입니다.

## 컴포넌트 구조

### 1. AttendanceClient (`components/attendance/attendance-client.tsx`)

메인 클라이언트 컴포넌트로 다음을 담당합니다:
- 탭 관리 (근무 기록 / 월별 요약 / 패턴 분석)
- 데이터 조회 및 상태 관리
- 다이얼로그 제어
- 필터 상태 관리 (연도, 월, 직원)

**주요 기능:**
- 근무 기록 CRUD
- 월별 요약 조회
- 직원 패턴 분석
- 엑셀 파일 업로드

### 2. AttendanceTable (`components/attendance/attendance-table.tsx`)

근무 기록 테이블 컴포넌트

**컬럼:**
- 날짜
- 직원명
- 출근/퇴근 시간
- 근무시간 (시간/분)
- 연장근무 (분, 경고색)
- 야간근무 (분, 인디고색)
- 휴일근무 (분, 에러색)
- 상태 배지 (정상/지각/조퇴/결근)

**상태 배지:**
- 정상 (green): 예정시간 이내 근무
- 지각 (yellow): actual_start > scheduled_start
- 조퇴 (orange): actual_end < scheduled_end
- 결근 (red): 근무 기록 없음

### 3. RecordForm (`components/attendance/record-form.tsx`)

근무 기록 입력/수정 폼 (react-hook-form + zod)

**필드:**
- 직원 선택 (드롭다운)
- 근무일 (date input)
- 예정 출근/퇴근 (HH:MM 텍스트)
- 실제 출근/퇴근 (HH:MM 텍스트)
- 휴게시간 (분, 0-480)
- 휴일 여부 (체크박스)
- 비고 (텍스트에어리어)

**실시간 미리보기:**
- 근무시간 계산
- 연장근무 계산
- 야간근무 계산 (22:00~06:00)

### 4. RecordFormDialog (`components/attendance/record-form-dialog.tsx`)

RecordForm을 감싸는 모달 다이얼로그

### 5. MonthlySummaryComponent (`components/attendance/monthly-summary.tsx`)

월별 요약 정보 표시

**구성:**
- 사업장 전체 통계 카드
  - 직원 수
  - 일평균 근무시간
  - 총 연장/야간/휴일근무
- 직원별 요약 테이블
  - 근무일, 근무시간, 연장/야간/휴일
  - 지각/조퇴/결근 카운트

### 6. AnalysisChart (`components/attendance/analysis-chart.tsx`)

근무 패턴 분석 차트 (recharts 미설치로 div 기반 bar chart)

**표시 정보:**
- 평균 출퇴근 시간
- 일평균 근무시간
- 월평균 연장근무
- 월별 연장근무 추세 (bar chart)
- 요일별 근무 분포 (bar chart)
- 경고 알림 (주 52시간 초과 등)

### 7. ExcelUpload (`components/attendance/excel-upload.tsx`)

엑셀/CSV 파일 업로드 컴포넌트

**기능:**
- 드래그앤드롭 영역
- 파일 선택 버튼
- 파일 크기/형식 검증 (xlsx, csv, 최대 10MB)
- 업로드 결과 표시 (성공/실패 건수 + 에러 상세)
- 템플릿 다운로드 버튼

## API 클라이언트 (`lib/api/attendance.ts`)

### 근무 기록

```typescript
createWorkRecord(data: WorkRecordCreate): Promise<WorkRecord>
getWorkRecords(params?: {...}): Promise<WorkRecordListResponse>
getWorkRecord(id: string): Promise<WorkRecord>
updateWorkRecord(id: string, data: WorkRecordUpdate): Promise<WorkRecord>
deleteWorkRecord(id: string): Promise<void>
```

### 엑셀 업로드

```typescript
importWorkRecords(file: File): Promise<ImportResult>
downloadTemplate(): Promise<Blob>
```

### 집계/분석

```typescript
getMonthlySummary(params: {year, month, employee_id?}): Promise<MonthlySummary>
getEmployeeAnalysis(params: {employee_id, from_date?, to_date?}): Promise<EmployeeAnalysis>
```

## 상태 관리 (`lib/stores/attendance-store.ts`)

Zustand 스토어로 다음을 관리합니다:

```typescript
interface AttendanceState {
  // 데이터
  workRecords: WorkRecord[]
  currentRecord: WorkRecord | null
  monthlySummary: MonthlySummary | null
  employeeAnalysis: EmployeeAnalysis | null
  importResult: ImportResult | null

  // 필터
  selectedEmployeeId: string | null
  selectedYear: number
  selectedMonth: number

  // 액션
  setWorkRecords(records)
  addWorkRecord(record)
  updateWorkRecord(id, record)
  removeWorkRecord(id)
  setMonthlySummary(summary)
  setEmployeeAnalysis(analysis)
  ...
}
```

## 타입 정의 (`types/attendance.ts`)

### 주요 타입

```typescript
// 근무 기록
interface WorkRecord {
  id: string
  employee_id: string
  employee_name: string
  work_date: string         // YYYY-MM-DD
  scheduled_start: string   // HH:MM
  scheduled_end: string     // HH:MM
  actual_start: string | null
  actual_end: string | null
  break_minutes: number
  total_work_minutes: number
  overtime_minutes: number
  night_minutes: number
  holiday_minutes: number
  is_holiday: boolean
  memo: string | null
  created_at: string
  updated_at: string | null
}

// 월별 요약
interface MonthlySummary {
  year: number
  month: number
  employees: EmployeeMonthlySummary[]
  company_total: CompanyTotalSummary
}

// 직원 분석
interface EmployeeAnalysis {
  employee_id: string
  employee_name: string
  period: { from: string, to: string }
  pattern: PatternData
  alerts: AnalysisAlert[]
}
```

## 계산 로직

### 근무시간 계산

```
근무시간 = actual_end - actual_start - break_minutes
```

야근으로 자정을 넘기는 경우: `actual_end < actual_start` 시 `actual_end += 24시간`

### 연장근무 계산

```
소정근로시간 = scheduled_end - scheduled_start - break_minutes
연장근무 = max(0, 근무시간 - 소정근로시간)
휴일인 경우: 0
```

### 야간근무 계산 (22:00 ~ 06:00)

```
야간대 시간 = 당일 야간대(22:00~24:00) + 다음날 야간대(0:00~6:00)
```

## 디자인 토큰

### 색상

- 정상: `bg-green-100 text-green-800`
- 지각: `bg-yellow-100 text-yellow-800`
- 조퇴: `bg-orange-100 text-orange-800`
- 결근: `bg-red-100 text-red-800`
- 연장: `text-warning-600`
- 야간: `text-indigo-600`
- 휴일: `text-error-600`

### 간격

- 카드 간격: `gap-4`
- 섹션 간격: `gap-6` / `space-y-6`
- 테이블 셀 패딩: `px-4 py-3`

## 사용 예시

### 기본 렌더링

```tsx
import { AttendanceClient } from '@/components/attendance/attendance-client';

export default function Page() {
  return <AttendanceClient />;
}
```

### 개별 컴포넌트 사용

```tsx
import { AttendanceTable } from '@/components/attendance/attendance-table';

// 근무 기록 테이블
<AttendanceTable
  records={records}
  onRowClick={(record) => console.log(record)}
/>
```

## 브라우저 호환성

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## 성능 고려사항

1. **Server Component**: 페이지는 RSC로 유지
2. **Client Component**: 상태/이벤트 필요한 컴포넌트만 `'use client'`
3. **API 호출**: `apiClient.getInstance()`로 axios 싱글톤 사용
4. **리렌더링**: Zustand 스토어로 상태 최소화

## 주의사항

1. 시간 입력은 `HH:MM` 형식만 허용 (정규식 검증)
2. 휴게시간은 0-480분 범위만 허용
3. actual_end < actual_start인 경우 다음날로 간주
4. 파일 업로드는 10MB 제한
