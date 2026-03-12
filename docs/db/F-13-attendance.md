# F-13 근태 관리 -- DB 스키마 확정본

## 개요
F-13 근태 관리 기능의 데이터베이스 스키마. work_records 테이블에 updated_at 컬럼 추가 및 UNIQUE 제약 추가.

## 변경 사항

### 마이그레이션: 005_f13_attendance_schema.py

**Revision ID**: 005
**Revises**: 004
**Create Date**: 2026-03-12

#### 변경 내용

1. **updated_at 컬럼 추가**
   - 타입: TIMESTAMPTZ (PostgreSQL 타임존 포함 타임스탬프)
   - Nullable: YES
   - 기본값: NULL
   - 용도: 근무 기록 수정 시 갱신 시간 추적

2. **UNIQUE 제약 추가**
   - 인덱스명: idx_work_records_unique_date
   - 컬럼: (employee_id, work_date)
   - 유형: B-Tree UNIQUE
   - 용도: 1일 1근무 기록 원칙 강제, 중복 입력 방지

---

## work_records 테이블 최종 스키마

### 컬럼 정의

| 컬럼명 | 타입 | Null | 기본값 | 제약조건 | 설명 |
|--------|------|------|--------|---------|------|
| id | UUID | NO | uuid_generate_v4() | PK | 근무 기록 고유 식별자 |
| employee_id | UUID | NO | - | FK(employees) | 직원 ID |
| company_id | UUID | NO | - | FK(companies) | 사업장 ID |
| work_date | DATE | NO | - | - | 근무 날짜 |
| scheduled_start | TIME | NO | - | - | 예정 출근 시간 (HH:MM:SS) |
| scheduled_end | TIME | NO | - | - | 예정 퇴근 시간 (HH:MM:SS) |
| actual_start | TIME | YES | NULL | - | 실제 출근 시간 (HH:MM:SS) |
| actual_end | TIME | YES | NULL | - | 실제 퇴근 시간 (HH:MM:SS) |
| break_minutes | INTEGER | NO | 60 | CHECK >= 0 AND <= 480 | 휴게시간 (분) |
| overtime_minutes | INTEGER | NO | 0 | CHECK >= 0 | 연장근무시간 (분, 자동 계산) |
| night_minutes | INTEGER | NO | 0 | CHECK >= 0 | 야간근무시간 (분, 자동 계산) |
| holiday_minutes | INTEGER | NO | 0 | CHECK >= 0 | 휴일근무시간 (분, 자동 계산) |
| is_holiday | BOOLEAN | NO | FALSE | - | 휴일 여부 |
| memo | TEXT | YES | NULL | - | 비고 |
| created_at | TIMESTAMPTZ | NO | CURRENT_TIMESTAMP | - | 생성 일시 |
| updated_at | TIMESTAMPTZ | YES | NULL | - | 수정 일시 (신규) |

### CREATE TABLE 문

```sql
CREATE TABLE work_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    employee_id UUID NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
    company_id UUID NOT NULL REFERENCES companies(id),
    work_date DATE NOT NULL,
    scheduled_start TIME NOT NULL,
    scheduled_end TIME NOT NULL,
    actual_start TIME,
    actual_end TIME,
    break_minutes INTEGER NOT NULL DEFAULT 60
        CHECK (break_minutes >= 0 AND break_minutes <= 480),
    overtime_minutes INTEGER NOT NULL DEFAULT 0
        CHECK (overtime_minutes >= 0),
    night_minutes INTEGER NOT NULL DEFAULT 0
        CHECK (night_minutes >= 0),
    holiday_minutes INTEGER NOT NULL DEFAULT 0
        CHECK (holiday_minutes >= 0),
    is_holiday BOOLEAN NOT NULL DEFAULT FALSE,
    memo TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ
);
```

### 인덱스

| 인덱스명 | 컬럼 | 유형 | 유니크 | 용도 |
|---------|------|------|--------|------|
| work_records_pkey | id | B-Tree | YES | Primary Key |
| idx_work_records_employee_date | (employee_id, work_date) | B-Tree | NO | 직원별 날짜 조회 최적화 |
| idx_work_records_company_date | (company_id, work_date) | B-Tree | NO | 사업장별 날짜 조회 최적화 |
| idx_work_records_unique_date | (employee_id, work_date) | B-Tree | YES | 중복 방지 (신규) |

**CREATE INDEX 문**:

```sql
-- 이미 존재 (001 마이그레이션)
CREATE INDEX idx_work_records_employee_date ON work_records(employee_id, work_date);
CREATE INDEX idx_work_records_company_date ON work_records(company_id, work_date);

-- 신규 (005 마이그레이션)
CREATE UNIQUE INDEX idx_work_records_unique_date ON work_records(employee_id, work_date);
```

---

## 관계도

```
employees (1) ----< (N) work_records
    ↑
    | FK(employee_id)
    |
companies (1) ----< (N) work_records
    |
    └─ FK(company_id)
```

---

## 마이그레이션 SQL

### Upgrade (005 마이그레이션)

```sql
-- 1. updated_at 컬럼 추가
ALTER TABLE work_records
ADD COLUMN updated_at TIMESTAMP WITH TIME ZONE;

-- 2. UNIQUE 인덱스 생성
CREATE UNIQUE INDEX idx_work_records_unique_date
ON work_records(employee_id, work_date);
```

### Downgrade

```sql
-- 1. UNIQUE 인덱스 삭제
DROP INDEX IF EXISTS idx_work_records_unique_date;

-- 2. updated_at 컬럼 삭제
ALTER TABLE work_records
DROP COLUMN IF EXISTS updated_at;
```

---

## 데이터 무결성

### Foreign Key 제약

1. **employee_id → employees.id**
   - ON DELETE CASCADE: 직원 삭제 시 근무 기록도 함께 삭제
   - 활성 직원 확인은 애플리케이션 레벨에서 수행

2. **company_id → companies.id**
   - ON DELETE: 제약 없음 (Soft Delete 사용)
   - 사업장별 데이터 격리 확인

### Check 제약

1. break_minutes: 0~480분 범위 검증
2. overtime_minutes, night_minutes, holiday_minutes: 음수 방지 (>= 0)

### Unique 제약

1. **(employee_id, work_date)**: 동일 직원의 같은 날짜 근무 기록 중복 방지
   - 1일 1근무 기록 원칙 강제

---

## 성능 설계

### 인덱스 전략

1. **조회 성능**
   - `idx_work_records_employee_date`: 직원별 근무 기록 조회 O(log N)
   - `idx_work_records_company_date`: 사업장별 날짜 범위 조회 O(log N)

2. **삽입 성능**
   - `idx_work_records_unique_date`: 중복 확인 (INSERT 전 UNIQUE 검증) O(log N)

3. **집계 쿼리**
   - company_date 인덱스로 월별 집계 최적화
   - WHERE company_id = ? AND work_date >= ? AND work_date <= ?

### 예상 쿼리 성능

**시나리오**: 50명 직원, 월 30일 근무, 총 1,500건

```sql
-- 직원별 월 조회 (3ms)
SELECT * FROM work_records
WHERE employee_id = ? AND work_date BETWEEN ? AND ?;

-- 사업장별 월 조회 (5ms)
SELECT * FROM work_records
WHERE company_id = ? AND work_date BETWEEN ? AND ?;

-- 중복 확인 (1ms)
SELECT 1 FROM work_records
WHERE employee_id = ? AND work_date = ?;
```

---

## 마이그레이션 이력

| Revision | 설명 | 상태 |
|----------|------|------|
| 001 | 초기 스키마 (work_records 생성) | 완료 |
| 002 | Company Soft Delete | 완료 |
| 003 | pgvector + Law Vectors | 완료 |
| 004 | Work Rule 추가 컬럼 | 완료 |
| 005 | F-13 근태 관리 (updated_at + UNIQUE) | 완료 |
| 006 | F-09 퇴직금/해고 | 예정 |
| 007 | ... | 예정 |

---

## 데이터 분석 쿼리

### 1. 월별 근무 시간 집계

```sql
SELECT
    employee_id,
    COUNT(DISTINCT work_date) as work_days,
    SUM(CASE WHEN actual_start IS NOT NULL
            THEN EXTRACT(EPOCH FROM (actual_end::time - actual_start::time)) / 60 - break_minutes
            ELSE 0 END) as total_work_minutes,
    SUM(overtime_minutes) as total_overtime_minutes,
    SUM(night_minutes) as total_night_minutes,
    SUM(holiday_minutes) as total_holiday_minutes
FROM work_records
WHERE company_id = ?
    AND EXTRACT(YEAR FROM work_date) = ?
    AND EXTRACT(MONTH FROM work_date) = ?
GROUP BY employee_id;
```

### 2. 지각/조퇴 현황

```sql
SELECT
    employee_id,
    COUNT(CASE WHEN actual_start > scheduled_start THEN 1 END) as late_count,
    COUNT(CASE WHEN actual_end < scheduled_end THEN 1 END) as early_leave_count
FROM work_records
WHERE company_id = ?
    AND EXTRACT(YEAR FROM work_date) = ?
    AND EXTRACT(MONTH FROM work_date) = ?
GROUP BY employee_id;
```

### 3. 월별 연장근무 추세

```sql
SELECT
    EXTRACT(YEAR FROM work_date)::int as year,
    EXTRACT(MONTH FROM work_date)::int as month,
    SUM(overtime_minutes) as total_overtime_minutes
FROM work_records
WHERE employee_id = ?
    AND work_date BETWEEN ? AND ?
GROUP BY year, month
ORDER BY year, month;
```

### 4. 주간 평균 근무시간

```sql
SELECT
    EXTRACT(DOW FROM work_date)::int as day_of_week,
    AVG(CASE WHEN actual_start IS NOT NULL
           THEN EXTRACT(EPOCH FROM (actual_end::time - actual_start::time)) / 60 - break_minutes
           ELSE 0 END) as avg_work_minutes
FROM work_records
WHERE employee_id = ? AND work_date BETWEEN ? AND ?
GROUP BY day_of_week
ORDER BY day_of_week;
```

---

## 기타

### 컬럼 선택 근거

- **updated_at 추가**: 수정 이력 추적 필요, 데이터 감사(Audit) 지원
- **UNIQUE (employee_id, work_date)**: 1일 1근무 기록 원칙, 중복 입력 방지

### 데이터 타입 선택

- **DATE vs TIMESTAMP**: 근무일은 DATE (시간 불필요)
- **TIME vs TIME WITHOUT TZ**: 출퇴근 시간은 현지 시간 (회사 지역), TZ 불필요
- **TIMESTAMPTZ**: 생성/수정 일시는 글로벌 타임스탬프

### 성능 트레이드오프

- **UNIQUE 인덱스 오버헤드**: INSERT 시 추가 검증 (무시할 수준)
- **메모리**: 3개 인덱스 유지 (총 ~50MB/월)
- **선택**: 데이터 무결성 우선

---

## 호환성

- PostgreSQL 13+ 지원
- SQLAlchemy 2.0+ ORM 사용
- asyncpg 드라이버 (비동기)

---

## 참고

- 설계: docs/specs/F-13-attendance/design.md
- API: docs/api/F-13-attendance.md
- 테스트: docs/tests/F-13-attendance/
