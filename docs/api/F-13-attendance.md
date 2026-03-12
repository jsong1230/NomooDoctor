# F-13 근태 관리 API 스펙

## 개요
F-13 근태 관리 API는 직원의 근무 기록을 관리하고, 연장/야간/휴일 근무시간을 자동으로 계산하며, 엑셀/CSV 파일을 통한 일괄 업로드를 지원합니다.

## 엔드포인트 목록

### 1. POST /api/v1/attendance/records
**목적**: 근무 기록 생성 (단건)
**인증**: JWT (company_id 필수)
**상태코드**: 201 Created

**Request**:
```json
{
  "employee_id": "uuid",
  "work_date": "2026-03-01",
  "scheduled_start": "09:00",
  "scheduled_end": "18:00",
  "actual_start": "08:55",
  "actual_end": "20:30",
  "break_minutes": 60,
  "is_holiday": false,
  "memo": "프로젝트 마감"
}
```

**Response** (201):
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "employee_id": "uuid",
    "employee_name": "홍길동",
    "work_date": "2026-03-01",
    "scheduled_start": "09:00",
    "scheduled_end": "18:00",
    "actual_start": "08:55",
    "actual_end": "20:30",
    "break_minutes": 60,
    "total_work_minutes": 635,
    "overtime_minutes": 150,
    "night_minutes": 0,
    "holiday_minutes": 0,
    "is_holiday": false,
    "memo": "프로젝트 마감",
    "created_at": "2026-03-01T09:00:00Z",
    "updated_at": null
  }
}
```

**에러**:
- 400 E-1001: 입력값 검증 실패
- 404 E-4004: 직원을 찾을 수 없음
- 409 E-4010: 해당 날짜에 이미 근무 기록 존재

---

### 2. GET /api/v1/attendance/records
**목적**: 근무 기록 목록 조회
**인증**: JWT (company_id 필수)
**상태코드**: 200 OK

**Query Parameters**:
- `employee_id` (optional): 직원 필터
- `from_date` (optional): 시작일 (YYYY-MM-DD)
- `to_date` (optional): 종료일 (YYYY-MM-DD)
- `year` (optional): 연도 필터 (from/to 대신 사용)
- `month` (optional): 월 필터 (year와 함께 사용)
- `limit` (optional, default=50): 페이지 크기 (최대 200)
- `cursor` (optional): 커서 기반 페이지네이션

**Response** (200):
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "employee_id": "uuid",
      "employee_name": "홍길동",
      "work_date": "2026-03-01",
      "scheduled_start": "09:00",
      "scheduled_end": "18:00",
      "actual_start": "08:55",
      "actual_end": "20:30",
      "break_minutes": 60,
      "total_work_minutes": 635,
      "overtime_minutes": 150,
      "night_minutes": 0,
      "holiday_minutes": 0,
      "is_holiday": false,
      "memo": "프로젝트 마감",
      "created_at": "2026-03-01T09:00:00Z",
      "updated_at": null
    }
  ],
  "meta": {
    "pagination": {
      "cursor": "...",
      "hasNext": true,
      "limit": 50
    }
  }
}
```

---

### 3. GET /api/v1/attendance/records/{record_id}
**목적**: 근무 기록 단건 조회
**인증**: JWT (company_id 필수)
**상태코드**: 200 OK

**Response**: 2번 엔드포인트의 data 항목과 동일

**에러**:
- 404: 근무 기록을 찾을 수 없음

---

### 4. PUT /api/v1/attendance/records/{record_id}
**목적**: 근무 기록 수정
**인증**: JWT (company_id 필수)
**상태코드**: 200 OK

**Request**: 1번 엔드포인트와 동일 (부분 업데이트 지원, employee_id 제외)

**Response**: 1번 엔드포인트와 동일

---

### 5. DELETE /api/v1/attendance/records/{record_id}
**목적**: 근무 기록 삭제
**인증**: JWT (company_id 필수)
**상태코드**: 204 No Content

**에러**:
- 404: 근무 기록을 찾을 수 없음

---

### 6. POST /api/v1/attendance/records/batch
**목적**: 근무 기록 일괄 생성
**인증**: JWT (company_id 필수)
**상태코드**: 201 Created

**Request**:
```json
{
  "records": [
    {
      "employee_id": "uuid",
      "work_date": "2026-03-01",
      "scheduled_start": "09:00",
      "scheduled_end": "18:00",
      "actual_start": "09:00",
      "actual_end": "18:00",
      "break_minutes": 60,
      "is_holiday": false
    }
  ]
}
```

**Response** (201):
```json
{
  "success": true,
  "data": {
    "total": 10,
    "created": 8,
    "skipped": 2,
    "errors": [
      {
        "index": 3,
        "employee_id": "uuid",
        "work_date": "2026-03-03",
        "reason": "이미 근무 기록이 존재합니다."
      }
    ]
  }
}
```

---

### 7. POST /api/v1/attendance/import
**목적**: 엑셀/CSV 파일로 근무 기록 일괄 업로드
**인증**: JWT (company_id 필수)
**상태코드**: 200 OK
**Content-Type**: multipart/form-data

**Request Parameters**:
- `file`: xlsx 또는 csv 파일 (최대 10MB)

**Response** (200):
```json
{
  "success": true,
  "data": {
    "total_rows": 150,
    "created": 140,
    "updated": 5,
    "skipped": 5,
    "errors": [
      {
        "row": 12,
        "column": "actual_start",
        "value": "abc",
        "reason": "시간 형식이 올바르지 않습니다. (HH:MM)"
      }
    ]
  }
}
```

**에러**:
- 400 E-1001: 파일 형식 오류
- 413 E-1004: 파일 크기 초과 (10MB)

**엑셀/CSV 템플릿 컬럼**:
1. employee_name (필수): 직원명
2. work_date (필수): YYYY-MM-DD
3. scheduled_start (필수): HH:MM
4. scheduled_end (필수): HH:MM
5. actual_start (선택): HH:MM
6. actual_end (선택): HH:MM
7. break_minutes (선택): 정수, 기본값 60
8. is_holiday (선택): 예/아니오 또는 Y/N, 기본값 아니오
9. memo (선택): 비고

---

### 8. GET /api/v1/attendance/import/template
**목적**: 엑셀 업로드용 템플릿 다운로드
**인증**: JWT (company_id 필수)
**상태코드**: 200 OK
**Content-Type**: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet

**Response**: Excel 파일 (바이너리)

---

### 9. GET /api/v1/attendance/summary
**목적**: 월별 근무 기록 요약
**인증**: JWT (company_id 필수)
**상태코드**: 200 OK

**Query Parameters**:
- `year` (필수): 연도 (2020~2099)
- `month` (필수): 월 (1~12)
- `employee_id` (선택): 직원 필터

**Response** (200):
```json
{
  "success": true,
  "data": {
    "year": 2026,
    "month": 3,
    "employees": [
      {
        "employee_id": "uuid",
        "employee_name": "홍길동",
        "employment_type": "정규직",
        "total_work_days": 22,
        "total_work_minutes": 10560,
        "total_overtime_minutes": 600,
        "total_night_minutes": 120,
        "total_holiday_minutes": 480,
        "total_break_minutes": 1320,
        "late_count": 2,
        "early_leave_count": 0,
        "absent_count": 0
      }
    ],
    "company_total": {
      "total_employees": 15,
      "avg_work_minutes_per_day": 480,
      "total_overtime_minutes": 3200,
      "total_night_minutes": 800,
      "total_holiday_minutes": 1920
    }
  }
}
```

---

### 10. GET /api/v1/attendance/analysis
**목적**: 직원별 근무 패턴 분석
**인증**: JWT (company_id 필수)
**상태코드**: 200 OK

**Query Parameters**:
- `employee_id` (필수): 직원 ID
- `from_date` (선택): 분석 시작일 (기본값: 3개월 전)
- `to_date` (선택): 분석 종료일 (기본값: 오늘)

**Response** (200):
```json
{
  "success": true,
  "data": {
    "employee_id": "uuid",
    "employee_name": "홍길동",
    "period": {
      "from": "2026-01-01",
      "to": "2026-03-31"
    },
    "pattern": {
      "avg_start_time": "08:52",
      "avg_end_time": "18:15",
      "avg_work_minutes_per_day": 498,
      "avg_overtime_minutes_per_month": 320,
      "overtime_trend": [
        {
          "year": 2026,
          "month": 1,
          "total_minutes": 280
        }
      ],
      "weekday_distribution": {
        "mon": 95,
        "tue": 96,
        "wed": 97,
        "thu": 96,
        "fri": 94,
        "sat": 10,
        "sun": 2
      },
      "weekly_hours_warning": false
    },
    "alerts": [
      {
        "type": "overtime_high",
        "message": "최근 3개월 평균 연장근무가 월 20시간을 초과합니다."
      }
    ]
  }
}
```

**에러**:
- 404: 직원을 찾을 수 없음

---

## 시간 계산 로직

### 총 근무시간 (total_work_minutes)
- 공식: actual_end - actual_start - break_minutes
- 야간을 걸쳐서 다음날까지 근무하는 경우: actual_end < actual_start일 때 actual_end += 24시간 처리

### 연장근무 (overtime_minutes)
- 소정근로시간 = scheduled_end - scheduled_start - break_minutes
- 연장근무 = max(0, total_work_minutes - 소정근로시간)
- 휴일인 경우: 계산하지만 holiday_minutes와 중복 가능

### 야간근무 (night_minutes)
- 야간: 22:00 ~ 06:00 (다음날)
- 휴게시간은 야간 시간에서 비례 차감하지 않음
- 자정 경계 처리: 당일 야간대(22:00~24:00) + 다음날 야간대(0:00~6:00)

### 휴일근무 (holiday_minutes)
- is_holiday=true인 경우: total_work_minutes 전체가 휴일근무
- 연장근무와 중복 가능 (휴일 연장 = 휴일수당 + 연장수당)

---

## 에러 코드

| HTTP | 코드 | 상황 |
|------|------|------|
| 400 | E-1001 | 입력값 검증 실패 |
| 400 | E-1003 | 필수 필드 누락 |
| 400 | E-1004 | 파일 크기 초과 |
| 401 | E-2001 | 인증 실패 |
| 403 | E-2003 | 권한 없음 |
| 404 | E-4004 | 리소스를 찾을 수 없음 |
| 409 | E-4010 | 중복 데이터 |
| 422 | E-4011 | 비즈니스 로직 검증 실패 |
| 500 | E-5001 | 서버 오류 |

---

## 구현 상세

### WorkRecordRepository
근무 기록 데이터 접근 계층. 다음 메서드를 제공합니다:
- `get_by_id()`: ID로 조회
- `get_by_id_and_company()`: ID + company_id로 조회 (권한 확인)
- `get_by_employee_and_date()`: 직원 + 날짜로 조회 (중복 확인)
- `list_by_company()`: 사업장별 목록 조회 (커서 기반 페이지네이션)
- `create()`, `create_batch()`: 생성
- `update()`: 수정
- `delete()`: 삭제

### AttendanceService
근태 관리 비즈니스 로직. 다음 메서드를 제공합니다:
- `calculate_work_times()`: 시간 자동 계산 핵심 로직
- `create_record()`: 근무 기록 생성 (직원 확인, 중복 확인, 시간 계산)
- `update_record()`: 근무 기록 수정 (시간 재계산)
- `delete_record()`: 근무 기록 삭제
- `get_monthly_summary()`: 월별 요약 (지각/조퇴 포함)
- `get_employee_analysis()`: 패턴 분석

### ExcelImportService
엑셀/CSV 임포트 서비스. 다음 메서드를 제공합니다:
- `parse_file()`: 파일 파싱 (xlsx/csv 자동 판단)
- `validate_rows()`: 파싱된 행 검증 (직원 매칭, 중복 확인)
- `import_records()`: 유효한 행 일괄 임포트
- `generate_template()`: 엑셀 템플릿 생성

---

## 마이그레이션

### 005_f13_attendance_schema.py
- work_records 테이블에 `updated_at` 컬럼 추가 (TIMESTAMPTZ, nullable)
- `idx_work_records_unique_date` UNIQUE 인덱스 생성 (employee_id, work_date)

---

## 데이터베이스 스키마

### work_records 테이블 (수정)
| 컬럼 | 타입 | 제약조건 | 설명 |
|------|------|----------|------|
| id | UUID | PK | 기록 고유 식별자 |
| employee_id | UUID | FK | 직원 ID |
| company_id | UUID | FK | 사업장 ID |
| work_date | DATE | NOT NULL | 근무일 |
| scheduled_start | TIME | NOT NULL | 예정 출근시간 |
| scheduled_end | TIME | NOT NULL | 예정 퇴근시간 |
| actual_start | TIME | | 실제 출근시간 |
| actual_end | TIME | | 실제 퇴근시간 |
| break_minutes | INTEGER | DEFAULT 60 | 휴게시간 (분) |
| overtime_minutes | INTEGER | DEFAULT 0 | 연장근무시간 (분) |
| night_minutes | INTEGER | DEFAULT 0 | 야간근무시간 (분) |
| holiday_minutes | INTEGER | DEFAULT 0 | 휴일근무시간 (분) |
| is_holiday | BOOLEAN | DEFAULT FALSE | 휴일 여부 |
| memo | TEXT | | 비고 |
| created_at | TIMESTAMPTZ | NOT NULL | 생성일시 |
| updated_at | TIMESTAMPTZ | | 수정일시 (신규) |

**인덱스**:
- idx_work_records_employee_date (employee_id, work_date)
- idx_work_records_company_date (company_id, work_date)
- idx_work_records_unique_date (employee_id, work_date, UNIQUE)

---

## 사용 예시

### 1. 근무 기록 생성
```bash
curl -X POST http://localhost:8000/api/v1/attendance/records \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "employee_id": "...",
    "work_date": "2026-03-01",
    "scheduled_start": "09:00",
    "scheduled_end": "18:00",
    "actual_start": "08:55",
    "actual_end": "20:30",
    "break_minutes": 60
  }'
```

### 2. 월별 요약 조회
```bash
curl -X GET "http://localhost:8000/api/v1/attendance/summary?year=2026&month=3" \
  -H "Authorization: Bearer {token}"
```

### 3. 엑셀 업로드
```bash
curl -X POST http://localhost:8000/api/v1/attendance/import \
  -H "Authorization: Bearer {token}" \
  -F "file=@attendance.xlsx"
```

---

## 성능 고려사항

1. **인덱스**: (employee_id, work_date) UNIQUE 인덱스로 중복 확인 및 조회 최적화
2. **페이지네이션**: 커서 기반 페이지네이션으로 대용량 데이터 조회 최적화
3. **집계**: 월별 요약은 필터링된 레코드 기반 Python 메모리 계산 (쿼리 성능 고려)
4. **엑셀 업로드**: 최대 10MB / ~5,000행 제한으로 메모리 안정성 보장

---

## 연동

### F-05 급여 자동 계산기와의 연동
- GET /api/v1/attendance/summary로 월별 연장/야간/휴일 시간 합계 조회 가능
- 급여 계산 API에서 이 값을 기반으로 수당 계산

### F-10 컴플라이언스와의 연동
- 근태 미등록 감점: work_records 기록 부재 시 점수 차감 가능

---

## 테스트

### 단위 테스트 (test_attendance_calculation.py)
- 시간 계산 로직 검증 (정상, 연장, 야간, 휴일 등)

### 통합 테스트 (test_attendance_api.py)
- API 엔드포인트 전체 검증
- 중복 확인, 권한 검증 등
